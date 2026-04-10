import { Router, Response } from 'express';
import { authMiddleware, AuthRequest } from '../middleware/auth.middleware.js';

const router = Router();

const TIER_LEVEL: Record<string, number> = {
  FREE: 0,
  BASICO: 1,
  AVANZADO: 2,
  PREMIUM: 3,
};

interface ModuleDef {
  id: string;
  number: string;
  title: string;
  chapter: number;
  tier: string;
  duration: number;
  viz: string | null;
  description: string;
}

const MODULES: ModuleDef[] = [
  { id: "mod02", number: "2", title: "Analisis de Incertidumbre", chapter: 2, tier: "BASICO", duration: 60, viz: "monty_hall_mcs.html", description: "Monty Hall, axiomas de probabilidad, significado de probabilidad." },
  { id: "mod02b", number: "2B", title: "Probabilidades Relativas", chapter: 2, tier: "BASICO", duration: 45, viz: "relative_probability.html", description: "P(A|I), Knight, Beta-Binomial updating." },
  { id: "mod02c", number: "2C", title: "Black-Scholes y Trinidad de Incertidumbre", chapter: 2, tier: "AVANZADO", duration: 50, viz: "bsm_uncertainty_trinity.html", description: "BSM, volatility smile, trinidad de incertidumbre." },
  { id: "mod02d", number: "2D", title: "Bias-Variance y No Free Lunch", chapter: 2, tier: "BASICO", duration: 45, viz: "bias_variance_nfl.html", description: "Tradeoff bias-varianza, NFL theorems." },
  { id: "mod02e", number: "2E", title: "Problema de la Induccion", chapter: 2, tier: "BASICO", duration: 40, viz: "induction_problem.html", description: "Russell's turkey, cisne negro, cambio de regimen." },
  { id: "mod03", number: "3", title: "Simulacion Monte Carlo", chapter: 3, tier: "BASICO", duration: 50, viz: "mcs_fat_tails.html", description: "MCS para finanzas, fat tails vs Normal." },
  { id: "mod03b", number: "3B", title: "Conceptos Estadisticos y Volatilidad", chapter: 3, tier: "BASICO", duration: 45, viz: "stat_concepts.html", description: "4 momentos, kurtosis, ergodicidad." },
  { id: "mod03c", number: "3C", title: "Normal vs Realidad", chapter: 3, tier: "BASICO", duration: 40, viz: "normal_vs_reality.html", description: "Tests JB/SW/AD, MLE fit, AIC/BIC." },
  { id: "mod03d", number: "3D", title: "LGN, TLC y Fundamentos MCS", chapter: 3, tier: "BASICO", duration: 45, viz: "lln_clt_mcs.html", description: "LGN, TLC, convergencia, Cauchy." },
  { id: "mod04", number: "4", title: "Peligros de NHST", chapter: 4, tier: "AVANZADO", duration: 55, viz: "nhst_dangers.html", description: "Falacia inversa, p-hacking, p-values." },
  { id: "mod04b", number: "4B", title: "NHST Aplicado: OLS, Base Rates", chapter: 4, tier: "AVANZADO", duration: 50, viz: "nhst_applied.html", description: "OLS diagnosticos, tasas base, PPV." },
  { id: "mod04c", number: "4C", title: "IC, CAPM y la Trampa de Alpha", chapter: 4, tier: "AVANZADO", duration: 50, viz: "ci_capm_alpha.html", description: "IC vs HDI, CAPM OLS, alpha." },
  { id: "mod05", number: "5", title: "Framework PML", chapter: 5, tier: "AVANZADO", duration: 50, viz: "pml_framework.html", description: "Prior, posterior, predictive." },
  { id: "mod05b", number: "5B", title: "Default de Bonos High-Yield", chapter: 5, tier: "AVANZADO", duration: 45, viz: "hy_default.html", description: "Priors por rating, Beta-Binomial." },
  { id: "mod06", number: "6", title: "MLE vs PML", chapter: 6, tier: "AVANZADO", duration: 55, viz: "mle_vs_pml.html", description: "MLE limitaciones, MCMC Metropolis." },
  { id: "mod06b", number: "6B", title: "Caso ZYX: MLE Falla", chapter: 6, tier: "AVANZADO", duration: 40, viz: "zyx_mle_failure.html", description: "MLE con pocos datos, prior sensitivity." },
  { id: "mod06c", number: "6C", title: "Grid, Markov Chains y MCMC", chapter: 6, tier: "AVANZADO", duration: 50, viz: "grid_mcmc.html", description: "Grid, Markov chains, Metropolis." },
  { id: "mod07", number: "7", title: "Ensambles Generativos con PyMC", chapter: 7, tier: "PREMIUM", duration: 65, viz: "ensemble_hdi.html", description: "PLE, HDI, spaghetti plot." },
  { id: "mod07b", number: "7B", title: "PLE Aplicado: Alpha, Hedging, CAPM", chapter: 7, tier: "PREMIUM", duration: 55, viz: "ple_applied.html", description: "Jensen's alpha, cross-hedging." },
  { id: "mod07c", number: "7C", title: "Retrodiccion, HMC y Evaluacion", chapter: 7, tier: "PREMIUM", duration: 50, viz: "retrodiction_eval.html", description: "Predictive checks, R2 probabilistico." },
  { id: "mod08", number: "8", title: "Decisiones: Kelly, GVaR, Ergodicidad", chapter: 8, tier: "PREMIUM", duration: 60, viz: "kelly_decisions.html", description: "Kelly, ergodicidad, GVaR." },
  { id: "mod08b", number: "8B", title: "Loss Functions, Volatility Drag, ES", chapter: 8, tier: "PREMIUM", duration: 50, viz: "loss_volatility.html", description: "Loss functions, VaR vs ES." },
  { id: "mod08c", number: "8C", title: "GVaR, GES y GTR: Riesgo Generativo", chapter: 8, tier: "PREMIUM", duration: 45, viz: "gvar_ges_gtr.html", description: "3 metricas generativas de riesgo." },
  { id: "mod08d", number: "8D", title: "MPT, CAPM y Critica Probabilistica", chapter: 8, tier: "PREMIUM", duration: 50, viz: "mpt_critique.html", description: "MPT critique, 1/N, crisis correlations." },
];

