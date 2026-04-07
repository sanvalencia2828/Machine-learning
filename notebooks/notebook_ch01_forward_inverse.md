# Notebook: Chapter 1 — Forward & Inverse Inference
#
# **Objetivo:** Entender la tríada de errores de modelado mediante
# Forward (MCS) e Inverse (MCMC) inference
#
# **Estructura:**
# 1. Introducción conceptual
# 2. Datos sintéticos (tasas de tarjetas de crédito)
# 3. Forward inference (Monte Carlo Simulation)
# 4. Inverse inference (MCMC & Bayes)
# 5. Posterior Predictive Checks
# 6. Ejercicios para estudiantes

# %%
# ## 1. INTRODUCCIÓN — La Tríada de Errores de Modelado
#
# En el capítulo anterior vimos que todo modelo probabilístico adolece de **tres fuentes de error:**
#
# 1. **Specification Error** — Suposición incorrecta sobre la familia de distribuciones (ej: Normal vs Binomial)
# 2. **Parameter Estimation Error** — Estimación imprecisa de parámetros (ej: estimamos ρ=0.8 cuando es 0.5)
# 3. **Non-Stationarity** — Los parámetros cambian con el tiempo (ej: Fed deja de subir tasas)
#
# Este notebook ilustra ambas direcciones de inferencia:
# - **Forward**: Parámetros conocidos → simulamos distribuciones de resultados
# - **Inverse**: Datos observados → recuperamos distribución posterior de parámetros

# %%
# ## 2. IMPORTS & SETUP

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binom, beta
import warnings
warnings.filterwarnings('ignore')

# Configure visualization defaults
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
%matplotlib inline

print("✅ Environment ready for Chapter 1 inference demos")

# %%
# ## 3. FORWARD INFERENCE — Monte Carlo Simulation (MCS)
#
# ### Scenario: Credit Card Rate Distribution
# Sistema bancario decide tasas de tarjetas de crédito basado en decisiones de la Fed.
# 
# **Pregunta:** Si la Fed sube tasas con probabilidad p en cada sesión,
# ¿cuál es la distribución de tasas de tarjetas de crédito al final de 8 sesiones?

def forward_mcs_binomial(
    base_rate=12.0,
    per_hike_bps=25.0,
    fed_meetings=8,
    prob_hike=0.7,
    n_sims=100_000
):
    """Forward simulation: fed hike prob → distribution of CC rates"""
    np.random.seed(42)
    n_hikes = np.random.binomial(fed_meetings, prob_hike, size=n_sims)
    cc_rates = base_rate + (n_hikes * per_hike_bps) / 100.0
    return cc_rates, n_hikes

# Run forward MCS
cc_rates_forward, n_hikes = forward_mcs_binomial(prob_hike=0.7, n_sims=100_000)

print(f"\n📊 Forward MCS Results (p=0.7, n_meetings=8):")
print(f"  Mean rate: {cc_rates_forward.mean():.4f}%")
print(f"  Std dev: {cc_rates_forward.std():.4f}%")
print(f"  Range: [{cc_rates_forward.min():.2f}%, {cc_rates_forward.max():.2f}%]")

# %%
# ### Visualizar Forward Inference

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram of empirical distribution
ax1 = axes[0]
ax1.hist(cc_rates_forward, bins=40, density=True, alpha=0.6, color='steelblue', 
         edgecolor='black', label='MCS Empirical')

# Overlay theoretical Binomial
k = np.arange(0, 9)
pmf = binom.pmf(k, 8, 0.7)
theo_rates = 12.0 + (k * 25.0) / 100.0
ax1.scatter(theo_rates, pmf, color='red', s=150, marker='o', zorder=5, 
            label='Theoretical Binomial', edgecolor='darkred', linewidth=2)

