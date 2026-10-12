# ChoreHero v1 — Per-Scenario Evidence Log

> One copy per scenario. Save under `evidence/US-<NN>-<slug>/` and
> reference the folder in `uat-report.md` §"Evidence index".

## Scenario metadata

| Field | Value |
|-------|-------|
| Scenario ID | `US-<NN>` |
| Scenario title | `<from scenarios/US-<NN>-<slug>.md>` |
| Priority | `Critical / High / Standard` |
| Feature area | `<Onboarding & Identity / Chores & Pools / Points & Streaks / Rewards & Redemption / Notifications / Sync & Offline / Empty States / Visual Identity>` |
| Executed by | `<name>` |
| Executed at | `<ISO timestamp>` |
| Staging build / image tag | `<tag>` |
| Result | `PASS / FAIL / BLOCKED / N/A` |

## Preconditions check

Confirm each precondition before starting. If any precondition
fails, mark the scenario `BLOCKED` and stop.

- [ ] Precondition 1: `<from scenario file>`
- [ ] Precondition 2: `<from scenario file>`
- [ ] ...

## Then-outcome checklist

For each numbered Then outcome in the scenario file, record the
result and the evidence reference.

| # | Expected outcome | Result | Evidence |
|---|------------------|--------|----------|
| 1 | <then-1 text> | `PASS / FAIL` | `<path to screenshot / trace / log>` |
| 2 | <then-2 text> | | |
| 3 | <then-3 text> | | |
| ... | | | |

## UI fidelity checklist

For each fidelity check in the scenario §"UI fidelity":

| # | Check | Expected (from design package) | Observed | Result | Evidence |
|---|-------|----------------------------------|----------|--------|----------|
| 1 | Token / component / copy | `<value>` | `<observed>` | `PASS / FAIL` | `<path>` |

## Accessibility checklist

For each accessibility check in the scenario §"Accessibility":

| # | Check | WCAG ref | Expected | Observed | Result | Evidence |
|---|-------|----------|----------|----------|--------|----------|
| 1 | Contrast ratio | 1.4.3 | ≥4.5:1 (or ≥3:1 for large text) | | | |
| 2 | Focus order | 2.4.3 | matches DOM order | | | |
| 3 | Keyboard reachability | 2.1.1 | all interactive elements reachable | | | |
| 4 | Aria labels | 4.1.2 | every interactive element has accessible name | | | |

## Network / API / WebSocket trace

Attach a `.har` export or paste the relevant requests inline.

| Method | URL | Status | Notes |
|--------|-----|--------|-------|
| | | | |

## Console output

Paste any warnings or errors emitted during the scenario.

```
<paste here>
```

## Dexie / IndexedDB dump

For US-46, US-48, US-49: paste the contents of the outbox tables
before and after the scenario.

## Notes

Free-form observations, oddities, or environmental issues
(browser version, OS-level push state, etc.).

```
<notes>
```