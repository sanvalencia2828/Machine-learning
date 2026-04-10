"use client";

interface Props {
  userName: string;
  onStart: () => void;
}

const BENEFITS = [
  {
    icon: "24",
    label: "Modulos Completos",
    detail: "Acceso a los 24 modulos interactivos (Capitulos 2-8)",
  },
  {
    icon: "18h",
    label: "Horas de Contenido",
    detail: "Video scripts + notebooks + ejercicios practicos",
  },
  {
    icon: "24",
    label: "Visualizaciones Plotly",
    detail: "Dashboards HTML interactivos por cada modulo",
  },
  {
    icon: "150+",
    label: "Ejercicios",
    detail: "Con datasets sinteticos y soluciones detalladas",
  },
  {
    icon: "PyMC",
    label: "Scripts Completos",
    detail: "Codigo fuente ejecutable en Python 3.9+",
  },
  {
    icon: "1:1",
    label: "Mentoria Grupal",
    detail: "Sesion mensual en vivo con el instructor",
  },
];

const LEARNING_PATH = [
  {
    phase: 1,
    name: "Fundamentos",
    weeks: "Semanas 1-2",
    color: "#3b82f6",
    modules: [
      { id: "mod02", label: "2 - Incertidumbre y Monty Hall" },
      { id: "mod02b", label: "2B - Probabilidades Relativas" },
      { id: "mod02d", label: "2D - Bias-Variance y NFL" },
      { id: "mod02e", label: "2E - Problema de la Induccion" },
    ],
    goal: "Entender por que los modelos convencionales fallan y como pensar probabilisticamente.",
  },
  {
    phase: 2,
    name: "Simulacion y Estadistica",
    weeks: "Semanas 3-4",
    color: "#06b6d4",
    modules: [
      { id: "mod03", label: "3 - Monte Carlo Simulation" },
      { id: "mod03b", label: "3B - Conceptos Estadisticos" },
      { id: "mod03c", label: "3C - Normal vs Realidad" },
      { id: "mod03d", label: "3D - LGN, TLC y MCS" },
    ],
    goal: "Dominar Monte Carlo, fat tails y por que la Normal subestima el riesgo real.",
  },
  {
    phase: 3,
    name: "Critica Estadistica",
    weeks: "Semanas 5-6",
    color: "#f59e0b",
    modules: [
      { id: "mod02c", label: "2C - Black-Scholes y Trinidad" },
      { id: "mod04", label: "4 - Peligros de NHST" },
      { id: "mod04b", label: "4B - NHST Aplicado (OLS)" },
      { id: "mod04c", label: "4C - IC, CAPM y Alpha" },
    ],
    goal: "Destruir mitos: p-values, intervalos de confianza, y la falsa precision de CAPM.",
  },
  {
    phase: 4,
    name: "Framework Probabilistico",
    weeks: "Semanas 7-8",
    color: "#10b981",
    modules: [
      { id: "mod05", label: "5 - Framework PML" },
      { id: "mod05b", label: "5B - Default High-Yield" },
      { id: "mod06", label: "6 - MLE vs PML" },
      { id: "mod06b", label: "6B - Caso ZYX" },
      { id: "mod06c", label: "6C - Grid y MCMC" },
    ],
    goal: "Construir intuicion Bayesiana: priors, posteriors, y cuando MLE falla.",
  },
  {
    phase: 5,
    name: "Ensambles Generativos",
    weeks: "Semanas 9-10",
    color: "#8b5cf6",
    modules: [
      { id: "mod07", label: "7 - PyMC Ensembles" },
      { id: "mod07b", label: "7B - PLE Aplicado" },
      { id: "mod07c", label: "7C - Retrodiccion y HMC" },
    ],
    goal: "Implementar modelos probabilisticos reales con PyMC y evaluar con ArviZ.",
  },
  {
    phase: 6,
    name: "Decisiones y Capital",
    weeks: "Semanas 11-12",
    color: "#ec4899",
    modules: [
      { id: "mod08", label: "8 - Kelly y Ergodicidad" },
      { id: "mod08b", label: "8B - Loss Functions y ES" },
      { id: "mod08c", label: "8C - GVaR, GES, GTR" },
      { id: "mod08d", label: "8D - MPT Critique" },
    ],
    goal: "Tomar decisiones de inversion con criterio de Kelly, riesgo generativo y critica a MPT.",
  },
];

