# ChoreHero v1 — UAT Package

> **Lane:** UAT (acceptance + UI fidelity verification)
> **Owner:** uat-engineer
> **Status:** Ready for execution once `design/` package and the deployed staging
> URL are available. The scenario files are executable as-is; the design-artifact
> references resolve against the design package produced by the frontend-designer
> lane (task `t_fba7600a`).
> **Last synthesised:** 2026-10-11 against `docs/scope-brief.md` §2 (55 user
> stories, 1:1 with `spec-v1-mvp.md`).

This package delivers the three artefacts specified by the task brief:

1. **`scenarios/`** — one executable scenario per user story (55 files,
   `US-<NN>-<slug>.md`) in Given/When/Then format with explicit expected
   outcomes, UI fidelity checks (tokens, component states, copy), and
   accessibility checks. Each scenario references the design artefact it
   must match.
2. **`runbook.md`** — how to execute the suite against the staging URL
   and how to record pass/fail evidence.
3. **`templates/`** — blank forms for the per-run UAT report
   (`uat-report.md`) and per-scenario evidence log (`evidence-log.md`).

A consolidated index of every scenario with its story number, title,
feature area, and a one-line expected outcome lives in
`scenarios/INDEX.md`.

## Sign-off criteria (unambiguous)

A v1 release candidate is **READY TO SHIP** if and only if every one of
these is true at run close:

| # | Criterion | Owner of evidence |
|---|-----------|-------------------|
| 1 | All 55 scenarios have a recorded execution result (`PASS`, `FAIL`, `BLOCKED`, or `N/A`). | UAT engineer |
| 2 | Zero `FAIL` results against the critical path (US-1, US-4, US-5, US-10, US-16, US-18, US-21, US-23, US-28, US-31, US-33 — see `runbook.md` §"Critical path"). | UAT engineer |
| 3 | Zero `BLOCKED` results against the critical path. | UAT engineer |
| 4 | All visual fidelity checks (per-scenario §"UI fidelity") pass against the designer's `design/` package. | UAT engineer + designer sign-off |
| 5 | All accessibility checks (per-scenario §"Accessibility") pass — WCAG 2.1 AA for color contrast, focus order, keyboard reachability, and aria labels on the screens touched by the scenario. | UAT engineer |
| 6 | All parent + kid copy strings on the touched screens match the strings in this scenario file (no silent rewording). | UAT engineer |
| 7 | Critical-path scenarios are re-run on the final staging build (post any hotfix) and all pass. | UAT engineer |
| 8 | A signed `templates/uat-report.md` is filed with the UAT engineer's count. | UAT engineer |
| 9 | All `BLOCKED` results have a written reason and a target resolver. | UAT engineer |

If any of 1–9 fails, the verdict is **NOT READY** and the report must
spell out what blocks ship.

## Conventions in every scenario file

Every scenario file follows the same shape:

- **Header** — story ID, title, feature area, designer artefact(s)
  referenced, priority (Critical / High / Standard), and preconditions
  that must be true before the scenario starts.
- **Given / When / Then** — the formal scenario body. "Then" enumerates
  the **expected outcomes** as a numbered list, not prose, so a
  pass/fail check is binary per item.
- **UI fidelity** — explicit checks against design tokens, component
  state, and copy. The expected token values are placeholders
  (`<from-design-package>`) until the design package lands; the
  UAT engineer resolves them against `design/tokens/*.json` and the
  matching component spec in `design/components/*.md`.
- **Accessibility** — explicit checks (focus order, contrast,
  keyboard, aria). Marked WCAG 2.1 AA reference.
- **Evidence to record** — what the engineer captures (screenshots,
  API traces, console output). Drives `templates/evidence-log.md`.
- **References** — the user-story source (`docs/scope-brief.md` §2.X),
  the spec section (`spec-v1-mvp.md` §...), the design artefact paths,
  and any linked cross-lane coordination note.

## Out of scope for this package

- API contract tests, state-machine unit tests, and Prisma migration
  smoke tests are owned by the backend-dev lane per the scope brief
  §3 and §5. UAT verifies behaviour end-to-end through the deployed
  staging URL.
- Playwright end-to-end automation is owned by the backend-dev /
  frontend-dev lane per the scope brief §3 "Test seam". UAT scenarios
  are written so a human can execute them, and a Playwright harness
  *could* be generated from the structure, but no automation is shipped
  in this package.

## Handoff dependencies

| Depends on | Artefact | Used for |
|------------|----------|----------|
| frontend-designer (`t_fba7600a`) | `design/tokens/*.json`, `design/components/*.md`, annotated wireframes | Every scenario's §"UI fidelity" block |
| backend-dev / frontend-dev | Deployed staging URL reachable by the UAT engineer | Scenario execution |
| backend-dev | API contract spec (OpenAPI or equivalent) | Evidence capture in scenario §"Evidence" |

See `runbook.md` §"Pre-flight" for the exact resolution procedure.