/** @type {import('next').NextConfig} */
const nextConfig = {
  // Permite que el build de Next.js co-exista con el sitio estático de MkDocs
  trailingSlash: true,

  // Headers de seguridad
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ]
  },

  // Redirigir /notebooks/ a la carpeta estática /site/
  async rewrites() {
    return [
      {
        source: '/notebooks/:path*',
        destination: '/site/:path*',
      },
    ]
  },
}

module.exports = nextConfig
