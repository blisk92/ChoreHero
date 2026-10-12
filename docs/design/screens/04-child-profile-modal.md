# Screen 04 — Child profile modal

> US 4. A modal opened from "Add child" / "Edit child" in parent
> settings. Captures name + avatar pick. The kid profile is the
> parent-picked identity for the child; the modal is the only
> surface where avatar is "edited".

## User story

- US 4 (create a child profile). Edit path: same modal, populated.

## Trigger

- Parent settings → "Children" section → "Add child" (primary CTA) or
  tap an existing child row → opens this modal.

## Layout (modal)

```
┌──────────────────────────────────────────────────────┐
│  Modal title                              ✕         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Name                                                │
│  [ text input ........................]              │
│  Helper: 1-30 characters.                            │
│                                                      │
│  Pick an avatar                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  ◯ ◯ ◯ ◯ ◯ ◯                                │    │
│  │  ◯ ◯ ◯ ◯ ◯ ◯                                │    │
│  └─────────────────────────────────────────────┘    │
│  (12 pre-shipped avatars, 6 across × 2 rows on     │
│   desktop, 4 across × 3 rows on mobile.)            │
│                                                      │
│  Helper: Tap one to choose.                          │
│                                                      │
│  [ Cancel ]                  [ Save child ]          │
└──────────────────────────────────────────────────────┘
```

- Modal width: 480dp on mobile, 560dp on desktop. Centered.
- Padding: `--ch-space-modal-padding`.

## Copy

| Element   | Copy                                                                |
|-----------|---------------------------------------------------------------------|
| Title     | "Add child"  /  "Edit [name]"                                       |
| Name lbl  | "Name"                                                               |
| Helper    | "1-30 characters."                                                   |
| Avatars sec | "Pick an avatar"                                                  |
| Avatars helper | "Tap one to choose."                                          |
| Cancel    | "Cancel"                                                             |
| Submit    | "Save child"                                                         |
| Validation error (name) | "Use 1-30 characters."                                  |
| Validation error (no avatar) | "Pick an avatar."                                |

## Tokens used

- Modal surface: `--ch-surface-card`.
- Modal radius: `--ch-radius-modal`.
- Modal shadow: `--ch-shadow-modal`.
- Backdrop: `--ch-surface-overlay`.
- Avatars: 64dp circles in a grid. Selected avatar carries the
  `ring` variant (3px brand-violet ring). Unselected: 1px
  `--ch-border-default` ring.

## Components used

- `<Modal variant="default">` (focus-trapping).
- `<Input variant="default">` for name.
- `<Avatar variant="default" | "ring" size="lg">` × 12.
- `<Button variant="secondary">` for Cancel.
- `<Button variant="primary">` for Save.

## Hierarchy

- H2: modal title.
- Section labels (not headings): "Name", "Pick an avatar".

## Tab order

1. Close (×).
2. Name input.
3. Avatar grid (Tab enters grid; arrow keys move; Space/Enter selects).
4. Cancel.
5. Save.

## States

| State               | How                                                              |
|---------------------|------------------------------------------------------------------|
| Default             | Name empty, no avatar selected; Save disabled.                   |
| Name invalid        | Border + helper text + `aria-invalid`. Save stays disabled.       |
| Avatar grid focus    | Active avatar carries focus ring; arrow keys move; Space selects. |
| Avatar selected     | Save enabled when name is valid + 1 avatar selected.             |
| Saving              | Save shows spinner + "Saving…"; Cancel disabled; `aria-busy`.   |
| Save success        | Modal closes; toast "Saved."; list re-renders with new child.    |
| Save error          | Inline error above Save: "Couldn't save. Try again?"             |
| Already saved (edit)| Modal pre-populates. Save shows "Save changes"; toast on close. |

## Accessibility

- Modal traps focus; `Esc` closes.
- Avatar grid has `role="radiogroup"` and each avatar
  `role="radio"` with `aria-checked`.
- "Pick one" radio group is keyboard-operable: arrow keys move,
  Space/Enter selects.
- The selected avatar announces its position + label
  (e.g. "Avatar 3 of 12, bunny, selected").
- Avatars carry `aria-label="[label of the character], [1-12] of 12"`.
- Reduced motion: avatar selection is instant (no scale).
- Forced colors: selected avatar uses Highlight outline + 2px
  outline width.

## Composition rules

- The modal can only save when name is valid AND 1 avatar is
  selected.
- "Cancel" closes the modal without saving; warning only if the
  user has typed or selected.
- The avatar grid is the ONLY place the parent can change avatar;
  the kid SPA does not expose this.

## Fidelity rules (UAT)

- F-2.2: parent palette.
- F-7.4: focus trap.
- F-7.7: selection visible by ring + label + position, not by
      colour alone.

## Anti-patterns

- ❌ Allowing a parent to upload a photo (open question 1 default =
     no).
- ❌ Letting the modal drag to dismiss (focus trap is canonical).
- ❌ Showing all 12 avatars at once on a tiny phone (grid
     collapses to 4×3, scrolls).
