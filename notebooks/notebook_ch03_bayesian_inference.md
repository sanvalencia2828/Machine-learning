# Capítulo 3: Inferencia Bayesiana y MCMC
#
# Notebook: Bayesian Inference with PyMC Chains
# Source: turn0browsertab744690698
# Last Updated: 2026-03-27

# ## SECCIÓN 1: INTRODUCCIÓN

# **Enfoque Bayesiano vs Frecuentista**
#
# Frecuentista: "Parámetro es fijo, datos son variable"
# Bayesiano: "Parámetro es variable (distribución), datos son observados"
#
# **Aplicación Financiera:**
# ¿Cuál es la tasa de default de una cartera de bonos?
# Frecuentista: estimador puntual → varianza de bootstrap
# Bayesiano: distribución posterior + incertidumbre cuantificada

# %%
# ## SECCIÓN 2: IMPORTS

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import beta, norm, binom
import warnings
warnings.filterwarnings('ignore')

try:
    import pymc as pm
    import arviz as az
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    print("⚠️  PyMC not installed. Using scipy distributions instead.")

%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')

print("✅ Chapter 3: Bayesian Inference Ready")

# %%
# ## SECCIÓN 3: MODELO BETA-BINOMIAL

def beta_binomial_model(observed_defaults=3, observed_total=50, alpha_prior=1, beta_prior=1):
    """
    Modelo simple: default rate de bonos corporativos.
    
    Prior: Beta(alpha, beta) - uniforme si alpha=beta=1
    Likelihood: Binomial
    Posterior: Beta (conjugate!)
    """
    
    # Prior
    alpha_post = alpha_prior + observed_defaults
    beta_post = beta_prior + (observed_total - observed_defaults)
    
    # Posterior distribution
    x = np.linspace(0, 1, 1000)
    prior_pdf = beta.pdf(x, alpha_prior, beta_prior)
    posterior_pdf = beta.pdf(x, alpha_post, beta_post)
    likelihood_scaled = binom.pmf(observed_defaults, observed_total, x) * 100
    
    return {
        'x': x,
        'prior': prior_pdf,
        'posterior': posterior_pdf,
        'likelihood': likelihood_scaled,
        'alpha_post': alpha_post,
        'beta_post': beta_post,
        'posterior_mean': alpha_post / (alpha_post + beta_post),
        'posterior_std': np.sqrt((alpha_post * beta_post) / 
                                ((alpha_post + beta_post)**2 * (alpha_post + beta_post + 1)))
    }

model_results = beta_binomial_model(observed_defaults=3, observed_total=50)

print("\n📊 Beta-Binomial Model:")
print(f"Observed: {3}/{50} defaults")
print(f"Prior: Beta(1,1) [uniform]")
print(f"Posterior Mean: {model_results['posterior_mean']:.4f}")
print(f"Posterior Std: {model_results['posterior_std']:.4f}")
print(f"95% Credible Interval: [{model_results['alpha_post']/(model_results['alpha_post']+model_results['beta_post'])-1.96*model_results['posterior_std']:.4f}, "
      f"{model_results['alpha_post']/(model_results['alpha_post']+model_results['beta_post'])+1.96*model_results['posterior_std']:.4f}]")

# %%
# ## SECCIÓN 4: MARKOV CHAIN MONTE CARLO (MCMC)

