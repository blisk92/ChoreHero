import { defineConfig } from 'vitest/config';

// ChoreHero contract tests boot a real Express server inside beforeAll and
// then issue HTTP requests to it. Vitest's default thread pool puts beforeAll
// in one worker and the test bodies in another, so the in-worker server is
// unreachable from the test. The forks pool with singleFork keeps the whole
// file in one child process so the bound port survives.

export default defineConfig({
  test: {
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true,
      },
    },
    fileParallelism: false,
    testTimeout: 60_000,
    hookTimeout: 120_000,
  },
});