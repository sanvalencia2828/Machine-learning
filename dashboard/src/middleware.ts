import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'
import { getRequiredTier, type UserTier } from './lib/supabase'

// ─── Rutas que SIEMPRE son públicas (sin login) ─────────────────────────────
const PUBLIC_PATHS = [
  '/login',
  '/register',
  '/upgrade',
  '/auth/callback',
  '/api/auth',
  '/_next',
  '/favicon',
  '/static',
]

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some(p => pathname.startsWith(p))
}

// ─── Rutas protegidas (requieren auth + tier check) ─────────────────────────
// Cualquier path que empiece con /notebook_ o sea el sitio estático de MkDocs
function isProtectedPath(pathname: string): boolean {
  return (
    pathname.startsWith('/notebooks/') ||
    pathname.startsWith('/notebook_') ||
    pathname.startsWith('/site/') ||
    pathname === '/search/search_index.json'
  )
}

// ─── Edge Middleware ─────────────────────────────────────────────────────────
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Dejar pasar rutas públicas sin verificación
  if (isPublicPath(pathname)) {
    return NextResponse.next()
  }

  // Crear response mutable para refresco de cookies
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet: { name: string; value: string; options: Record<string, unknown> }[]) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  // Obtener sesión del usuario
  const { data: { user } } = await supabase.auth.getUser()

  // ── Sin sesión → redirect a /login ──────────────────────────────────────
  if (!user) {
    const loginUrl = request.nextUrl.clone()
    loginUrl.pathname = '/login'
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // ── Con sesión pero en ruta protegida → verificar tier ──────────────────
  if (isProtectedPath(pathname)) {
    const userTier = (user.user_metadata?.tier as UserTier) ?? 1
    const requiredTier = getRequiredTier(pathname)

    if (userTier < requiredTier) {
      const upgradeUrl = request.nextUrl.clone()
      upgradeUrl.pathname = '/upgrade'
      upgradeUrl.searchParams.set('required', String(requiredTier))
      upgradeUrl.searchParams.set('chapter', pathname)
      return NextResponse.redirect(upgradeUrl)
    }
  }

  return supabaseResponse
}

// ─── Matcher: qué rutas intercepta el middleware ─────────────────────────────
export const config = {
  matcher: [
    /*
     * Intercepta TODAS las rutas excepto:
     * - Archivos estáticos de Next.js (_next/static, _next/image)
     * - Imágenes y assets de MkDocs con extensión
     */
    '/((?!_next/static|_next/image|.*\\.(?:ico|png|jpg|jpeg|gif|svg|woff2?|css|js|map)).*)',
  ],
}
