const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

export interface User {
  id: string;
  email: string;
  name: string | null;
  plan: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}

export interface ModuleItem {
  id: string;
  number: string;
  title: string;
  chapter: number;
  tier: string;
  duration: number;
  viz: string | null;
  description: string;
  unlocked: boolean;
  requiredPlan: string;
}

export interface ModulesResponse {
  modules: ModuleItem[];
  userPlan: string;
  stats: { total: number; unlocked: number; locked: number };
}

// ─── Token Storage ───
function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("pml_access_token");
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("pml_refresh_token");
}

function saveTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem("pml_access_token", accessToken);
  localStorage.setItem("pml_refresh_token", refreshToken);
  // Backward compat: old key used by some pages
  localStorage.setItem("pml_token", accessToken);
}

function clearTokens() {
  localStorage.removeItem("pml_access_token");
  localStorage.removeItem("pml_refresh_token");
  localStorage.removeItem("pml_token");
}

function authHeaders(): HeadersInit {
  const token = getAccessToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

// ─── Auto-refresh on 401 ───
let refreshPromise: Promise<AuthResponse> | null = null;

async function refreshTokens(): Promise<AuthResponse> {
  const rt = getRefreshToken();
  if (!rt) throw new Error("No refresh token");

  const res = await fetch(`${API_URL}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refreshToken: rt }),
  });

  if (!res.ok) {
    clearTokens();
    throw new Error("Sesion expirada");
  }

  const data: AuthResponse = await res.json();
  saveTokens(data.accessToken, data.refreshToken);
  return data;
}

async function fetchWithRefresh(url: string, options: RequestInit = {}): Promise<Response> {
  let res = await fetch(url, { ...options, headers: { ...authHeaders(), ...options.headers } });

  if (res.status === 401 && getRefreshToken()) {
    try {
      // Deduplicate concurrent refresh calls
      if (!refreshPromise) {
        refreshPromise = refreshTokens();
      }
      await refreshPromise;
      refreshPromise = null;

      // Retry with new token
      res = await fetch(url, { ...options, headers: { ...authHeaders(), ...options.headers } });
    } catch {
      refreshPromise = null;
      clearTokens();
      throw new Error("Sesion expirada");
    }
  }

  return res;
}

// ─── Auth API ───
export async function register(email: string, password: string, name: string): Promise<AuthResponse> {
  const res = await fetch(`${API_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Error al registrar");
  }
  const data: AuthResponse = await res.json();
  saveTokens(data.accessToken, data.refreshToken);
  return data;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Error al iniciar sesion");
  }
  const data: AuthResponse = await res.json();
  saveTokens(data.accessToken, data.refreshToken);
  return data;
}

export async function getMe(): Promise<User | null> {
  const token = getAccessToken();
  if (!token && !getRefreshToken()) return null;

  try {
    const res = await fetchWithRefresh(`${API_URL}/api/auth/me`);
    if (!res.ok) return null;
    const data = await res.json();
    return data.user;
  } catch {
    return null;
  }
}

export async function updatePlan(plan: string): Promise<AuthResponse> {
  const res = await fetchWithRefresh(`${API_URL}/api/auth/plan`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plan }),
  });
  if (!res.ok) throw new Error("Error al actualizar plan");
  const data = await res.json();
  // Plan update only returns accessToken (no refresh rotation)
  if (data.accessToken) {
    localStorage.setItem("pml_access_token", data.accessToken);
    localStorage.setItem("pml_token", data.accessToken);
  }
  return { accessToken: data.accessToken, refreshToken: getRefreshToken() || "", user: data.user };
}

export async function getModules(): Promise<ModulesResponse> {
  const res = await fetchWithRefresh(`${API_URL}/api/modules`);
  if (!res.ok) throw new Error("Error al obtener modulos");
  return res.json();
}

export async function logout() {
  const rt = getRefreshToken();
  if (rt) {
    // Revocar refresh token en servidor (fire and forget)
    fetch(`${API_URL}/api/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refreshToken: rt }),
    }).catch(() => {});
  }
  clearTokens();
}
