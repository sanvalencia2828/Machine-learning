import { redirect } from 'next/navigation'

// La página raíz redirige al login.
// El contenido del curso vive en el sitio estático de MkDocs.
export default function RootPage() {
  redirect('/login')
}
