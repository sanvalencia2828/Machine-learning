"""
Demo: MLE vs PML -- Peligros de la IA Convencional.

Compara MLE (punto unico) vs PML (distribucion completa), demuestra
correlaciones espurias, implementa grid approximation y MCMC Metropolis
para estimar nu de una Student-t.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/mle_vs_pml_demo.py
"""
import numpy as np
from scipy import stats


def demo_mle_vs_pml():
    """Compara MLE vs PML para earnings prediction."""
    print("=" * 65)
    print("1. MLE vs PML: PREDICCION DE EARNINGS")
    print("=" * 65)

    np.random.seed(42)
    earnings = np.array([2.1, 2.3, 2.0, 2.5, 2.2])

    # MLE
    mu_mle = earnings.mean()
    sigma_mle = earnings.std(ddof=0)

    # PML (Normal-Normal conjugado)
    prior_mu, prior_sigma = 2.0, 0.5
    tau_prior = 1 / prior_sigma**2
    tau_data = len(earnings) / sigma_mle**2
    tau_post = tau_prior + tau_data
    mu_post = (tau_prior * prior_mu + tau_data * mu_mle) / tau_post
    sigma_post = 1 / np.sqrt(tau_post)

    # Predictive
    sigma_pred = np.sqrt(sigma_post**2 + sigma_mle**2)
    hdi_pred = (mu_post - 1.96 * sigma_pred, mu_post + 1.96 * sigma_pred)

    print(f"\n  Datos: {earnings.tolist()} (5 trimestres)")
    print(f"\n  {'Metrica':<30} {'MLE':<20} {'PML'}")
    print(f"  {'-'*55}")
    print(f"  {'Estimacion mu':<30} {mu_mle:<20.3f} {mu_post:.3f}")
    print(f"  {'Incertidumbre':<30} {'NINGUNA':<20} +/- {1.96*sigma_post:.3f} (HDI)")
    print(f"  {'Prediccion proxima':<30} {mu_mle:<20.3f} {mu_post:.3f}")
    print(f"  {'Rango prediccion 95%':<30} {'N/A':<20} ({hdi_pred[0]:.2f}, {hdi_pred[1]:.2f})")

    # Con outlier
    earnings_outlier = np.append(earnings, 3.5)
    mu_mle_out = earnings_outlier.mean()
    sigma_mle_out = earnings_outlier.std(ddof=0)
    tau_data_out = len(earnings_outlier) / sigma_mle_out**2
    tau_post_out = tau_prior + tau_data_out
    mu_post_out = (tau_prior * prior_mu + tau_data_out * mu_mle_out) / tau_post_out

    cambio_mle = (mu_mle_out - mu_mle) / mu_mle * 100
    cambio_pml = (mu_post_out - mu_post) / mu_post * 100

    print(f"\n  Con outlier (+3.5 earnings surprise):")
    print(f"    MLE se mueve: {mu_mle:.3f} -> {mu_mle_out:.3f} ({cambio_mle:+.1f}%)")
    print(f"    PML se mueve: {mu_post:.3f} -> {mu_post_out:.3f} ({cambio_pml:+.1f}%)")
    print(f"\n  -> MLE: {abs(cambio_mle):.0f}% de cambio. PML: {abs(cambio_pml):.0f}%.")
    print(f"  -> El prior protege contra outliers.")


def demo_correlaciones_espurias():
    """Demuestra correlaciones espurias en datasets aleatorios."""
    print("\n" + "=" * 65)
    print("2. CORRELACIONES ESPURIAS")
    print("=" * 65)

    np.random.seed(42)
    n_series = 50
    n_dias = 252

    # Generar series completamente independientes
    datos = np.random.normal(0, 1, (n_dias, n_series))

    # Calcular todas las correlaciones
    corr_matrix = np.corrcoef(datos.T)
    np.fill_diagonal(corr_matrix, 0)

    # Encontrar las "mejores"
    triu = np.triu_indices(n_series, k=1)
    corrs = corr_matrix[triu]

    print(f"\n  {n_series} series aleatorias, {n_dias} dias cada una")
    print(f"  Correlaciones posibles: {len(corrs)}")
    print(f"\n  Distribucion de correlaciones espurias:")
    print(f"    |r| > 0.10: {(np.abs(corrs) > 0.10).sum()} pares")
    print(f"    |r| > 0.15: {(np.abs(corrs) > 0.15).sum()} pares")
    print(f"    |r| > 0.20: {(np.abs(corrs) > 0.20).sum()} pares")

    # Top 5
    top_idx = np.argsort(np.abs(corrs))[-5:][::-1]
    print(f"\n  Top 5 'mejores' correlaciones (TODAS espurias):")
    for idx in top_idx:
        i, j = triu[0][idx], triu[1][idx]
        print(f"    Serie {i+1} vs Serie {j+1}: r = {corrs[idx]:+.3f}")

    print(f"\n  -> TODAS estas series son independientes")
    print(f"  -> Un modelo de ML las usaria como 'features'")
    print(f"  -> Resultado: overfitting garantizado")