def metropolis_hastings_mcmc(
    observed_data,
    n_iterations=10000,
    proposal_std=0.05,
    prior_mean=0.5,
    prior_std=0.2
):
    """
    Algoritmo Metropolis-Hastings para simular la posterior.
    
    Usado cuando no hay forma conjugada (mayoría de problemas reales).
    """
    
    chain = np.zeros(n_iterations)
    chain[0] = np.random.uniform(0, 1)
    
    n_defaults = observed_data.sum()
    n_total = len(observed_data)
    
    accepted = 0
    
    for t in range(1, n_iterations):
        current = chain[t-1]
        
        # Proposal: normal random walk
        proposal = current + np.random.normal(0, proposal_std)
        
        if proposal < 0 or proposal > 1:
            chain[t] = current
            continue
        
        # Log-likelihood
        ll_current = np.sum(np.log(binom.pmf(observed_data, 1, current) + 1e-10))
        ll_proposal = np.sum(np.log(binom.pmf(observed_data, 1, proposal) + 1e-10))
        
        # Log-prior
        lp_current = norm.logpdf(current, prior_mean, prior_std)
        lp_proposal = norm.logpdf(proposal, prior_mean, prior_std)
        
        # MH ratio
        log_ratio = (ll_proposal + lp_proposal) - (ll_current + lp_current)
        
        if np.log(np.random.uniform(0, 1)) < log_ratio:
            chain[t] = proposal
            accepted += 1
        else:
            chain[t] = current
    
    acceptance_rate = accepted / n_iterations
    return chain, acceptance_rate

# Simulate 50 Bernoulli trials (bond defaults)
observed = np.random.binomial(1, 0.05, 50)  # 5% true rate
chain, acc_rate = metropolis_hastings_mcmc(observed)

# Burn-in
burn_in = 2000
chain_burned = chain[burn_in:]

print(f"\n🔗 MCMC Results:")
print(f"Acceptance Rate: {acc_rate:.2%}")
print(f"Posterior Mean (MCMC): {chain_burned.mean():.4f}")
print(f"Posterior Std (MCMC): {chain_burned.std():.4f}")

# %%
# ## SECCIÓN 5: POSTERIOR PREDICTIVE CHECK (PPC)

def posterior_predictive_check(chain, observed_data, n_samples=1000):
    """
    ¿El modelo genera datos similares a lo observado?
    Compara estadísticos observados vs. generados por posterior.
    """
    
    n_total = len(observed_data)
    observed_mean = observed_data.mean()
    
    ppc_samples = []
    for p_sample in np.random.choice(chain, n_samples):
        ppc = np.random.binomial(1, p_sample, n_total).mean()
        ppc_samples.append(ppc)
    
    ppc_samples = np.array(ppc_samples)
    
    return {
        'observed_mean': observed_mean,
        'ppc_mean': ppc_samples.mean(),
        'ppc_samples': ppc_samples,
        'p_value': (ppc_samples > observed_mean + 2*observed_data.std()).mean()
    }

ppc_result = posterior_predictive_check(chain_burned, observed)

print(f"\n🎯 Posterior Predictive Check:")
print(f"Observed Default Rate: {ppc_result['observed_mean']:.4f}")
print(f"PPC Mean: {ppc_result['ppc_mean']:.4f}")
print(f"Model Fit (p-value): {ppc_result['p_value']:.3f}")
if ppc_result['p_value'] > 0.05:
    print("✅ Model fits data reasonably well")
else:
    print("⚠️  Model may be misspecified")

# %%
# ## SECCIÓN 6: VISUALIZACIÓN

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Prior vs Posterior
ax = axes[0, 0]
ax.fill_between(model_results['x'], model_results['prior'], alpha=0.3, label='Prior')
ax.fill_between(model_results['x'], model_results['posterior'], alpha=0.5, label='Posterior')
ax.set_xlabel('Default Rate')
ax.set_ylabel('Density')
ax.set_title('Beta-Binomial Model: Prior vs Posterior')
ax.legend()
ax.grid(alpha=0.3)

# MCMC Trace Plot
ax = axes[0, 1]
ax.plot(chain[:1000], alpha=0.7, linewidth=0.5)
ax.axvline(burn_in, color='red', linestyle='--', label='Burn-in')
ax.set_xlabel('Iteration')
ax.set_ylabel('Default Rate')
ax.set_title('MCMC Trace (First 1000 Iterations)')
ax.legend()
ax.grid(alpha=0.3)

