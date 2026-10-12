# ChoreHero merge-review runner

A self-contained, stdlib-only Python tool that performs a `git merge --no-commit --no-ff <feature>` of every ChoreHero merge-review job into a fresh worktree based on `master`, classifies the result, and produces a structured report.

## What it does

1. **Clean merge path**
   - `git diff --check` — surface whitespace concerns in the merged tree.
   - Linter autodiscovery — scans the repo for config files (`.eslintrc*`, `eslint.config.js`, `ruff.toml`, `.ruff.toml`, `pyproject.toml`, `.golangci.*`, `biome.json`, `biome.jsonc`) and runs whichever binary is on PATH (eslint, ruff, golangci-lint, biome, check-jsonschema).
   - **QA gate pass** — once the merge is clean and linters have run, evaluate four gates against the merged worktree:
     1. **Tests** — autodetects `pytest`, `npm test`, or `go test` and runs it; any non-zero exit (other than the documented "no tests ran" code) fails the gate.
     2. **Coverage delta vs master** — runs the project's coverage tool on touched files and compares each file's coverage against the master's baseline. A new file with 0% coverage is treated as a regression.
     3. **Lint delta vs master** — diffs the lint findings produced in the worktree against a fresh baseline captured from `master`. Any (tool, file, line, message) tuple that is new on the worktree fails the gate.
     4. **Card-level acceptance criteria** — parses the card body for `AC:` line entries (with `[x]` / `[ ]` checkboxes) and/or a fenced YAML `acceptance_criteria:` block. Any unmet AC fails the gate, even when tests, coverage, and lint all pass.
   - Marks the verdict `clean-merge` (or `qa-fail` if the gate tripped) and writes the QA verdict into the report under `qa_verdict`.

2. **Conflict path**
   - Parses each conflicted file's `<<<<<<<` / `=======` / `>>>>>>>` blocks.
   - Classifies each block using `git diff --name-status` against the merge base:
     - `trivial-add-add` — pure add/add where at least one side is empty.
     - `trivial-delete-modify` — one side deleted, the other modified only.
     - `real` — anything else; flagged for manual review.
   - Auto-applies a resolution **only** for trivially-safe blocks. Anything `real` is left untouched.
   - If a file has any `real` blocks, the file is reported as `manual-conflict` and the in-progress merge is **aborted** — the worktree is left clean on the base branch.
   - Suggested resolution order is derived from merge-base / log blame topology (shallower paths first, then by recency of last change).

## Usage

```bash
# As part of a merge-review job
python tools/merge-review/merge_review.py \
    --repo /path/to/repo \
    --feature branch-name \
    --base master \
    --report /path/to/report.json
```

### Exit codes

| Code | Meaning                                                  |
| ---- | -------------------------------------------------------- |
| 0    | Clean merge — QA gate passed, lint report attached       |
| 1    | Real conflicts OR QA gate failed — manual action required|
| 2    | Trivial conflicts auto-resolved — reviewer should verify |
| 3    | Internal error (worktree, git, etc.)                     |

### Driving the QA gate

The QA gate only runs when the runner is handed a card body. Two ways to feed it in:

```bash
# 1. Via a sidecar file
python tools/merge-review/merge_review.py \
    --repo /path/to/repo \
    --feature branch-name \
    --base master \
    --card-body-file /path/to/card-body.md \
    --report /path/to/report.json

# 2. Via env var (useful when the orchestrator already has the body in memory)
CHOREHERO_CARD_BODY="$(cat card.md)" \
    python tools/merge-review/merge_review.py \
        --repo /path/to/repo --feature branch-name \
        --report /path/to/report.json
```

Card bodies can carry ACs in either form (or both — they are merged):

```markdown
Implement widget X.

AC: widget.py exists [x]
AC: widget.py has a unit test [ ]
```

```yaml
```yaml
acceptance_criteria:
  - description: spec exists
    met: true
  - description: spec reviewed
    met: false
