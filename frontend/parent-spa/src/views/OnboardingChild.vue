<script setup lang="ts">
// Onboarding step — "Create your child's profile".
//
// Per design: name input + 12-avatar picker grid. Fetches the
// pre-shipped avatar SVGs from the public /api/avatars endpoint so
// the same set ships everywhere (D1 in the task body). Submits a
// POST to /api/households/{id}/children and forwards to the
// dashboard on success.
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { auth, createChild, refreshMe } from '../lib/auth';
import { api, ApiError } from '../lib/api';

interface AvatarEntry {
  id: string;
  label: string;
  svg: string;
}

const router = useRouter();
const name = ref('');
const avatars = ref<AvatarEntry[]>([]);
const selectedId = ref<string | null>(null);
const avatarsError = ref<string | null>(null);
const submitting = ref(false);
const error = ref<string | null>(null);

const canSubmit = computed(
  () => name.value.trim().length > 0 && selectedId.value !== null && !submitting.value,
);

onMounted(async () => {
  if (!auth.initialized) {
    await refreshMe();
  }
  if (!auth.token) {
    await router.push({ name: 'signin' });
    return;
  }
  try {
    const res = await api<{ avatars: AvatarEntry[] }>('/api/avatars', { auth: false });
    avatars.value = res.avatars;
  } catch (err) {
    avatarsError.value =
      err instanceof ApiError
        ? 'Could not load avatars. Try again.'
        : 'Could not load avatars. Try again.';
  }
});

async function onSubmit(): Promise<void> {
  if (!canSubmit.value || !selectedId.value) return;
  error.value = null;
  submitting.value = true;
  try {
    await createChild({ name: name.value.trim(), avatar_id: selectedId.value });
    await router.push({ name: 'dashboard' });
  } catch (err) {
    if (err instanceof ApiError && err.code === 'child_already_exists') {
      // Parent came back to this step after creating a child. Just go
      // to the dashboard.
      await router.push({ name: 'dashboard' });
      return;
    }
    error.value = 'Could not save the profile. Try again.';
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <main class="page">
    <header class="topnav">
      <a class="topnav__back" href="/sign-in" aria-label="Back">← Back</a>
      <span class="topnav__brand">ChoreHero</span>
      <span aria-hidden="true" />
    </header>

    <section class="layout">
      <h1>Create your child's profile</h1>
      <p class="subhead">
        Pick a name and an avatar. You can change both later.
      </p>

      <form @submit.prevent="onSubmit" novalidate>
        <label class="field">
          <span class="field__label">Child's name <span aria-hidden="true">*</span></span>
          <input
            v-model="name"
            type="text"
            maxlength="60"
            autocomplete="off"
            required
            aria-required="true"
            placeholder="e.g. Maya"
          />
        </label>

        <fieldset class="avatars">
          <legend class="field__label">Choose an avatar</legend>
          <p v-if="avatarsError" class="form-error" role="alert">{{ avatarsError }}</p>
          <div v-else class="grid">
            <button
              v-for="a in avatars"
              :key="a.id"
              type="button"
              class="tile"
              :class="{ 'tile--selected': a.id === selectedId }"
              :aria-pressed="a.id === selectedId"
              :aria-label="a.label"
              @click="selectedId = a.id"
            >
              <span class="tile__svg" v-html="a.svg" />
              <span class="tile__label">{{ a.label }}</span>
            </button>
          </div>
        </fieldset>

        <p v-if="error" class="form-error" role="alert">{{ error }}</p>

        <button class="btn btn--primary" type="submit" :disabled="!canSubmit" :aria-busy="submitting">
          {{ submitting ? 'Saving…' : 'Create profile' }}
        </button>
      </form>
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
.topnav__back {
  color: var(--ch-color-brand-violet-700, #3F2A8C);
  font-weight: 500;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}
.topnav__brand {
  font-weight: 600;
  letter-spacing: 0.5px;
}
.layout {
  max-width: 640px;
  margin: 24px auto 80px;
  padding: 0 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}
.subhead {
  margin: -8px 0 8px;
  color: #4A4A55;
  font-size: 14px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field__label {
  font-size: 13px;
  font-weight: 500;
  color: #2D1B5E;
}
.field input {
  border: 1px solid #C8C2D9;
  border-radius: 8px;
  padding: 12px 14px;
  min-height: 44px;
  background: #FFFFFF;
  color: #1A0B3D;
  outline: none;
}
.field input:focus {
  border-color: #5538B8;
  box-shadow: 0 0 0 3px rgba(85, 56, 184, 0.18);
}
.avatars {
  border: 0;
  padding: 0;
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.avatars legend {
  padding: 0;
}
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
@media (max-width: 480px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}
.tile {
  border: 2px solid #E0DAF5;
  border-radius: 16px;
  background: #FFFFFF;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  min-height: 88px;
  transition: transform 120ms cubic-bezier(0.2, 0, 0.2, 1);
}
.tile:hover {
  transform: translateY(-1px);
}
.tile--selected {
  border-color: #5538B8;
  box-shadow: 0 0 0 3px rgba(85, 56, 184, 0.18);
}
.tile__svg {
  display: block;
  width: 56px;
  height: 56px;
  line-height: 0;
}
.tile__svg :deep(svg) {
  width: 56px;
  height: 56px;
  display: block;
}
.tile__label {
  font-size: 12px;
  font-weight: 500;
  color: #2D1B5E;
}
.form-error {
  background: #FDECEC;
  border: 1px solid #B22D2D;
  color: #8B1F1F;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  margin: 0;
}
.btn {
  border: 0;
  border-radius: 8px;
  padding: 14px 16px;
  min-height: 48px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
}
.btn--primary {
  background: #3F2A8C;
  color: #FFFFFF;
  width: 100%;
}
.btn--primary:disabled {
  background: #B8A8F0;
  cursor: not-allowed;
}
</style>
