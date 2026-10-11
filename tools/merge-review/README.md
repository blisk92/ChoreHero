# ChoreHero merge-review runner

A self-contained, stdlib-only Python tool that performs a `git merge --no-commit --no-ff <feature>` of every ChoreHero merge-review job into a fresh worktree based on `master`, classifies the result, and produces a structured report.

## What it does

1. **Clean merge path**
   - `git diff --check` — surface whitespace concerns in the merged tree.
   - Linter autodiscovery — scans the repo for config files (`.eslintrc*`, `eslint.config.js`, `ruff.toml`, `.ruff.toml`, `pyproject.toml`, `.golangci.*`, `biome.json`, `biome.jsonc`) and runs whichever binary is on PATH (eslint, ruff, golangci-lint, biome, check-jsonschema).
   - Marks the verdict `clean-merge` and writes the lint output.

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
| 0    | Clean merge — ready to ship, lint report attached        |
| 1    | Real conflicts, merge aborted — manual resolution required|
| 2    | Trivial conflicts auto-resolved — reviewer should verify |
| 3    | Internal error (worktree, git, etc.)                     |

### Report shape

The JSON report contains:

```json
{
  "verdict": "clean-merge | trivial-auto-merge | real-conflict | error",
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
  "notes": ["..."]
}
```

## Tests

```bash
# Builds fresh fixtures in a tmp dir, runs the runner against each, asserts verdict.
python tools/merge-review/tests/test_scenarios.py
```

Three documented scenarios are covered:

| Fixture             | Topology                                       | Expected verdict        |
| ------------------- | ---------------------------------------------- | ----------------------- |
| `clean-merge`       | feature adds a new file                        | `clean-merge` (rc=0)    |
| `trivial-auto-merge`| feature deletes a block, master edits a comment| `trivial-auto-merge` (rc=2) |
| `real-conflict`     | both branches edit the same line               | `real-conflict` (rc=1)  |

`build_fixtures.py` can be re-run with `--out <path>` to materialise the fixtures for manual experimentation.

## Dependencies

- Python 3.10+ (uses `subprocess`, `dataclasses`, `pathlib`; no third-party packages).
- `git` on PATH.
- Linters are autodiscovered; the tool runs whichever it can find. Missing linters are silently skipped (with a `notes` entry if you wire one up via the `LINTER_DISCOVERY` table).

## Why a worktree?

Each merge-review job gets a brand-new worktree based on the base branch. This guarantees:

- The real working repo (and any sibling worktrees) is never touched.
- A previous failed merge state can't leak into the next run.
- Cleanup is mechanical — `git worktree remove --force`.