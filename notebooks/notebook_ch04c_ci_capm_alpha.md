# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .md
#       format_name: markdown
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Modulo 4C: Intervalos de Confianza, CAPM y la Trampa de Alpha
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Estimar alpha y beta de un activo con OLS (Statsmodels) e interpretar sus IC
# 2. Distinguir IC del parametro vs IC de la prediccion y sus limitaciones
# 3. Demostrar los 3 errores de interpretacion de intervalos de confianza
# 4. Comparar IC frecuentista vs intervalo credible bayesiano
# 5. Aplicar diagnosticos para validar si los IC son confiables

# %% [markdown]
# ---
# ## 1. Setup

# %%
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
plt.rcParams.update({
    'figure.figsize': (10, 6), 'font.size': 12,
    'axes.grid': True, 'grid.alpha': 0.3,
})

try:
    import statsmodels.api as sm
    HAS_SM = True
    print(f"Statsmodels: {sm.__version__}")
except ImportError:
    HAS_SM = False
    print("Statsmodels no disponible. Usando OLS manual.")

# %% [markdown]
# ---
# ## 2. Generar Retornos Sinteticos AAPL vs SPY

# %%
def generar_aapl_spy(n=504, alpha_real=0.0002, beta_real=1.25,
                      sigma_mkt=0.012, sigma_eps=0.010, nu=4, seed=42):
    """Genera retornos sinteticos tipo AAPL vs SPY (2 anos).

    Parametros
    ----------
    n : int
        Dias de trading.
    alpha_real : float
        Alpha real diario del activo.
    beta_real : float
        Beta real vs mercado.
    sigma_mkt : float
        Vol diaria del mercado.
    sigma_eps : float
        Vol idiosincratica.
    nu : float
        Grados de libertad (fat tails).

    Retorna
    -------
    tuple : (r_spy, r_aapl)
    """
    np.random.seed(seed)
    r_spy = 0.0003 + sigma_mkt * np.random.standard_t(nu, n)
    epsilon = sigma_eps * np.random.standard_t(nu, n)
    r_aapl = alpha_real + beta_real * r_spy + epsilon
    return r_spy, r_aapl


r_spy, r_aapl = generar_aapl_spy()
print(f"Datos: {len(r_spy)} dias (~2 anos)")
print(f"SPY:  media={r_spy.mean()*252:.1%}/ano, vol={r_spy.std()*np.sqrt(252):.1%}")
print(f"AAPL: media={r_aapl.mean()*252:.1%}/ano, vol={r_aapl.std()*np.sqrt(252):.1%}")

# %% [markdown]
# ---
# ## 3. OLS con Statsmodels

# %%
if HAS_SM:
    X = sm.add_constant(r_spy)
    modelo = sm.OLS(r_aapl, X).fit()
    print(modelo.summary())
else:
    # OLS manual
    X = np.column_stack([np.ones(len(r_spy)), r_spy])
    b = np.linalg.lstsq(X, r_aapl, rcond=None)[0]
    res = r_aapl - X @ b
    n, k = len(r_aapl), 2
    mse = np.sum(res**2) / (n - k)
    se = np.sqrt(mse * np.diag(np.linalg.inv(X.T @ X)))
    t_stat = b / se
    p_vals = 2 * (1 - stats.t.cdf(np.abs(t_stat), n - k))
    ci_lo = b - 1.96 * se
    ci_hi = b + 1.96 * se

    print(f"\n  {'Param':<8} {'Coef':<12} {'SE':<10} {'t':<8} {'p':<10} {'IC 95%'}")
    print(f"  {'-'*60}")
    print(f"  {'alpha':<8} {b[0]:<12.6f} {se[0]:<10.6f} {t_stat[0]:<8.3f} "
          f"{p_vals[0]:<10.4f} ({ci_lo[0]:.6f}, {ci_hi[0]:.6f})")
    print(f"  {'beta':<8} {b[1]:<12.4f} {se[1]:<10.4f} {t_stat[1]:<8.3f} "
          f"{p_vals[1]:<10.2e} ({ci_lo[1]:.4f}, {ci_hi[1]:.4f})")

# %% [markdown]
# ### Extraer IC de alpha y beta

# %%
if HAS_SM:
    ci = modelo.conf_int(alpha=0.05)
    alpha_est = modelo.params[0]
    beta_est = modelo.params[1]
    alpha_ci = ci.iloc[0].values
    beta_ci = ci.iloc[1].values
    alpha_p = modelo.pvalues[0]
    beta_p = modelo.pvalues[1]
else:
    alpha_est, beta_est = b[0], b[1]
    alpha_ci = [ci_lo[0], ci_hi[0]]
    beta_ci = [ci_lo[1], ci_hi[1]]
    alpha_p, beta_p = p_vals[0], p_vals[1]

