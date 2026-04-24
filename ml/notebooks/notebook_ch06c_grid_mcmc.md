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
# # Modulo 6C: Grid Approximation, Markov Chains y MCMC Metropolis
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Implementar grid approximation y entender por que no escala
# 2. Simular Markov chains de estados de mercado (bear/bull/stagnant)
# 3. Implementar MCMC Metropolis desde cero para muestrear posteriors
# 4. Estimar grados de libertad (nu) de Student-t con MCMC
# 5. Evaluar diagnosticos de cadenas: trace plots, aceptacion, Rhat

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
print("Entorno listo.")

# %% [markdown]
# ---
# ## 2. Grid Approximation: Funciona Pero No Escala

# %%
def grid_approximation(k, n, alpha_prior=2, beta_prior=2, n_grid=1000):
    """Grid approximation para Beta-Binomial.

    Parametros
    ----------
    k : int
        Exitos observados.
    n : int
        Intentos totales.
    alpha_prior, beta_prior : float
        Parametros del prior Beta.
    n_grid : int
        Numero de puntos en la grilla.

    Retorna
    -------
    tuple : (theta_grid, posterior_grid)
    """
    theta = np.linspace(0.001, 0.999, n_grid)
    prior = stats.beta.pdf(theta, alpha_prior, beta_prior)
    likelihood = stats.binom.pmf(k, n, theta)
    posterior_raw = prior * likelihood
    delta = theta[1] - theta[0]
    posterior = posterior_raw / (posterior_raw.sum() * delta)
    return theta, posterior


# Caso ZYX: 7 beats en 8 trimestres
theta_grid, post_grid = grid_approximation(k=7, n=8)
post_analitico = stats.beta(2+7, 2+1)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(theta_grid * 100, post_grid, 'orangered', lw=2, label='Grid approx (1000 pts)')
ax.plot(theta_grid * 100, post_analitico.pdf(theta_grid), 'steelblue', ls='--', lw=2,
        label='Analitico Beta(9,3)')
ax.set_xlabel('P(beat) %')
ax.set_ylabel('Densidad')
ax.set_title('Grid Approximation: converge al resultado exacto', fontsize=13)
ax.legend()
plt.tight_layout()
plt.show()

# Maldicion de la dimensionalidad
print("=== MALDICION DE LA DIMENSIONALIDAD ===\n")
for dims in [1, 2, 3, 5, 10]:
    evals = 100**dims
    print(f"  {dims} parametro(s): {evals:>20,} evaluaciones"
          f"{'  <- factible' if evals < 1e6 else '  <- IMPOSIBLE' if evals > 1e9 else '  <- lento'}")

# %% [markdown]
# ---
# ## 3. Markov Chains: Estados de Mercado

# %%
def simular_markov_mercado(n_pasos=1000, seed=42):
    """Simula Markov chain con 3 estados de mercado.

    Estados: 0=Bear, 1=Stagnant, 2=Bull
    """
    np.random.seed(seed)
    estados = ["Bear", "Stagnant", "Bull"]
    # Matriz de transicion
    T = np.array([
        [0.6, 0.3, 0.1],   # Desde Bear
        [0.2, 0.5, 0.3],   # Desde Stagnant
        [0.1, 0.3, 0.6],   # Desde Bull
    ])

    cadena = np.zeros(n_pasos, dtype=int)
    cadena[0] = 1  # Empieza en Stagnant

    for t in range(1, n_pasos):
        cadena[t] = np.random.choice(3, p=T[cadena[t-1]])

    # Frecuencias observadas vs estacionarias
    freq_obs = np.bincount(cadena, minlength=3) / n_pasos

    # Distribucion estacionaria: eigenvector de T^T con eigenvalue=1
    eigenvalues, eigenvectors = np.linalg.eig(T.T)
    idx = np.argmin(np.abs(eigenvalues - 1))
    estacionaria = np.abs(eigenvectors[:, idx])
    estacionaria /= estacionaria.sum()

    return cadena, estados, T, freq_obs, estacionaria


cadena, estados, T, freq_obs, estacionaria = simular_markov_mercado()

print("=== MARKOV CHAIN: ESTADOS DE MERCADO ===\n")
print("  Matriz de transicion:")
print(f"  {'':>12} {'Bear':>8} {'Stagnant':>10} {'Bull':>8}")
for i, nombre in enumerate(estados):
    print(f"  {nombre:>12}", end="")
    for j in range(3):
        print(f" {T[i,j]:>8.1%}", end="")
    print()

