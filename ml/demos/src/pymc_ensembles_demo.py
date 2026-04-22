"""
Demo: Ensambles Generativos -- OLS vs Regresion Probabilistica.

Implementa OLS y regresion probabilistica (sin PyMC) para comparar
intervalos de confianza vs intervalos creibles, y genera un ensamble
de lineas de regresion desde el posterior.

Nota: usa Normal-Normal conjugado como aproximacion a PyMC para
que el script funcione sin dependencias pesadas (PyMC no requerido).

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/pymc_ensembles_demo.py
"""
import numpy as np
from scipy import stats


def generar_datos_mercado(n=252, alpha=0.0002, beta=1.25,
                           sigma=0.010, seed=42):
    """Genera retornos sinteticos AAPL vs SP500."""
    np.random.seed(seed)
    r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_asset = alpha + beta * r_mkt + sigma * np.random.standard_t(4, n)
    return r_mkt, r_asset


def demo_ols():
    """OLS clasico con IC."""
    print("=" * 65)
    print("1. OLS CLASICO: MARKET MODEL")
    print("=" * 65)

    r_mkt, r_asset = generar_datos_mercado()
    n = len(r_mkt)
    X = np.column_stack([np.ones(n), r_mkt])
    b = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    res = r_asset - X @ b
    mse = np.sum(res**2) / (n - 2)
    se = np.sqrt(mse * np.diag(np.linalg.inv(X.T @ X)))

    print(f"\n  {'Param':<8} {'Coef':<12} {'SE':<10} {'IC 95%'}")
    print(f"  {'-'*50}")
    for i, nombre in enumerate(["alpha", "beta"]):
        lo = b[i] - 1.96 * se[i]
        hi = b[i] + 1.96 * se[i]
        print(f"  {nombre:<8} {b[i]:<12.6f} {se[i]:<10.6f} ({lo:.6f}, {hi:.6f})")

    r_sq = 1 - np.sum(res**2) / np.sum((r_asset - r_asset.mean())**2)
    jb_s, jb_p = stats.jarque_bera(res)
    print(f"\n  R-squared: {r_sq:.4f}")
    print(f"  Jarque-Bera: p={jb_p:.2e} -> {'RECHAZA normalidad' if jb_p < 0.05 else 'OK'}")

    return r_mkt, r_asset, b, se, mse


def demo_probabilistic(r_mkt, r_asset, b_ols, se_ols, mse_ols):
    """Regresion probabilistica via conjugado Normal (simula PyMC)."""
    print("\n" + "=" * 65)
    print("2. REGRESION PROBABILISTICA (APROXIMACION CONJUGADA)")
    print("=" * 65)

    n = len(r_mkt)

    # Posterior de alpha (Normal-Normal conjugado)
    prior_alpha_mu, prior_alpha_sigma = 0.0, 0.001
    tau_pr = 1 / prior_alpha_sigma**2
    tau_d = 1 / se_ols[0]**2
    tau_po = tau_pr + tau_d
    alpha_post_mu = (tau_pr * prior_alpha_mu + tau_d * b_ols[0]) / tau_po
    alpha_post_sigma = 1 / np.sqrt(tau_po)

    # Posterior de beta (Normal-Normal conjugado)
    prior_beta_mu, prior_beta_sigma = 1.0, 0.5
    tau_pr_b = 1 / prior_beta_sigma**2
    tau_d_b = 1 / se_ols[1]**2
    tau_po_b = tau_pr_b + tau_d_b
    beta_post_mu = (tau_pr_b * prior_beta_mu + tau_d_b * b_ols[1]) / tau_po_b
    beta_post_sigma = 1 / np.sqrt(tau_po_b)

    print(f"\n  Priors:")
    print(f"    alpha ~ Normal({prior_alpha_mu}, {prior_alpha_sigma})")
    print(f"    beta ~ Normal({prior_beta_mu}, {prior_beta_sigma})")
    print(f"\n  {'Param':<8} {'OLS':<14} {'Posterior':<14} {'HDI 95%':<28} {'P(>0)'}")
    print(f"  {'-'*70}")

    a_hdi = (alpha_post_mu - 1.96*alpha_post_sigma, alpha_post_mu + 1.96*alpha_post_sigma)
    b_hdi = (beta_post_mu - 1.96*beta_post_sigma, beta_post_mu + 1.96*beta_post_sigma)
    p_alpha_pos = 1 - stats.norm.cdf(0, alpha_post_mu, alpha_post_sigma)
    p_beta_gt1 = 1 - stats.norm.cdf(1.0, beta_post_mu, beta_post_sigma)

    print(f"  {'alpha':<8} {b_ols[0]:<14.6f} {alpha_post_mu:<14.6f} "
          f"({a_hdi[0]:.6f}, {a_hdi[1]:.6f})  {p_alpha_pos:.1%}")
    print(f"  {'beta':<8} {b_ols[1]:<14.4f} {beta_post_mu:<14.4f} "
          f"({b_hdi[0]:.4f}, {b_hdi[1]:.4f}){'':>8} P(>1)={p_beta_gt1:.1%}")

    return alpha_post_mu, alpha_post_sigma, beta_post_mu, beta_post_sigma