print(f"=== ESTIMACIONES CON IC 95% ===\n")
print(f"  Alpha: {alpha_est:.6f}  IC: ({alpha_ci[0]:.6f}, {alpha_ci[1]:.6f})")
print(f"    Incluye 0? {'SI' if alpha_ci[0] <= 0 <= alpha_ci[1] else 'NO'}")
print(f"    p-value: {alpha_p:.4f}")
print(f"    Ancho IC: {alpha_ci[1]-alpha_ci[0]:.6f} "
      f"(vs alpha={abs(alpha_est):.6f}, ratio={abs(alpha_ci[1]-alpha_ci[0])/max(abs(alpha_est),1e-10):.1f}x)")
print(f"\n  Beta: {beta_est:.4f}  IC: ({beta_ci[0]:.4f}, {beta_ci[1]:.4f})")
print(f"    Incluye 0? {'SI' if beta_ci[0] <= 0 <= beta_ci[1] else 'NO'}")
print(f"    p-value: {beta_p:.2e}")
print(f"    Ancho IC: {beta_ci[1]-beta_ci[0]:.4f}")

# %% [markdown]
# ---
# ## 4. IC del Parametro vs IC de la Prediccion

# %%
x_plot = np.linspace(r_spy.min(), r_spy.max(), 200)

if HAS_SM:
    X_pred = sm.add_constant(x_plot)
    pred = modelo.get_prediction(X_pred)
    ci_mean = pred.conf_int(alpha=0.05)  # IC del parametro (media)
    ci_obs = pred.conf_int(obs=True, alpha=0.05)  # IC de prediccion
    y_pred = pred.predicted_mean
else:
    y_pred = b[0] + b[1] * x_plot
    se_pred = np.sqrt(mse * (1/n + (x_plot - r_spy.mean())**2 / np.sum((r_spy - r_spy.mean())**2)))
    ci_mean = np.column_stack([y_pred - 1.96*se_pred, y_pred + 1.96*se_pred])
    se_obs = np.sqrt(mse + se_pred**2)
    ci_obs = np.column_stack([y_pred - 1.96*se_obs, y_pred + 1.96*se_obs])

fig, ax = plt.subplots(figsize=(12, 7))
ax.scatter(r_spy * 100, r_aapl * 100, s=8, alpha=0.3, color='gray', label='Datos')
ax.plot(x_plot * 100, y_pred * 100, 'orangered', lw=2, label='OLS fit')
ax.fill_between(x_plot * 100, ci_mean[:, 0] * 100, ci_mean[:, 1] * 100,
                alpha=0.3, color='orangered', label='IC parametro 95%')
ax.fill_between(x_plot * 100, ci_obs[:, 0] * 100, ci_obs[:, 1] * 100,
                alpha=0.1, color='steelblue', label='IC prediccion 95%')
ax.set_xlabel('Retorno SPY (%)')
ax.set_ylabel('Retorno AAPL (%)')
ax.set_title('IC del Parametro (estrecho) vs IC de Prediccion (ancho)', fontsize=13)
ax.legend(fontsize=10)
plt.tight_layout()
plt.show()

ancho_param = (ci_mean[:, 1] - ci_mean[:, 0]).mean() * 100
ancho_pred = (ci_obs[:, 1] - ci_obs[:, 0]).mean() * 100
print(f"Ancho medio IC parametro: {ancho_param:.2f}%")
print(f"Ancho medio IC prediccion: {ancho_pred:.2f}%")
print(f"Ratio: prediccion es {ancho_pred/ancho_param:.0f}x mas ancho que parametro")
print(f"\n-> El IC de prediccion es tan ancho que es practicamente inutil")

# %% [markdown]
# ---
# ## 5. Los 3 Errores de Interpretacion de IC

# %%
def demo_cobertura_ic(mu_real=0.05, sigma=0.20, n_obs=10,
                       n_rep=10000, alpha=0.05, seed=42):
    """Simula la cobertura real de IC 95%."""
    np.random.seed(seed)
    contiene = 0
    intervalos = []

    for _ in range(n_rep):
        datos = np.random.normal(mu_real, sigma, n_obs)
        mu_hat = datos.mean()
        se = datos.std(ddof=1) / np.sqrt(n_obs)
        t_crit = stats.t.ppf(1 - alpha/2, n_obs - 1)
        lo = mu_hat - t_crit * se
        hi = mu_hat + t_crit * se
        intervalos.append((lo, hi))
        if lo <= mu_real <= hi:
            contiene += 1

    cobertura = contiene / n_rep
    return cobertura, intervalos


cobertura, intervalos = demo_cobertura_ic()

print("=== DEMO: COBERTURA DE IC 95% ===\n")
print(f"  Parametro real: mu = 5%")
print(f"  Muestra: n = 10 retornos anuales (sigma = 20%)")
print(f"  Repeticiones: 10,000")
print(f"  Cobertura empirica: {cobertura:.1%} (teorica: 95%)")

