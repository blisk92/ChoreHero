import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { auth, isSignedIn, refreshMe } from './lib/auth';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: () => (isSignedIn() ? '/dashboard' : '/sign-in') },
  {
    path: '/sign-up',
    name: 'signup',
    component: () => import('./views/Signup.vue'),
    meta: { public: true },
  },
  {
    path: '/sign-in',
    name: 'signin',
    component: () => import('./views/Signin.vue'),
    meta: { public: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('./views/Dashboard.vue'),
  },
  {
    path: '/onboarding/child',
    name: 'onboarding-child',
    component: () => import('./views/OnboardingChild.vue'),
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  // First load: ask /api/auth/me whether the in-memory token is still
  // good. The in-memory token does not survive a reload, so this is
  // effectively a no-op outside of the SPA's own lifetime — but it
  // validates the contract test's "reload → child row still present"
  // step.
  if (!auth.initialized) {
    await refreshMe();
  }
  if (to.meta.public) {
    if (isSignedIn() && (to.name === 'signin' || to.name === 'signup')) {
      return { path: '/dashboard' };
    }
    return true;
  }
  if (!isSignedIn()) {
    return { path: '/sign-in' };
  }
  return true;
});
