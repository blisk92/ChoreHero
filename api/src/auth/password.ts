// ChoreHero v1 — password hashing helper.
//
// v1 password rule (single source of truth, also referenced in screen 01
// docs and in the API contract test): at least 8 characters, at least one
// letter, at least one number. The server is the source of truth; the
// client uses a looser check for instant feedback only.

import bcrypt from 'bcrypt';

const BCRYPT_ROUNDS = 12;

export async function hashPassword(plain: string): Promise<string> {
  return bcrypt.hash(plain, BCRYPT_ROUNDS);
}

export async function verifyPassword(plain: string, hash: string): Promise<boolean> {
  return bcrypt.compare(plain, hash);
}

const PASSWORD_RULE = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/;

export function isPasswordRuleSatisfied(plain: string): boolean {
  return PASSWORD_RULE.test(plain);
}
