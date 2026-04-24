"""
Demo: Retrodiccion, HMC y Evaluacion de PLEs.

Implementa prior/posterior predictive checks, demuestra como el
ensamble ensancha intervalos en extrapolacion, y calcula R2 probabilistico.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/retrodiction_eval_demo.py
"""
import numpy as np
from scipy import stats


def generar_datos(n=252, seed=42):
    np.random.seed(seed)
    r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_asset = 0.0002 + 1.25 * r_mkt + 0.010 * np.random.standard_t(4, n)
    return r_mkt, r_asset


def posterior_aproximado(r_mkt, r_asset):
    """Calcula posterior conjugado para alpha/beta."""
    n = len(r_mkt)
    X = np.column_stack([np.ones(n), r_mkt])
    b = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    res = r_asset - X @ b
    mse = np.sum(res**2) / (n - 2)
    se = np.sqrt(mse * np.diag(np.linalg.inv(X.T @ X)))
    sigma_res = np.sqrt(mse)

    # Posterior con priors
    tau_a = 1/0.001**2 + 1/se[0]**2
    mu_a = (0/0.001**2 + b[0]/se[0]**2) / tau_a
    sig_a = 1 / np.sqrt(tau_a)

    tau_b = 1/0.5**2 + 1/se[1]**2
    mu_b = (1/0.5**2 + b[1]/se[1]**2) / tau_b
    sig_b = 1 / np.sqrt(tau_b)

    return mu_a, sig_a, mu_b, sig_b, sigma_res, b


def demo_prior_predictive():
    """Prior predictive check."""
    print("=" * 65)
    print("1. PRIOR PREDICTIVE CHECK (RETRODICCION PREVIA)")
    print("=" * 65)

    np.random.seed(42)
    n_sims = 500
    n_pts = 50
    x_sim = np.linspace(-0.05, 0.05, n_pts)

    # Simular desde priors
    alpha_prior = np.random.normal(0, 0.001, n_sims)
    beta_prior = np.random.normal(1, 0.5, n_sims)
    sigma_prior = np.abs(np.random.standard_t(4, n_sims)) * 0.02

    # Rango de retornos simulados
    y_sims = []
    for a, b, s in zip(alpha_prior, beta_prior, sigma_prior):
        y = a + b * x_sim + np.random.normal(0, s, n_pts)
        y_sims.append(y)
    y_sims = np.array(y_sims)

    y_min = y_sims.min()
    y_max = y_sims.max()
    y_mean_range = y_sims.mean(axis=1)

    print(f"\n  500 simulaciones desde los priors:")
    print(f"  Rango de retornos simulados: ({y_min*100:.1f}%, {y_max*100:.1f}%)")
    print(f"  Retornos reales tipicos: (-5%, +5%)")
    print(f"  Los priors son plausibles? {'SI' if abs(y_max) < 0.5 else 'Demasiado amplios'}")
    print(f"\n  -> Si el prior genera retornos de +100%: MALO")
    print(f"  -> Si genera retornos de -5% a +5%: razonable")


def demo_posterior_predictive(r_mkt, r_asset, mu_a, sig_a, mu_b, sig_b, sigma_res):
    """Posterior predictive check (retrodiccion posterior)."""
    print("\n" + "=" * 65)
    print("2. POSTERIOR PREDICTIVE CHECK (RETRODICCION POSTERIOR)")
    print("=" * 65)

    np.random.seed(42)
    n = len(r_mkt)
    n_sims = 1000

    # Simular datos desde posterior
    dentro_95 = np.zeros(n)
    for i in range(n):
        alphas = np.random.normal(mu_a, sig_a, n_sims)
        betas = np.random.normal(mu_b, sig_b, n_sims)
        y_sims = alphas + betas * r_mkt[i] + sigma_res * np.random.standard_t(4, n_sims)
        lo = np.percentile(y_sims, 2.5)
        hi = np.percentile(y_sims, 97.5)
        dentro_95[i] = (lo <= r_asset[i] <= hi)

    cobertura = dentro_95.mean()
    print(f"\n  Cobertura 95% (datos reales dentro del HDI simulado): {cobertura:.1%}")
    print(f"  Esperado: ~95%")
    print(f"  Resultado: {'OK - modelo calibrado' if 0.90 <= cobertura <= 1.0 else 'REVISAR modelo'}")