# Mostrar 10 intervalos aleatorios
print(f"\n  10 intervalos de ejemplo (mu_real = 0.05):")
np.random.seed(99)
idx = np.random.choice(len(intervalos), 10, replace=False)
for i in idx:
    lo, hi = intervalos[i]
    contiene_str = "OK" if lo <= 0.05 <= hi else "FALLA"
    print(f"    ({lo:>+.3f}, {hi:>+.3f})  {contiene_str}")

print(f"""
  ERROR 1: "95% de prob de que mu este en (0.02, 0.12)"
    -> FALSO. mu es fijo. El IC es aleatorio.

  ERROR 2: "Si el IC no incluye 0, alpha es significativo"
    -> Equivale a NHST. Mismos problemas de base rate.

  ERROR 3: "El IC mide mi incertidumbre sobre mu"
    -> Solo mide precision muestral, no incorpora priors.
""")

# %% [markdown]
# ---
# ## 6. IC Frecuentista vs Intervalo Credible Bayesiano

# %%
def comparar_ic_bayesiano(r_spy, r_aapl, prior_alpha_mu=0.0,
                           prior_alpha_sigma=0.0005):
    """Compara IC frecuentista vs intervalo credible para alpha.

    Bayesiano simplificado: conjugado Normal-Normal para alpha.
    """
    n = len(r_aapl)
    # Frecuentista
    X = np.column_stack([np.ones(n), r_spy])
    b = np.linalg.lstsq(X, r_aapl, rcond=None)[0]
    res = r_aapl - X @ b
    mse = np.sum(res**2) / (n - 2)
    se_alpha = np.sqrt(mse * np.linalg.inv(X.T @ X)[0, 0])
    freq_ci = (b[0] - 1.96 * se_alpha, b[0] + 1.96 * se_alpha)

    # Bayesiano (Normal-Normal conjugado para alpha)
    tau_prior = 1 / prior_alpha_sigma**2
    tau_data = 1 / se_alpha**2
    tau_post = tau_prior + tau_data
    mu_post = (tau_prior * prior_alpha_mu + tau_data * b[0]) / tau_post
    sigma_post = 1 / np.sqrt(tau_post)
    bayes_hdi = (mu_post - 1.96 * sigma_post, mu_post + 1.96 * sigma_post)

    return {
        "alpha_mle": b[0], "se": se_alpha,
        "freq_ci": freq_ci, "freq_ancho": freq_ci[1] - freq_ci[0],
        "mu_post": mu_post, "sigma_post": sigma_post,
        "bayes_hdi": bayes_hdi, "bayes_ancho": bayes_hdi[1] - bayes_hdi[0],
        "p_alpha_pos_bayes": 1 - stats.norm.cdf(0, mu_post, sigma_post),
    }


comp = comparar_ic_bayesiano(r_spy, r_aapl)

print("=== IC FRECUENTISTA vs INTERVALO CREDIBLE BAYESIANO ===\n")
print(f"  Prior bayesiano: alpha ~ N(0, {0.0005:.4f})")
print(f"  (esceptico: alpha probablemente cercano a 0)\n")

print(f"  {'Metrica':<30} {'Frecuentista':<25} {'Bayesiano'}")
print(f"  {'-'*65}")
print(f"  {'Alpha estimado':<30} {comp['alpha_mle']:<25.6f} {comp['mu_post']:.6f}")
print(f"  {'Intervalo 95%':<30} ({comp['freq_ci'][0]:.6f}, {comp['freq_ci'][1]:.6f})"
      f"  ({comp['bayes_hdi'][0]:.6f}, {comp['bayes_hdi'][1]:.6f})")
print(f"  {'Ancho':<30} {comp['freq_ancho']:<25.6f} {comp['bayes_ancho']:.6f}")
print(f"  {'P(alpha > 0)':<30} {'No calculable':<25} {comp['p_alpha_pos_bayes']:.1%}")

print(f"\n  -> El prior encoge alpha hacia 0 (escepticismo razonable)")
print(f"  -> El bayesiano responde directamente: P(alpha > 0) = {comp['p_alpha_pos_bayes']:.0%}")
print(f"  -> El frecuentista NO puede responder esa pregunta")

# %% [markdown]
# ---
# ## 7. Resumen
#
# | Concepto | IC Frecuentista | Intervalo Credible |
# |----------|----------------|-------------------|
# | Interpretacion | Cobertura repetida | P(param en intervalo) |
# | Incorpora prior | No | Si |
# | Responde P(alpha>0) | No | Si |
# | Con pocos datos | Muy ancho | Prior lo acota |
#
# ### La trampa de alpha
# 1. Alpha real es probablemente ~0 (eficiencia de mercado)
# 2. IC frecuentista es demasiado ancho para detectar alphas pequenos
# 3. IC de prediccion es aun peor (inutil en la practica)
# 4. Multiple testing infla falsos positivos
# 5. El intervalo credible con prior esceptico es mas honesto
#
# ---
# *source_ref: turn0browsertab744690698*