def demo_grid_approximation():
    """Grid approximation para posterior de moneda sesgada."""
    print("\n" + "=" * 65)
    print("3. GRID APPROXIMATION")
    print("=" * 65)

    # Datos: 7 caras en 10 lanzamientos
    n, k = 10, 7

    # Grilla
    theta = np.linspace(0.001, 0.999, 1000)

    # Prior: Beta(2, 2)
    prior = stats.beta.pdf(theta, 2, 2)

    # Likelihood: Binomial
    likelihood = stats.binom.pmf(k, n, theta)

    # Posterior (no normalizado)
    posterior_raw = prior * likelihood
    posterior = posterior_raw / (posterior_raw.sum() * (theta[1] - theta[0]))

    # Comparar con analitico
    posterior_analitico = stats.beta.pdf(theta, 2 + k, 2 + n - k)

    media_grid = np.sum(theta * posterior * (theta[1] - theta[0]))
    media_analitica = (2 + k) / (2 + k + 2 + n - k)

    print(f"\n  Datos: {k} caras en {n} lanzamientos")
    print(f"  Prior: Beta(2, 2)")
    print(f"  Grilla: {len(theta)} puntos")
    print(f"\n  Media posterior (grid):      {media_grid:.4f}")
    print(f"  Media posterior (analitica):  {media_analitica:.4f}")
    print(f"  Error: {abs(media_grid - media_analitica):.6f}")
    print(f"\n  -> Grid approximation converge al resultado exacto")
    print(f"  -> Funciona con cualquier prior/likelihood")
    print(f"  -> Limitacion: no escala a muchos parametros")


def demo_mcmc_metropolis():
    """MCMC Metropolis para estimar nu de Student-t."""
    print("\n" + "=" * 65)
    print("4. MCMC METROPOLIS: ESTIMAR nu DE STUDENT-T")
    print("=" * 65)

    np.random.seed(42)
    # Generar datos con Student-t(4)
    nu_real = 4.0
    datos = 0.01 * np.random.standard_t(nu_real, 500)

    # MCMC para estimar nu
    def log_posterior(nu, datos, mu=0):
        if nu <= 1:
            return -np.inf
        log_prior = stats.expon.logpdf(nu, scale=30)
        log_like = np.sum(stats.t.logpdf(datos, nu, loc=mu, scale=datos.std()))
        return log_prior + log_like

    n_iter = 20000
    burn = 5000
    nu_chain = np.zeros(n_iter)
    nu_chain[0] = 10.0  # Inicio
    accepted = 0

    for i in range(1, n_iter):
        # Propuesta
        nu_prop = nu_chain[i-1] + np.random.normal(0, 1.0)
        if nu_prop <= 1:
            nu_chain[i] = nu_chain[i-1]
            continue

        log_ratio = log_posterior(nu_prop, datos) - log_posterior(nu_chain[i-1], datos)

        if np.log(np.random.random()) < log_ratio:
            nu_chain[i] = nu_prop
            accepted += 1
        else:
            nu_chain[i] = nu_chain[i-1]

    chain_post = nu_chain[burn:]
    rate = accepted / n_iter

    print(f"\n  Datos: 500 retornos ~ Student-t(nu={nu_real})")
    print(f"  MCMC: {n_iter} iteraciones, burn-in {burn}")
    print(f"  Tasa de aceptacion: {rate:.1%}")
    print(f"\n  nu posterior:")
    print(f"    Media:    {chain_post.mean():.2f} (real: {nu_real})")
    print(f"    Mediana:  {np.median(chain_post):.2f}")
    print(f"    HDI 95%:  ({np.percentile(chain_post, 2.5):.2f}, "
          f"{np.percentile(chain_post, 97.5):.2f})")
    print(f"\n  -> MCMC recupera nu ~ {chain_post.mean():.1f} (real = {nu_real})")
    print(f"  -> HDI confirma fat tails (nu << 30 = Normal)")


def demo_resumen():
    """Resumen MLE vs PML."""
    print("\n" + "=" * 65)
    print("5. RESUMEN: MLE vs PML")
    print("=" * 65)
    print("""
  Dimension              MLE / Deep Learning      PML
  -------------------------------------------------------------------
  Prediccion             Punto unico              Distribucion completa
  Incertidumbre          No reporta               Cuantifica siempre
  Datos pequenos         Overfitting severo        Prior regulariza
  Correlaciones          Las encuentra (espurias)  Las pondera
  Causalidad             No distingue              Prior codifica estructura
  Transparencia          Caja negra (DL)           Supuestos explicitos

  Implicaciones para finanzas:
  1. MLE con 5 datos = accidente esperando pasar
  2. Deep learning + 100 features = correlaciones espurias garantizadas
  3. Prediccion sin incertidumbre = decision ciega
  4. PML: no es perfecto, pero es HONESTO sobre lo que no sabe
""")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: MLE vs PML -- PELIGROS DE LA IA CONVENCIONAL")
    print("  Modulo 6")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_mle_vs_pml()
    demo_correlaciones_espurias()
    demo_grid_approximation()
    demo_mcmc_metropolis()
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