def demo_extrapolacion(mu_a, sig_a, mu_b, sig_b, sigma_res):
    """Demuestra ensanchamiento de intervalos en extrapolacion."""
    print("\n" + "=" * 65)
    print("3. EXTRAPOLACION: INTERVALOS SE ENSANCHAN")
    print("=" * 65)

    np.random.seed(42)
    escenarios = [
        ("r_mkt = 0% (centro)", 0.0),
        ("r_mkt = +2% (dentro)", 0.02),
        ("r_mkt = +5% (borde)", 0.05),
        ("r_mkt = +10% (extrapolacion)", 0.10),
    ]

    print(f"\n  {'Escenario':<35} {'Media':<10} {'HDI 95%':<25} {'Ancho'}")
    print(f"  {'-'*75}")

    ancho_base = None
    for nombre, r in escenarios:
        alphas = np.random.normal(mu_a, sig_a, 50000)
        betas = np.random.normal(mu_b, sig_b, 50000)
        preds = alphas + betas * r + sigma_res * np.random.standard_t(4, 50000)
        media = preds.mean()
        hdi = (np.percentile(preds, 2.5), np.percentile(preds, 97.5))
        ancho = hdi[1] - hdi[0]
        if ancho_base is None:
            ancho_base = ancho
        ratio = ancho / ancho_base
        print(f"  {nombre:<35} {media*100:>+6.2f}%   ({hdi[0]*100:>+6.2f}%, {hdi[1]*100:>+6.2f}%)  "
              f"{ancho*100:.2f}% ({ratio:.1f}x)")

    print(f"\n  -> El modelo ENSANCHA intervalos en extrapolacion")
    print(f"  -> OLS mantiene el mismo ancho -> falsa confianza")


def demo_r2_probabilistico(r_mkt, r_asset, mu_a, sig_a, mu_b, sig_b):
    """R-squared como distribucion."""
    print("\n" + "=" * 65)
    print("4. R-SQUARED PROBABILISTICO")
    print("=" * 65)

    np.random.seed(42)
    n_sims = 5000
    r2_sims = []
    var_y = np.var(r_asset)

    for _ in range(n_sims):
        a = np.random.normal(mu_a, sig_a)
        b = np.random.normal(mu_b, sig_b)
        pred = a + b * r_mkt
        res = r_asset - pred
        r2 = 1 - np.var(res) / var_y
        r2_sims.append(r2)

    r2_arr = np.array(r2_sims)

    # OLS R2
    X = np.column_stack([np.ones(len(r_mkt)), r_mkt])
    b_ols = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    r2_ols = 1 - np.var(r_asset - X @ b_ols) / var_y

    print(f"\n  OLS R2: {r2_ols:.4f} (punto unico)")
    print(f"  PLE R2: media={r2_arr.mean():.4f}, HDI=({np.percentile(r2_arr, 2.5):.4f}, "
          f"{np.percentile(r2_arr, 97.5):.4f})")
    print(f"  P(R2 > 0.5): {(r2_arr > 0.5).mean():.1%}")
    print(f"  P(R2 > 0.7): {(r2_arr > 0.7).mean():.1%}")
    print(f"\n  -> R2 es una DISTRIBUCION, no un solo numero")
    print(f"  -> Cuantifica incertidumbre sobre la calidad del modelo")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: RETRODICCION, HMC Y EVALUACION DE PLEs")
    print("  Modulo 7C")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    r_mkt, r_asset = generar_datos()
    mu_a, sig_a, mu_b, sig_b, sigma_res, b_ols = posterior_aproximado(r_mkt, r_asset)

    demo_prior_predictive()
    demo_posterior_predictive(r_mkt, r_asset, mu_a, sig_a, mu_b, sig_b, sigma_res)
    demo_extrapolacion(mu_a, sig_a, mu_b, sig_b, sigma_res)
    demo_r2_probabilistico(r_mkt, r_asset, mu_a, sig_a, mu_b, sig_b)

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