ax1.set_xlabel('Credit Card Rate (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Probability Density', fontsize=12, fontweight='bold')
ax1.set_title('Forward MCS vs Theoretical Distribution', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# CDF comparison
ax2 = axes[1]
sorted_rates = np.sort(cc_rates_forward)
empirical_cdf = np.arange(1, len(sorted_rates) + 1) / len(sorted_rates)
ax2.plot(sorted_rates, empirical_cdf, 'o-', color='steelblue', alpha=0.6, 
         markersize=3, label='Empirical CDF')

theo_cdf = binom.cdf(k, 8, 0.7)
ax2.step(theo_rates, theo_cdf, 'r-', where='mid', linewidth=2.5, 
         label='Theoretical CDF', alpha=0.8)

ax2.set_xlabel('Credit Card Rate (%)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Cumulative Probability', fontsize=12, fontweight='bold')
ax2.set_title('Cumulative Distribution Function', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('notebook_ch01_forward_mcs.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Figure saved: notebook_ch01_forward_mcs.png")

# %%
# ## 4. INVERSE INFERENCE — MCMC (Markov Chain Monte Carlo)
#
# ### Formulación Bayesiana
# Observamos: n_hikes = [3, 5, 2, 6, 4, 7, 5, 3] (8 observaciones del número de subidas)
#
# **Pregunta:** ¿Cuál es la posterior distribution de p (probabilidad de subida)?

# Simulate "observed" data
np.random.seed(42)
observed_n_hikes = np.random.binomial(8, 0.7, size=8)  # 8 observaciones de hikes per 8-week period
print(f"\n🔍 Observed data (number of hikes): {observed_n_hikes}")

# %%
# ### Simple Metropolis-Hastings MCMC

class SimpleMetropolisHastings:
    def __init__(self, seed=42):
        self.seed = seed
        np.random.seed(seed)
    
    def log_likelihood(self, data, n, p):
        """Log likelihood of Binomial model"""
        p = np.clip(p, 1e-10, 1 - 1e-10)
        return (data * np.log(p) + (n - data) * np.log(1 - p)).sum()
    
    def log_prior(self, p, alpha=1.0, beta_p=1.0):
        """Beta prior on p"""
        if p <= 0 or p >= 1:
            return -np.inf
        return (alpha - 1) * np.log(p) + (beta_p - 1) * np.log(1 - p)
    
    def log_posterior(self, data, n, p, alpha=1.0, beta_p=1.0):
        return self.log_likelihood(data, n, p) + self.log_prior(p, alpha, beta_p)
    
    def sample(self, data, n, n_iter=10_000, proposal_std=0.05):
        samples = np.zeros(n_iter)
        p_current = 0.5
        log_post_current = self.log_posterior(data, n, p_current)
        n_accepted = 0
        
        for i in range(n_iter):
            p_proposed = p_current + np.random.normal(0, proposal_std)
            
            if p_proposed <= 0 or p_proposed >= 1:
                samples[i] = p_current
                continue
            
            log_post_proposed = self.log_posterior(data, n, p_proposed)
            log_alpha = log_post_proposed - log_post_current
            
            if np.log(np.random.uniform()) < log_alpha:
                p_current = p_proposed
                log_post_current = log_post_proposed
                n_accepted += 1
            
            samples[i] = p_current
        
        return samples, n_accepted / n_iter

# Run MCMC
sampler = SimpleMetropolisHastings(seed=42)
posterior_samples, acceptance_rate = sampler.sample(
    data=observed_n_hikes,
    n=8,
    n_iter=10_000,
    proposal_std=0.05
)

burnin = 1000
post_burnin = posterior_samples[burnin:]

print(f"\n🎯 MCMC Results:")
print(f"  Acceptance rate: {acceptance_rate:.1%}")
print(f"  Posterior mean: {post_burnin.mean():.4f}")
print(f"  Posterior std: {post_burnin.std():.4f}")
print(f"  95% HPD interval: [{np.percentile(post_burnin, 2.5):.4f}, {np.percentile(post_burnin, 97.5):.4f}]")

# %%
# ### MCMC Diagnostics

fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# Trace plot (full)
axes[0, 0].plot(posterior_samples, linewidth=0.5, alpha=0.7, color='steelblue')
axes[0, 0].axvline(burnin, color='red', linestyle='--', linewidth=2, label=f'Burn-in={burnin}')
axes[0, 0].set_xlabel('Iteration', fontsize=11)
axes[0, 0].set_ylabel('p', fontsize=11)
axes[0, 0].set_title('Trace Plot (Full Chain)', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Trace plot (post burn-in)
axes[0, 1].plot(post_burnin, linewidth=0.5, alpha=0.7, color='steelblue')
axes[0, 1].set_xlabel('Iteration (post burn-in)', fontsize=11)
axes[0, 1].set_ylabel('p', fontsize=11)
axes[0, 1].set_title('Trace Plot (After Burn-in)', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)

# Posterior histogram
axes[1, 0].hist(post_burnin, bins=50, density=True, alpha=0.6, color='steelblue', edgecolor='black')
axes[1, 0].axvline(post_burnin.mean(), color='red', linestyle='--', linewidth=2, 
                   label=f'Mean={post_burnin.mean():.3f}')
axes[1, 0].set_xlabel('p (Fed hike probability)', fontsize=11)
axes[1, 0].set_ylabel('Posterior Density', fontsize=11)
axes[1, 0].set_title('Posterior Distribution of p', fontsize=12, fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Autocorrelation
max_lag = 50
acf_vals = [np.corrcoef(post_burnin[:-lag], post_burnin[lag:])[0,1] for lag in range(1, max_lag+1)]
axes[1, 1].bar(range(1, max_lag+1), acf_vals, color='steelblue', edgecolor='black', alpha=0.7)
axes[1, 1].axhline(0, color='black', linestyle='-', linewidth=0.5)
axes[1, 1].axhline(0.05, color='red', linestyle='--', linewidth=1, label='5% threshold')
axes[1, 1].set_xlabel('Lag', fontsize=11)
axes[1, 1].set_ylabel('Autocorrelation', fontsize=11)
axes[1, 1].set_title('Autocorrelation Function (ACF)', fontsize=12, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('notebook_ch01_mcmc_diagnostics.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Figure saved: notebook_ch01_mcmc_diagnostics.png")

# %%
# ## 5. POSTERIOR PREDICTIVE CHECK (PPC)
#
# ¿Nuestro modelo posterior genera datos similares a lo observado?

print("\n🔬 Posterior Predictive Check:")
print(f"  Observed data: mean={observed_n_hikes.mean():.2f}, std={observed_n_hikes.std():.2f}")

# Generate synthetic data from posterior
np.random.seed(43)
n_ppc = 1000
ppc_samples = np.zeros((len(post_burnin), n_ppc))

for i, p in enumerate(post_burnin):
    ppc_samples[i, :] = np.random.binomial(8, p, size=n_ppc)

ppc_means = ppc_samples.mean(axis=1)
print(f"  PPC distribution: mean={ppc_means.mean():.2f}, std={ppc_means.std():.2f}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(13, 4))

# Histogram
axes[0].hist(observed_n_hikes, bins=range(0, 10), alpha=0.5, label='Observed', 
             color='blue', edgecolor='black', linewidth=1.5)
axes[0].hist(ppc_samples.flatten(), bins=range(0, 10), alpha=0.5, label='PPC', 
             color='red', edgecolor='black', linewidth=1.5)
axes[0].set_xlabel('Number of Hikes', fontsize=11)
axes[0].set_ylabel('Count', fontsize=11)
axes[0].set_title('Posterior Predictive Check — Distribution', fontsize=12, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')

# Mean comparison
axes[1].hist(ppc_means, bins=30, alpha=0.6, color='red', edgecolor='black', label='PPC Mean Dist')
axes[1].axvline(observed_n_hikes.mean(), color='blue', linestyle='--', linewidth=2.5, 
                label=f'Observed Mean={observed_n_hikes.mean():.2f}')
axes[1].set_xlabel('Mean (number of hikes)', fontsize=11)
axes[1].set_ylabel('Frequency', fontsize=11)
axes[1].set_title('Posterior Predictive Check — Mean', fontsize=12, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('notebook_ch01_posterior_predictive.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Figure saved: notebook_ch01_posterior_predictive.png")

# %%
# ## 6. EJERCICIOS PARA ESTUDIANTES

print("\n" + "="*70)
print("EJERCICIOS — Capítulo 1: Forward & Inverse Inference")
print("="*70)

exercises = """
### Ejercicio 1: Sensibilidad Forward
Repite la Forward MCS (Sección 3) con tres valores diferentes de p:
- p = 0.3 (Fed es conservadora)
- p = 0.7 (escenario base)
- p = 0.95 (Fed agresiva)

**PREGUNTA:** ¿Cómo cambian E[rate] y Var[rate]?

### Ejercicio 2: Interpretación de Posterior
Basándote en los resultados MCMC (Sección 4):
- ¿El posterior contiene el valor observado en los datos (mean≈5 hikes)?
- ¿El intervalo 95% HPD es razonable?
- ¿Qué dirías sobre la "information" que aportan 8 observaciones?

### Ejercicio 3: Specification Error
En la Sección 5, el modelo asume Binomial(8, p).
**PREGUNTA:** Si la verdadera distribución fuera Normal (con parámetros equivalentes),
¿cómo se vería afectado el PPC? (Hint: Normal permite valores negativos y reales)

### Ejercicio 4: Non-Stationarity
Supón que el verdadero p cambió a mitad de período:
- Primeras 4 sesiones: p=0.3 (Fed cutting)
- Últimas 4 sesiones: p=0.8 (Fed hiking)

Genera datos bajo este modelo y luego estima con MCMC asumiendo p constante.
**PREGUNTA:** ¿Qué p estima el modelo? ¿Puede el posterior ser bimodal?

### Ejercicio 5: Robustness
Repite el MCMC (Sección 4) con diferentes valores de proposal_std (e.g., 0.01, 0.1, 0.5).
**PREGUNTA:** ¿Cómo afecta al acceptance_rate y a la qualidad del posterior?
"""

print(exercises)

print("\n✅ Notebook complete. All figures saved to working directory.")
