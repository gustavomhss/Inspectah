import { endpoints } from '../api/endpoints';
import { httpClient } from '../api/http-client';
import { env } from '../config/env';
import type { AuthSession, AuthUser, LoginCredentials, LoginResponse } from './auth-types';

const STORAGE_KEY = env.authStorageKey;

export function loadSession(): AuthSession | null {
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY) || window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

export function saveSession(session: AuthSession) {
  window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearSession() {
  window.sessionStorage.removeItem(STORAGE_KEY);
  window.localStorage.removeItem(STORAGE_KEY);
}

export async function login(credentials: LoginCredentials): Promise<AuthSession> {
  const username = credentials.username.trim();
  const password = credentials.password.trim();
  if (!username || !password) {
    throw new Error('Credenciais obrigatórias');
  }

  const response = await httpClient<LoginResponse>(endpoints.auth.login, {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });

  const token = response.token || response.access_token;
  if (!token) {
    throw new Error('Resposta de auth inválida: token ausente');
  }

  const user: AuthUser = {
    id: response.user?.id || response.user_id || username,
    name: response.user?.name || username,
    email: response.user?.email || response.email,
    roles: response.user?.roles || response.roles,
  };

  return {
    token,
    user,
  };
}

export async function logout(): Promise<void> {
  clearSession();
}
