// ChoreHero v1 — pre-shipped avatar registry.
//
// Per the v1-02 task body (D1: avatar set is locked in this card), we ship
// exactly 12 hand-drawn illustrations, each referenced by a stable
// `avatar_id` from the kid-side and parent-side UI. v1 avatars are
// strings, not files; the SPA inlines the SVG so the API can ship them
// through the standard /api/households/{id}/children response without
// needing a CDN.
//
// Style: flat vector with hand-drawn accent strokes per CONTEXT.md
// ("flat vector base for icons and tiles; hand-drawn accent strokes
// (organic line, irregular shape) for the mascot"). The viewBox is 96x96
// and the figures are centered with a 12dp safe margin.

export interface AvatarEntry {
  id: string;
  label: string;
  /** Inline SVG markup, safe to drop into Vue via v-html or a Vue
   *  component slot. All markup is hand-authored; no user data. */
  svg: string;
}

const wrap = (inner: string): string =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img" aria-label="avatar">` +
  inner +
  `</svg>`;

export const AVATARS: ReadonlyArray<AvatarEntry> = [
  {
    id: 'fox',
    label: 'Fox',
    svg: wrap(
      `<circle cx="48" cy="58" r="22" fill="#F4A261"/>` +
      `<polygon points="32,40 40,28 46,40" fill="#F4A261"/>` +
      `<polygon points="50,40 56,28 64,40" fill="#F4A261"/>` +
      `<circle cx="40" cy="56" r="3" fill="#1B1410"/>` +
      `<circle cx="56" cy="56" r="3" fill="#1B1410"/>` +
      `<path d="M44 66 Q48 70 52 66" stroke="#1B1410" stroke-width="2" fill="none" stroke-linecap="round"/>` +
      `<path d="M30 50 Q34 56 30 62" stroke="#7C3F0F" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.6"/>`,
    ),
  },
  {
    id: 'cat',
    label: 'Cat',
    svg: wrap(
      `<circle cx="48" cy="56" r="24" fill="#9D7CD8"/>` +
      `<polygon points="30,40 32,24 40,38" fill="#9D7CD8"/>` +
      `<polygon points="56,38 64,24 66,40" fill="#9D7CD8"/>` +
      `<circle cx="40" cy="54" r="3" fill="#1B1410"/>` +
      `<circle cx="56" cy="54" r="3" fill="#1B1410"/>` +
      `<path d="M44 64 Q48 68 52 64" stroke="#1B1410" stroke-width="2" fill="none" stroke-linecap="round"/>` +
      `<line x1="28" y1="58" x2="36" y2="60" stroke="#1B1410" stroke-width="1.2" stroke-linecap="round"/>` +
      `<line x1="28" y1="62" x2="36" y2="62" stroke="#1B1410" stroke-width="1.2" stroke-linecap="round"/>` +
      `<line x1="60" y1="60" x2="68" y2="58" stroke="#1B1410" stroke-width="1.2" stroke-linecap="round"/>` +
      `<line x1="60" y1="62" x2="68" y2="62" stroke="#1B1410" stroke-width="1.2" stroke-linecap="round"/>`,
    ),
  },
  {
    id: 'owl',
    label: 'Owl',
    svg: wrap(
      `<ellipse cx="48" cy="54" rx="26" ry="28" fill="#8B5A2B"/>` +
      `<circle cx="40" cy="48" r="8" fill="#FFF4D6"/>` +
      `<circle cx="56" cy="48" r="8" fill="#FFF4D6"/>` +
      `<circle cx="40" cy="48" r="3" fill="#1B1410"/>` +
      `<circle cx="56" cy="48" r="3" fill="#1B1410"/>` +
      `<polygon points="48,54 44,58 52,58" fill="#F4A261"/>` +
      `<path d="M30 70 Q48 76 66 70" stroke="#5C3818" stroke-width="2" fill="none" stroke-linecap="round"/>`,
    ),
  },
  {
    id: 'dragon',
    label: 'Dragon',
    svg: wrap(
      `<circle cx="48" cy="56" r="22" fill="#4CB5AE"/>` +
      `<path d="M30 44 Q40 30 50 38" fill="#4CB5AE" stroke="#2A6E69" stroke-width="1.5"/>` +
      `<circle cx="40" cy="56" r="3" fill="#1B1410"/>` +
      `<circle cx="56" cy="56" r="3" fill="#1B1410"/>` +
      `<path d="M40 66 Q48 70 56 66" stroke="#1B1410" stroke-width="2" fill="none" stroke-linecap="round"/>` +
      `<path d="M66 50 Q72 56 66 64" fill="#4CB5AE" stroke="#2A6E69" stroke-width="1.5"/>`,
    ),
  },
  {
    id: 'robot',
    label: 'Robot',
    svg: wrap(
      `<rect x="28" y="30" width="40" height="44" rx="6" fill="#C0C7D1"/>` +
      `<rect x="34" y="42" width="28" height="14" rx="2" fill="#1B1410"/>` +
      `<circle cx="42" cy="49" r="3" fill="#FFD166"/>` +
      `<circle cx="54" cy="49" r="3" fill="#FFD166"/>` +
      `<line x1="48" y1="20" x2="48" y2="30" stroke="#C0C7D1" stroke-width="3" stroke-linecap="round"/>` +
      `<circle cx="48" cy="18" r="3" fill="#FFD166"/>` +
      `<rect x="40" y="62" width="16" height="6" rx="1" fill="#9BA3AE"/>`,
    ),
  },
  {
    id: 'rocket',
    label: 'Rocket',
    svg: wrap(
      `<path d="M48 14 C58 24 60 40 56 56 L40 56 C36 40 38 24 48 14 Z" fill="#EF476F"/>` +
      `<circle cx="48" cy="32" r="6" fill="#FFF4D6" stroke="#1B1410" stroke-width="1.5"/>` +
      `<path d="M40 56 L30 70 L36 56 Z" fill="#FFD166"/>` +
      `<path d="M56 56 L66 70 L60 56 Z" fill="#FFD166"/>` +
      `<path d="M44 60 L48 80 L52 60" fill="#FFD166"/>`,
    ),
  },
  {
    id: 'star',
    label: 'Star',
    svg: wrap(
      `<circle cx="48" cy="48" r="26" fill="#FFD166"/>` +
      `<polygon points="48,28 53,44 70,44 56,54 61,70 48,60 35,70 40,54 26,44 43,44" fill="#1B1410"/>`,
    ),
  },
  {
    id: 'leaf',
    label: 'Leaf',
    svg: wrap(
      `<path d="M20 70 Q24 30 70 22 Q66 70 20 70 Z" fill="#62B860"/>` +
      `<path d="M22 68 Q46 50 70 24" stroke="#1B5B22" stroke-width="2" fill="none" stroke-linecap="round"/>`,
    ),
  },
  {
    id: 'dino',
    label: 'Dino',
    svg: wrap(
      `<ellipse cx="48" cy="58" rx="26" ry="20" fill="#62B860"/>` +
      `<circle cx="40" cy="48" r="6" fill="#62B860"/>` +
      `<circle cx="38" cy="46" r="2" fill="#1B1410"/>` +
      `<path d="M28 70 L20 80" stroke="#1B5B22" stroke-width="3" stroke-linecap="round"/>` +
      `<path d="M44 70 L42 80" stroke="#1B5B22" stroke-width="3" stroke-linecap="round"/>` +
      `<path d="M58 70 L62 80" stroke="#1B5B22" stroke-width="3" stroke-linecap="round"/>`,
    ),
  },
  {
    id: 'penguin',
    label: 'Penguin',
    svg: wrap(
      `<ellipse cx="48" cy="56" rx="22" ry="28" fill="#1B1410"/>` +
      `<ellipse cx="48" cy="62" rx="14" ry="18" fill="#FFF4D6"/>` +
      `<circle cx="40" cy="46" r="2.5" fill="#FFF4D6"/>` +
      `<circle cx="56" cy="46" r="2.5" fill="#FFF4D6"/>` +
      `<polygon points="48,52 44,56 52,56" fill="#F4A261"/>`,
    ),
  },
  {
    id: 'wizard',
    label: 'Wizard',
    svg: wrap(
      `<path d="M28 30 L48 16 L68 30 L60 30 L60 70 L36 70 L36 30 Z" fill="#7C3AED"/>` +
      `<circle cx="48" cy="60" r="14" fill="#FFD9B3"/>` +
      `<circle cx="43" cy="60" r="1.5" fill="#1B1410"/>` +
      `<circle cx="53" cy="60" r="1.5" fill="#1B1410"/>` +
      `<path d="M44 66 Q48 68 52 66" stroke="#1B1410" stroke-width="1.5" fill="none" stroke-linecap="round"/>` +
      `<circle cx="48" cy="14" r="2" fill="#FFD166"/>`,
    ),
  },
  {
    id: 'wave',
    label: 'Wave',
    svg: wrap(
      `<circle cx="48" cy="48" r="28" fill="#9CC9F2"/>` +
      `<path d="M22 50 Q32 42 42 50 T62 50 T82 50" stroke="#1B4E7A" stroke-width="3" fill="none" stroke-linecap="round"/>` +
      `<path d="M22 60 Q32 52 42 60 T62 60 T82 60" stroke="#1B4E7A" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    ),
  },
];

const AVATAR_BY_ID = new Map(AVATARS.map((a) => [a.id, a]));

export function isKnownAvatarId(id: string): boolean {
  return AVATAR_BY_ID.has(id);
}

export function getAvatar(id: string): AvatarEntry | undefined {
  return AVATAR_BY_ID.get(id);
}
