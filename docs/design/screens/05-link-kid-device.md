# Screen 05 — Link a kid device

> US 5 (generate code + QR). US 6 (same code persists). US 7 (parent
> can regenerate; the previous code immediately stops working).
> The parent shows this code on their device; the kid device scans
> it or types the 6-character code.

## User story

- US 5, US 6, US 7.

## Trigger

- Parent settings → "Kid devices" section → "Link a new kid device".

## Route

- `/settings/kid-devices/link` (parent SPA).

## Layout

```
┌────────────────────────────────────────────────────────────┐
│  ← Back                  H1: Link a kid device              │
├────────────────────────────────────────────────────────────┤
│  H2: Step 1 — Open the link screen on the kid's tablet.    │
│  Helper: On the tablet, tap "I'm a kid" and scan the code. │
│                                                            │
│  H2: Step 2 — Scan or type the code below.                 │
│  ┌──────────────────┐   ┌─────────────────────────────┐    │
│  │                  │   │     H H X 9 K Z              │    │
│  │                  │   │     (mono, 6 chars,         │    │
│  │      QR CODE     │   │      monospaced, large.)    │    │
│  │                  │   │                             │    │
│  │                  │   │   "Last linked: never."     │    │
│  │   240 × 240dp    │   │                             │    │
│  │                  │   │                             │    │
│  └──────────────────┘   └─────────────────────────────┘    │
│                                                            │
│  H2: Code stays the same                                  │
│  Helper: Use this code any time. Don't share it outside    │
│          your family. To change it, regenerate below.      │
│                                                            │
│  [ Regenerate code ]   ← danger variant, needs confirm    │
│                                                            │
│  Card: "Currently linked devices"                          │
│   (empty state if none yet)                                │
└────────────────────────────────────────────────────────────┘
```

## Copy

| Element                | Copy                                                 |
|------------------------|------------------------------------------------------|
| H1                     | "Link a kid device"                                   |
| Step 1 H2              | "Step 1 — Open the link screen on the kid's tablet." |
| Step 1 helper          | "On the tablet, tap 'I'm a kid' and scan the code."   |
| Step 2 H2              | "Step 2 — Scan or type the code below."               |
| Code helper            | "If you can't scan, type the 6 characters above."    |
| Last linked            | "Last linked: [relative time or "never"]."            |
| Stay helper H2         | "Code stays the same"                                 |
| Stay body              | "Use this code any time. Don't share it outside your family. To change it, regenerate below." |
| Regenerate             | "Regenerate code"                                     |
| Regenerate confirm     | "Regenerate code? Previous code stops working immediately." |
| Regen success toast    | "New code ready. Old code no longer works."           |
| Devices card heading   | "Currently linked devices"                            |
| Empty state            | "No devices linked yet." → "Link your first one." (this is the screen you're on) |

## Tokens used

- Background: `--ch-surface-app-parent`.
- Cards: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- QR card uses `--ch-surface-card` with a centered SVG QR block
  (240dp on desktop, 200dp on mobile).
- Code text: `--ch-text-code-lg`, mono font.
- Card padding: `--ch-space-card-padding`.

## Components used

- `<TopNav variant="parent-app">`.
- `<Card>`.
- `<Button variant="secondary">` for "Regenerate".
- `<Modal variant="confirm">` for regenerate confirmation.
- `<EmptyState variant="parent">` for device list.

## Hierarchy

- H1: "Link a kid device".
- H2 (3): "Step 1 …", "Step 2 …", "Code stays the same".

## Tab order

1. Back.
2. Step 1 helper link ("open the link screen").
3. QR code (decorative; not focusable).
4. Code text (selectable; user can copy).
5. "Copy code" button.
6. "Regenerate code" button.
7. Confirmation modal Cancel / Regenerate (when open).
8. Devices list rows (link / revoke per device).

## States

| State                  | How                                                        |
|------------------------|------------------------------------------------------------|
| Default                | QR + code rendered from server-side generated `HouseholdCode`. |
| Code just regenerated  | Toast success; QR + code both refresh.                     |
| Regenerate confirm     | Modal traps focus; Cancel + Regenerate.                    |
| Regen error            | Modal-level error: "Couldn't regenerate. Try again."       |
| QR loading             | Skeleton block in QR card.                                  |
| Code loading           | Skeleton text (4 chars wide).                              |
| Active socket          | QR may pulse subtly when the latest kid device just linked (fade). |
| Device linked (live)   | The "Last linked" time updates.                            |

## Accessibility

- QR is decorative (`alt=""` + `aria-hidden="true"`); the text code
  is the primary information.
- Code text is `aria-label="Household code: H H X 9 K Z"` so it
  reads letter-by-letter to screen readers.
- "Copy code" button: copies to clipboard, toast confirms.
- Regenerate confirm modal follows the standard modal pattern.
- Step headings are H2 (proper hierarchy under H1).
- Helper text is `aria-describedby` from the heading it accompanies.
- Touch targets: 44dp+.

## Composition rules

- The QR encodes the same code shown textually; both must always be
  in sync.
- When the code regenerates, the QR animates a brief "shuffle"
  (fade-out → fade-in) at `--ch-duration-slow`. No continuous motion.
- Page never auto-regenerates; it is always a deliberate parent
  action.
- The list of currently linked devices lives below; this screen
  also answers US 8's "list" half.

## Fidelity rules (UAT)

- F-9.8: QR ≥ 200dp; code in monospace.
- F-3.1: parent touch targets.
- F-7.4: confirm modal focus trap.
- F-8.5: code monospace + tabular.

## Anti-patterns

- ❌ A QR without a textual fallback for camera-locked devices.
- ❌ A regenerate button that doesn't warn about invalidating
     existing devices.
- ❌ A page that loses the QR while the modal is open.
