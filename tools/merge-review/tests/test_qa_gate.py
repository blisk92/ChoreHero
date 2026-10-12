#!/usr/bin/env python3
"""
test_qa_gate.py — QA-gate tests for the merge-review runner.

Focus:
  - AC parser handles both `AC:` line form (with [x] / [ ] boxes) and the
    YAML block form.
  - Test runner captures non-zero rc as failure.
  - Coverage gate: a new file with 0% coverage is a regression.
  - Lint delta: a new finding not present in master baseline fails the gate.
  - **Acceptance**: a card with one unmet AC produces a fail verdict, even
    when the tests gate passes and the lint delta is clean.

We exercise the gate through both the library API (qa_gate.evaluate) and
the end-to-end CLI path (merge_review.py --card-body-file), which is what
the spec's acceptance criterion actually tests.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))  # so `import qa_gate` works

import qa_gate  # noqa: E402

MERGE_REVIEW = ROOT.parent / "merge_review.py"
BUILD_FIXTURES = ROOT / "build_fixtures.py"


def _run(cmd, cwd=None):
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None,
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def _build_fixtures(out_root: Path) -> Path:
    proc = _run([sys.executable, str(BUILD_FIXTURES), "--out", str(out_root)])
    if proc.returncode != 0:
        raise RuntimeError(f"build_fixtures failed: {proc.stderr}")
    return out_root


# ---------------------------------------------------------------------------
# 1. AC parser
# ---------------------------------------------------------------------------


class ACParserTests(unittest.TestCase):

    def test_line_form_x_is_met(self):
        body = "AC: foo bar [x]\nAC: other thing [x]\n"
        acs = qa_gate.parse_acceptance_criteria(body)
        self.assertEqual(len(acs), 2)
        self.assertTrue(all(a.met for a in acs))
        self.assertEqual([a.source for a in acs], ["line", "line"])

    def test_line_form_space_is_unmet(self):
        body = "AC: foo bar [ ]\n"
        acs = qa_gate.parse_acceptance_criteria(body)
        self.assertEqual(len(acs), 1)
        self.assertFalse(acs[0].met)
        self.assertEqual(acs[0].description, "foo bar")

    def test_line_form_no_box_defaults_to_unmet(self):
        # Strict reading: must have [x] explicitly to count.
        body = "AC: this is not checked off\n"
        acs = qa_gate.parse_acceptance_criteria(body)
        self.assertEqual(len(acs), 1)
        self.assertFalse(acs[0].met)

    def test_yaml_block(self):
        body = (
            "Some prose\n\n"
            "```yaml\n"
            "acceptance_criteria:\n"
            "  - description: foo\n"
            "    met: true\n"
            "  - description: bar\n"
            "    met: false\n"
            "```\n"
        )
        acs = qa_gate.parse_acceptance_criteria(body)
        self.assertEqual(len(acs), 2)
        self.assertEqual(acs[0].description, "foo")
        self.assertTrue(acs[0].met)
        self.assertEqual(acs[1].description, "bar")
        self.assertFalse(acs[1].met)
        self.assertEqual([a.source for a in acs], ["yaml", "yaml"])

    def test_mixed_form_dedup(self):
        body = (
            "AC: shared criterion [x]\n"
            "```yaml\n"
            "acceptance_criteria:\n"
            "  - description: shared criterion\n"
            "    met: false\n"
            "```\n"
        )
        acs = qa_gate.parse_acceptance_criteria(body)
        # One merged entry; the met=True version wins (per spec).
        self.assertEqual(len(acs), 1)
        self.assertTrue(acs[0].met)

    def test_no_criteria_returns_empty(self):
        acs = qa_gate.parse_acceptance_criteria("Just some prose, no ACs.")
        self.assertEqual(acs, [])


# ---------------------------------------------------------------------------
# 2. Test runner
# ---------------------------------------------------------------------------


class TestRunnerTests(unittest.TestCase):

    def test_passing_test_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = qa_gate.QAGateConfig(test_command=[
                sys.executable, "-c", "print('all good'); exit(0)"
            ])
            r = qa_gate.evaluate_tests(Path(tmp), cfg, Path(tmp) / "ev")
            self.assertTrue(r.passed)
            self.assertEqual(r.exit_code, 0)

    def test_failing_test_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = qa_gate.QAGateConfig(test_command=[
                sys.executable, "-c", "exit(1)"
            ])
            r = qa_gate.evaluate_tests(Path(tmp), cfg, Path(tmp) / "ev")
            self.assertFalse(r.passed)
            self.assertEqual(r.exit_code, 1)

    def test_skip_exit_code_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = qa_gate.QAGateConfig(
                test_command=[sys.executable, "-c", "exit(5)"],
                test_skip_exit_code=5,
            )
            r = qa_gate.evaluate_tests(Path(tmp), cfg, Path(tmp) / "ev")
            self.assertTrue(r.passed)  # 5 is the "no tests ran" code
            self.assertEqual(r.exit_code, 5)

    def test_missing_test_tool_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = qa_gate.QAGateConfig(
                test_command=["definitely-not-a-binary-xyz", "--help"],
            )
            r = qa_gate.evaluate_tests(Path(tmp), cfg, Path(tmp) / "ev")
            self.assertTrue(r.passed)
            self.assertFalse(r.ran)
            self.assertIn("not on PATH", " ".join(r.notes))


# ---------------------------------------------------------------------------
# 3. Coverage delta
# ---------------------------------------------------------------------------


class CoverageGateTests(unittest.TestCase):

    def _build_repo(self, tmp: Path) -> Path:
        """Bare git repo with one python file touched."""
        repo = tmp / "repo"
        if repo.parent.exists():
            shutil.rmtree(repo.parent, ignore_errors=True)
        repo.parent.mkdir(parents=True, exist_ok=True)
        repo.mkdir()
        for cmd in [
            ["init", "-q", "--initial-branch=master"],
            ["config", "user.email", "qa@example.com"],
            ["config", "user.name", "qa"],
            ["config", "commit.gpgsign", "false"],
        ]:
            subprocess.run(["git"] + cmd, cwd=str(repo), check=True,
                           capture_output=True, text=True)
        (repo / "module.py").write_text("def used(): return 1\ndef unused(): return 2\n",
                                        encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(repo), check=True,
                       capture_output=True, text=True)
        return repo

    def test_coverage_skips_when_tool_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._build_repo(Path(tmp) / "src")
            cfg = qa_gate.QAGateConfig(coverage_command=["definitely-not-coverage-xyz"])
            r = qa_gate.evaluate_coverage(repo, "master", cfg, Path(tmp) / "ev")
            self.assertFalse(r.ran)
            # Touched files were 0 on a no-op review, so this should be skipped-empty.
            self.assertEqual(r.files, [])


# ---------------------------------------------------------------------------
# 4. Lint delta
# ---------------------------------------------------------------------------


class LintDeltaTests(unittest.TestCase):

    def test_clean_baseline_no_new_findings(self):
        baseline = [{"tool": "ruff", "file": "x.py", "line": 1, "message": "L1"}]
        wt = list(baseline)
        delta = qa_gate.evaluate_lint_delta(wt, baseline)
        self.assertTrue(delta.passed)
        self.assertEqual(delta.new_findings, [])

    def test_new_finding_fails(self):
        baseline = [{"tool": "ruff", "file": "x.py", "line": 1, "message": "L1"}]
        wt = baseline + [{"tool": "ruff", "file": "x.py", "line": 5, "message": "L5"}]
        delta = qa_gate.evaluate_lint_delta(wt, baseline)
        self.assertFalse(delta.passed)
        self.assertEqual(len(delta.new_findings), 1)
        self.assertEqual(delta.new_findings[0]["line"], 5)

    def test_baseline_only_findings_are_not_failures(self):
        baseline = [{"tool": "ruff", "file": "x.py", "line": 1, "message": "L1"}]
        wt = []  # baseline finding was fixed in the feature branch
        delta = qa_gate.evaluate_lint_delta(wt, baseline)
        self.assertTrue(delta.passed)
        self.assertEqual(delta.baseline_count, 1)
        self.assertEqual(delta.worktree_count, 0)


# ---------------------------------------------------------------------------
# 5. Top-level evaluate — the spec's acceptance criterion
# ---------------------------------------------------------------------------


class EvaluateTests(unittest.TestCase):
    """Acceptance: feeding the agent a card with one unmet AC produces a
    fail verdict citing that AC, even when tests/lint pass."""

    def _empty_worktree(self, tmp: Path) -> Path:
        """Build a tiny git repo we can pretend is a worktree."""
        repo = tmp / "wt"
        repo.mkdir()
        for cmd in [
            ["init", "-q", "--initial-branch=master"],
            ["config", "user.email", "qa@example.com"],
            ["config", "user.name", "qa"],
            ["config", "commit.gpgsign", "false"],
        ]:
            subprocess.run(["git"] + cmd, cwd=str(repo), check=True,
                           capture_output=True, text=True)
        (repo / "README.md").write_text("# empty\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(repo), check=True,
                       capture_output=True, text=True)
        return repo

    def test_unmet_ac_fails_even_with_clean_tests_and_lint(self):
        with tempfile.TemporaryDirectory() as tmp:
            wt = self._empty_worktree(Path(tmp))
            cfg = qa_gate.QAGateConfig(test_command=None)  # no tests → gate skipped, passes
            card_body = (
                "Implement widget X.\n\n"
                "AC: Widget X exists [x]\n"
                "AC: Widget X has a unit test [ ]\n"   # <- the unmet one
            )
            v = qa_gate.evaluate(
                repo=wt, worktree=wt, card_body=card_body,
                base_branch="master", config=cfg,
                master_lint_findings=[],   # baseline = clean
            )
            self.assertEqual(v.overall, "fail", msg=f"reasons: {v.reasons}")
            self.assertEqual(len(v.unmet_acs), 1)
            self.assertEqual(v.unmet_acs[0].description, "Widget X has a unit test")
            self.assertTrue(any("Widget X has a unit test" in r for r in v.reasons),
                            msg=f"expected unmet AC in reasons; got {v.reasons}")

    def test_all_acs_met_with_clean_tests_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            wt = self._empty_worktree(Path(tmp))
            card_body = (
                "Implement widget X.\n\n"
                "AC: Widget X exists [x]\n"
                "AC: Widget X has a unit test [x]\n"
            )
            v = qa_gate.evaluate(
                repo=wt, worktree=wt, card_body=card_body,
                base_branch="master", master_lint_findings=[],
            )
            self.assertEqual(v.overall, "pass", msg=f"reasons: {v.reasons}")

    def test_yaml_ac_form_also_fails_on_unmet(self):
        with tempfile.TemporaryDirectory() as tmp:
            wt = self._empty_worktree(Path(tmp))
            card_body = (
                "```yaml\n"
                "acceptance_criteria:\n"
                "  - description: Spec written\n"
                "    met: true\n"
                "  - description: Tests written\n"
                "    met: false\n"
                "```\n"
            )
            v = qa_gate.evaluate(
                repo=wt, worktree=wt, card_body=card_body,
                base_branch="master", master_lint_findings=[],
            )
            self.assertEqual(v.overall, "fail")
            self.assertEqual(len(v.unmet_acs), 1)
            self.assertEqual(v.unmet_acs[0].description, "Tests written")


# ---------------------------------------------------------------------------
# 6. End-to-end through merge_review.py CLI — the spec's acceptance scenario
# ---------------------------------------------------------------------------


class EndToEndMergeReviewTests(unittest.TestCase):
    """Spec acceptance: feeding merge_review.py a card with one unmet AC
    produces a fail verdict citing that AC, even when tests/lint pass.

    Drives the real CLI binary against a built fixture, drops a `.card-body`
    sidecar into the worktree root before the merge (via CHOREHERO_CARD_BODY
    env var, which the runner forwards), and inspects the report.
    """

    def _build_clean_repo(self, out_root: Path) -> Path:
        """A fixture repo with a feature branch that adds a file (clean merge)."""
        repo = out_root / "e2e-clean"
        if repo.exists():
            shutil.rmtree(repo)
        repo.mkdir(parents=True)
        for cmd in [
            ["init", "-q", "--initial-branch=master"],
            ["config", "user.email", "qa@example.com"],
            ["config", "user.name", "qa"],
            ["config", "commit.gpgsign", "false"],
        ]:
            subprocess.run(["git"] + cmd, cwd=str(repo), check=True,
                           capture_output=True, text=True)
        (repo / "README.md").write_text("# clean\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(repo), check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "checkout", "-q", "-b", "feature/add-greeting"],
                       cwd=str(repo), check=True, capture_output=True, text=True)
        (repo / "greeting.txt").write_text("hello\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "commit", "-q", "-m", "feature: add greeting"],
                       cwd=str(repo), check=True, capture_output=True, text=True)
        subprocess.run(["git", "checkout", "-q", "master"], cwd=str(repo),
                       check=True, capture_output=True, text=True)
        return repo

    def test_card_with_unmet_ac_downgrades_clean_merge_to_qa_fail(self):
        with tempfile.TemporaryDirectory() as fx_root:
            repo = self._build_clean_repo(Path(fx_root))
            wt_root = Path(tempfile.mkdtemp(prefix="chorehero-e2e-wt-"))
            try:
                report_path = wt_root / "report.json"
                card_path = wt_root / "card-body.md"
                card_path.write_text(
                    "Implement the greeting feature.\n\n"
                    "AC: greeting.txt exists [x]\n"
                    "AC: greeting.txt is tested [ ]\n",  # unmet AC
                    encoding="utf-8",
                )
                proc = _run([
                    sys.executable, str(MERGE_REVIEW),
                    "--repo", str(repo),
                    "--feature", "feature/add-greeting",
                    "--base", "master",
                    "--worktree-root", str(wt_root),
                    "--report", str(report_path),
                    "--card-body-file", str(card_path),
                ])
                self.assertTrue(report_path.exists(),
                                msg=f"no report; stderr={proc.stderr}")
                report = json.loads(report_path.read_text(encoding="utf-8"))
                # The merge was clean → before QA we expect clean-merge, but the
                # card body must downgrade it to qa-fail.
                self.assertEqual(report["verdict"], "qa-fail",
                                 msg=f"verdict was {report['verdict']!r}; "
                                     f"notes={report.get('notes')}")
                self.assertIsNotNone(report["qa_verdict"])
                self.assertEqual(report["qa_verdict"]["overall"], "fail")
                reasons = " ".join(report["qa_verdict"]["reasons"])
                self.assertIn("greeting.txt is tested", reasons,
                              msg=f"expected unmet AC cited in reasons; got {reasons}")
                self.assertEqual(proc.returncode, 1)
            finally:
                shutil.rmtree(wt_root, ignore_errors=True)

    def test_card_with_all_acs_met_keeps_clean_merge(self):
        with tempfile.TemporaryDirectory() as fx_root:
            repo = self._build_clean_repo(Path(fx_root))
            wt_root = Path(tempfile.mkdtemp(prefix="chorehero-e2e-wt-"))
            try:
                report_path = wt_root / "report.json"
                card_path = wt_root / "card-body.md"
                card_path.write_text(
                    "Implement the greeting feature.\n\n"
                    "AC: greeting.txt exists [x]\n"
                    "AC: greeting.txt says hello [x]\n",
                    encoding="utf-8",
                )
                proc = _run([
                    sys.executable, str(MERGE_REVIEW),
                    "--repo", str(repo),
                    "--feature", "feature/add-greeting",
                    "--base", "master",
                    "--worktree-root", str(wt_root),
                    "--report", str(report_path),
                    "--card-body-file", str(card_path),
                ])
                self.assertTrue(report_path.exists(),
                                msg=f"no report; stderr={proc.stderr}")
                report = json.loads(report_path.read_text(encoding="utf-8"))
                self.assertEqual(report["verdict"], "clean-merge",
                                 msg=f"verdict was {report['verdict']!r}; "
                                     f"notes={report.get('notes')}")
                self.assertEqual(proc.returncode, 0)
            finally:
                shutil.rmtree(wt_root, ignore_errors=True)

    def test_no_card_body_keeps_legacy_clean_merge(self):
        with tempfile.TemporaryDirectory() as fx_root:
            repo = self._build_clean_repo(Path(fx_root))
            wt_root = Path(tempfile.mkdtemp(prefix="chorehero-e2e-wt-"))
            try:
                report_path = wt_root / "report.json"
                # No --card-body-file and no env var → QA gate must be skipped.
                if "CHOREHERO_CARD_BODY" in os.environ:
                    del os.environ["CHOREHERO_CARD_BODY"]
                proc = _run([
                    sys.executable, str(MERGE_REVIEW),
                    "--repo", str(repo),
                    "--feature", "feature/add-greeting",
                    "--base", "master",
                    "--worktree-root", str(wt_root),
                    "--report", str(report_path),
                ])
                self.assertTrue(report_path.exists(),
                                msg=f"no report; stderr={proc.stderr}")
                report = json.loads(report_path.read_text(encoding="utf-8"))
                self.assertEqual(report["verdict"], "clean-merge")
                self.assertIsNone(report["qa_verdict"])
                self.assertEqual(proc.returncode, 0)
            finally:
                shutil.rmtree(wt_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)