print(f"\n  {'Estado':<12} {'Frecuencia obs':<18} {'Estacionaria':<15}")
print(f"  {'-'*45}")
for i, nombre in enumerate(estados):
    print(f"  {nombre:<12} {freq_obs[i]:<18.1%} {estacionaria[i]:.1%}")

# %%
# Visualizar la cadena
fig, axes = plt.subplots(2, 1, figsize=(14, 7))

# Trace de estados
colores_estado = {0: '#e74c3c', 1: '#f39c12', 2: '#2ecc71'}
for t in range(len(cadena) - 1):
    axes[0].plot([t, t+1], [cadena[t], cadena[t+1]],
                 color=colores_estado[cadena[t]], lw=0.5, alpha=0.7)
axes[0].set_yticks([0, 1, 2])
axes[0].set_yticklabels(estados)
axes[0].set_title('Markov Chain: trayectoria de estados de mercado', fontsize=13)
axes[0].set_xlabel('Paso')

# Convergencia a estacionaria
window = 50
for i, (nombre, color) in enumerate(zip(estados, ['#e74c3c', '#f39c12', '#2ecc71'])):
    freq_acum = np.cumsum(cadena == i) / np.arange(1, len(cadena) + 1)
    axes[1].plot(freq_acum, color=color, lw=1.5, label=f'{nombre} (est={estacionaria[i]:.1%})')
    axes[1].axhline(estacionaria[i], color=color, ls=':', alpha=0.5)

axes[1].set_title('Convergencia a distribucion estacionaria', fontsize=13)
axes[1].set_xlabel('Paso')
axes[1].set_ylabel('Frecuencia acumulada')
axes[1].legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 4. MCMC Metropolis: Muestrear el Posterior de nu

# %%
def metropolis_student_t(datos, n_iter=30000, burn=5000, sigma_prop=0.8, seed=42):
    """MCMC Metropolis para estimar nu de una Student-t.

    Parametros
    ----------
    datos : array
        Retornos observados.
    n_iter : int
        Iteraciones totales.
    burn : int
        Burn-in (muestras descartadas).
    sigma_prop : float
        Std de la propuesta Random Walk.
    seed : int
        Semilla.

    Retorna
    -------
    dict con cadena, tasa de aceptacion, posterior.
    """
    np.random.seed(seed)
    mu_datos = np.median(datos)
    scale_datos = np.median(np.abs(datos - mu_datos)) * 1.4826  # MAD estimator

    def log_posterior(nu):
        if nu <= 2:
            return -np.inf
        log_prior = stats.expon.logpdf(nu, scale=30)
        log_like = np.sum(stats.t.logpdf(datos, nu, loc=mu_datos, scale=scale_datos))
        return log_prior + log_like

    chain = np.zeros(n_iter)
    chain[0] = 10.0
    accepted = 0

    for i in range(1, n_iter):
        propuesta = chain[i-1] + np.random.normal(0, sigma_prop)
        if propuesta <= 2:
            chain[i] = chain[i-1]
            continue
        log_ratio = log_posterior(propuesta) - log_posterior(chain[i-1])
        if np.log(np.random.random()) < log_ratio:
            chain[i] = propuesta
            accepted += 1
        else:
            chain[i] = chain[i-1]

    posterior = chain[burn:]
    return {
        "chain": chain, "posterior": posterior,
        "acceptance_rate": accepted / n_iter,
        "mean": posterior.mean(), "median": np.median(posterior),
        "hdi": (np.percentile(posterior, 2.5), np.percentile(posterior, 97.5)),
    }


# Generar datos con fat tails
np.random.seed(42)
nu_real = 4.0
retornos = 0.012 * np.random.standard_t(nu_real, 500)

result = metropolis_student_t(retornos)

print("=== MCMC METROPOLIS: ESTIMAR nu DE STUDENT-T ===\n")
print(f"  Datos: 500 retornos ~ Student-t(nu={nu_real})")
print(f"  Iteraciones: 30,000 (burn-in: 5,000)")
print(f"  Tasa aceptacion: {result['acceptance_rate']:.1%}")
print(f"\n  nu posterior:")
print(f"    Media:   {result['mean']:.2f}")
print(f"    Mediana: {result['median']:.2f}")
print(f"    HDI 95%: ({result['hdi'][0]:.2f}, {result['hdi'][1]:.2f})")
print(f"    Real:    {nu_real}")

