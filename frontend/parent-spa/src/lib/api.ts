// Tiny fetch wrapper for the ChoreHero API. Adds the JWT bearer token
// (when present) and parses JSON. Throws ApiError on non-2xx so call
// sites can do `try/catch` and surface the message in a banner.

import { getToken } from './auth';

export class ApiError extends Error {
  constructor(public status: number, public code: string, public detail: unknown) {
    super(typeof detail === 'object' && detail && 'message' in detail
      ? String((detail as { message: string }).message)
      : code);
  }
}

export interface ApiOpts {
  method?: 'GET' | 'POST';
  body?: unknown;
  auth?: boolean;
}

export async function api<T>(path: string, opts: ApiOpts = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (opts.body !== undefined) headers['content-type'] = 'application/json';
  if (opts.auth !== false) {
    const t = getToken();
    if (t) headers['authorization'] = `Bearer ${t}`;
  }
  const res = await fetch(path, {
    method: opts.method ?? 'GET',
    headers,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
  });
  let parsed: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }
  }
  if (!res.ok) {
    const code = (parsed && typeof parsed === 'object' && 'error' in parsed)
      ? String((parsed as { error: string }).error)
      : `http_${res.status}`;
    throw new ApiError(res.status, code, parsed);
  }
  return parsed as T;
}
