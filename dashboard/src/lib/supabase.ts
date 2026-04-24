import { createBrowserClient, createServerClient } from '@supabase/ssr'

// ─── Tipos ─────────────────────────────────────────────────────────────────
export type UserTier = 1 | 2 | 3 | 4

export interface UserProfile {
  id: string
  email: string
  tier: UserTier
  tierName: 'Basico' | 'Estandar' | 'Premium' | 'Enterprise'
  isAdmin: boolean
}

// ─── Mapa de acceso por capítulo ────────────────────────────────────────────
// Derivado directamente de pricing_features.csv
export const CHAPTER_ACCESS_MAP: Record<string, UserTier> = {
  // Tier 1 — Básico (preface + ch01)
  'index': 1,
  'notebook_ch01_forward_inverse': 1,
  'notebook_ch01_trifecta_errors': 1,

  // Tier 2 — Estándar (ch01–ch04)
  'notebook_ch02_monty_hall_uncertainty': 2,
  'notebook_ch02_ltcm_analysis': 2,
  'notebook_ch02_relative_probability': 2,
  'notebook_ch02c_bsm_uncertainty_trinity': 2,
  'notebook_ch02d_bias_variance_nfl': 2,
  'notebook_ch02e_induction_problem': 2,
  'notebook_ch03_bayesian_inference': 2,
  'notebook_ch03_monte_carlo_finance': 2,
  'notebook_ch03b_stat_concepts': 2,
  'notebook_ch03c_normal_vs_reality': 2,
  'notebook_ch03d_lln_clt_mcs': 2,
  'notebook_ch04_monte_carlo': 2,
  'notebook_ch04_nhst_dangers': 2,
  'notebook_ch04b_nhst_applied': 2,
  'notebook_ch04c_ci_capm_alpha': 2,

  // Tier 3 — Premium (ch01–ch07)
  'notebook_ch05_pml_framework': 3,
  'notebook_ch05_volatility_models': 3,
  'notebook_ch05b_hy_default': 3,
  'notebook_ch06_mle_vs_probabilistic': 3,
  'notebook_ch06_tail_risks': 3,
  'notebook_ch06b_zyx_mle_failure': 3,
  'notebook_ch06c_grid_mcmc': 3,
  'notebook_ch07_ml_finance': 3,
  'notebook_ch07_pymc_ensembles': 3,

  // Tier 4 — Enterprise (todos)
  'notebook_ch08_kelly_capital_allocation': 4,
  'notebook_ch08_stress_testing': 4,
}

export const TIER_NAMES: Record<UserTier, string> = {
  1: 'Básico',
  2: 'Estándar',
  3: 'Premium',
  4: 'Enterprise',
}

export const TIER_PRICES: Record<UserTier, string> = {
  1: 'Gratis – $30',
  2: '$30 – $150',
  3: '$150 – $800',
  4: '$800+',
}

// ─── Cliente Browser (componentes cliente) ──────────────────────────────────
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )
}

// ─── Cliente Server (Server Components / Route Handlers) ────────────────────
export function createServerSupabaseClient(
  cookieStore: {
    get: (name: string) => { value: string } | undefined
    set: (name: string, value: string, options: object) => void
    delete: (name: string, options: object) => void
  }
) {
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
        set(name: string, value: string, options: object) {
          cookieStore.set(name, value, options)
        },
        remove(name: string, options: object) {
          cookieStore.delete(name, options)
        },
      },
    }
  )
}

// ─── Helpers ────────────────────────────────────────────────────────────────

/**
 * Extrae el slug del capítulo desde una URL de MkDocs.
 * Ejemplo: "/notebook_ch02_monty_hall_uncertainty/" → "notebook_ch02_monty_hall_uncertainty"
 */
export function extractChapterSlug(pathname: string): string | null {
  const clean = pathname.replace(/^\/|\/$/g, '') // quita slashes
  const parts = clean.split('/')
  const slug = parts[parts.length - 1] || parts[0]
  return slug || null
}

/**
 * Devuelve el tier mínimo requerido para un pathname dado.
 * Si no está en el mapa, asume tier 1 (público con login).
 */
export function getRequiredTier(pathname: string): UserTier {
  const slug = extractChapterSlug(pathname)
  if (!slug) return 1
  return CHAPTER_ACCESS_MAP[slug] ?? 1
}