# %%
# Diagnosticos visuales
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# Trace plot
axes[0, 0].plot(result['chain'], lw=0.3, color='steelblue', alpha=0.7)
axes[0, 0].axhline(nu_real, color='red', ls='--', lw=1.5, label=f'Real: nu={nu_real}')
axes[0, 0].axvline(5000, color='orange', ls=':', label='Burn-in')
axes[0, 0].set_title('Trace Plot')
axes[0, 0].set_ylabel('nu')
axes[0, 0].legend(fontsize=9)

# Histograma posterior
axes[0, 1].hist(result['posterior'], bins=50, density=True, alpha=0.6, color='orangered')
axes[0, 1].axvline(nu_real, color='red', ls='--', lw=2, label=f'Real: {nu_real}')
axes[0, 1].axvline(result['mean'], color='steelblue', ls='--', lw=2,
                    label=f'Media: {result["mean"]:.1f}')
axes[0, 1].set_title('Posterior de nu')
axes[0, 1].legend(fontsize=9)

# Autocorrelacion
from numpy import correlate as np_corr
post = result['posterior']
post_centered = post - post.mean()
acf = np.correlate(post_centered, post_centered, mode='full')
acf = acf[len(acf)//2:]
acf /= acf[0]
axes[1, 0].bar(range(min(50, len(acf))), acf[:50], color='steelblue', alpha=0.7)
axes[1, 0].set_title('Autocorrelacion (primeros 50 lags)')
axes[1, 0].set_xlabel('Lag')
axes[1, 0].axhline(0, color='gray')

# Normal vs Student-t ajustada
x_range = np.linspace(-0.08, 0.08, 300)
axes[1, 1].hist(retornos, bins=50, density=True, alpha=0.3, color='gray', label='Datos')
axes[1, 1].plot(x_range, stats.norm.pdf(x_range, retornos.mean(), retornos.std()),
                'steelblue', ls='--', lw=2, label='Normal')
nu_est = result['median']
axes[1, 1].plot(x_range, stats.t.pdf(x_range, nu_est, retornos.mean(),
                np.median(np.abs(retornos - np.median(retornos))) * 1.4826),
                'orangered', lw=2, label=f'Student-t(nu={nu_est:.1f})')
axes[1, 1].set_title('Ajuste: Normal vs Student-t estimada')
axes[1, 1].legend(fontsize=9)

plt.suptitle('MCMC Metropolis: Diagnosticos', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 5. De Metropolis a HMC (Hamiltonian Monte Carlo)
#
# Metropolis funciona pero es lento para muchos parametros.
# HMC usa el **gradiente** del log-posterior para proponer
# saltos mas inteligentes. Es lo que PyMC usa internamente.
#
# | Propiedad | Metropolis | HMC |
# |-----------|-----------|-----|
# | Propuesta | Random walk | Usa gradiente |
# | Eficiencia | Baja (muchos rechazos) | Alta (pocos rechazos) |
# | Parametros | < 10 practico | Miles |
# | Autocorrelacion | Alta | Baja |
# | Implementacion | Simple (20 lineas) | Compleja (usa PyMC/Stan) |
#
# En Modulo 7 usaremos PyMC que implementa NUTS (HMC adaptativo).

# %% [markdown]
# ---
# ## 6. Resumen
#
# | Metodo | Cuando usar | Limitacion |
# |--------|------------|------------|
# | **Conjugados** | Modelo simple (Beta-Binomial) | Solo modelos con conjugados |
# | **Grid** | 1-2 parametros, cualquier modelo | No escala a 3+ params |
# | **Metropolis** | 1-10 parametros | Lento, alta autocorrelacion |
# | **HMC/NUTS** | 10-1000+ parametros | Requiere gradientes (PyMC) |
#
# ### Takeaways
# 1. Grid es exacto pero no escala por la maldicion de dimensionalidad
# 2. Markov chains convergen a distribuciones estacionarias (propiedad clave de MCMC)
# 3. Metropolis explora el posterior sin calcular P(datos) explicitamente
# 4. Diagnosticos (trace, aceptacion, autocorrelacion) son OBLIGATORIOS
# 5. HMC/NUTS (PyMC) es Metropolis con esteroides: usa gradientes
#
# ---
# *source_ref: turn0browsertab744690698*
