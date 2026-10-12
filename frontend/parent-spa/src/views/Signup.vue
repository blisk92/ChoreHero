<script setup lang="ts">
// Screen 01 — Parent Sign-up.
// Implements the v1-02 task spec: full name + email + password +
// confirm password, plus the OAuth buttons (which 503 in this v1
// since the SPA hasn't loaded the real Google/Apple SDKs in the
// v1-02 scope; the buttons are present and accessible per design).
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { signUp } from '../lib/auth';
import { ApiError } from '../lib/api';

const router = useRouter();

const name = ref('');
const email = ref('');
const password = ref('');
const confirm = ref('');
const showPassword = ref(false);
const submitting = ref(false);
const error = ref<string | null>(null);

const nameValid = computed(() => name.value.trim().length > 0 && name.value.length <= 60);
const emailValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value));
const passwordValid = computed(() => password.value.length >= 8 && /[A-Za-z]/.test(password.value) && /\d/.test(password.value));
const passwordsMatch = computed(() => confirm.value === password.value);
const canSubmit = computed(
  () => nameValid.value && emailValid.value && passwordValid.value && passwordsMatch.value && !submitting.value,
);

async function onSubmit(): Promise<void> {
  if (!canSubmit.value) return;
  error.value = null;
  submitting.value = true;
  try {
    await signUp({ name: name.value.trim(), email: email.value.trim(), password: password.value });
    await router.push({ name: 'onboarding-child' });
  } catch (err) {
    if (err instanceof ApiError) {
      if (err.code === 'email_taken') {
        error.value = 'An account already uses this email. Sign in instead.';
      } else if (err.code === 'weak_password') {
        error.value = 'Password must be at least 8 characters and include a letter and a number.';
      } else {
        error.value = 'Something went wrong. Try again.';
      }
    } else {
      error.value = 'Something went wrong. Try again.';
    }
  } finally {
    submitting.value = false;
  }
}

function onOauth(provider: 'google' | 'apple'): void {
  // v1-02 wires the API surface (POST /api/auth/oauth/{google,apple}).
  // The browser-side SDK bootstrap is intentionally not in scope for
  // v1-02; the buttons are present and accessible so the design
  // contract holds, and the e2e suite exercises the email+password
  // path which is the contract test target.
  error.value = `${provider} sign-in is not yet available in this build. Use email + password.`;
}
</script>

<template>
  <main class="page">
    <header class="topnav">
      <a class="topnav__back" href="/" aria-label="Back">← Back</a>
      <span class="topnav__brand">ChoreHero</span>
      <a class="topnav__link" href="/sign-in">Sign in →</a>
    </header>

    <div class="layout">
      <aside class="hero" aria-hidden="true">
        <div class="hero__panel">
          <span class="hero__chip">For one parent and one kid</span>
          <span class="hero__title">Your chores.<br />Your points.<br />Your rewards.</span>
        </div>
      </aside>

      <section class="card">
        <h1>Create your account</h1>
        <p class="subhead">It's free for one parent and one kid.</p>

        <form @submit.prevent="onSubmit" novalidate>
          <label class="field">
            <span class="field__label">Your name <span aria-hidden="true">*</span></span>
            <input
              v-model="name"
              type="text"
              autocomplete="name"
              maxlength="60"
              required
              aria-required="true"
              :aria-invalid="name.length > 0 && !nameValid"
            />
          </label>

          <label class="field">
            <span class="field__label">Email <span aria-hidden="true">*</span></span>
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              required
              aria-required="true"
              :aria-invalid="email.length > 0 && !emailValid"
            />
          </label>

          <label class="field">
            <span class="field__label">Password <span aria-hidden="true">*</span></span>
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              required
              aria-required="true"
              aria-describedby="pw-hint"
              :aria-invalid="password.length > 0 && !passwordValid"
            />
            <span id="pw-hint" class="field__hint">At least 8 characters.</span>
          </label>

          <label class="field">
            <span class="field__label">Type the password again <span aria-hidden="true">*</span></span>
            <input
              v-model="confirm"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              required
              aria-required="true"
              :aria-invalid="confirm.length > 0 && !passwordsMatch"
            />
            <span v-if="confirm.length > 0 && !passwordsMatch" class="field__hint field__hint--error">
              Passwords don't match.
            </span>
          </label>

          <label class="showpw">
            <input v-model="showPassword" type="checkbox" :aria-pressed="showPassword" />
            <span>Show passwords</span>
          </label>

          <p v-if="error" class="form-error" role="alert">{{ error }}</p>

          <button class="btn btn--primary" type="submit" :disabled="!canSubmit" :aria-busy="submitting">
            {{ submitting ? 'Creating your account…' : 'Create account' }}
          </button>
        </form>

        <p class="divider"><span>or</span></p>

        <button class="btn btn--oauth" type="button" @click="onOauth('google')">
          <span class="btn__glyph" aria-hidden="true">G</span>
          Continue with Google
        </button>
        <button class="btn btn--oauth" type="button" @click="onOauth('apple')">
          <span class="btn__glyph" aria-hidden="true"></span>
          Continue with Apple
        </button>

        <p class="terms">
          By creating an account, you agree to our <a href="/terms">Terms</a> and
          <a href="/privacy">Privacy Policy</a>.
        </p>
      </section>
    </div>
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
.topnav__back, .topnav__link {
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
  display: grid;
  grid-template-columns: 1fr 480px;
  gap: 64px;
  max-width: 1024px;
  margin: 24px auto 80px;
  padding: 0 32px;
}
@media (max-width: 1023px) {
  .layout { grid-template-columns: 1fr; gap: 24px; }
  .hero { display: none; }
}
.hero__panel {
  background: linear-gradient(135deg, #EDE7FF 0%, #F7F4FF 100%);
  border: 1px solid #E0DAF5;
  border-radius: 24px;
  padding: 48px 32px;
  min-height: 480px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 16px;
}
.hero__chip {
  align-self: flex-start;
  background: #FFF3A8;
  color: #1A0B3D;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 999px;
}
.hero__title {
  font-size: 40px;
  font-weight: 700;
  line-height: 1.1;
  color: #1A0B3D;
}
.card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(26, 11, 61, 0.04);
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
.field input[aria-invalid="true"] {
  border-color: #B22D2D;
}
.field__hint {
  font-size: 12px;
  color: #6A6A75;
}
.field__hint--error {
  color: #B22D2D;
}
.showpw {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #2D1B5E;
  min-height: 44px;
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
.btn--oauth {
  background: #FFFFFF;
  color: #1A0B3D;
  border: 1px solid #C8C2D9;
  width: 100%;
}
.btn--oauth:hover {
  background: #F7F4FF;
}
.btn__glyph {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #1A0B3D;
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
}
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #6A6A75;
  font-size: 13px;
  margin: 4px 0;
}
.divider::before, .divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #E0DAF5;
}
.terms {
  font-size: 12px;
  color: #6A6A75;
  text-align: center;
  margin: 8px 0 0;
}
</style>