```
```

Lines without a `[x]` / `[ ]` checkbox are treated as unmet (the runner is strict). When the QA gate fails the merge verdict is downgraded to `qa-fail`, exit code 1, with the failing reasons listed in `report["qa_verdict"]["reasons"]`.

### Report shape

The JSON report contains:

```json
{
  "verdict": "clean-merge | trivial-auto-merge | real-conflict | qa-fail | error",
  "feature_branch": "...",
  "base_branch": "master",
  "merge_base": "<sha>",
  "whitespace_warnings": ["..."],
  "lint_findings": [{ "tool": "ruff", "file": "...", "line": 12, "severity": "warning", "message": "..." }],
  "linters_run": ["ruff", "eslint"],
  "file_conflicts": [{
    "file": "src/foo.ts",
    "classification": "auto-resolvable | manual-conflict",
    "auto_resolved": true,
    "blocks": [{
      "hunk_index": 1,
      "ours_label": "HEAD",
      "theirs_label": "feature/foo",
      "ours_lines": ["..."],
      "theirs_lines": ["..."],
      "classification": "trivial-delete-modify",
      "rationale": "..."
    }]
  }],
  "auto_resolved_files": ["src/foo.ts"],
  "manual_conflict_files": ["src/bar.ts"],
  "suggested_resolution_order": ["src/bar.ts", "src/foo.ts"],
  "notes": ["..."],
  "qa_verdict": {
    "overall": "pass | fail",
    "reasons": ["unmet acceptance criteria: ..."],
    "unmet_acs": [{"description": "...", "met": false, "source": "line"}],
    "test_result": {...},
    "coverage_result": {...},
    "lint_delta": {"new_findings": [...], "passed": true},
    "evidence_paths": ["<worktree>/.qa-evidence/test-output.log"]
  }
}
```

## Tests

```bash
# Merge-review scenario tests (the three documented topologies).
python tools/merge-review/tests/test_scenarios.py

# QA-gate tests (AC parser, test runner, coverage, lint delta, end-to-end).
python tools/merge-review/tests/test_qa_gate.py
```

Three documented scenarios are covered:

| Fixture             | Topology                                       | Expected verdict        |
| ------------------- | ---------------------------------------------- | ----------------------- |
| `clean-merge`       | feature adds a new file                        | `clean-merge` (rc=0)    |
| `trivial-auto-merge`| feature deletes a block, master edits a comment| `trivial-auto-merge` (rc=2) |
| `real-conflict`     | both branches edit the same line               | `real-conflict` (rc=1)  |

`build_fixtures.py` can be re-run with `--out <path>` to materialise the fixtures for manual experimentation.

## Trigger scheduler (`trigger.py`)

The trigger polls the Kanban board for cards that have just transitioned to
`done` with a git worktree reference, and runs `merge_review.py` against each
new candidate. It is the watch-and-dispatch loop that turns "card is done"
into "card has a review_status".

### How a card is picked up

1. Every `TRIGGER_INTERVAL_SEC` the trigger runs `hermes kanban list --status done --json`.
2. For each card it checks two possible sources of a worktree reference:
   - `task.branch_name` (set when the card was originally dispatched onto a worktree).
   - The most recent completed run's `metadata.branch` (set by the worker).
3. The branch must resolve as a real local branch in `GIT_REPO_PATH` (`git for-each-ref refs/heads`). Phantom branch names are silently skipped.
4. Cards the trigger has already reviewed (per `STATE_FILE`) are skipped, so a `done` card gets at most one review unless `--card` forces it.

### What the trigger does, per card