export default function PremiumOnboarding({ userName, onStart }: Props) {
  return (
    <div className="min-h-screen" style={{ backgroundColor: "#0f172a" }}>
      {/* Hero */}
      <div
        className="relative overflow-hidden"
        style={{
          background: "linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 100%)",
        }}
      >
        <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 text-center relative z-10">
          <span
            className="inline-block rounded-full px-4 py-1 text-xs font-bold mb-4"
            style={{ backgroundColor: "#a855f722", color: "#c084fc", border: "1px solid #a855f744" }}
          >
            PLAN PREMIUM
          </span>
          <h1 className="text-3xl sm:text-4xl font-bold mb-3" style={{ color: "#f1f5f9" }}>
            Bienvenido, {userName}
          </h1>
          <p className="text-lg mb-2" style={{ color: "#c4b5fd" }}>
            ML Probabilistico para Finanzas e Inversion
          </p>
          <p className="text-sm max-w-2xl mx-auto" style={{ color: "#a5b4fc" }}>
            Tienes acceso completo a los 24 modulos, 24 visualizaciones interactivas,
            150+ ejercicios, scripts PyMC y mentoria grupal. Aqui esta tu ruta de aprendizaje.
          </p>
        </div>
        {/* Decorative gradient orbs */}
        <div
          className="absolute -top-20 -right-20 w-64 h-64 rounded-full opacity-20 blur-3xl"
          style={{ backgroundColor: "#a855f7" }}
        />
        <div
          className="absolute -bottom-10 -left-10 w-48 h-48 rounded-full opacity-15 blur-3xl"
          style={{ backgroundColor: "#3b82f6" }}
        />
      </div>

      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        {/* Benefits Grid */}
        <section className="-mt-8 relative z-20">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {BENEFITS.map((b) => (
              <div
                key={b.label}
                className="rounded-xl p-4 text-center"
                style={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
              >
                <div className="text-xl font-bold mb-1" style={{ color: "#a855f7" }}>
                  {b.icon}
                </div>
                <div className="text-xs font-semibold mb-1" style={{ color: "#f1f5f9" }}>
                  {b.label}
                </div>
                <div className="text-[10px] leading-tight" style={{ color: "#64748b" }}>
                  {b.detail}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Learning Path */}
        <section className="mt-12 mb-8">
          <h2 className="text-xl font-bold mb-1" style={{ color: "#f1f5f9" }}>
            Ruta de Aprendizaje (12 semanas)
          </h2>
          <p className="text-sm mb-8" style={{ color: "#64748b" }}>
            Sigue este orden para maximizar tu comprension. Cada fase construye sobre la anterior.
          </p>

          <div className="relative">
            {/* Vertical line */}
            <div
              className="absolute left-6 top-0 bottom-0 w-0.5 hidden sm:block"
              style={{ backgroundColor: "#334155" }}
            />

            <div className="flex flex-col gap-6">
              {LEARNING_PATH.map((phase) => (
                <div key={phase.phase} className="flex gap-4 sm:gap-6">
                  {/* Phase circle */}
                  <div className="flex-shrink-0 relative z-10">
                    <div
                      className="w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold"
                      style={{
                        backgroundColor: phase.color + "22",
                        color: phase.color,
                        border: `2px solid ${phase.color}66`,
                      }}
                    >
                      {phase.phase}
                    </div>
                  </div>

                  {/* Phase content */}
                  <div
                    className="flex-1 rounded-xl p-5"
                    style={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
                  >
                    <div className="flex flex-wrap items-center gap-3 mb-3">
                      <h3 className="text-base font-bold" style={{ color: "#f1f5f9" }}>
                        {phase.name}
                      </h3>
                      <span
                        className="rounded-full px-2.5 py-0.5 text-xs font-medium"
                        style={{ backgroundColor: phase.color + "18", color: phase.color }}
                      >
                        {phase.weeks}
                      </span>
                    </div>

                    <p className="text-sm mb-3" style={{ color: "#94a3b8" }}>
                      {phase.goal}
                    </p>

                    <div className="flex flex-wrap gap-2">
                      {phase.modules.map((m) => (
                        <span
                          key={m.id}
                          className="rounded-lg px-2.5 py-1 text-xs"
                          style={{ backgroundColor: "#0f172a", color: "#94a3b8", border: "1px solid #334155" }}
                        >
                          {m.label}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Quick Start Tips */}
        <section
          className="rounded-xl p-6 mb-8"
          style={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
        >
          <h3 className="text-base font-bold mb-4" style={{ color: "#f1f5f9" }}>
            Como empezar
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              {
                step: "1",
                title: "Configura tu entorno",
                detail: "Python 3.9+, VS Code con Jupyter, o usa Google Colab directamente.",
              },
              {
                step: "2",
                title: "Empieza por Fase 1",
                detail: "Los modulos de Incertidumbre (Cap 2) son la base de todo lo demas.",
              },
              {
                step: "3",
                title: "Ejecuta las visualizaciones",
                detail: "Cada modulo tiene un dashboard Plotly interactivo. Click en 'Ver demo'.",
              },
              {
                step: "4",
                title: "Haz los ejercicios",
                detail: "150+ ejercicios con datasets sinteticos. La practica es lo que consolida.",
              },
            ].map((s) => (
              <div key={s.step} className="flex gap-3">
                <div
                  className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{ backgroundColor: "#3b82f622", color: "#3b82f6" }}
                >
                  {s.step}
                </div>
                <div>
                  <p className="text-sm font-semibold" style={{ color: "#f1f5f9" }}>
                    {s.title}
                  </p>
                  <p className="text-xs mt-0.5" style={{ color: "#64748b" }}>
                    {s.detail}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <div className="text-center pb-16">
          <button
            onClick={onStart}
            className="rounded-xl px-8 py-4 text-base font-bold cursor-pointer transition-all hover:scale-105"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #a855f7)",
              color: "#fff",
              boxShadow: "0 4px 24px rgba(168,85,247,0.3)",
            }}
          >
            Comenzar el Curso
          </button>
          <p className="text-xs mt-3" style={{ color: "#64748b" }}>
            Ir al dashboard con todos los modulos desbloqueados
          </p>
        </div>
      </div>
    </div>
  );
}
