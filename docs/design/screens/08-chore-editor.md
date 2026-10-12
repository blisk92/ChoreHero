# Screen 08 — Chore editor (modal)

> US 10, US 11, US 12, US 13, US 14. The modal at `/chores → Add
> chore` (or Edit chore). Captures name, point value, recurring/
> one-off, deadline, review-flagged.

## User story

- US 10 (create), US 11 (recurring/one-off toggle), US 12 (edit /
> delete row), US 13 (deadline on one-off), US 14 (review-flagged).

## Trigger

- "+ Add chore" on /chores; or tap Edit on an existing row.

## Layout (modal, two-column on desktop)

```
┌──────────────────────────────────────────────────────────────┐
│  Title                                  ✕                  │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Name                                                │    │
│  │ [ Make bed                                      ]   │    │
│  │ Helper: 1-60 chars.                                 │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │ Points                                              │    │
│  │ [ 5 ]  pts   ← stepper, +/- buttons (44dp min)       │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │ Kind                                                │    │
│  │ [ Recurring ] [ One-off ]   ← segmented             │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │ Deadline (one-off only)                             │    │
│  │ [ Date picker · Time picker ]  Helper: optional     │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │ ☑ Require parent approval before points are given   │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │ Helper (live): "Total chores in pool: N."           │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [ Cancel ]                          [ Save chore ]          │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element        | Copy                                                                  |
|----------------|-----------------------------------------------------------------------|
| Title (new)    | "Add chore"                                                           |
| Title (edit)   | "Edit chore"                                                          |
| Name lbl       | "Name"                                                                 |
| Points lbl     | "Points"                                                              |
| Kind lbl       | "Kind"                                                                 |
| Recurring      | "Recurring"                                                            |
| One-off        | "One-off"                                                              |
| Recurring helper | "Returns to the pool after the kid finishes it."                  |
| One-off helper | "Removed from the pool when finished or skipped."                  |
| Deadline lbl   | "Deadline (optional)"                                                 |
| Deadline helper | "Set a time and the chore expires if not finished by then."        |
| Review lbl     | "Require my approval before points are given"                       |
| Review helper  | "You'll get a notification when the kid marks it done."              |
| Pool helper    | "You're adding to the [Recurring | One-off] pool."                   |
| Cancel         | "Cancel"                                                              |
| Save           | "Save chore" / "Save changes"                                          |

## Tokens used

- Modal: `--ch-surface-card`, `--ch-radius-modal`, `--ch-shadow-modal`.
- Stepper buttons: secondary variant, square 44dp.
- Segmented control: `--ch-color-brand-violet-100` selected,
  `--ch-surface-card` unselected, `--ch-border-default` border.
- Switch (review-flagged): track `--ch-color-neutral-ink-300` off,
  `--ch-color-brand-violet-600` on.

## Components used

- `<Modal>`.
- `<Input>` for name.
- `<Stepper>` for points (1-100, default 5).
- `<SegmentedControl>` for kind.
- `<DateTimePicker>` (one-off only).
- `<Switch>` for review-flagged.
- `<Button>` Cancel + Save.
- `<FormError>` for inline field errors.

## Hierarchy

- H2: title.
- Field labels are not headings.

## Tab order

1. Close (×).
2. Name.
3. Points (stepper).
4. Kind segmented.
5. Deadline (when visible).
6. Review-flagged switch.
7. Cancel.
8. Save.

## States

| State              | How                                                         |
|--------------------|-------------------------------------------------------------|
| Default (new)      | Name empty, points 5, kind Recurring (default per US 11 spec). |
| Default (edit)     | Prefilled; Save shows "Save changes".                       |
| Name invalid       | Helper + `aria-invalid`.                                    |
| Points invalid     | Min 1, max 100 enforced by stepper; clamp.                  |
| Kind switched      | Deadline field shows/hides with `--ch-duration-fast`.       |
| Deadline in past   | Save disabled + helper "Pick a future time."                |
| Review-flagged on  | Save enabled; submit captures true.                         |
| Saving             | Save shows spinner; Cancel disabled.                        |
| Save success       | Modal closes; toast "Chore saved."; row updates in list.    |
| Save error         | Inline: "Couldn't save. Try again?"                         |
| Network failure    | Form-level error above Save.                                |

## Validation

| Field      | Rule                                                                |
|------------|---------------------------------------------------------------------|
| Name       | Non-empty, ≤ 60 chars.                                              |
| Points     | 1-100 integer.                                                       |
| Kind       | Required (one of Recurring/One-off).                                |
| Deadline   | Optional, must be in the future when set.                            |
| Review-flagged | Boolean.                                                        |

## Accessibility

- Modal traps focus; `Esc` closes (with unsaved-changes confirm).
- Switch (`role="switch"`, `aria-checked`) for review-flagged.
- Segmented control exposes `role="radiogroup"` + `role="radio"` for
  keyboard support.
- DateTimePicker is a popover; `Enter` opens, calendar grid is
  roving-tabindex, `Esc` closes.
- Error focus moves to the first invalid field on submit.
- Save disabled state uses `aria-disabled="true"`.
- The form has a single visible error region with
  `role="alert"` for form-level errors.

## Composition rules

- The Save button is the primary CTA. Cancel is secondary.
- Edit mode: Title is "Edit chore"; Save copy is "Save changes".
- Unsaved changes trigger an `onbeforeunload`-style confirm if the
  parent tries to navigate or close.

## Fidelity rules (UAT)

- F-2.2: parent palette.
- F-7.4: modal focus trap.
- F-7.10: labels.
- F-7.x: a11y.

## Anti-patterns

- ❌ A free-text points field (stepper only).
- ❌ A deadline field for a recurring chore (US 13: deadline only
     on one-off).
- ❌ Saving with an invalid deadline silently.