def demo_ensamble(r_mkt, alpha_mu, alpha_sig, beta_mu, beta_sig):
    """Genera ensamble de lineas de regresion."""
    print("\n" + "=" * 65)
    print("3. ENSAMBLE GENERATIVO: 200 LINEAS DE REGRESION")
    print("=" * 65)

    np.random.seed(42)
    n_lines = 200
    alphas = np.random.normal(alpha_mu, alpha_sig, n_lines)
    betas = np.random.normal(beta_mu, beta_sig, n_lines)

    x_range = np.linspace(r_mkt.min(), r_mkt.max(), 100)

    # Para cada x, calcular rango de predicciones
    preds = np.array([a + b * x_range for a, b in zip(alphas, betas)])
    media = preds.mean(axis=0)
    hdi_lo = np.percentile(preds, 2.5, axis=0)
    hdi_hi = np.percentile(preds, 97.5, axis=0)

    # Ancho en x=0, x=min, x=max
    for label, idx in [("x=media", len(x_range)//2),
                       ("x=min", 0), ("x=max", -1)]:
        ancho = (hdi_hi[idx] - hdi_lo[idx]) * 100
        print(f"  {label}: HDI ancho = {ancho:.3f}%")

    print(f"\n  -> Las lineas CONVERGEN en el centro (alta certeza)")
    print(f"  -> Las lineas DIVERGEN en los extremos (baja certeza)")
    print(f"  -> El ensamble SABE que no sabe en extrapolaciones")


def demo_retrodiction_prediction():
    """Retrodiction y prediction con el ensamble."""
    print("\n" + "=" * 65)
    print("4. RETRODICTION vs PREDICTION")
    print("=" * 65)

    np.random.seed(42)
    r_mkt, r_asset = generar_datos_mercado()

    # Posterior simple
    n = len(r_mkt)
    X = np.column_stack([np.ones(n), r_mkt])
    b = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    res = r_asset - X @ b
    sigma_est = res.std()

    # Retrodiction: simular datos desde el modelo
    n_sim = 1000
    retro_means = X @ b
    retro_sims = retro_means[:, None] + sigma_est * np.random.standard_t(4, (n, n_sim))

    # Chequeo: los datos reales caen dentro de los simulados?
    dentro = np.zeros(n)
    for i in range(n):
        lo = np.percentile(retro_sims[i], 2.5)
        hi = np.percentile(retro_sims[i], 97.5)
        dentro[i] = (lo <= r_asset[i] <= hi)

    cobertura = dentro.mean()

    # Prediction: proximo retorno dado r_mkt = 0.01 (dia alcista)
    r_nuevo = 0.01
    pred_mu = b[0] + b[1] * r_nuevo
    pred_sims = pred_mu + sigma_est * np.random.standard_t(4, 10000)
    pred_hdi = (np.percentile(pred_sims, 2.5), np.percentile(pred_sims, 97.5))

    print(f"\n  Retrodiction (posterior predictive check):")
    print(f"    Cobertura 95%: {cobertura:.1%} de datos dentro del HDI simulado")
    print(f"    (Deberia ser ~95%: {'OK' if 0.90 <= cobertura <= 1.0 else 'revisar'})")

    print(f"\n  Prediction (proximo retorno si r_mkt = +1%):")
    print(f"    Media: {pred_mu*100:+.3f}%")
    print(f"    HDI 95%: ({pred_hdi[0]*100:+.3f}%, {pred_hdi[1]*100:+.3f}%)")
    print(f"    Ancho: {(pred_hdi[1]-pred_hdi[0])*100:.3f}%")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: ENSAMBLES GENERATIVOS CON REGRESION PROBABILISTICA")
    print("  Modulo 7")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    r_mkt, r_asset, b_ols, se_ols, mse = demo_ols()
    a_mu, a_sig, b_mu, b_sig = demo_probabilistic(r_mkt, r_asset, b_ols, se_ols, mse)
    demo_ensamble(r_mkt, a_mu, a_sig, b_mu, b_sig)
    demo_retrodiction_prediction()

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
