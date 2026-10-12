// ChoreHero API — vitest config.
//
// Lets the contract tests `import '../src/index.js'` (the v1-01 sync-lww
// pattern) and `import '../src/index.ts'` (the v1-02 auth spec) resolve
// to the TypeScript source under src/index.ts. We register the .ts
// extension explicitly so the dynamic import in beforeAll doesn't need
// a prebuild step.

import { defineConfig } from 'vitest/config';

export default defineConfig({
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.mjs', '.json'],
  },
  test: {
    env: {
      // Used by the prisma client; tests build a real DATABASE_URL in beforeAll.
      DATABASE_URL: 'mysql://root:***@127.0.0.1:3306/chorehero',
    },
  },
});
