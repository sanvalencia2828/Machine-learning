'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { TIER_NAMES, TIER_PRICES, type UserTier } from '../../lib/supabase'

const TIER_FEATURES: Record<UserTier, string[]> = {
  1: ['Prefacio + Capítulo 1', 'Acceso básico al contenido'],
  2: ['Capítulos 1 al 4', '8 horas de contenido', '2 notebooks descargables', 'Soporte por email'],
  3: ['Capítulos 1 al 7', '20 horas de contenido', '7 notebooks descargables', '5h de mentoría', 'Soporte prioritario'],
  4: ['Todos los capítulos (1–8)', '40+ horas de contenido', 'Todos los notebooks', 'Repo privado', 'Documentación regulatoria', 'Mentoría dedicada'],
}

const TIER_COLORS: Record<UserTier, string> = {
  1: '#94a3b8', 2: '#22c55e', 3: '#6366f1', 4: '#f59e0b',
}

function UpgradeContent() {
  const searchParams = useSearchParams()
  const requiredTier = (Number(searchParams.get('required')) || 2) as UserTier
  const chapter = searchParams.get('chapter') || ''

  const tiers: UserTier[] = [1, 2, 3, 4]

  return (
    <div className="upgrade-root">
      <div className="bg-orb bg-orb-1"/><div className="bg-orb bg-orb-2"/>

      <div className="lock-icon">🔒</div>
      <div className="upgrade-badge">Acceso restringido</div>
      <h1 className="upgrade-title">Este contenido requiere<br/><span>un plan superior</span></h1>
      <p className="upgrade-subtitle">
        El capítulo que intentas acceder requiere el plan <strong>{TIER_NAMES[requiredTier]}</strong>.
        Elige el plan que mejor se adapte a tu nivel de aprendizaje.
      </p>

      <div className="tiers-grid">
        {tiers.map(t => (
          <div
            key={t}
            className={`tier-card ${t===requiredTier?'highlighted recommended':''}`}
          >
            <div className="tier-dot" style={{background: TIER_COLORS[t]}}/>
            <div className="tier-card-name" style={{color: TIER_COLORS[t]}}>{TIER_NAMES[t]}</div>
            <div className="tier-card-price">{TIER_PRICES[t]}</div>
            <ul className="tier-features">
              {TIER_FEATURES[t].map(f=><li key={f}>{f}</li>)}
            </ul>
            {t===1
              ? <Link href="/login" className="tier-btn secondary">Tu plan actual</Link>
              : <a href={`mailto:contacto@tudominio.com?subject=Upgrade a ${TIER_NAMES[t]}`} className="tier-btn primary">Solicitar acceso →</a>
            }
          </div>
        ))}
      </div>

      <Link href="/" className="back-link">← Volver al inicio</Link>
    </div>
  )
}

export default function UpgradePage() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
        body{background:#080b14;font-family:'Inter',sans-serif;color:#f1f5f9}
        .upgrade-root{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 20px;position:relative;overflow:hidden}
        .bg-orb{position:absolute;border-radius:50%;filter:blur(140px);opacity:.12;pointer-events:none}
        .bg-orb-1{width:700px;height:700px;background:#6366f1;top:-300px;left:-200px}
        .bg-orb-2{width:500px;height:500px;background:#06b6d4;bottom:-200px;right:-100px}
        .lock-icon{font-size:48px;margin-bottom:16px}
        .upgrade-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.25);border-radius:999px;padding:6px 16px;font-size:12px;color:#fca5a5;font-weight:500;letter-spacing:.05em;text-transform:uppercase;margin-bottom:20px}
        .upgrade-title{font-size:clamp(1.8rem,4vw,2.8rem);font-weight:700;text-align:center;letter-spacing:-.02em;margin-bottom:12px}
        .upgrade-title span{background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
        .upgrade-subtitle{font-size:15px;color:#64748b;text-align:center;max-width:520px;line-height:1.6;margin-bottom:56px}
        .tiers-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;width:100%;max-width:900px;margin-bottom:40px}
        .tier-card{background:rgba(15,20,35,.6);border:1px solid rgba(255,255,255,.06);border-radius:20px;padding:28px 24px;transition:transform .2s,border-color .2s;cursor:default;position:relative;overflow:hidden}
        .tier-card.highlighted{border-color:rgba(99,102,241,.5);box-shadow:0 0 0 1px rgba(99,102,241,.2),0 20px 60px rgba(0,0,0,.4);transform:translateY(-4px)}
        .tier-card.recommended::before{content:'Recomendado';position:absolute;top:14px;right:14px;background:rgba(99,102,241,.2);border:1px solid rgba(99,102,241,.3);color:#a5b4fc;font-size:10px;font-weight:600;padding:3px 8px;border-radius:999px;letter-spacing:.05em;text-transform:uppercase}
        .tier-card:hover{transform:translateY(-2px);border-color:rgba(255,255,255,.12)}
        .tier-card.highlighted:hover{transform:translateY(-6px)}
        .tier-dot{width:10px;height:10px;border-radius:50%;margin-bottom:16px}
        .tier-card-name{font-size:1.1rem;font-weight:700;margin-bottom:4px}
        .tier-card-price{font-size:13px;color:#64748b;margin-bottom:20px}
        .tier-features{list-style:none;display:flex;flex-direction:column;gap:8px;margin-bottom:24px}
        .tier-features li{font-size:13px;color:#94a3b8;display:flex;align-items:center;gap:8px}
        .tier-features li::before{content:'✓';color:#6366f1;font-weight:700;font-size:11px;flex-shrink:0}
        .tier-btn{display:block;width:100%;padding:11px;border-radius:10px;font-size:13px;font-weight:600;text-align:center;text-decoration:none;transition:opacity .2s;border:none;cursor:pointer;font-family:'Inter',sans-serif}
        .tier-btn.primary{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white}
        .tier-btn.secondary{background:rgba(255,255,255,.06);color:#94a3b8;border:1px solid rgba(255,255,255,.08)}
        .tier-btn:hover{opacity:.85}
        .back-link{font-size:13px;color:#475569;text-decoration:none;display:flex;align-items:center;gap:6px;transition:color .2s}
        .back-link:hover{color:#94a3b8}
      `}</style>

      <Suspense fallback={<div className="upgrade-root" style={{color:'#64748b'}}>Cargando...</div>}>
        <UpgradeContent />
      </Suspense>
    </>
  )
}