// GET /api/modules — returns all modules with access info
router.get('/', authMiddleware, (req: AuthRequest, res: Response) => {
  const userLevel = TIER_LEVEL[req.user?.plan || 'FREE'] ?? 0;

  const result = MODULES.map((mod) => {
    const requiredLevel = TIER_LEVEL[mod.tier] ?? 0;
    const unlocked = userLevel >= requiredLevel;
    return {
      ...mod,
      unlocked,
      requiredPlan: mod.tier,
    };
  });

  res.json({
    modules: result,
    userPlan: req.user?.plan || 'FREE',
    stats: {
      total: MODULES.length,
      unlocked: result.filter((m) => m.unlocked).length,
      locked: result.filter((m) => !m.unlocked).length,
    },
  });
});

// GET /api/modules/:id — returns single module (only if unlocked)
router.get('/:id', authMiddleware, (req: AuthRequest, res: Response) => {
  const mod = MODULES.find((m) => m.id === req.params.id);
  if (!mod) {
    res.status(404).json({ error: 'Modulo no encontrado' });
    return;
  }

  const userLevel = TIER_LEVEL[req.user?.plan || 'FREE'] ?? 0;
  const requiredLevel = TIER_LEVEL[mod.tier] ?? 0;

  if (userLevel < requiredLevel) {
    res.status(403).json({
      error: 'Plan insuficiente para acceder a este modulo',
      required: mod.tier,
      current: req.user?.plan || 'FREE',
      module: { id: mod.id, title: mod.title, tier: mod.tier },
    });
    return;
  }

  res.json({ module: mod, unlocked: true });
});

export default router;