# Posterior Distribution (MCMC)
ax = axes[1, 0]
ax.hist(chain_burned, bins=50, density=True, alpha=0.6, edgecolor='black')
ax.axvline(chain_burned.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {chain_burned.mean():.3f}')
ax.set_xlabel('Default Rate')
ax.set_ylabel('Density')
ax.set_title('Posterior Distribution (MCMC)')
ax.legend()
ax.grid(alpha=0.3, axis='y')

# Posterior Predictive Check
ax = axes[1, 1]
ax.hist(ppc_result['ppc_samples'], bins=30, alpha=0.6, label='Posterior Predictive', edgecolor='black')
ax.axvline(ppc_result['observed_mean'], color='red', linestyle='--', linewidth=2.5, label='Observed')
ax.set_xlabel('Default Rate')
ax.set_ylabel('Frequency')
ax.set_title('Posterior Predictive Check')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('nb_ch03_bayesian_mcmc.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Visualization saved: nb_ch03_bayesian_mcmc.png")

# %%
# ## SECCIÓN 7: CONVERGENCE DIAGNOSTICS

def gelman_rubin_rhat(chains_list, var_name="parameter"):
    """
    Rhat diagnostic: ¿Han convergido múltiples cadenas?
    Rhat ~ 1.0 → Convergida
    Rhat > 1.1 → Convergencia dudosa
    """
    m = len(chains_list)  # número de cadenas
    n = len(chains_list[0])  # largura de cada cadena
    
    chain_means = np.array([chain.mean() for chain in chains_list])
    grand_mean = chain_means.mean()
    
    B = (n / (m - 1)) * np.sum((chain_means - grand_mean)**2)
    
    within_var = np.mean([np.var(chain, ddof=1) for chain in chains_list])
    
    var_plus = ((n - 1) / n) * within_var + (1 / n) * B
    
    rhat = np.sqrt(var_plus / within_var)
    
    return rhat

# Run 4 MCMC chains
chains = []
for _ in range(4):
    chain_i, _ = metropolis_hastings_mcmc(observed, n_iterations=5000)
    chains.append(chain_i[2000:])  # Burn-in

rhat = gelman_rubin_rhat(chains)

print(f"\n🩺 Convergence Diagnostics:")
print(f"Rhat: {rhat:.4f}")
if rhat < 1.05:
    print("✅ Chains have converged well")
elif rhat < 1.1:
    print("⚠️  Borderline convergence. Run more iterations.")
else:
    print("❌ Chains have NOT converged. Check model specification.")

# %%
# ## SECCIÓN 8: INTERPRETACIÓN

print("""
📈 INTERPRETACIÓN BAYESIANA (Default Rate):

1. **Prior:** Creencia inicial sobre tasa de default
   - Vago (Beta 1,1): No asumimos nada a priori
   - Informativo (Beta 1,10): Levemente pesimista (~10% default)

2. **Likelihood:** Datos observados (3 defaults en 50 bonos)
   - Actualiza nuestra creencia
   
3. **Posterior:** Síntesis Prior + Likelihood
   - Media: 6% (vs 6% empírico)
   - Desviación: ±2% (cuantifica incertidumbre)
   
4. **Uso Práctico:**
   ✓ Precio de bonos con incertidumbre
   ✓ Reserva para pérdidas esperadas
   ✓ Decisión de cobertura
   
5. **vs Frecuentista:**
   Frecuentista: "Default rate = 6% (con intervalo de confianza 95%)"
               Pero ¿qué significa? ¿Se repite el experimento infinitas veces?
   
   Bayesiano: "Default rate ~ N(6%, 2%). Probabilidad que exceda 10% = 2.3%"
             Más directo para decisiones.
""")

# %%
if __name__ == "__main__":
    print("✅ Capítulo 3 ejecutable. Próximo: Capítulo 4 (Monte Carlo)")