1. Creates a fresh worktree at `<REVIEW_WORKTREE_ROOT>/<task_id>` on top of `<MERGE_REVIEW_BASE>` (default `master`). If a stale worktree or `merge-review/<base>` branch is left over from a prior run, it is pruned first so each run starts clean.
2. Invokes `merge_review.py` as a subprocess, captures stdout/stderr/exit code, and parses the JSON report from `--report`.
3. Records the verdict (`clean-merge`, `trivial-auto-merge`, `real-conflict`, `error`, `qa-fail`) in the local state file under `reviewed[<task_id>].review_status`.
4. Writes `review_status` (plus `review_branch`, `review_base_branch`, `review_exit_code`, `review_worktree_path`, `review_conflicts`, `review_auto_resolved_files`, `review_manual_conflict_files`, `review_notes`, `review_reviewed_at`) back to the card's latest-completed-run metadata via `hermes kanban edit --metadata`. The existing `task.result` is read back and re-passed unchanged so the original worker's handoff stays intact.
5. Posts a Markdown comment summarising the verdict and the raw JSON report (truncated to 12 KB).

### Invocation

```bash
# One polling pass (cron-friendly, default if no mode flag is given):
python tools/merge-review/trigger.py --once

# Foreground daemon — polls every TRIGGER_INTERVAL_SEC:
python tools/merge-review/trigger.py --watch

# Force-review one specific card (bypasses the state-file dedupe):
python tools/merge-review/trigger.py --card t_abc123
```

CLI flags (each overrides the matching env var):

| Flag | Env var | Default |
| --- | --- | --- |
| `--board` | `KANBAN_BOARD` | `chorehero` |
| `--repo` | `GIT_REPO_PATH` | `<script-dir>/../..` (the ChoreHero repo root) |
| `--base` | `MERGE_REVIEW_BASE` | `master` |
| `--interval` | `TRIGGER_INTERVAL_SEC` | `900` (15 min) |
| `--state-file` | `STATE_FILE` | `<script-dir>/.trigger-state.json` |
| _(positional)_ | `REVIEW_WORKTREE_ROOT` | `<GIT_REPO_PATH>/.worktrees/review` |
| _(positional)_ | `MERGE_REVIEW_BIN` | `<script-dir>/merge_review.py` |

`KBOARD_TOKEN` is reserved for future HTTP-mode use; the trigger currently
talks to Kanban via the `hermes kanban` CLI and inherits the profile's local
auth, so no token is needed in the local-CLI path.

### Schedule format

`TRIGGER_INTERVAL_SEC` is an integer number of seconds. The trigger itself
does not register itself with a scheduler — it only knows how to sleep
between passes (`--watch`) or run once (`--once`). To schedule it on a real
clock, wrap it in whatever your host uses:

```bash
# crontab — every 15 minutes
*/15 * * * * cd /path/to/ChoreHero && python tools/merge-review/trigger.py --once

# systemd timer / launchd — invoke the same `--once` command on the wall clock.

# Docker / k8s — run `trigger.py --once` as a periodic Job/CronJob.
```

For a true daemon (no scheduler), `python tools/merge-review/trigger.py --watch`
will foreground-loop and print one line per pass; Ctrl+C to stop.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | All candidates processed successfully (or there were none) |
| `1` | At least one card failed review processing (a verdict of `error`) |
| `2` | Internal error (config, missing CLI, not a git repo) |

### Acceptance

A single `--once` pass against a board with at least two `done` cards whose
`branch_name` resolves locally produces exactly one review job per candidate
and updates both cards' `review_status` metadata field plus comments within
the polling window. The state file then ensures subsequent passes are
no-ops until the next card transitions to `done`.

## Dependencies

- Python 3.10+ (uses `subprocess`, `dataclasses`, `pathlib`; no third-party packages).
- `git` on PATH.
- Linters are autodiscovered; the tool runs whichever it can find. Missing linters are silently skipped (with a `notes` entry if you wire one up via the `LINTER_DISCOVERY` table).

## Why a worktree?

Each merge-review job gets a brand-new worktree based on the base branch. This guarantees:

- The real working repo (and any sibling worktrees) is never touched.
- A previous failed merge state can't leak into the next run.
- Cleanup is mechanical — `git worktree remove --force`.