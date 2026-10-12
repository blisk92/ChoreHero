// Auth state — a reactive store backed by an in-memory JWT + a thin
// profile object. Per the v1-02 task body the token is *not* persisted
// to localStorage in v1 (refresh-token rotation is a v1-09 decision).
// A page reload therefore logs the user out; the dashboard empty-state
// copy directs them back to /sign-in.
//
// This is intentionally not Pinia — the surface is small (token, parent,
// household, a children list, a setter for each) and a plain
// reactive-exported object keeps the SPA dependency-light.

import { reactive } from 'vue';
import { api } from './api';

export interface Parent {
  id: string;
  email: string;
  name: string | null;
  householdId: string;
  oauthProvider: string | null;
  oauthSubject: string | null;
  createdAt: string;
}

export interface Household {
  id: string;
  name: string | null;
  timezone: string;
  createdAt: string;
}

export interface Child {
  id: string;
  name: string;
  avatarId: string;
  createdAt?: string;
}

interface AuthBundle {
  parent: Parent;
  household: Household;
  token: string;
}

interface MeResponse {
  parent: Parent;
  household: Household;
}

interface ChildrenResponse {
  children: Child[];
}

export interface AuthState {
  token: string | null;
  parent: Parent | null;
  household: Household | null;
  children: Child[];
  initialized: boolean;
}

const state = reactive<AuthState>({
  token: null,
  parent: null,
  household: null,
  children: [],
  initialized: false,
});

export function getToken(): string | null {
  return state.token;
}

export function isSignedIn(): boolean {
  return state.token !== null && state.parent !== null;
}

function applyBundle(bundle: AuthBundle): void {
  state.token = bundle.token;
  state.parent = bundle.parent;
  state.household = bundle.household;
  state.children = [];
}

export async function signUp(input: {
  email: string;
  password: string;
  name: string;
}): Promise<void> {
  const bundle = await api<AuthBundle>('/api/auth/signup', { method: 'POST', body: input, auth: false });
  applyBundle(bundle);
}

export async function signIn(input: { email: string; password: string }): Promise<void> {
  const bundle = await api<AuthBundle>('/api/auth/signin', { method: 'POST', body: input, auth: false });
  applyBundle(bundle);
}

export async function refreshMe(): Promise<void> {
  if (!state.token) {
    state.initialized = true;
    return;
  }
  try {
    const me = await api<MeResponse>('/api/auth/me');
    state.parent = me.parent;
    state.household = me.household;
  } catch {
    // Token rejected — drop the session so the router can redirect.
    signOut();
  } finally {
    state.initialized = true;
  }
}

export async function refreshChildren(): Promise<void> {
  if (!state.household) return;
  const res = await api<ChildrenResponse>(`/api/households/${state.household.id}/children`);
  state.children = res.children;
}

export async function createChild(input: { name: string; avatar_id: string }): Promise<Child> {
  if (!state.household) throw new Error('not_signed_in');
  const res = await api<{ child: Child }>(
    `/api/households/${state.household.id}/children`,
    { method: 'POST', body: input },
  );
  state.children = [...state.children, res.child];
  return res.child;
}

export function signOut(): void {
  state.token = null;
  state.parent = null;
  state.household = null;
  state.children = [];
}

export const auth = state;
