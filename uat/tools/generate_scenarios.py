"""Generate the 55 UAT scenario markdown files for ChoreHero v1.

Reads the stories list (defined inline in this script) and writes one
`US-<NN>-<slug>.md` per story into `uat/scenarios/`. Also writes
`uat/scenarios/INDEX.md` aggregating all stories.

This script is run once at scenario-pack synthesis time. It is
deterministic; running it again overwrites the same files with the
same content.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "scenarios"
ROOT.mkdir(parents=True, exist_ok=True)


# -- Story data -------------------------------------------------------------
# Each story dict has the structured fields the scenario file template
# consumes. Keeping it in one place makes later tweaks cheap.

ONBOARDING_25 = "Onboarding & Identity"
CHORES = "Chores & Pools"
POINTS = "Points & Streaks"
REWARDS = "Rewards & Redemption"
NOTIFS = "Notifications"
SYNC = "Sync & Offline"
EMPTY = "Empty States & Onboarding Nudges"
VISUAL = "Visual Identity"

STORIES = [
    # ----- 1-9 Onboarding & Identity -----
    {
        "id": "US-1", "slug": "signup-email-password",
        "title": "Sign up by email + password",
        "area": ONBOARDING_25, "priority": "Critical",
        "sources": {"scope": "§2.1", "spec": "§User Stories 1"},
        "design": [
            "design/screens/sign-up.md",
            "design/components/form-field.md",
            "design/components/button.md",
            "design/tokens/colors.json",
        ],
        "preconditions": [
            "Staging parent URL is reachable (runbook §3).",
            "Test parent email and password are fresh — not previously registered on this staging DB.",
            "Marketing / landing page loads without console errors.",
        ],
        "given": "a new visitor on the marketing page with no active session",
        "when": "they submit the sign-up form with email + password (twice) and tap \"Create account\"",
        "then": [
            "API responds 2xx with a session token within 2 s of submit.",
            "A `Parent` row exists with the submitted email and a bcrypt password hash (never plaintext over the wire or at rest).",
            "A `Household` row exists with the parent as its sole member.",
            "The parent lands on the parent dashboard signed in; no intermediate interstitial asking them to log in again.",
            "A success toast or in-app confirmation reads \"Welcome — your household is ready.\" (or the design-package equivalent).",
        ],
        "ui": [
            "Email + password fields render using `form-field.md` with labels above inputs.",
            "Primary CTA uses `button.md` `variant=primary`, palette token `action/cta` (sunshine yellow per CONTEXT.md).",
            "Error states for invalid email / weak password render inline beneath the field, not as a modal.",
        ],
        "a11y": [
            "Form fields have associated <label> elements (WCAG 1.3.1, 4.1.2).",
            "Tab order: email → password → confirm password → submit (WCAG 2.4.3).",
            "Submit button reachable via keyboard and operable via Enter / Space (WCAG 2.1.1).",
            "Color contrast for primary CTA text on yellow background ≥ 4.5:1 (WCAG 1.4.3).",
        ],
        "evidence": [
            "Screenshot of empty sign-up form (`US-01-step-1.png`).",
            "Screenshot of filled form just before submit (`US-01-step-2.png`).",
            "Screenshot of dashboard after redirect (`US-01-step-3.png`).",
            "Network `.har` showing `POST /api/auth/signup` 2xx and the follow-up `GET /api/household` call.",
            "DB row dump for `Parent` and `Household` (anonymised; no password).",
        ],
    },
    {
        "id": "US-2", "slug": "oauth-signin",
        "title": "Sign in faster with OAuth (Google / Apple)",
        "area": ONBOARDING_25, "priority": "High",
        "sources": {"scope": "§2.2", "spec": "§User Stories 2"},
        "design": ["design/screens/sign-in.md", "design/components/button.md"],
        "preconditions": [
            "Staging parent URL reachable.",
            "Test Google (and Apple, if shipped in v1) OAuth account available; not previously bound to a different parent on this staging DB.",
            "OAuth redirect URLs configured in the staging env.",
        ],
        "given": "a parent on the sign-in screen",
        "when": "they tap \"Continue with Google\" (or Apple) and complete the OAuth round-trip",
        "then": [
            "API responds 2xx with a session token.",
            "If this is the first use of the OAuth subject, a new `Parent` row + `Household` are created; otherwise the existing `Parent` is matched by `oauth_subject`.",
            "The parent lands on the parent dashboard signed in.",
            "`oauth_provider` and `oauth_subject` are populated on the `Parent` row.",
        ],
        "ui": [
            "OAuth buttons sit below the email/password form, visually de-emphasised (`button.md` `variant=secondary`).",
            "Buttons show the provider brand mark per each provider's current usage rules.",
        ],
        "a11y": [
            "OAuth buttons have accessible names that include the provider name (WCAG 4.17.2 / 2.34).",
            "Keyboard reachability and focus indicator visible (WCAG 2.1.1, 2.4.7).",
        ],
        "evidence": [
            "Screenshot of sign-in screen with both auth paths visible.",
            "Network `.har` capturing the OAuth redirect chain and the final `POST /api/auth/oauth` exchange.",
            "DB row showing `oauth_provider` / `oauth_subject` populated.",
        ],
    },
    {
        "id": "US-3", "slug": "auto-household-create",
        "title": "Automatic household creation on signup",
        "area": ONBOARDING_25, "priority": "High",
        "sources": {"scope": "§2.3", "spec": "§User Stories 3"},
        "design": ["design/tokens/spacing.json", "design/screens/parent-dashboard.md"],
        "preconditions": [
            "Fresh staging DB (no orphan `Household` rows).",
            "Sign-up flow (US-1) completed for the test parent.",
        ],
        "given": "a freshly signed-up parent",
        "when": "the sign-up API call returns 2xx",
        "then": [
            "A `Household` row exists with the parent's `household_id` foreign key.",
            "No user-visible configuration step is required before the parent can add a chore.",
            "Subsequent parent API calls (e.g. chore create) succeed without first selecting a household.",
        ],
        "ui": ["No empty-state config card is shown — the parent lands on the standard dashboard skeleton."],
        "a11y": ["Skip — covered by US-1 sign-up a11y."],
        "evidence": [
            "DB dump: `Household` and `Parent` rows present; foreign keys set.",
            "Screenshot of parent dashboard immediately post-signup.",
        ],
    },
    {
        "id": "US-4", "slug": "create-child-profile",
        "title": "Create a child profile with name + avatar",
        "area": ONBOARDING_25, "priority": "Critical",
        "sources": {"scope": "§2.4", "spec": "§User Stories 4"},
        "design": [
            "design/components/avatar-picker.md",
            "design/components/modal.md",
            "design/tokens/colors.json",
        ],
        "preconditions": [
            "Parent signed in (US-1).",
            "Test child name and chosen avatar ID are recorded in the runbook §3.",
        ],
        "given": "a signed-in parent on the parent dashboard or settings",
        "when": "they open \"Add child\", enter a name, and pick an avatar",
        "then": [
            "A `Child` row exists in the parent's household with the submitted name and `avatar_id`.",
            "The chosen avatar is rendered in the kid SPA on the next device link (verified by US-5 / US-9).",
            "The parent dashboard now lists one child in the household section.",
            "No avatar upload path is exposed (v1 is pre-shipped SVG set per scope-brief §7 Q1 default).",
        ],
        "ui": [
            "Avatar picker is a modal (`modal.md`) on `surface/elevated`; tile grid renders the pre-shipped SVG set.",
            "Selected avatar is visually highlighted with the parent's primary accent (`action/primary-selected`).",
        ],
        "a11y": [
            "Each avatar tile has an accessible name (e.g. \"robot\", \"fox\") (WCAG 4.1.2).",
            "Tile grid reachable via arrow keys; selection announced via aria-live or focus (WCAG 1.3.1, 4.1.3).",
            "Modal traps focus while open (WCAG 2.4.3).",
            "Avatar swatches are not the sole carrier of identity — name is also shown (WCAG 1.4.1).",
        ],
        "evidence": [
            "Screenshot of empty avatar picker.",
            "Screenshot with avatar selected.",
            "Screenshot of completed dashboard with child card.",
            "Network `.har` for `POST /api/children`.",
            "DB row for `Child`.",
        ],
    },
    {
        "id": "US-5", "slug": "household-code-qr",
        "title": "Generate household code + QR from \"Link a kid device\"",
        "area": ONBOARDING_25, "priority": "Critical",
        "sources": {"scope": "§2.5", "spec": "§User Stories 5"},
        "design": ["design/screens/link-kid-device.md", "design/components/qr-tile.md"],
        "preconditions": [
            "Parent signed in, child profile created (US-4).",
            "Test kid device available with the kid SPA loaded.",
        ],
        "given": "a parent in settings with no `HouseholdCode` row yet",
        "when": "they tap \"Link a kid device\" for the first time",
        "then": [
            "A `HouseholdCode` row is created (lazy) with a hashed code.",
            "A 6-character alphanumeric plaintext code is shown to the parent: charset excludes 0/O, 1/I/L (per CONTEXT.md & spec schema).",
            "A QR code encodes the same 6-character string; scanning the QR on the kid SPA enters the code automatically.",
            "Manual code entry on the kid SPA accepts the code and completes the link handshake.",
            "The kid SPA lands on the welcome screen (US-9).",
        ],
        "ui": [
            "QR + code render side-by-side using `qr-tile.md`; sufficient contrast between QR and background for scanner reliability.",
            "Code is rendered in a monospace token so ambiguous characters are unambiguous.",
        ],
        "a11y": [
            "Plaintext code has an accessible name and copyable announcement (WCAG 4.1.2).",
            "Manual entry input has an associated label and supports paste (WCAG 1.3.1, 2.1.1).",
            "QR alone is not the sole channel — manual entry is an equivalent path (WCAG 1.1.1 / non-text content).",
        ],
        "evidence": [
            "Screenshot of QR + code visible.",
            "Screenshot of kid SPA after QR scan or manual entry.",
            "Network `.har` for code-generation endpoint and link handshake.",
            "DB row for `HouseholdCode` (note: only hash stored, never plaintext).",
        ],
    },
    {
        "id": "US-6", "slug": "code-permanent",
        "title": "Household code is permanent until regenerated",
        "area": ONBOARDING_25, "priority": "High",
        "sources": {"scope": "§2.6", "spec": "§User Stories 6"},
        "design": ["design/screens/link-kid-device.md"],
        "preconditions": [
            "An existing `HouseholdCode` row exists from a prior run.",
            "A new kid device is available to link.",
        ],
        "given": "a parent whose household already has a code",
        "when": "a new kid device is linked (via QR or manual entry) without regenerating",
        "then": [
            "The previously-issued code is still valid and accepted by the link endpoint.",
            "No `HouseholdCode` row is overwritten; the existing row continues to be the active one.",
            "The new `KidDevice` row is created successfully.",
        ],
        "ui": ["Settings → \"Link a kid device\" still shows the same QR + code as before."],
        "a11y": ["Skip — same surface as US-5; a11y inherited."],
        "evidence": [
            "Network `.har` for the link call on a \"new\" device using an old code.",
            "DB row count: `HouseholdCode` count unchanged, `KidDevice` count incremented.",
        ],
    },
    {
        "id": "US-7", "slug": "regenerate-code",
        "title": "Regenerate the household code",
        "area": ONBOARDING_25, "priority": "High",
        "sources": {"scope": "§2.7", "spec": "§User Stories 7"},
        "design": ["design/screens/link-kid-device.md", "design/components/confirmation-dialog.md"],
        "preconditions": [
            "Existing `HouseholdCode` row.",
            "At least one currently-linked kid device that will become orphan after regeneration.",
        ],
        "given": "a parent in settings with an active household code",
        "when": "they tap \"Regenerate code\" and confirm the destructive action",
        "then": [
            "The previous code's hash is replaced (or a new row takes over per implementation).",
            "Attempting to link a new device with the *old* code returns 4xx.",
            "A new 6-character code (matching the no-0/O/1/I/L charset) is shown with a fresh QR.",
            "Existing linked devices are not automatically logged out in v1 (per spec out-of-scope notes); the parent is informed in copy that previously-linked devices will need to re-link.",
        ],
        "ui": [
            "Regenerate requires a confirmation dialog (`confirmation-dialog.md`) — destructive intent.",
            "After regenerate, the UI shows the new code + QR; old code is not visible anywhere.",
        ],
        "a11y": [
            "Confirmation dialog traps focus and is announced (WCAG 2.4.3, 4.1.3).",
            "Destructive action uses both colour and iconography to convey severity (WCAG 1.4.1).",
        ],
        "evidence": [
            "Screenshot of regenerate confirmation dialog.",
            "Screenshot of new code + QR.",
            "Network `.har` showing the regenerate call + a failed link call with the old code.",
            "DB row diff for `HouseholdCode`.",
        ],
    },
    {
        "id": "US-8", "slug": "list-revoke-kid-devices",
        "title": "List and revoke kid devices",
        "area": ONBOARDING_25, "priority": "High",
        "sources": {"scope": "§2.8", "spec": "§User Stories 8"},
        "design": ["design/components/list-item.md", "design/components/confirmation-dialog.md"],
        "preconditions": ["At least one `KidDevice` linked to the household (from US-5)."],
        "given": "a parent in settings → \"Kid devices\"",
        "when": "they open the device list",
        "then": [
            "Every registered `KidDevice` is listed with friendly name, `last_seen_at`, and a revoke control.",
            "Tapping revoke sets `revoked_at`, invalidates the device token, and the device is removed from the active list (or marked revoked).",
            "Subsequent kid-device API calls with the revoked token return 401.",
        ],
        "ui": [
            "List uses `list-item.md`; each row has friendly name, relative timestamp (\"last seen 3 min ago\"), and a destructive Revoke action.",
            "Empty state copy: \"No kid devices linked yet.\" with a CTA to US-5.",
        ],
        "a11y": [
            "List is semantic `<ul>` / `<li>` or aria-equivalent (WCAG 1.3.1).",
            "Each row's revoke button has an accessible name including the device's friendly name (WCAG 4.1.2).",
            "Confirm-revoke dialog traps focus (WCAG 2.4.3).",
        ],
        "evidence": [
            "Screenshot of populated device list.",
            "Screenshot of confirm-revoke dialog.",
            "Network `.har` for revoke call.",
            "Network `.har` showing a 401 from the kid SPA after revoke.",
        ],
    },
    {
        "id": "US-9", "slug": "kid-welcome-first-launch",
        "title": "Kid welcome on first launch",
        "area": ONBOARDING_25, "priority": "High",
        "sources": {"scope": "§2.9", "spec": "§User Stories 9 + 53"},
        "design": [
            "design/screens/kid-welcome.md",
            "design/components/avatar.md",
            "design/tokens/colors.json",
        ],
        "preconditions": ["Kid device freshly linked (US-5), zero chores in either pool."],
        "given": "a freshly linked kid device with zero chores",
        "when": "the kid opens the kiosk",
        "then": [
            "The welcome screen shows \"Welcome, [name]!\" with the chosen avatar hero.",
            "No parent-side nav or chrome is visible (kiosk surface).",
            "The moment any chore lands in either pool, the screen auto-transitions to the regular \"No chores yet\" empty state or the live pool — without a refresh.",
        ],
        "ui": [
            "Avatar uses `avatar.md` at hero size (per design spec); the ChoreHero emblem does not compete (CONTEXT.md mascot rule).",
            "Palette uses the kid-side accent treatment; parent-side quiet-palette is NOT applied here.",
        ],
        "a11y": [
            "Avatar has an `alt`/aria-label with the kid's name (WCAG 1.1.1).",
            "Greeting text is the primary heading; readable at 200% zoom (WCAG 1.4.4).",
            "No flashing animation that exceeds safe thresholds (WCAG 2.3.1).",
        ],
        "evidence": [
            "Screenshot of welcome screen on a fresh kid device.",
            "Screenshot taken moments after chore creation showing auto-transition to pool.",
        ],
    },

    # ----- 10-20 Chores & Pools -----
    {
        "id": "US-10", "slug": "create-chore",
        "title": "Create a chore",
        "area": CHORES, "priority": "Critical",
        "sources": {"scope": "§2.10", "spec": "§User Stories 10"},
        "design": [
            "design/screens/chore-editor.md",
            "design/components/form-field.md",
            "design/components/button.md",
        ],
        "preconditions": ["Parent signed in (US-1).", "Child profile exists (US-4)."],
        "given": "a parent on the chores page",
        "when": "they create a chore with name, point value, optional `review_flagged`, and optional `due_at`",
        "then": [
            "A `Chore` row is created in the correct pool (recurring vs one-off, decided by the parent — see US-11).",
            "The chore is visible to the kid on the next sync tick.",
            "Validation: name non-empty; point value > 0; `due_at` only meaningful for one-off chores (see US-13).",
        ],
        "ui": [
            "Editor uses `form-field.md` for name + value, toggle switch for `review_flagged` and recurring/one-off, date picker for `due_at` (disabled unless one-off).",
            "Submit CTA is disabled until required fields are valid.",
        ],
        "a11y": [
            "All form fields labelled (WCAG 1.3.1).",
            "Toggle switches announce on/off state via aria (WCAG 4.1.2).",
            "Validation errors are programmatically associated to fields and announced (WCAG 1.3.1, 3.3.1).",
        ],
        "evidence": [
            "Screenshot of editor pre-fill.",
            "Screenshot of validation error.",
            "Screenshot of kid SPA showing the new chore in the pool.",
            "Network `.har` for `POST /api/chores`.",
            "DB row for `Chore`.",
        ],
    },
    {
        "id": "US-11", "slug": "recurring-vs-oneoff",
        "title": "Choose recurring vs one-off when creating",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.11", "spec": "§User Stories 11"},
        "design": ["design/screens/chore-editor.md", "design/components/toggle.md"],
        "preconditions": ["Same as US-10."],
        "given": "a parent creating a chore",
        "when": "they toggle recurring/one-off in the editor",
        "then": [
            "The chore's `kind` field is set to `recurring` or `one_off` accordingly.",
            "Recurring: no `due_at` exposed / accepted.",
            "One-off: `due_at` input becomes enabled.",
            "Lifecycle on resolve behaves per CONTEXT.md glossary: recurring returns to pool; one-off is removed from circulation on resolve.",
        ],
        "ui": [
            "Toggle uses `toggle.md`; both states labelled inline.",
            "When switching to recurring, the `due_at` field collapses (animatable).",
        ],
        "a11y": [
            "Toggle's on/off state is conveyed by both text label and visual position (WCAG 1.4.1).",
            "Disabled `due_at` is announced as disabled to assistive tech (WCAG 4.1.2).",
        ],
        "evidence": ["Screenshots of editor in both toggle positions.", "DB row showing `kind` field."],
    },
    {
        "id": "US-12", "slug": "edit-delete-chore",
        "title": "Edit or delete a pooled chore",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.12", "spec": "§User Stories 12"},
        "design": ["design/screens/chore-editor.md", "design/components/confirmation-dialog.md"],
        "preconditions": [
            "At least one chore exists in the pool (from US-10).",
            "The chore is in `status: pool` — not claimed.",
        ],
        "given": "a parent viewing a pooled chore",
        "when": "they edit a field and save, OR tap Delete and confirm",
        "then": [
            "Edit: change persists; kid sees updated values on the next sync tick.",
            "Edit: `updated_at` per field advances; per-field last-write-wins applies (US-49).",
            "Delete: chore row archived (or removed per implementation) and disappears from the kid pool on the next sync.",
            "Edit a claimed chore is disabled in v1 (per scope-brief §2.12); the editor surfaces a disabled state with explanatory copy.",
        ],
        "ui": [
            "Delete requires `confirmation-dialog.md`.",
            "Edit form pre-populates current values.",
        ],
        "a11y": [
            "Edit fields keep their labels and order from US-10.",
            "Delete confirmation traps focus (WCAG 2.4.3).",
        ],
        "evidence": [
            "Screenshots of edit form and confirm-delete dialog.",
            "Network `.har` for `PATCH /api/chores/:id` and `DELETE /api/chores/:id`.",
            "DB row diff for the chore.",
            "Screenshot of kid SPA reflecting the change.",
        ],
    },
    {
        "id": "US-13", "slug": "deadline-oneoff",
        "title": "Deadline on a one-off chore",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.13", "spec": "§User Stories 13"},
        "design": ["design/components/date-picker.md"],
        "preconditions": ["Creating or editing a one-off chore."],
        "given": "a parent creating or editing a one-off chore",
        "when": "they set a `due_at` timestamp",
        "then": [
            "The chore's deadline-expiry path is active.",
            "If the kid does not complete it by `due_at`, the server-side expiry pass transitions the chore to `status: expired` and enqueues a parent notification (US-38).",
            "Validation: cannot set `due_at` on a recurring chore (US-11).",
        ],
        "ui": ["Date picker uses `date-picker.md`; default value unset; reasonable future-only restriction."],
        "a11y": [
            "Date picker is keyboard-operable and announces selected value (WCAG 1.3.1, 2.1.1).",
            "Error state for past dates is announced.",
        ],
        "evidence": [
            "Screenshot of editor with `due_at` set.",
            "DB row showing `due_at`.",
            "(Time-dependent) screenshot after expiry pass — force fixed staging time per runbook §9.",
        ],
    },
    {
        "id": "US-14", "slug": "review-flagged",
        "title": "Mark a chore review-flagged",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.14", "spec": "§User Stories 14"},
        "design": ["design/components/toggle.md"],
        "preconditions": ["Creating or editing a chore."],
        "given": "a parent creating or editing a chore",
        "when": "they set `review_flagged = true`",
        "then": [
            "The chore is marked `review_flagged = true`.",
            "When the kid marks it complete (US-18), the server holds the points until parent approval (US-33 path for approval; the denied path returns the chore to pool per spec state machine).",
        ],
        "ui": ["Toggle has visible explanation: \"I'll approve before points are awarded.\""],
        "a11y": ["Help text associated to the toggle via `aria-describedby` (WCAG 1.3.1, 3.3.2)."],
        "evidence": [
            "Screenshot of editor with review flag on.",
            "End-to-end: chore created → kid marks done → points NOT awarded yet → parent approves → points awarded.",
        ],
    },
    {
        "id": "US-15", "slug": "available-extras",
        "title": "Kid sees \"Available Extras\"",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.15", "spec": "§User Stories 15"},
        "design": ["design/screens/kid-today.md", "design/components/chore-card.md"],
        "preconditions": [
            "At least one chore in pool (US-10).",
            "Kid device signed in (US-5).",
        ],
        "given": "a kid on the kiosk on the Today screen",
        "when": "they open Today",
        "then": [
            "Every claimable chore (status: pool) across both pools is listed under \"Available Extras\".",
            "Each card shows chore name, point value, recurring/one-off indicator, and (for one-off) a deadline.",
            "Claimed chores do NOT also appear here (US-17).",
        ],
        "ui": [
            "Section header \"Available Extras\" using the kid-side accent.",
            "Chore cards use `chore-card.md` with point token shown prominently.",
        ],
        "a11y": [
            "Cards are buttons with accessible names including chore name and point value (WCAG 4.1.2).",
            "Section headings use semantic heading levels (WCAG 1.3.1).",
        ],
        "evidence": [
            "Screenshot of Today screen with populated Available Extras.",
            "Network `.har` for `GET /api/chores` (or equivalent).",
        ],
    },
    {
        "id": "US-16", "slug": "claim-chore-one-tap",
        "title": "Claim a chore with one tap",
        "area": CHORES, "priority": "Critical",
        "sources": {"scope": "§2.16", "spec": "§User Stories 16"},
        "design": ["design/components/chore-card.md", "design/components/button.md"],
        "preconditions": ["Available Extras has at least one chore (US-15)."],
        "given": "a kid viewing Available Extras",
        "when": "they tap a chore",
        "then": [
            "Chore `status` becomes `claimed`; `claimed_by_child_id` and `claimed_at` are set.",
            "The chore moves into the kid's \"My Active\" section (US-17).",
            "Optimistic UI: card moves out of Available Extras immediately (US-46 path).",
            "No second device prompt; one tap suffices.",
        ],
        "ui": ["Tapping the card (not a separate \"Claim\" button) initiates the claim per spec."],
        "a11y": [
            "Tap target ≥ 44x44 CSS px (WCAG 2.5.5).",
            "Action result announced via aria-live (WCAG 4.1.3).",
        ],
        "evidence": [
            "Screenshot of Available Extras before tap.",
            "Screenshot after tap showing chore in My Active.",
            "Network `.har` for the claim mutation.",
            "DB row showing `status: claimed`.",
        ],
    },
    {
        "id": "US-17", "slug": "my-active",
        "title": "See \"My Active\" claimed chores",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.17", "spec": "§User Stories 17"},
        "design": ["design/screens/kid-today.md", "design/components/chore-card.md"],
        "preconditions": ["At least one claimed chore (US-16)."],
        "given": "a kid with one or more claimed chores",
        "when": "they open Today",
        "then": [
            "Claimed chores appear under \"My Active\".",
            "Claimed chores do NOT also appear in Available Extras.",
            "Each card shows Done and Skip affordances.",
        ],
        "ui": [
            "\"My Active\" section uses kid-side accent with subtle elevation difference from Available Extras.",
        ],
        "a11y": [
            "Cards maintain accessible names; Done and Skip buttons have descriptive accessible names (WCAG 4.1.2).",
        ],
        "evidence": [
            "Screenshot of Today with both sections populated.",
            "Screenshot showing a claimed chore absent from Available Extras.",
        ],
    },
    {
        "id": "US-18", "slug": "mark-chore-done",
        "title": "Mark a claimed chore done",
        "area": CHORES, "priority": "Critical",
        "sources": {"scope": "§2.18", "spec": "§User Stories 18"},
        "design": ["design/components/chore-card.md", "design/components/celebration-toast.md"],
        "preconditions": ["At least one claimed chore (US-16)."],
        "given": "a kid with a claimed chore in My Active",
        "when": "they tap \"Done\"",
        "then": [
            "`Chore.status = completed`.",
            "Non-review-flagged: a positive `PointsLedger` entry is appended immediately and the balance updates within the same frame (US-22).",
            "Review-flagged: points held until parent approval (US-37 → US-43 path); chore status remains `completed` (pending review).",
            "A celebratory affordance renders per the design spec (no over-the-top theatre; one phrase + avatar).",
        ],
        "ui": [
            "Done action visibly responds within the same frame on non-review completion.",
            "Review-flagged variant shows a quieter acknowledgement (\"Sent for review\").",
        ],
        "a11y": [
            "Celebration does not rely on sound or animation alone; the balance change is announced to assistive tech (WCAG 1.4.1, 4.1.3).",
        ],
        "evidence": [
            "Screenshot before and after tap.",
            "Network `.har` for complete mutation.",
            "DB rows for chore status transition and (if non-review) ledger entry.",
        ],
    },
    {
        "id": "US-19", "slug": "skip-chore",
        "title": "Skip a claimed chore",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.19", "spec": "§User Stories 19"},
        "design": ["design/components/chore-card.md"],
        "preconditions": ["A claimed chore exists."],
        "given": "a kid with a claimed chore",
        "when": "they tap \"Skip\"",
        "then": [
            "Recurring → chore returns to pool; no ledger entry; no parent ping.",
            "One-off with deadline → chore status becomes `expired`; parent is notified (US-38).",
            "One-off without deadline → chore returns to pool; no ledger entry; no parent ping.",
        ],
        "ui": [
            "Skip is a secondary affordance (less prominent than Done).",
            "For deadline one-offs, the post-skip state shows a quiet \"This chore expired\" affordance on the kid side.",
        ],
        "a11y": [
            "Skip action announces the outcome variant that will happen (e.g. \"Skip — chore will return to pool\") (WCAG 4.1.3).",
        ],
        "evidence": [
            "Three scenarios × screenshots: recurring skip, deadline one-off skip (parent ping), at-will one-off skip.",
            "DB row transitions per kind.",
        ],
    },
    {
        "id": "US-20", "slug": "streak-inline",
        "title": "See streak count on a recurring chore",
        "area": CHORES, "priority": "High",
        "sources": {"scope": "§2.20", "spec": "§User Stories 20"},
        "design": ["design/components/chore-card.md", "design/components/streak-pill.md"],
        "preconditions": [
            "At least one recurring chore with a non-zero `Streak.current_length` (run for several days or seed via admin).",
        ],
        "given": "a kid viewing a recurring chore",
        "when": "they view it in Available Extras or My Active",
        "then": [
            "Current streak is shown inline on the card (e.g. \"🔥 3\").",
            "Streak value is read from the `Streak` projection, not recomputed on the client (per scope brief).",
        ],
        "ui": ["Streak pill uses `streak-pill.md`; kid-side accent; clearly secondary to the chore name."],
        "a11y": [
            "Streak value is announced textually (e.g. \"3-day streak\"), not via emoji-only (WCAG 1.1.1, 1.4.1).",
        ],
        "evidence": [
            "Screenshot of recurring chore with streak.",
            "Network `.har` for chore fetch.",
            "DB row for `Streak` matching displayed value.",
        ],
    },

    # ----- 21-27 Points & Streaks -----
    {
        "id": "US-21", "slug": "kid-running-balance",
        "title": "Kid sees running balance on home",
        "area": POINTS, "priority": "Critical",
        "sources": {"scope": "§2.21", "spec": "§User Stories 21"},
        "design": ["design/screens/kid-home.md", "design/components/balance-badge.md"],
        "preconditions": [
            "Kid device signed in (US-5).",
            "At least one ledger entry (or seed balance of 0).",
        ],
        "given": "a kid on the kiosk home",
        "when": "they open the home screen",
        "then": [
            "Balance shown = `SUM(PointsLedger.delta) WHERE child_id = ?`.",
            "Balance is prominent (top of screen / hero area).",
            "When balance is 0, badge shows `0` with no special copy (per CONTEXT.md).",
        ],
        "ui": ["Badge uses `balance-badge.md`; large number; kid-side accent."],
        "a11y": [
            "Badge has accessible name including the numeric value (WCAG 4.1.2).",
            "Color contrast on the badge text ≥ 4.5:1.",
        ],
        "evidence": [
            "Screenshot of home screen with balance.",
            "Network `.har` for balance fetch.",
            "DB ledger sum compared to displayed value.",
        ],
    },
    {
        "id": "US-22", "slug": "instant-balance-update",
        "title": "Instant balance update on non-review completion",
        "area": POINTS, "priority": "Critical",
        "sources": {"scope": "§2.22", "spec": "§User Stories 22"},
        "design": ["design/components/balance-badge.md"],
        "preconditions": [
            "Kid on home screen with at least one claimed non-review chore (US-16 + chore with `review_flagged = false`).",
        ],
        "given": "a kid completes a non-review-flagged chore",
        "when": "the local mutation commits",
        "then": [
            "Balance updates within the same frame (no waiting on the network round-trip).",
            "The optimistic value matches what the server eventually returns (no flicker / no rollback to lower value on success).",
        ],
        "ui": ["Badge updates with a subtle animation (≤ 200 ms) — no theatrical scale."],
        "a11y": ["Balance change announced via aria-live polite (WCAG 4.1.3)."],
        "evidence": [
            "Network-throttled recording showing the balance update precedes the API response.",
            "Server ledger entry timestamp ≤ posted order.",
        ],
    },
    {
        "id": "US-23", "slug": "parent-sees-balance",
        "title": "Parent sees kid's balance on dashboard",
        "area": POINTS, "priority": "Critical",
        "sources": {"scope": "§2.23", "spec": "§User Stories 23"},
        "design": ["design/screens/parent-dashboard.md", "design/components/balance-card.md"],
        "preconditions": [
            "Parent signed in (US-1).",
            "Child profile exists (US-4).",
            "At least one ledger entry.",
        ],
        "given": "a parent on the dashboard",
        "when": "the dashboard loads",
        "then": [
            "Kid's current balance is visible.",
            "Balance equals the server-computed `SUM(PointsLedger.delta)` for the child.",
        ],
        "ui": ["Balance card uses `balance-card.md`; parent-side quiet palette (US-55)."],
        "a11y": ["Card has accessible name including child name and balance value (WCAG 4.1.2)."],
        "evidence": [
            "Screenshot of parent dashboard.",
            "DB ledger sum matches displayed value.",
        ],
    },
    {
        "id": "US-24", "slug": "streak-increment",
        "title": "Streak increments on consecutive-day completion",
        "area": POINTS, "priority": "High",
        "sources": {"scope": "§2.24", "spec": "§User Stories 24"},
        "design": ["design/components/streak-pill.md"],
        "preconditions": [
            "A recurring chore with `Streak.last_completed_on = D-1`.",
            "Force staging clock per runbook §9.",
        ],
        "given": "a recurring chore with streak last completed yesterday",
        "when": "the child completes the chore on day D",
        "then": [
            "`Streak.current_length` increments by 1.",
            "`Streak.last_completed_on = D`.",
            "Longest length updated if exceeded.",
        ],
        "ui": ["Streak pill on kid + parent views reflects the new length (US-20, US-26)."],
        "a11y": ["Skip — inherited from US-20 / US-26."],
        "evidence": [
            "DB row for `Streak` before and after.",
            "Screenshot of streak pill before and after.",
        ],
    },
    {
        "id": "US-25", "slug": "streak-reset",
        "title": "Streak resets on a missed day",
        "area": POINTS, "priority": "High",
        "sources": {"scope": "§2.25", "spec": "§User Stories 25"},
        "design": ["design/components/streak-pill.md"],
        "preconditions": [
            "Recurring chore with `Streak.last_completed_on < D-1`.",
            "Force staging clock per runbook §9.",
        ],
        "given": "a recurring chore with a stale streak",
        "when": "day D arrives without completion and then the child completes it",
        "then": [
            "`Streak.current_length` resets to 1 (fresh streak).",
            "`Streak.last_completed_on = D`.",
            "Longest length is preserved.",
        ],
        "ui": ["Streak pill shows `1` post-completion."],
        "a11y": ["Skip — inherited from US-20."],
        "evidence": ["DB row for `Streak`.", "Screenshot of streak pill."],
    },
    {
        "id": "US-26", "slug": "parent-streaks",
        "title": "Parent sees per-chore streaks",
        "area": POINTS, "priority": "High",
        "sources": {"scope": "§2.26", "spec": "§User Stories 26"},
        "design": ["design/screens/chore-detail.md", "design/components/streak-pill.md"],
        "preconditions": ["At least one recurring chore with non-zero streak (US-24)."],
        "given": "a parent viewing a chore detail",
        "when": "they open it",
        "then": [
            "Current streak length is visible.",
            "Longest streak length is visible.",
            "Last completed date is visible.",
        ],
        "ui": [
            "Detail screen uses `chore-detail.md`; streak block uses `streak-pill.md` (parent variant).",
        ],
        "a11y": [
            "Numeric values announced in plain language (\"current 5-day streak, longest 12\") (WCAG 1.1.1).",
        ],
        "evidence": ["Screenshot of chore detail.", "DB row for `Streak`."],
    },
    {
        "id": "US-27", "slug": "streak-milestone-notification",
        "title": "Streak milestone notification (kid, in-app)",
        "area": POINTS, "priority": "High",
        "sources": {"scope": "§2.27", "spec": "§User Stories 27"},
        "design": ["design/components/celebratory-surface.md", "design/components/avatar.md"],
        "preconditions": [
            "Recurring chore; kid completes the chore on day 7 (or 30) with no prior celebration at that milestone.",
        ],
        "given": "a kid hits a 7-day or 30-day milestone",
        "when": "the streak reducer runs",
        "then": [
            "An in-app notification / celebratory surface appears for the kid.",
            "The kid's avatar is the hero per CONTEXT.md mascot rules (US-54).",
            "Celebratory phrase is one of the design-approved phrases; not theatrical.",
            "A `Notification` row is written for the kid device.",
        ],
        "ui": [
            "Surface uses `celebratory-surface.md`; large avatar; one phrase; brief animation (≤ 1s).",
        ],
        "a11y": [
            "Surface is announced via aria-live; the phrase is the readable primary text (WCAG 1.4.1, 2.3.1).",
            "No flashing content above safe thresholds (WCAG 2.3.1).",
        ],
        "evidence": [
            "Screenshot of celebratory surface.",
            "DB row for `Notification`.",
        ],
    },

    # ----- 28-36 Rewards & Redemption -----
    {
        "id": "US-28", "slug": "create-reward",
        "title": "Create a reward",
        "area": REWARDS, "priority": "Critical",
        "sources": {"scope": "§2.28", "spec": "§User Stories 28"},
        "design": ["design/screens/reward-editor.md", "design/components/form-field.md"],
        "preconditions": ["Parent signed in (US-1)."],
        "given": "a parent on the rewards page",
        "when": "they create a reward with name, point cost, and optional `stock_remaining`",
        "then": [
            "A `Reward` row exists in the household.",
            "The reward is visible to the kid in the catalog on the next sync (US-30).",
            "Validation: name non-empty; cost ≥ 1; if `stock_remaining` set, must be ≥ 0.",
        ],
        "ui": [
            "Editor uses `reward-editor.md`; stock field is optional and disabled unless the parent toggles \"limited stock\".",
        ],
        "a11y": [
            "Stock toggle follows US-11 a11y.",
            "Cost field has associated label and validation messaging.",
        ],
        "evidence": [
            "Screenshot of reward editor.",
            "DB row for `Reward`.",
            "Screenshot of kid catalog showing the new reward.",
        ],
    },
    {
        "id": "US-29", "slug": "edit-remove-reward",
        "title": "Edit or remove a reward",
        "area": REWARDS, "priority": "High",
        "sources": {"scope": "§2.29", "spec": "§User Stories 29"},
        "design": ["design/screens/reward-editor.md", "design/components/confirmation-dialog.md"],
        "preconditions": ["At least one reward exists (US-28)."],
        "given": "a parent viewing a reward",
        "when": "they edit a field and save, OR tap Remove and confirm",
        "then": [
            "Edit: change persists; kid sees updated catalog on next sync.",
            "Remove: reward disappears from the kid catalog on next sync; no in-flight redemption created.",
        ],
        "ui": [
            "Remove requires `confirmation-dialog.md`.",
            "Catalog update is eventual; UI does not require a manual refresh on the kid side.",
        ],
        "a11y": [
            "Edit fields labelled; remove confirmation traps focus (WCAG 2.4.3).",
        ],
        "evidence": [
            "Screenshots of edit form and confirm-remove dialog.",
            "Network `.har` for edit/remove calls.",
            "DB row diff.",
        ],
    },
    {
        "id": "US-30", "slug": "browse-reward-catalog",
        "title": "Kid browses the reward catalog",
        "area": REWARDS, "priority": "High",
        "sources": {"scope": "§2.30", "spec": "§User Stories 30"},
        "design": ["design/screens/kid-redeem.md", "design/components/reward-card.md"],
        "preconditions": ["At least one reward exists (US-28)."],
        "given": "a kid on the kiosk",
        "when": "they open Redeem",
        "then": [
            "Every reward is shown with name, description (if any), and point cost.",
            "Out-of-stock rewards are visibly marked (US-36).",
        ],
        "ui": ["Catalog uses `reward-card.md`; cost badge uses kid-side accent."],
        "a11y": [
            "Each card has accessible name with reward name and cost (WCAG 4.1.2).",
            "Out-of-stock state is conveyed by both visual badge and accessible name (\"Out of stock\") (WCAG 1.4.1).",
        ],
        "evidence": [
            "Screenshot of catalog with multiple rewards.",
            "Screenshot of catalog with out-of-stock reward.",
        ],
    },
    {
        "id": "US-31", "slug": "request-redemption",
        "title": "Kid requests a redemption",
        "area": REWARDS, "priority": "Critical",
        "sources": {"scope": "§2.31", "spec": "§User Stories 31"},
        "design": ["design/screens/kid-redeem.md", "design/components/reward-card.md"],
        "preconditions": [
            "Reward catalog has a reward the kid can afford.",
            "Kid has a non-zero balance.",
        ],
        "given": "a kid on the Redeem screen",
        "when": "they tap a reward",
        "then": [
            "A `Redemption` row is created with `status: pending`.",
            "A parent notification is enqueued (US-39).",
            "No points are deducted at this stage.",
            "Optimistic local state shows the request as pending on the kid side.",
        ],
        "ui": [
            "Tap target is the reward card.",
            "Confirmation affordance: design may include a confirm step before request commits.",
        ],
        "a11y": [
            "Tap target ≥ 44x44 CSS px (WCAG 2.5.5).",
            "Result announced via aria-live (WCAG 4.1.3).",
        ],
        "evidence": [
            "Screenshot before and after tap.",
            "Network `.har` for `POST /api/redemptions`.",
            "DB rows: `Redemption` and `Notification`.",
        ],
    },
    {
        "id": "US-32", "slug": "parent-pending-queue",
        "title": "Parent sees pending requests on dashboard",
        "area": REWARDS, "priority": "High",
        "sources": {"scope": "§2.32", "spec": "§User Stories 32"},
        "design": ["design/screens/parent-dashboard.md", "design/components/pending-item.md"],
        "preconditions": ["At least one pending redemption (US-31)."],
        "given": "a parent on the dashboard",
        "when": "the dashboard loads",
        "then": [
            "Pending redemptions are listed with kid name, reward name, and cost.",
            "Each row has Approve and Deny controls.",
        ],
        "ui": ["List uses `pending-item.md`; parent-side quiet palette."],
        "a11y": [
            "List semantic structure preserved (WCAG 1.3.1).",
            "Approve/Deny buttons have accessible names with reward context.",
        ],
        "evidence": [
            "Screenshot of dashboard with pending queue.",
            "Network `.har` for `GET /api/redemptions?status=pending`.",
        ],
    },
    {
        "id": "US-33", "slug": "parent-approve",
        "title": "Parent approves a pending redemption",
        "area": REWARDS, "priority": "Critical",
        "sources": {"scope": "§2.33", "spec": "§User Stories 33"},
        "design": ["design/screens/parent-dashboard.md", "design/components/pending-item.md"],
        "preconditions": ["Pending redemption exists (US-31)."],
        "given": "a parent on a pending redemption row",
        "when": "they tap Approve",
        "then": [
            "`Redemption.status = approved`.",
            "A negative `PointsLedger` entry is appended (delta = -cost).",
            "The kid is notified (US-44).",
            "If `stock_remaining` is set, stock is decremented (or refused per scope-brief §7 Q6 default — refuse at request time when stock = 0, decrement at approval).",
        ],
        "ui": ["Approve is a primary action; Deny is secondary in the row."],
        "a11y": [
            "Action result announced (WCAG 4.1.3).",
            "Focus moves to the next pending item or to the empty state.",
        ],
        "evidence": [
            "Screenshot of row before and after.",
            "Network `.har` for approval call.",
            "DB rows: `Redemption` (status), `PointsLedger` (delta), `Notification` (kid).",
        ],
    },
    {
        "id": "US-34", "slug": "parent-deny",
        "title": "Parent denies with optional reason",
        "area": REWARDS, "priority": "High",
        "sources": {"scope": "§2.34", "spec": "§User Stories 34"},
        "design": ["design/components/deny-dialog.md"],
        "preconditions": ["Pending redemption exists."],
        "given": "a parent on a pending redemption row",
        "when": "they tap Deny and optionally enter a reason",
        "then": [
            "`Redemption.status = denied` with `denial_reason` captured if provided.",
            "No points moved.",
            "The kid is notified (US-44).",
        ],
        "ui": ["Deny opens a dialog with an optional textarea; reason optional per spec."],
        "a11y": [
            "Dialog traps focus; textarea has associated label (WCAG 1.3.1, 2.4.3).",
            "Submit button label clarifies \"Deny without reason\" vs \"Deny with reason\".",
        ],
        "evidence": [
            "Screenshot of deny dialog.",
            "DB row for `Redemption` with status and reason.",
        ],
    },
    {
        "id": "US-35", "slug": "parent-reverse",
        "title": "Parent reverses an approved redemption",
        "area": REWARDS, "priority": "High",
        "sources": {"scope": "§2.35", "spec": "§User Stories 35"},
        "design": ["design/screens/parent-dashboard.md", "design/components/confirmation-dialog.md"],
        "preconditions": ["An approved `Redemption` exists."],
        "given": "a previously approved redemption",
        "when": "the parent taps Reverse and confirms",
        "then": [
            "A positive `PointsLedger` entry offsets the original debit.",
            "`Redemption.status = reversed`.",
            "The kid is notified (US-44).",
        ],
        "ui": ["Reverse requires a confirmation dialog (destructive)."],
        "a11y": ["Confirmation traps focus and is announced."],
        "evidence": [
            "Screenshot of confirmation dialog.",
            "DB rows: `Redemption` (status), `PointsLedger` (positive delta), `Notification`.",
        ],
    },
    {
        "id": "US-36", "slug": "stock-limited-overflow",
        "title": "Stock-limited reward refuses overflow",
        "area": REWARDS, "priority": "High",
        "sources": {"scope": "§2.36", "spec": "§User Stories 36"},
        "design": ["design/components/reward-card.md"],
        "preconditions": ["Reward with `stock_remaining = 0` (seeded via runbook §4.4 or admin)."],
        "given": "a kid viewing an out-of-stock reward",
        "when": "they tap it",
        "then": [
            "The request is refused client-side (visible out-of-stock state).",
            "No `Redemption` row is created.",
            "No parent notification.",
            "Server returns 4xx if a request slips through.",
        ],
        "ui": [
            "Out-of-stock badge is shown on the card; tap does not initiate redemption.",
            "Affordance is disabled (greyed) with a tooltip or label \"Out of stock\".",
        ],
        "a11y": [
            "Disabled state conveyed by both visual styling and `aria-disabled` (WCAG 4.1.2).",
            "Out-of-stock label is in the accessible name.",
        ],
        "evidence": [
            "Screenshot of out-of-stock reward card.",
            "Network `.har` confirming no `POST /api/redemptions` for the reward.",
        ],
    },

    # ----- 37-45 Notifications -----
    {
        "id": "US-37", "slug": "parent-ping-review-pending",
        "title": "Parent ping: review-flagged completion",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.37", "spec": "§User Stories 37"},
        "design": ["design/components/notification-list.md", "design/components/notification-toast.md"],
        "preconditions": ["Review-flagged chore; kid marks it complete (US-18)."],
        "given": "a review-flagged chore is marked done",
        "when": "the completion commits server-side",
        "then": [
            "Parent's in-app notification list gains a \"Review pending\" entry with the chore name.",
            "If parent opted into web push on this device (US-45), a web-push notification is delivered.",
        ],
        "ui": [
            "Notification uses parent-side quiet palette; affordance to jump to the pending review.",
        ],
        "a11y": [
            "Notification announced via aria-live; actionable with a single activation (WCAG 4.1.3, 2.1.1).",
        ],
        "evidence": [
            "Screenshot of parent notification list.",
            "(If push opt-in) screenshot of lock-screen push on the parent device.",
            "DB row for `Notification`.",
        ],
    },
    {
        "id": "US-38", "slug": "parent-ping-deadline-expired",
        "title": "Parent ping: deadline expired",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.38", "spec": "§User Stories 38"},
        "design": ["design/components/notification-list.md"],
        "preconditions": [
            "Deadline one-off chore exists; force staging clock past `due_at` per runbook §9.",
        ],
        "given": "a deadline one-off chore passes `due_at` without completion",
        "when": "the expiry pass runs",
        "then": [
            "Chore transitions to `status: expired`.",
            "Parent's in-app notification list gains an entry.",
            "If push opt-in, web-push fires.",
        ],
        "ui": ["Skip — inherited from US-37."],
        "a11y": ["Skip — inherited from US-37."],
        "evidence": [
            "DB row for chore (status) and notification.",
            "Screenshot of notification.",
        ],
    },
    {
        "id": "US-39", "slug": "parent-ping-redemption-requested",
        "title": "Parent ping: redemption requested",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.39", "spec": "§User Stories 39"},
        "design": ["design/components/notification-list.md"],
        "preconditions": ["Kid requests a redemption (US-31)."],
        "given": "a kid requests a redemption",
        "when": "the request commits",
        "then": [
            "Parent's in-app notification list gains a \"Redemption requested\" entry.",
            "If push opt-in, web-push fires.",
        ],
        "ui": ["Skip — inherited from US-37."],
        "a11y": ["Skip — inherited from US-37."],
        "evidence": ["DB row for notification.", "Screenshot of notification."],
    },
    {
        "id": "US-40", "slug": "parent-ping-pool-empty",
        "title": "Parent ping: recurring pool empty",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.40", "spec": "§User Stories 40"},
        "design": ["design/components/notification-list.md"],
        "preconditions": [
            "Recurring pool had claimable chores; the last one was claimed / completed (no recurrings left).",
        ],
        "given": "the recurring pool's claimable count drops to 0",
        "when": "that state change is observed",
        "then": [
            "Parent's in-app notification list gains an entry.",
            "If push opt-in, web-push fires.",
            "Notification fires once per empty transition (not on every poll).",
        ],
        "ui": ["Skip — inherited from US-37."],
        "a11y": ["Skip — inherited from US-37."],
        "evidence": ["DB row for notification.", "Screenshot of notification."],
    },
    {
        "id": "US-41", "slug": "kid-ping-new-chore",
        "title": "Kid ping: new chore in pool",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.41", "spec": "§User Stories 41"},
        "design": ["design/components/kid-notification-toast.md"],
        "preconditions": [
            "Parent creates a chore (US-10); kid SPA is in-app (open or backgrounded).",
        ],
        "given": "a parent adds a chore",
        "when": "the chore is committed",
        "then": [
            "Kid device's in-app notification list gains an entry.",
            "If the kid SPA is open and the chore is in a visible pool, the UI updates without manual refresh (eventually-consistent on next sync tick).",
            "Kid devices NEVER receive a web-push (out of scope per CONTEXT.md).",
        ],
        "ui": ["Toast uses kid-side accent; the chore name + point value is on the surface."],
        "a11y": [
            "Toast announced via aria-live; not the only signal (list also updates) (WCAG 1.4.1, 4.1.3).",
        ],
        "evidence": [
            "Screenshot of kid SPA toast.",
            "DB row for `Notification`.",
        ],
    },
    {
        "id": "US-42", "slug": "kid-ping-streak-milestone",
        "title": "Kid ping: streak milestone (celebratory)",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.42", "spec": "§User Stories 42"},
        "design": ["design/components/celebratory-surface.md"],
        "preconditions": ["Recurring chore; milestone (7-day or 30-day) reached (US-27)."],
        "given": "a kid hits a milestone",
        "when": "the streak reducer runs",
        "then": [
            "An in-app celebratory surface appears (US-27).",
            "Avatar is the hero (US-54).",
            "No web-push (kid devices never receive push).",
        ],
        "ui": ["Inherits US-27 / US-54 surface styling."],
        "a11y": ["Inherits US-27 a11y."],
        "evidence": ["Screenshot of celebratory surface.", "DB row for `Notification`."],
    },
    {
        "id": "US-43", "slug": "kid-ping-points-awarded",
        "title": "Kid ping: points awarded after parent approval",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.43", "spec": "§User Stories 43"},
        "design": ["design/components/kid-notification-toast.md"],
        "preconditions": [
            "Review-flagged completion approved (US-37 → US-33-style approval for chore completion).",
        ],
        "given": "a parent approves a review-flagged completion",
        "when": "the approval commits",
        "then": [
            "Kid receives an in-app notification announcing the points increase.",
            "Kid's balance updates accordingly.",
            "No web-push.",
        ],
        "ui": ["Inherits US-41 toast styling."],
        "a11y": ["Inherits US-41 a11y."],
        "evidence": [
            "Screenshot of kid SPA toast and updated balance.",
            "DB rows: notification + ledger.",
        ],
    },
    {
        "id": "US-44", "slug": "kid-ping-redemption-resolved",
        "title": "Kid ping: redemption approved or denied",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.44", "spec": "§User Stories 44"},
        "design": ["design/components/kid-notification-toast.md"],
        "preconditions": [
            "Redemption exists; parent acts (approve US-33 / deny US-34 / reverse US-35).",
        ],
        "given": "a redemption resolves",
        "when": "the parent acts",
        "then": [
            "Kid receives an in-app notification with the outcome.",
            "If approved, balance reflects the debit.",
            "If denied, balance unchanged; optional reason shown.",
            "If reversed, balance reflects the offset.",
            "No web-push.",
        ],
        "ui": ["Inherits US-41 toast styling."],
        "a11y": ["Inherits US-41 a11y."],
        "evidence": [
            "Screenshots per outcome variant (approved / denied / reversed).",
            "DB rows: notifications + ledger entries.",
        ],
    },
    {
        "id": "US-45", "slug": "web-push-opt-in",
        "title": "Per-device web-push opt-in (parent only)",
        "area": NOTIFS, "priority": "High",
        "sources": {"scope": "§2.45", "spec": "§User Stories 45"},
        "design": ["design/components/toggle.md", "design/components/lock-screen-notification.md"],
        "preconditions": [
            "Parent signed in on a parent device.",
            "Staging VAPID keys configured; OS-level push enabled.",
        ],
        "given": "a parent on a device",
        "when": "they toggle \"Allow push\" in settings",
        "then": [
            "The device is subscribed to the parent's VAPID push endpoint.",
            "Subsequent events 37-40 deliver a web-push ping to the lock screen.",
            "Toggle is off by default.",
            "Kid devices never subscribe (out of scope).",
        ],
        "ui": [
            "Toggle uses `toggle.md`; default off; explanation mentions what pings they'll receive.",
        ],
        "a11y": [
            "Toggle state announced; the explanation is programmatically associated via `aria-describedby` (WCAG 1.3.1, 3.3.2).",
        ],
        "evidence": [
            "Screenshot of toggle off (default).",
            "Screenshot of toggle on with subscription state.",
            "Screenshot of lock-screen push on the parent device.",
            "DB row for the subscription.",
        ],
    },

    # ----- 46-49 Sync & Offline -----
    {
        "id": "US-46", "slug": "kid-offline",
        "title": "Kid works offline (Dexie outbox)",
        "area": SYNC, "priority": "High",
        "sources": {"scope": "§2.46", "spec": "§User Stories 46"},
        "design": ["design/screens/kid-today.md"],
        "preconditions": [
            "Kid device linked; kid SPA loaded at least once so the SW + Dexie store are primed.",
        ],
        "given": "a kid device with no network",
        "when": "the kid claims or completes a chore",
        "then": [
            "The mutation is persisted in the Dexie outbox.",
            "The UI updates optimistically (US-22 applies).",
            "On reconnect, the mutation replays with the original `updated_at` and a stable operation ID for idempotency.",
            "The SW does NOT intercept mutation requests (per scope brief §3; mutations go through Dexie first).",
        ],
        "ui": ["Subtle offline indicator (banner or icon) signals the kid is in offline mode."],
        "a11y": ["Offline indicator announced via aria-live (WCAG 4.1.3)."],
        "evidence": [
            "Dexie / IndexedDB dump before and after the offline mutation.",
            "Screenshot of UI update while offline.",
            "Screenshot of the offline indicator.",
            "Network `.har` showing no outbound request until reconnect.",
            "DB rows applied on reconnect with original `updated_at`.",
        ],
    },
    {
        "id": "US-47", "slug": "parent-realtime-activity",
        "title": "Parent sees near-real-time kid activity",
        "area": SYNC, "priority": "High",
        "sources": {"scope": "§2.47", "spec": "§User Stories 47"},
        "design": ["design/screens/parent-dashboard.md"],
        "preconditions": ["Both parent and kid devices online; parent SPA open."],
        "given": "both devices online",
        "when": "the kid takes an action (claim, complete, redeem)",
        "then": [
            "Parent's dashboard reflects the change within a few seconds via WebSocket fan-out.",
            "No manual refresh required.",
            "Reconnect path: when the WS is closed and reopened, the parent sees a single GET resume plus a fresh WS handshake.",
        ],
        "ui": ["Updated state visible on the relevant dashboard card / pending queue."],
        "a11y": ["Skip — covered by per-component a11y (US-22, US-23, US-32)."],
        "evidence": [
            "WebSocket trace showing the event pushed to the parent.",
            "Screenshot before and after the kid action.",
        ],
    },
    {
        "id": "US-48", "slug": "offline-edits-reconcile",
        "title": "Offline edits flow in cleanly on reconnect",
        "area": SYNC, "priority": "High",
        "sources": {"scope": "§2.48", "spec": "§User Stories 48"},
        "design": ["design/screens/kid-today.md"],
        "preconditions": [
            "Parent edits a chore (e.g. point value) while the kid is offline.",
            "Kid reconnects.",
        ],
        "given": "a parent edited a chore while the kid was offline",
        "when": "the kid reconnects",
        "then": [
            "The kid's local cache reconciles without losing either side's intent.",
            "Per-field last-write-wins resolves any conflict (US-49).",
            "No clobbering of offline kid actions; no clobbering of the parent's edit.",
        ],
        "ui": ["UI updates on kid side without manual refresh."],
        "a11y": ["Skip — covered by component a11y."],
        "evidence": [
            "DB row state after reconciliation.",
            "Screenshot of kid UI post-reconnect.",
        ],
    },
    {
        "id": "US-49", "slug": "last-write-wins-per-field",
        "title": "Per-field last-write-wins on conflicts",
        "area": SYNC, "priority": "High",
        "sources": {"scope": "§2.49", "spec": "§User Stories 49"},
        "design": [],
        "preconditions": [
            "Same chore edited on both parent and kid sides on different fields while disconnected.",
        ],
        "given": "the parent and kid both edited different fields of the same chore",
        "when": "both edits arrive at the server",
        "then": [
            "Each field is applied independently with its own `updated_at`.",
            "The union persists; neither side clobbers the other.",
            "The server applies if-and-only-if `received.updated_at > stored.updated_at` for that field (per spec §\"Architectural decisions\").",
        ],
        "ui": ["No UI; backend behaviour."],
        "a11y": ["N/A — backend logic."],
        "evidence": [
            "DB row showing per-field `updated_at` after both writes applied.",
            "Server logs capturing the per-field apply / skip decisions.",
        ],
    },

    # ----- 50-53 Empty States & Onboarding Nudges -----
    {
        "id": "US-50", "slug": "parent-first-chore-cta",
        "title": "Parent first chore CTA",
        "area": EMPTY, "priority": "Standard",
        "sources": {"scope": "§2.50", "spec": "§User Stories 50"},
        "design": ["design/components/cta-card.md", "design/components/nudge-banner.md"],
        "preconditions": ["Parent signed in; zero chores exist in the household."],
        "given": "a parent with zero chores",
        "when": "they open the dashboard",
        "then": [
            "Primary CTA reads \"Add your first chore\" with secondary copy describing chore kinds.",
            "Nudge banner stays until ≥1 chore exists in either pool.",
            "Once a chore exists, the CTA/banner is replaced by the normal dashboard skeleton.",
        ],
        "ui": [
            "CTA card uses `cta-card.md`; parent-side quiet palette.",
            "Banner uses `nudge-banner.md`; dismissible but auto-hides once a chore exists.",
        ],
        "a11y": [
            "CTA has accessible name including \"Add your first chore\".",
            "Banner uses polite aria-live on dismissal/auto-hide (WCAG 4.1.3).",
        ],
        "evidence": [
            "Screenshot of dashboard with empty state.",
            "Screenshot after adding the first chore (banner gone).",
        ],
    },
    {
        "id": "US-51", "slug": "parent-first-reward-cta",
        "title": "Parent first reward CTA",
        "area": EMPTY, "priority": "Standard",
        "sources": {"scope": "§2.51", "spec": "§User Stories 51"},
        "design": ["design/components/cta-card.md"],
        "preconditions": ["Parent signed in; zero rewards exist."],
        "given": "a parent with zero rewards",
        "when": "they open the rewards page",
        "then": [
            "Primary CTA reads \"Add your first reward\" with example suggestions (\"30 min screen time\", \"Pick dinner\").",
            "No auto-seeded rewards.",
        ],
        "ui": ["CTA card uses `cta-card.md`; parent-side quiet palette."],
        "a11y": ["CTA has accessible name including \"Add your first reward\"."],
        "evidence": ["Screenshot of rewards page empty state."],
    },
    {
        "id": "US-52", "slug": "kid-no-chores-empty",
        "title": "Kid no-chores empty state",
        "area": EMPTY, "priority": "Standard",
        "sources": {"scope": "§2.52", "spec": "§User Stories 52"},
        "design": ["design/components/empty-state.md", "design/components/illustration.md"],
        "preconditions": ["Kid device linked; zero chores in either pool."],
        "given": "a kid with no chores in either pool",
        "when": "they open the kiosk",
        "then": [
            "Copy: \"No chores yet. Ask a parent to add some.\"",
            "A small illustration is rendered.",
            "When the first chore lands, the state auto-transitions to the regular pool.",
        ],
        "ui": [
            "Empty state uses `empty-state.md` + `illustration.md`.",
            "Illustration follows CONTEXT.md style (hand-drawn accents).",
        ],
        "a11y": [
            "Illustration has `alt` text describing intent, not just visual content (WCAG 1.1.1).",
            "Page remains fully readable without the illustration (WCAG 1.4.1).",
        ],
        "evidence": [
            "Screenshot of empty state.",
            "Screenshot after first chore arrives (auto-transition).",
        ],
    },
    {
        "id": "US-53", "slug": "kid-first-link-welcome",
        "title": "Kid first-link welcome",
        "area": EMPTY, "priority": "Standard",
        "sources": {"scope": "§2.53", "spec": "§User Stories 53 (= US-9)"},
        "design": ["design/screens/kid-welcome.md"],
        "preconditions": ["Kid device freshly linked; zero chores."],
        "given": "a kid on first link before any chore exists",
        "when": "they open the kiosk",
        "then": [
            "Welcome screen renders with kid's name and avatar (US-9).",
            "Once a chore lands, auto-transitions to the empty-state / pool (US-52).",
        ],
        "ui": ["Inherits US-9."],
        "a11y": ["Inherits US-9."],
        "evidence": ["Inherits US-9 evidence."],
    },

    # ----- 54-55 Visual Identity -----
    {
        "id": "US-54", "slug": "avatar-celebratory",
        "title": "Avatar in celebratory moments",
        "area": VISUAL, "priority": "Standard",
        "sources": {"scope": "§2.54", "spec": "§User Stories 54"},
        "design": ["design/components/avatar.md", "design/components/celebratory-surface.md"],
        "preconditions": [
            "A kid has hit a milestone (US-27) or had a redemption approved (US-33 → US-44).",
        ],
        "given": "a kid who hits a milestone or gets a redemption approved",
        "when": "the celebratory surface renders",
        "then": [
            "The kid's chosen avatar is the hero.",
            "The ChoreHero emblem does not compete with the kid's avatar.",
        ],
        "ui": [
            "Avatar at hero size; emblem relegated to corner or absent per design spec.",
        ],
        "a11y": [
            "Avatar is the primary readable content (name + celebratory phrase in text) (WCAG 1.4.1).",
        ],
        "evidence": ["Screenshot of celebratory surface."],
    },
    {
        "id": "US-55", "slug": "parent-quiet-palette",
        "title": "Parent-side quiet palette",
        "area": VISUAL, "priority": "Standard",
        "sources": {"scope": "§2.55", "spec": "§User Stories 55"},
        "design": ["design/tokens/colors.json", "design/tokens/spacing.json"],
        "preconditions": ["Parent SPA surfaces rendered."],
        "given": "a parent surface",
        "when": "it renders",
        "then": [
            "Same palette (deep violet + sunshine yellow) is used but with more white space and quieter accents.",
            "Parent's phone does not feel like a toddler's toy.",
        ],
        "ui": [
            "Tokens: parent surfaces use `surface/parent-quiet` token; whitespace via `spacing/parent-roomy`.",
            "Accent usage limited to primary actions; kid-side celebratory treatments are not present.",
        ],
        "a11y": [
            "Color contrast unaffected by the quieter palette — all text-on-background meets WCAG 1.4.3.",
        ],
        "evidence": [
            "Screenshots of multiple parent surfaces (dashboard, chores, rewards, settings).",
            "Resolved token values cited from `design/tokens/colors.json`.",
        ],
    },
]

assert len(STORIES) == 55, f"expected 55, got {len(STORIES)}"


# -- Renderers ---------------------------------------------------------------

def render_bulleted(items):
    return "\n".join(f"{i + 1}. {x}" for i, x in enumerate(items))


def render_design(design_paths):
    if not design_paths:
        return "_No design artefact — backend-only behaviour._"
    return "\n".join(f"- `{p}`" for p in design_paths)


def render_scenario(s):
    then_block = "\n".join(f"{i + 1}. {x}" for i, x in enumerate(s["then"]))
    pre_block = render_bulleted(s["preconditions"])
    ui_block = render_bulleted(s["ui"])
    a11y_block = render_bulleted(s["a11y"])
    ev_block = render_bulleted(s["evidence"])
    design_block = render_design(s["design"])

    return (
        f"# `{s['id']}` — {s['title']}\n"
        f"\n"
        f"| Field | Value |\n"
        f"|-------|-------|\n"
        f"| Story ID | `{s['id']}` |\n"
        f"| Title | {s['title']} |\n"
        f"| Feature area | {s['area']} |\n"
        f"| Priority | {s['priority']} |\n"
        f"| Scope brief ref | `docs/scope-brief.md` {s['sources']['scope']} |\n"
        f"| Spec ref | `spec-v1-mvp.md` {s['sources']['spec']} |\n"
        f"\n"
        f"## Designer artefacts to match\n"
        f"\n"
        f"The UI fidelity checks below reference these files in the design\n"
        f"package (produced by the frontend-designer lane, task\n"
        f"`t_fba7600a`). The UAT engineer resolves the\n"
        f"`<from-design-package>` placeholders against these paths before\n"
        f"executing the scenario.\n"
        f"\n"
        f"{design_block}\n"
        f"\n"
        f"## Preconditions\n"
        f"\n"
        f"{pre_block}\n"
        f"\n"
        f"## Scenario\n"
        f"\n"
        f"**Given** {s['given']}\n"
        f"\n"
        f"**When** {s['when']}\n"
        f"\n"
        f"**Then** the following expected outcomes are observed:\n"
        f"\n"
        f"{then_block}\n"
        f"\n"
        f"## UI fidelity\n"
        f"\n"
        f"Each item below is a binary pass/fail check against the design\n"
        f"package. Token values in `<from-design-package>` are resolved\n"
        f"against `design/tokens/*.json` and the matching component spec\n"
        f"in `design/components/*.md` before execution.\n"
        f"\n"
        f"{ui_block}\n"
        f"\n"
        f"## Accessibility (WCAG 2.1 AA)\n"
        f"\n"
        f"{a11y_block}\n"
        f"\n"
        f"## Evidence to record\n"
        f"\n"
        f"Capture under `evidence/{s['id']}-{s['slug']}/` and reference\n"
        f"from `templates/uat-report.md` §\"Evidence index\".\n"
        f"\n"
        f"{ev_block}\n"
        f"\n"
        f"## References\n"
        f"\n"
        f"- User-story source: `docs/scope-brief.md` {s['sources']['scope']}\n"
        f"- Spec section: `spec-v1-mvp.md` {s['sources']['spec']}\n"
        f"- Cross-lane coordination: see scope-brief §5 for stories\n"
        f"  spanning multiple lanes.\n"
        f"- Glossary terms: `CONTEXT.md` ({s['area']} cluster).\n"
        f"- Runbook procedure: `uat/runbook.md` §5 (per-scenario\n"
        f"  procedure), §7 (critical path), §9 (failure modes).\n"
    )


# -- File writes -------------------------------------------------------------

for s in STORIES:
    path = ROOT / f"{s['id']}-{s['slug']}.md"
    path.write_text(render_scenario(s), encoding="utf-8")

# -- INDEX -------------------------------------------------------------------

index_lines = [
    "# ChoreHero v1 — UAT Scenario Index",
    "",
    "> One row per user story in `docs/scope-brief.md` §2. Click any",
    "> story id to jump to its executable scenario file.",
    "",
    "| ID | Title | Feature area | Priority | Critical-path | File |",
    "|----|-------|--------------|----------|---------------|------|",
]
critical_path = {
    "US-1", "US-4", "US-5", "US-10", "US-16", "US-18",
    "US-21", "US-23", "US-28", "US-31", "US-33",
}
for s in STORIES:
    cp = "★" if s["id"] in critical_path else ""
    index_lines.append(
        f"| `{s['id']}` | {s['title']} | {s['area']} | {s['priority']} | {cp} | "
        f"[`{s['id']}-{s['slug']}.md`](./{s['id']}-{s['slug']}.md) |"
    )

index_lines += [
    "",
    "**Critical path (★)** — re-run on the final staging build before",
    "sign-off. A `FAIL` or `BLOCKED` on any of these blocks ship.",
    "Matches `uat/runbook.md` §7 and the critical-path table in",
    "`uat/templates/uat-report.md`.",
    "",
    "## Totals by area",
    "",
    "| Feature area | Count |",
    "|--------------|-------|",
]
from collections import Counter
area_counts = Counter(s["area"] for s in STORIES)
for area, count in area_counts.items():
    index_lines.append(f"| {area} | {count} |")
index_lines += [
    "",
    f"**Total scenarios:** {len(STORIES)}",
    "",
    "## Synthesis provenance",
    "",
    "- Source of truth: `docs/scope-brief.md` §2 (55 Given/When/Then user stories).",
    "- Cross-checked against: `spec-v1-mvp.md` §User Stories 1–55.",
    "- Voice + palette anchors: `CONTEXT.md`.",
    "- Locked architecture: `docs/adr/0001-kid-identity-is-the-device.md`.",
    "- Designer fidelity rules: `design/tokens/*.json` + `design/components/*.md`",
    "  (placeholder paths until `t_fba7600a` ships the package).",
    "- Authoring run: programmatic via `uat/tools/generate_scenarios.py`",
    "  (deterministic; safe to regenerate).",
]

(ROOT / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

print(f"wrote {len(STORIES)} scenario files + INDEX.md")