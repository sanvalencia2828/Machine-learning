"""
Demo: PLE Aplicado -- Jensen's Alpha, Cross-Hedging, Market Neutral.

Implementa 4 aplicaciones financieras del Probabilistic Linear Ensemble
usando aproximacion conjugada (sin PyMC).

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/ple_applied_demo.py
"""
import numpy as np
from scipy import stats


def generar_datos(n=252, alpha=0.0001, beta=1.20, sigma=0.010, seed=42):
    """Genera retornos sinteticos activo vs mercado."""
    np.random.seed(seed)
    r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_asset = alpha + beta * r_mkt + sigma * np.random.standard_t(4, n)
    return r_mkt, r_asset


def posterior_conjugado(r_mkt, r_asset):
    """Calcula posterior aproximado para alpha y beta."""
    n = len(r_mkt)
    X = np.column_stack([np.ones(n), r_mkt])
    b = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    res = r_asset - X @ b
    mse = np.sum(res**2) / (n - 2)
    se = np.sqrt(mse * np.diag(np.linalg.inv(X.T @ X)))

    # Posteriors con priors
    # alpha: prior N(0, 0.001)
    tau_a = 1/0.001**2 + 1/se[0]**2
    mu_a = (0/0.001**2 + b[0]/se[0]**2) / tau_a
    sig_a = 1 / np.sqrt(tau_a)

    # beta: prior N(1, 0.5)
    tau_b = 1/0.5**2 + 1/se[1]**2
    mu_b = (1/0.5**2 + b[1]/se[1]**2) / tau_b
    sig_b = 1 / np.sqrt(tau_b)

    return {
        "ols_alpha": b[0], "ols_beta": b[1], "ols_se": se,
        "alpha_mu": mu_a, "alpha_sig": sig_a,
        "beta_mu": mu_b, "beta_sig": sig_b,
        "r_sq": 1 - np.sum(res**2)/np.sum((r_asset-r_asset.mean())**2),
        "sigma_est": np.sqrt(mse),
    }


def demo_jensens_alpha(post):
    """Aplicacion 1: tiene el gestor alpha real?"""
    print("=" * 65)
    print("1. JENSEN'S ALPHA: P(alpha > 0)?")
    print("=" * 65)

    p_pos = 1 - stats.norm.cdf(0, post["alpha_mu"], post["alpha_sig"])
    hdi = (post["alpha_mu"] - 1.96*post["alpha_sig"],
           post["alpha_mu"] + 1.96*post["alpha_sig"])

    print(f"\n  OLS alpha: {post['ols_alpha']:.6f}")
    print(f"  Posterior: mu={post['alpha_mu']:.6f}, sigma={post['alpha_sig']:.6f}")
    print(f"  HDI 95%: ({hdi[0]:.6f}, {hdi[1]:.6f})")
    print(f"  P(alpha > 0) = {p_pos:.1%}")
    print(f"\n  -> {'Evidencia de alpha' if p_pos > 0.9 else 'Sin evidencia clara de alpha'}")
    print(f"  -> OLS no puede dar P(alpha > 0). PLE si.")


def demo_cross_hedging(post):
    """Aplicacion 2: hedge ratio optimo."""
    print("\n" + "=" * 65)
    print("2. CROSS-HEDGING: DISTRIBUCION DEL HEDGE RATIO")
    print("=" * 65)

    hdi = (post["beta_mu"] - 1.96*post["beta_sig"],
           post["beta_mu"] + 1.96*post["beta_sig"])

    print(f"\n  OLS beta (hedge ratio): {post['ols_beta']:.4f}")
    print(f"  Posterior beta: {post['beta_mu']:.4f} +/- {post['beta_sig']:.4f}")
    print(f"  HDI 95%: ({hdi[0]:.4f}, {hdi[1]:.4f})")
    print(f"\n  Para cubrir $1M de exposicion:")
    print(f"    OLS dice: vender ${post['ols_beta']*1e6:,.0f} del indice")
    print(f"    PLE dice: vender entre ${hdi[0]*1e6:,.0f} y ${hdi[1]*1e6:,.0f}")
    print(f"  -> PLE te da un RANGO de cobertura, no un solo numero")


def demo_market_neutral(post):
    """Aplicacion 3: es el fondo market neutral?"""
    print("\n" + "=" * 65)
    print("3. MARKET NEUTRAL: P(|beta| < 0.1)?")
    print("=" * 65)

    p_neutral = (stats.norm.cdf(0.1, post["beta_mu"], post["beta_sig"]) -
                 stats.norm.cdf(-0.1, post["beta_mu"], post["beta_sig"]))

    print(f"\n  Beta posterior: {post['beta_mu']:.4f}")
    print(f"  P(|beta| < 0.1) = {p_neutral:.1%}")
    print(f"  P(|beta| < 0.2) = "
          f"{stats.norm.cdf(0.2, post['beta_mu'], post['beta_sig']) - stats.norm.cdf(-0.2, post['beta_mu'], post['beta_sig']):.1%}")
    print(f"\n  -> {'Market neutral CONFIRMADO' if p_neutral > 0.5 else 'NO es market neutral'} "
          f"(beta={post['beta_mu']:.2f} es demasiado alto)")


def demo_cost_of_equity(post):
    """Aplicacion 4: CAPM cost of equity probabilistico."""
    print("\n" + "=" * 65)
    print("4. COST OF EQUITY: CAPM PROBABILISTICO")
    print("=" * 65)

    r_f = 0.045  # 4.5% tasa libre de riesgo
    erp = 0.06   # 6% equity risk premium

    np.random.seed(42)
    betas = np.random.normal(post["beta_mu"], post["beta_sig"], 50000)
    r_e = r_f + betas * erp

    hdi_re = (np.percentile(r_e, 2.5), np.percentile(r_e, 97.5))
    re_ols = r_f + post["ols_beta"] * erp

    print(f"\n  r_f = {r_f:.1%}, ERP = {erp:.1%}")
    print(f"  OLS: r_e = {re_ols:.2%} (punto unico)")
    print(f"  PLE: r_e = {r_e.mean():.2%}")
    print(f"  HDI 95%: ({hdi_re[0]:.2%}, {hdi_re[1]:.2%})")
    print(f"  Rango: {(hdi_re[1]-hdi_re[0])*100:.1f}pp de incertidumbre")
    print(f"\n  -> En DCF, esta incertidumbre cambia la valuacion +/- 15-25%")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: PLE APLICADO -- 4 PREGUNTAS FINANCIERAS")
    print("  Modulo 7B")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    r_mkt, r_asset = generar_datos()
    post = posterior_conjugado(r_mkt, r_asset)

    print(f"\n  Datos: {len(r_mkt)} dias, R2={post['r_sq']:.3f}")

    demo_jensens_alpha(post)
    demo_cross_hedging(post)
    demo_market_neutral(post)
    demo_cost_of_equity(post)

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
