"""
Demo: Intervalos de Confianza, CAPM y la Trampa de Alpha.

Estima alpha/beta de AAPL vs SPY con OLS, analiza IC del parametro
vs IC de prediccion, demuestra los 3 errores de interpretacion, y
compara IC frecuentista vs intervalo credible bayesiano.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/ci_capm_alpha_demo.py
"""
import numpy as np
from scipy import stats


def demo_ols_ic():
    """Estima alpha/beta y sus IC."""
    print("=" * 65)
    print("1. OLS: AAPL vs SPY -- ALPHA, BETA E IC 95%")
    print("=" * 65)

    np.random.seed(42)
    n = 504
    r_spy = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_aapl = 0.0002 + 1.25 * r_spy + 0.010 * np.random.standard_t(4, n)

    X = np.column_stack([np.ones(n), r_spy])
    b = np.linalg.lstsq(X, r_aapl, rcond=None)[0]
    res = r_aapl - X @ b
    mse = np.sum(res**2) / (n - 2)
    se = np.sqrt(mse * np.diag(np.linalg.inv(X.T @ X)))
    t_crit = stats.t.ppf(0.975, n - 2)

    print(f"\n  r_AAPL = alpha + beta * r_SPY + epsilon")
    print(f"\n  {'Param':<8} {'Coef':<12} {'SE':<10} {'IC 95%':<30} {'Incluye 0?'}")
    print(f"  {'-'*65}")

    for i, nombre in enumerate(["alpha", "beta"]):
        lo = b[i] - t_crit * se[i]
        hi = b[i] + t_crit * se[i]
        incl = "SI" if lo <= 0 <= hi else "NO"
        ancho = hi - lo
        print(f"  {nombre:<8} {b[i]:<12.6f} {se[i]:<10.6f} "
              f"({lo:>+.6f}, {hi:>+.6f})  {incl}  (ancho={ancho:.6f})")

    # IC de prediccion
    x_mid = r_spy.mean()
    se_pred_param = np.sqrt(mse * (1/n + (x_mid - r_spy.mean())**2 / np.sum((r_spy - r_spy.mean())**2)))
    se_pred_obs = np.sqrt(mse + se_pred_param**2)

    print(f"\n  IC de prediccion (en r_spy = media):")
    print(f"    IC parametro: ancho = {2*t_crit*se_pred_param*100:.3f}%")
    print(f"    IC prediccion: ancho = {2*t_crit*se_pred_obs*100:.3f}%")
    print(f"    Ratio: prediccion es {se_pred_obs/se_pred_param:.0f}x mas ancho")
    print(f"\n  -> IC prediccion: r_AAPL en ({(b[0]+b[1]*x_mid - t_crit*se_pred_obs)*100:+.2f}%, "
          f"{(b[0]+b[1]*x_mid + t_crit*se_pred_obs)*100:+.2f}%)")
    print(f"  -> Practicamente inutil como prediccion")

    return b, se, r_spy, r_aapl


def demo_errores_ic():
    """Demuestra los 3 errores de interpretacion."""
    print("\n" + "=" * 65)
    print("2. LOS 3 ERRORES DE INTERPRETACION DE IC")
    print("=" * 65)

    np.random.seed(42)
    mu_real = 0.05
    n_rep = 10000
    contiene = 0

    for _ in range(n_rep):
        datos = np.random.normal(mu_real, 0.20, 10)
        mu_hat = datos.mean()
        se = datos.std(ddof=1) / np.sqrt(10)
        t_c = stats.t.ppf(0.975, 9)
        if mu_hat - t_c * se <= mu_real <= mu_hat + t_c * se:
            contiene += 1

    print(f"\n  Cobertura empirica (10,000 reps): {contiene/n_rep:.1%}")
    print(f"""
  ERROR 1: "95% de prob de que mu este en mi IC"
    -> FALSO. mu=0.05 es fijo. El IC es aleatorio.
    -> Correcto: {contiene/n_rep:.0%} de los ICs contienen mu.

  ERROR 2: "IC no incluye 0 = efecto significativo"
    -> Equivale a NHST. Ignora base rate y multiples tests.

  ERROR 3: "Ancho del IC = mi incertidumbre"
    -> Solo mide precision muestral, no conocimiento previo.
""")


def demo_bayesiano_vs_freq():
    """Compara IC vs intervalo credible para alpha."""
    print("=" * 65)
    print("3. IC FRECUENTISTA vs INTERVALO CREDIBLE BAYESIANO")
    print("=" * 65)

    np.random.seed(42)
    n = 504
    r_spy = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_aapl = 0.0002 + 1.25 * r_spy + 0.010 * np.random.standard_t(4, n)

    X = np.column_stack([np.ones(n), r_spy])
    b = np.linalg.lstsq(X, r_aapl, rcond=None)[0]
    res = r_aapl - X @ b
    mse = np.sum(res**2) / (n - 2)
    se_alpha = np.sqrt(mse * np.linalg.inv(X.T @ X)[0, 0])

    # Frecuentista
    freq_lo = b[0] - 1.96 * se_alpha
    freq_hi = b[0] + 1.96 * se_alpha

    # Bayesiano (Normal-Normal)
    prior_mu, prior_sigma = 0.0, 0.0005
    tau_prior = 1 / prior_sigma**2
    tau_data = 1 / se_alpha**2
    tau_post = tau_prior + tau_data
    mu_post = (tau_prior * prior_mu + tau_data * b[0]) / tau_post
    sigma_post = 1 / np.sqrt(tau_post)
    bayes_lo = mu_post - 1.96 * sigma_post
    bayes_hi = mu_post + 1.96 * sigma_post
    p_alpha_pos = 1 - stats.norm.cdf(0, mu_post, sigma_post)

    print(f"\n  Prior: alpha ~ N(0, {prior_sigma:.4f}) (esceptico)")
    print(f"\n  {'Metrica':<25} {'Frecuentista':<20} {'Bayesiano'}")
    print(f"  {'-'*55}")
    print(f"  {'Alpha':<25} {b[0]:<20.6f} {mu_post:.6f}")
    print(f"  {'Intervalo 95%':<25} ({freq_lo:.6f}, {freq_hi:.6f})  "
          f"({bayes_lo:.6f}, {bayes_hi:.6f})")
    print(f"  {'Ancho':<25} {freq_hi-freq_lo:<20.6f} {bayes_hi-bayes_lo:.6f}")
    print(f"  {'P(alpha > 0)':<25} {'N/A':<20} {p_alpha_pos:.1%}")

    print(f"\n  -> El bayesiano responde directamente: P(alpha > 0) = {p_alpha_pos:.0%}")
    print(f"  -> El frecuentista NO puede dar esa respuesta")
    print(f"  -> El prior encoge alpha hacia 0 (escepticismo razonable)")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: IC, CAPM Y LA TRAMPA DE ALPHA")
    print("  Modulo 4C")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_ols_ic()
    demo_errores_ic()
    demo_bayesiano_vs_freq()

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
