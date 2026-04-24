'use client'

import { useState, useEffect, Suspense } from 'react'
import { createClient } from '../../lib/supabase'
import { useRouter, useSearchParams } from 'next/navigation'

function LoginForm() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const router = useRouter()
  const searchParams = useSearchParams()
  const redirectTo = searchParams.get('redirect') || '/'
  const supabase = createClient()

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) router.replace(redirectTo)
    })
  }, [router, redirectTo, supabase.auth])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    if (mode === 'login') {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) {
        setError(error.message === 'Invalid login credentials'
          ? 'Email o contraseña incorrectos.'
          : error.message)
      } else {
        router.replace(redirectTo)
      }
    } else {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { name, tier: 1, tierName: 'Basico' } },
      })
      if (error) {
        setError(error.message)
      } else {
        setSuccess('¡Cuenta creada! Revisa tu email para confirmar tu registro.')
      }
    }
    setLoading(false)
  }

  return (
    <div className="auth-root">
      <div className="auth-bg">
        <div className="orb orb-1"/><div className="orb orb-2"/><div className="orb orb-3"/>
      </div>

      {/* Branding */}
      <div className="auth-left">
        <div className="brand-badge"><div className="brand-dot"/>ML Probabilístico para Finanzas</div>
        <h1>El conocimiento que los<br/><span>mercados no te enseñan</span></h1>
        <p>28 notebooks interactivos de Machine Learning Probabilístico aplicado a finanzas. Basado en Deepak K. Kanungo (O'Reilly, 2023).</p>
        <div className="tier-list">
          {[
            {cls:'t1',icon:'📖',name:'Básico',desc:'Prefacio + Capítulo 1',price:'Gratis–$30'},
            {cls:'t2',icon:'📊',name:'Estándar',desc:'Caps. 1–4 · 8h',price:'$30–$150'},
            {cls:'t3',icon:'🚀',name:'Premium',desc:'Caps. 1–7 · 20h + mentoring',price:'$150–$800'},
            {cls:'t4',icon:'⚡',name:'Enterprise',desc:'Todo · 40h+ · Repo privado',price:'$800+'},
          ].map(t=>(
            <div key={t.name} className="tier-item">
              <div className={`tier-icon ${t.cls}`}>{t.icon}</div>
              <div className="tier-info">
                <div className="tier-name">{t.name}</div>
                <div className="tier-desc">{t.desc}</div>
              </div>
              <div className="tier-price">{t.price}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Form */}
      <div className="auth-right">
        <div className="auth-card">
          <div className="card-logo">🧠</div>
          <div className="card-title">{mode==='login'?'Bienvenido de vuelta':'Crea tu cuenta'}</div>
          <div className="card-subtitle">{mode==='login'?'Ingresa a tu espacio de aprendizaje':'Empieza con acceso Básico gratuito'}</div>
          <div className="mode-toggle">
            <button className={`mode-btn ${mode==='login'?'active':''}`} onClick={()=>{setMode('login');setError(null);setSuccess(null)}}>Iniciar sesión</button>
            <button className={`mode-btn ${mode==='register'?'active':''}`} onClick={()=>{setMode('register');setError(null);setSuccess(null)}}>Registrarse</button>
          </div>
          <form onSubmit={handleSubmit}>
            {error&&<div className="alert alert-error"><span>⚠️</span>{error}</div>}
            {success&&<div className="alert alert-success"><span>✅</span>{success}</div>}
            {mode==='register'&&(
              <div className="field">
                <label htmlFor="auth-name">Nombre completo</label>
                <input id="auth-name" type="text" placeholder="Santiago Valencia" value={name} onChange={e=>setName(e.target.value)} required autoComplete="name"/>
              </div>
            )}
            <div className="field">
              <label htmlFor="auth-email">Email</label>
              <input id="auth-email" type="email" placeholder="tu@email.com" value={email} onChange={e=>setEmail(e.target.value)} required autoComplete="email"/>
            </div>
            <div className="field">
              <label htmlFor="auth-password">Contraseña</label>
              <input id="auth-password" type="password" placeholder={mode==='register'?'Mínimo 8 caracteres':'••••••••'} value={password} onChange={e=>setPassword(e.target.value)} required minLength={mode==='register'?8:1} autoComplete={mode==='login'?'current-password':'new-password'}/>
            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading?'⏳ Procesando...':mode==='login'?'→ Entrar':'→ Crear cuenta gratuita'}
            </button>
          </form>
          <div className="divider">acceso seguro con Supabase Auth</div>
        </div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
        .auth-root{min-height:100vh;display:flex;background:#080b14;font-family:'Inter',sans-serif;overflow:hidden;position:relative}
        .auth-bg{position:absolute;inset:0;overflow:hidden;pointer-events:none}
        .orb{position:absolute;border-radius:50%;filter:blur(120px);opacity:.18;animation:drift 12s ease-in-out infinite alternate}
        .orb-1{width:600px;height:600px;background:#6366f1;top:-200px;left:-150px}
        .orb-2{width:400px;height:400px;background:#06b6d4;bottom:-100px;right:-100px;animation-delay:-4s}
        .orb-3{width:300px;height:300px;background:#8b5cf6;top:40%;left:40%;animation-delay:-8s}
        @keyframes drift{from{transform:translate(0,0) scale(1)}to{transform:translate(30px,-20px) scale(1.08)}}
        .auth-left{flex:1;display:flex;flex-direction:column;justify-content:center;padding:60px;position:relative;z-index:1}
        .brand-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.3);border-radius:999px;padding:6px 14px;font-size:12px;color:#a5b4fc;font-weight:500;letter-spacing:.05em;text-transform:uppercase;width:fit-content;margin-bottom:32px}
        .brand-dot{width:6px;height:6px;border-radius:50%;background:#6366f1;animation:pulse 2s ease infinite}
        @keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.4)}}
        .auth-left h1{font-size:clamp(2rem,4vw,3rem);font-weight:700;line-height:1.15;color:#f1f5f9;margin-bottom:20px;letter-spacing:-.02em}
        .auth-left h1 span{background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
        .auth-left p{font-size:1rem;color:#94a3b8;line-height:1.7;max-width:400px;margin-bottom:48px}
        .tier-list{display:flex;flex-direction:column;gap:12px}
        .tier-item{display:flex;align-items:center;gap:14px;padding:14px 18px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:12px;transition:border-color .2s}
        .tier-item:hover{border-color:rgba(99,102,241,.3)}
        .tier-icon{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
        .tier-icon.t1{background:rgba(148,163,184,.1)}.tier-icon.t2{background:rgba(34,197,94,.1)}.tier-icon.t3{background:rgba(99,102,241,.15)}.tier-icon.t4{background:rgba(245,158,11,.1)}
        .tier-info{flex:1}.tier-name{font-size:13px;font-weight:600;color:#e2e8f0}.tier-desc{font-size:11px;color:#64748b;margin-top:2px}.tier-price{font-size:12px;font-weight:600;color:#6366f1;white-space:nowrap}
        .auth-right{width:460px;flex-shrink:0;display:flex;align-items:center;justify-content:center;padding:40px;position:relative;z-index:1}
        .auth-card{width:100%;background:rgba(15,20,35,.8);border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:40px;backdrop-filter:blur(20px);box-shadow:0 0 0 1px rgba(99,102,241,.05),0 32px 80px rgba(0,0,0,.5)}
        .card-logo{width:48px;height:48px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:24px;box-shadow:0 8px 24px rgba(99,102,241,.3)}
        .card-title{font-size:1.5rem;font-weight:700;color:#f1f5f9;margin-bottom:6px;letter-spacing:-.01em}
        .card-subtitle{font-size:13px;color:#64748b;margin-bottom:32px}
        .mode-toggle{display:flex;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:4px;margin-bottom:28px}
        .mode-btn{flex:1;padding:8px;border:none;border-radius:7px;font-size:13px;font-weight:500;cursor:pointer;transition:all .2s;background:transparent;color:#64748b;font-family:'Inter',sans-serif}
        .mode-btn.active{background:rgba(99,102,241,.2);color:#a5b4fc;box-shadow:0 2px 8px rgba(0,0,0,.2)}
        .field{margin-bottom:16px}
        .field label{display:block;font-size:12px;font-weight:500;color:#94a3b8;margin-bottom:6px;letter-spacing:.02em;text-transform:uppercase}
        .field input{width:100%;padding:12px 16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:10px;font-size:14px;color:#f1f5f9;outline:none;transition:border-color .2s,box-shadow .2s;font-family:'Inter',sans-serif}
        .field input::placeholder{color:#475569}
        .field input:focus{border-color:rgba(99,102,241,.5);box-shadow:0 0 0 3px rgba(99,102,241,.1)}
        .submit-btn{width:100%;padding:13px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border:none;border-radius:10px;font-size:14px;font-weight:600;color:white;cursor:pointer;margin-top:8px;transition:opacity .2s,transform .1s;font-family:'Inter',sans-serif}
        .submit-btn:hover:not(:disabled){opacity:.9;transform:translateY(-1px)}.submit-btn:disabled{opacity:.5;cursor:not-allowed}
        .alert{padding:12px 14px;border-radius:10px;font-size:13px;margin-bottom:16px;display:flex;align-items:flex-start;gap:8px}
        .alert-error{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);color:#fca5a5}
        .alert-success{background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.2);color:#86efac}
        .divider{display:flex;align-items:center;gap:12px;margin:24px 0 0;color:#334155;font-size:12px}
        .divider::before,.divider::after{content:'';flex:1;height:1px;background:rgba(255,255,255,.06)}
        @media(max-width:768px){.auth-left{display:none}.auth-right{width:100%}}
      `}</style>

      <Suspense fallback={<div className="auth-root" style={{justifyContent:'center', alignItems:'center', color:'#64748b'}}>Cargando...</div>}>
        <LoginForm />
      </Suspense>
    </>
  )
}
