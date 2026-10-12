<script setup lang="ts">
// Screen 03 — Parent dashboard.
//
// v1-02 ships the empty-state and onboarding-CTA portion of the
// dashboard per CONTEXT.md: when the household has no chore and no
// reward and no child yet, the parent sees the big primary CTAs that
// nudge them through onboarding. Higher-density widgets (pending
// redemptions, streaks, notification strip) arrive with v1-04
// (chores/rewards) and v1-05 (notifications). The empty state is the
// only state the v1-02 e2e tests against, and it's the state new
// parents will live in until those tickets land.
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { auth, refreshChildren, refreshMe, signOut, type Child } from '../lib/auth';

const router = useRouter();
const ready = ref(false);

onMounted(async () => {
  // /api/auth/me resolves the in-memory token (or null on a hard
  // reload). After that, fetch the children list so the empty-state
  // CTA can flip from "Create your first chore" to "Set up [Kid]'s
  // profile" once a child row exists.
  if (!auth.initialized) {
    await refreshMe();
  }
  if (!auth.token) {
    await router.push({ name: 'signin' });
    return;
  }
  try {
    await refreshChildren();
  } catch {
    // Children endpoint failed (token expired). Drop the session.
    signOut();
    await router.push({ name: 'signin' });
    return;
  }
  ready.value = true;
});

const child = computed<Child | null>(() => auth.children[0] ?? null);
const parentName = computed(() => auth.parent?.name ?? auth.parent?.email ?? 'there');

function onSignOut(): void {
  signOut();
  router.push({ name: 'signin' });
}
</script>

<template>
  <main class="page">
    <header class="topnav">
      <span class="topnav__brand">ChoreHero</span>
      <button class="topnav__signout" type="button" @click="onSignOut">Sign out</button>
    </header>

    <div v-if="!ready" class="loading" aria-live="polite">Loading…</div>

    <section v-else class="layout">
      <h1 class="hello">Hi, {{ parentName }}.</h1>
      <p class="subhead">
        <template v-if="!child">
          Let's set up your household. Start by creating your child's profile.
        </template>
        <template v-else>
          {{ child.name }} is ready to go. Add your first chore or reward.
        </template>
      </p>

      <div class="ctas">
        <button
          v-if="!child"
          class="cta cta--primary"
          type="button"
          @click="router.push({ name: 'onboarding-child' })"
        >
          <span class="cta__title">Create your child's profile</span>
          <span class="cta__sub">Pick a name and an avatar in under a minute.</span>
        </button>

        <template v-else>
          <button class="cta cta--primary" type="button" disabled>
            <span class="cta__title">Add your first chore</span>
            <span class="cta__sub">Available in v1-04 — chores + rewards.</span>
          </button>
          <button class="cta cta--primary" type="button" disabled>
            <span class="cta__title">Add your first reward</span>
            <span class="cta__sub">Available in v1-04 — chores + rewards.</span>
          </button>
        </template>
      </div>

      <div v-if="child" class="kid">
        <span class="kid__label">Your kid</span>
        <span class="kid__name">{{ child.name }}</span>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--ch-surface-app-parent, #F7F4FF);
}
.topnav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  font-size: 14px;
}
.topnav__brand {
  font-weight: 600;
  letter-spacing: 0.5px;
}
.topnav__signout {
  border: 0;
  background: transparent;
  color: var(--ch-color-brand-violet-700, #3F2A8C);
  font-weight: 500;
  min-height: 44px;
  padding: 0 12px;
  cursor: pointer;
}
.loading {
  padding: 64px 32px;
  text-align: center;
  color: #6A6A75;
}
.layout {
  max-width: 720px;
  margin: 32px auto;
  padding: 0 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.hello {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}
.subhead {
  margin: 0 0 16px;
  color: #4A4A55;
  font-size: 15px;
}
.ctas {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.cta {
  border: 0;
  border-radius: 16px;
  background: var(--ch-color-brand-violet-700, #3F2A8C);
  color: #FFFFFF;
  padding: 24px;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: 0 8px 20px rgba(85, 56, 184, 0.20), 0 2px 4px rgba(85, 56, 184, 0.12);
  min-height: 80px;
}
.cta:hover:not(:disabled) {
  background: var(--ch-color-brand-violet-800, #2D1B5E);
}
.cta:disabled {
  background: #B8A8F0;
  cursor: not-allowed;
}
.cta__title {
  font-size: 18px;
  font-weight: 700;
}
.cta__sub {
  font-size: 13px;
  opacity: 0.9;
}
.kid {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: #FFFFFF;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 1px 2px rgba(26, 11, 61, 0.06);
  align-self: flex-start;
}
.kid__label {
  font-size: 12px;
  color: #6A6A75;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.kid__name {
  font-size: 16px;
  font-weight: 600;
}
</style>
