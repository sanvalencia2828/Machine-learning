"use client";

import { useState, useEffect, useCallback } from "react";
import { chapters, tierConfig } from "./data/modules";
import type { Module } from "./data/modules";
import * as api from "./lib/api";
import PremiumOnboarding from "./components/PremiumOnboarding";

type View = "login" | "register" | "dashboard" | "plans" | "onboarding";

const TIER_LABELS: Record<string, string> = {
  FREE: "Gratuito",
  BASICO: "Basico",
  AVANZADO: "Avanzado",
  PREMIUM: "Premium",
};

const TIER_COLORS: Record<string, string> = {
  FREE: "#64748b",
  BASICO: "#22c55e",
  AVANZADO: "#f59e0b",
  PREMIUM: "#a855f7",
};

/* ─── Auth Forms ─── */
function AuthForm({
  mode,
  onSuccess,
  onSwitch,
}: {
  mode: "login" | "register";
  onSuccess: (user: api.User) => void;
  onSwitch: () => void;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res =
        mode === "login"
          ? await api.login(email, password)
          : await api.register(email, password, name);
      onSuccess(res.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ backgroundColor: "#0f172a" }}>
      <div className="w-full max-w-md rounded-2xl p-8" style={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}>
        <h1 className="text-2xl font-bold mb-1" style={{ color: "#f1f5f9" }}>
          PML Finance
        </h1>
        <p className="text-sm mb-6" style={{ color: "#64748b" }}>
          {mode === "login" ? "Inicia sesion para acceder al curso" : "Crea tu cuenta"}
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {mode === "register" && (
            <input
              type="text"
              placeholder="Nombre"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="rounded-lg px-4 py-3 text-sm outline-none"
              style={{ backgroundColor: "#0f172a", color: "#e2e8f0", border: "1px solid #334155" }}
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="rounded-lg px-4 py-3 text-sm outline-none"
            style={{ backgroundColor: "#0f172a", color: "#e2e8f0", border: "1px solid #334155" }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="rounded-lg px-4 py-3 text-sm outline-none"
            style={{ backgroundColor: "#0f172a", color: "#e2e8f0", border: "1px solid #334155" }}
          />
          {error && <p className="text-sm" style={{ color: "#ef4444" }}>{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg py-3 text-sm font-semibold transition-colors cursor-pointer"
            style={{ backgroundColor: "#3b82f6", color: "#fff" }}
          >
            {loading ? "..." : mode === "login" ? "Iniciar Sesion" : "Crear Cuenta"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm" style={{ color: "#64748b" }}>
          {mode === "login" ? "No tienes cuenta?" : "Ya tienes cuenta?"}{" "}
          <button onClick={onSwitch} className="font-medium cursor-pointer" style={{ color: "#3b82f6" }}>
            {mode === "login" ? "Registrate" : "Inicia Sesion"}
          </button>
        </p>
      </div>
    </div>
  );
}

/* ─── Plan Selector ─── */
function PlanSelector({
  currentPlan,
  onSelect,
  onBack,
}: {
  currentPlan: string;
  onSelect: (plan: string) => void;
  onBack: () => void;
}) {
  const plans = [
    {
      id: "BASICO",
      name: "Basico",
      price: "$29 USD",
      features: ["Capitulos 2-3 (9 modulos)", "9 visualizaciones interactivas", "~6h de contenido", "Certificado basico"],
      color: "#22c55e",
    },
    {
      id: "AVANZADO",
      name: "Avanzado",
      price: "$79 USD",
      features: [
        "Todo del Basico",
        "Capitulos 4-6 (8 modulos mas)",
        "17 visualizaciones total",
        "~12h de contenido",
        "Comunidad Discord",
      ],
      color: "#f59e0b",
      popular: true,
    },
    {
      id: "PREMIUM",
      name: "Premium",
      price: "$149 USD",
      features: [
        "Todo del Avanzado",
        "Capitulos 7-8 (7 modulos mas)",
        "24 visualizaciones total",
        "~18h de contenido",
        "Scripts PyMC completos",
        "Mentoria grupal mensual",
      ],
      color: "#a855f7",
    },
  ];

  return (
    <div className="min-h-screen p-4 sm:p-8" style={{ backgroundColor: "#0f172a" }}>
      <div className="mx-auto max-w-5xl">
        <button
          onClick={onBack}
          className="mb-6 text-sm font-medium cursor-pointer"
          style={{ color: "#3b82f6" }}
        >
          &larr; Volver al dashboard
        </button>

        <h2 className="text-2xl font-bold mb-2" style={{ color: "#f1f5f9" }}>
          Selecciona tu Plan
        </h2>
        <p className="text-sm mb-8" style={{ color: "#64748b" }}>
          Plan actual:{" "}
          <span className="font-semibold" style={{ color: TIER_COLORS[currentPlan] }}>
            {TIER_LABELS[currentPlan]}
          </span>
        </p>

        <div className="grid gap-6 sm:grid-cols-3">
          {plans.map((plan) => {
            const isCurrent = currentPlan === plan.id;
            return (
              <div
                key={plan.id}
                className="relative flex flex-col rounded-2xl p-6"
                style={{
                  backgroundColor: "#1e293b",
                  border: `2px solid ${isCurrent ? plan.color : "#334155"}`,
                }}
              >
                {plan.popular && (
                  <span
                    className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full px-3 py-0.5 text-xs font-bold"
                    style={{ backgroundColor: plan.color, color: "#000" }}
                  >
                    Popular
                  </span>
                )}
                <h3 className="text-lg font-bold" style={{ color: plan.color }}>
                  {plan.name}
                </h3>
                <p className="text-3xl font-bold mt-2 mb-4" style={{ color: "#f1f5f9" }}>
                  {plan.price}
                </p>
                <ul className="flex-1 flex flex-col gap-2 mb-6">
                  {plan.features.map((f) => (
                    <li key={f} className="text-sm" style={{ color: "#94a3b8" }}>
                      &#10003; {f}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => onSelect(plan.id)}
                  disabled={isCurrent}
                  className="rounded-lg py-3 text-sm font-semibold transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-default"
                  style={{
                    backgroundColor: isCurrent ? "#334155" : plan.color + "22",
                    color: isCurrent ? "#64748b" : plan.color,
                    border: `1px solid ${plan.color}44`,
                  }}
                >
                  {isCurrent ? "Plan Actual" : "Seleccionar"}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/* ─── Module Card ─── */
function TierBadge({ tier }: { tier: string }) {
  const tierKey = tier.toLowerCase() as keyof typeof tierConfig;
  const cfg = tierConfig[tierKey];
  if (!cfg) return null;
  return (
    <span
      className="inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold"
      style={{ backgroundColor: cfg.color + "22", color: cfg.color, border: `1px solid ${cfg.color}44` }}
    >
      {cfg.label}
    </span>
  );
}

function ModuleCard({
  mod,
  unlocked,
  onClick,
  onUpgrade,
}: {
  mod: api.ModuleItem;
  unlocked: boolean;
  onClick: () => void;
  onUpgrade: () => void;
}) {
  const ch = chapters.find((c) => c.number === mod.chapter);
  return (
    <div
      className="relative flex flex-col gap-3 rounded-xl p-5 transition-all duration-200"
      style={{
        backgroundColor: "#1e293b",
        border: `1px solid ${unlocked ? "#334155" : "#1e293b"}`,
        opacity: unlocked ? 1 : 0.65,
      }}
    >
      {!unlocked && (
        <div className="absolute inset-0 flex items-center justify-center rounded-xl z-10" style={{ backgroundColor: "rgba(15,23,42,0.6)" }}>
          <button
            onClick={onUpgrade}
            className="rounded-lg px-4 py-2 text-sm font-semibold cursor-pointer"
            style={{ backgroundColor: "#3b82f622", color: "#3b82f6", border: "1px solid #3b82f644" }}
          >
            Requiere {mod.requiredPlan}
          </button>
        </div>
      )}
      <div className="flex items-center justify-between">
        <span
          className="rounded-lg px-2 py-1 text-xs font-bold"
          style={{ backgroundColor: (ch?.color || "#3b82f6") + "22", color: ch?.color }}
        >
          Cap {mod.chapter} &middot; Mod {mod.number}
        </span>
        <TierBadge tier={mod.tier.toLowerCase()} />
      </div>
      <h3 className="text-base font-semibold leading-tight" style={{ color: "#f1f5f9" }}>
        {mod.title}
      </h3>
      <p className="text-sm leading-relaxed" style={{ color: "#94a3b8" }}>
        {mod.description}
      </p>
      <div className="mt-auto flex items-center justify-between pt-2">
        <span className="text-xs" style={{ color: "#64748b" }}>
          {mod.duration} min
        </span>
        {unlocked && mod.viz && (
          <button
            onClick={onClick}
            className="text-xs font-medium cursor-pointer"
            style={{ color: "#3b82f6" }}
          >
            Ver demo &rarr;
          </button>
        )}
      </div>
    </div>
  );
}

/* ─── Main App ─── */
export default function Home() {
  const [view, setView] = useState<View>("login");
  const [user, setUser] = useState<api.User | null>(null);
  const [modules, setModules] = useState<api.ModuleItem[]>([]);
  const [stats, setStats] = useState<{ total: number; unlocked: number; locked: number } | null>(null);
  const [selectedViz, setSelectedViz] = useState<string | null>(null);
  const [filterChapter, setFilterChapter] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  const loadModules = useCallback(async () => {
    try {
      const data = await api.getModules();
      setModules(data.modules);
      setStats(data.stats);
    } catch {
      // token invalid
      api.logout();
      setUser(null);
      setView("login");
    }
  }, []);

  // Check existing session on mount
  useEffect(() => {
    (async () => {
      const existing = await api.getMe();
      if (existing) {
        setUser(existing);
        setView("dashboard");
        await loadModules();
      }
      setLoading(false);
    })();
  }, [loadModules]);

  const handleAuthSuccess = async (u: api.User) => {
    setUser(u);
    await loadModules();
    // Show onboarding for paid plans on login
    const seenKey = `pml_onboarding_${u.id}`;
    if (u.plan !== "FREE" && !localStorage.getItem(seenKey)) {
      localStorage.setItem(seenKey, "1");
      setView("onboarding");
    } else {
      setView("dashboard");
    }
  };

  const handlePlanSelect = async (plan: string) => {
    try {
      const res = await api.updatePlan(plan);
      setUser(res.user);
      await loadModules();
      setView("onboarding");
    } catch {
      // handle error
    }
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    setModules([]);
    setView("login");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "#0f172a" }}>
        <p style={{ color: "#64748b" }}>Cargando...</p>
      </div>
    );
  }

  // Auth views
  if (view === "login") {
    return <AuthForm mode="login" onSuccess={handleAuthSuccess} onSwitch={() => setView("register")} />;
  }
  if (view === "register") {
    return <AuthForm mode="register" onSuccess={handleAuthSuccess} onSwitch={() => setView("login")} />;
  }
  if (view === "plans") {
    return <PlanSelector currentPlan={user?.plan || "FREE"} onSelect={handlePlanSelect} onBack={() => setView("dashboard")} />;
  }
  if (view === "onboarding" && user) {
    return (
      <PremiumOnboarding
        userName={user.name || user.email.split("@")[0]}
        onStart={() => setView("dashboard")}
      />
    );
  }

  // Dashboard
  const filtered = modules.filter((m) => filterChapter === 0 || m.chapter === filterChapter);

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#0f172a" }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: "#1e293b" }}>
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold" style={{ color: "#f1f5f9" }}>
              PML Finance
            </h1>
            <p className="text-xs" style={{ color: "#64748b" }}>
              ML Probabilistico para Finanzas e Inversion
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setView("plans")}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium cursor-pointer transition-colors"
              style={{
                backgroundColor: TIER_COLORS[user?.plan || "FREE"] + "18",
                color: TIER_COLORS[user?.plan || "FREE"],
                border: `1px solid ${TIER_COLORS[user?.plan || "FREE"]}33`,
              }}
            >
              {TIER_LABELS[user?.plan || "FREE"]}
              <span className="text-xs opacity-60">&#9650;</span>
            </button>
            {user?.plan !== "FREE" && (
              <button
                onClick={() => setView("onboarding")}
                className="rounded-lg px-3 py-2 text-xs font-medium cursor-pointer"
                style={{ backgroundColor: "#1e293b", color: "#94a3b8", border: "1px solid #334155" }}
              >
                Mi Ruta
              </button>
            )}
            <span className="text-sm" style={{ color: "#94a3b8" }}>{user?.name || user?.email}</span>
            <button
              onClick={handleLogout}
              className="text-xs cursor-pointer"
              style={{ color: "#64748b" }}
            >
              Salir
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: "Total Modulos", value: stats.total },
              { label: "Desbloqueados", value: stats.unlocked, color: "#22c55e" },
              { label: "Bloqueados", value: stats.locked, color: stats.locked > 0 ? "#f59e0b" : "#22c55e" },
              { label: "Tu Plan", value: TIER_LABELS[user?.plan || "FREE"], color: TIER_COLORS[user?.plan || "FREE"] },
            ].map((s) => (
              <div
                key={s.label}
                className="rounded-xl p-4 text-center"
                style={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
              >
                <div className="text-2xl font-bold" style={{ color: s.color || "#3b82f6" }}>
                  {s.value}
                </div>
                <div className="text-xs mt-1" style={{ color: "#94a3b8" }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Upgrade banner */}
        {user?.plan === "FREE" && (
          <div
            className="mt-6 rounded-xl p-5 flex items-center justify-between"
            style={{ backgroundColor: "#3b82f611", border: "1px solid #3b82f633" }}
          >
            <div>
              <p className="font-semibold text-sm" style={{ color: "#f1f5f9" }}>
                Desbloquea contenido del curso
              </p>
              <p className="text-xs mt-1" style={{ color: "#64748b" }}>
                Elige un plan para acceder a visualizaciones interactivas, ejercicios y mas.
              </p>
            </div>
            <button
              onClick={() => setView("plans")}
              className="rounded-lg px-5 py-2.5 text-sm font-semibold cursor-pointer"
              style={{ backgroundColor: "#3b82f6", color: "#fff" }}
            >
              Ver Planes
            </button>
          </div>
        )}

        {/* Filters */}
        <div className="mt-6 flex flex-wrap gap-3">
          <select
            value={filterChapter}
            onChange={(e) => setFilterChapter(Number(e.target.value))}
            className="rounded-lg px-3 py-2 text-sm"
            style={{ backgroundColor: "#1e293b", color: "#e2e8f0", border: "1px solid #334155" }}
          >
            <option value={0}>Todos los capitulos</option>
            {chapters.map((c) => (
              <option key={c.number} value={c.number}>
                Cap {c.number}: {c.title}
              </option>
            ))}
          </select>
          <span className="flex items-center text-sm" style={{ color: "#64748b" }}>
            {filtered.length} modulos
          </span>
        </div>

        {/* Modules by chapter */}
        {chapters
          .filter((c) => filterChapter === 0 || c.number === filterChapter)
          .map((ch) => {
            const chMods = filtered.filter((m) => m.chapter === ch.number);
            if (chMods.length === 0) return null;
            return (
              <section key={ch.number} className="mt-8">
                <h2 className="mb-4 flex items-center gap-3 text-lg font-semibold">
                  <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: ch.color }} />
                  <span style={{ color: "#f1f5f9" }}>
                    Capitulo {ch.number}: {ch.title}
                  </span>
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {chMods.map((mod) => (
                    <ModuleCard
                      key={mod.id}
                      mod={mod}
                      unlocked={mod.unlocked}
                      onClick={() => mod.viz && setSelectedViz(mod.viz)}
                      onUpgrade={() => setView("plans")}
                    />
                  ))}
                </div>
              </section>
            );
          })}
      </main>

      {/* Viz Modal */}
      {selectedViz && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ backgroundColor: "rgba(0,0,0,0.8)" }}
        >
          <div
            className="relative flex flex-col rounded-2xl w-full max-w-6xl"
            style={{ backgroundColor: "#1e293b", border: "1px solid #334155", height: "90vh" }}
          >
            <div className="flex items-center justify-between border-b px-5 py-3" style={{ borderColor: "#334155" }}>
              <h3 className="text-sm font-semibold" style={{ color: "#f1f5f9" }}>
                {modules.find((m) => m.viz === selectedViz)?.title}
              </h3>
              <div className="flex gap-2">
                <a
                  href={`/viz/${selectedViz}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-lg px-3 py-1.5 text-xs font-medium"
                  style={{ backgroundColor: "#334155", color: "#e2e8f0" }}
                >
                  Nueva ventana
                </a>
                <button
                  onClick={() => setSelectedViz(null)}
                  className="rounded-lg px-3 py-1.5 text-xs font-medium cursor-pointer"
                  style={{ backgroundColor: "#ef444422", color: "#ef4444" }}
                >
                  Cerrar
                </button>
              </div>
            </div>
            <iframe
              src={`/viz/${selectedViz}`}
              className="flex-1 w-full rounded-b-2xl"
              style={{ border: "none", backgroundColor: "#fff" }}
              title="Visualization"
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t mt-12 py-6" style={{ borderColor: "#1e293b" }}>
        <div className="mx-auto max-w-7xl px-4 text-center text-xs sm:px-6" style={{ color: "#475569" }}>
          PML Finance &mdash; Basado en Kanungo, <em>Probabilistic ML for Finance and Investing</em> (O&apos;Reilly 2023)
        </div>
      </footer>
    </div>
  );
}
