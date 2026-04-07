# Capítulo 6: Riesgos de Cola y Eventos Extremos
#
# Notebook: Extreme Value Theory, Copulas, Tail Risk Metrics
# Source: turn0browsertab744690698
# Last Updated: 2026-03-27

# ## SECCIÓN 1: INTRODUCCIÓN

# **Black Swan problem:**
# Retornos financieros tienen colas más gordas que la distribución Normal.
# Eventos que la Normal predice cada 100,000 años ocurren cada 10 años.
#
# Soluciones:
# - Extreme Value Theory (EVT)
# - Copulas (modelar dependencia de colas)
# - Risk metrics (CVaR, ES)

# %%
# ## SECCIÓN 2: IMPORTS

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm, t, gumbel_r, pareto
import warnings
warnings.filterwarnings('ignore')

%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')

print("✅ Chapter 6: Tail Risks Ready")

# %%
# ## SECCIÓN 3: DISTRIBUCIONES CON COLAS GORDAS

def generate_tail_data(n_samples=10000, tail_weight=3):
    """
    Genera datos con colas gordas:
    - tail_weight=2: muy gordo (Pareto)
    - tail_weight=3: moderado (t-student)
    - tail_weight=∞: delgado (Normal)
    """
    
    if tail_weight == 'normal':
        data = np.random.normal(0, 1, n_samples)
    elif tail_weight == 'pareto':
        data = np.random.pareto(1.5, n_samples)
    else:
        # Student-t distribution
        data = np.random.standard_t(tail_weight, n_samples)
    
    return data

normal_returns = np.random.normal(0, 1, 10000)
fat_tail_returns = np.random.standard_t(3, 10000)  # df=3

print(f"\n📊 Tail Comparison:")
print(f"Normal - Kurtosis: {3 + 0} (by definition)")
print(f"Fat-tail - Kurtosis: {(fat_tail_returns**4).mean() / (fat_tail_returns.std()**4):.2f}")
print(f"Normal - 5-sigma events: {(np.abs(normal_returns) > 5).sum()}")
print(f"Fat-tail - 5-sigma events: {(np.abs(fat_tail_returns) > 5).sum()}")

# %%
# ## SECCIÓN 4: EXTREME VALUE THEORY (EVT)

def gumbel_fit_maxima(data, n_bins=10):
    """
    Extreme Value Theory: Gumbel distribution
    Modela máximos (o mínimos) de bloques.
    
    Aplicación: ¿Cuál es la peor pérdida esperada en el próximo mes?
    """
    
    # Block maxima (mensual si data es diaria)
    n_blocks = len(data) // n_bins
    blocks = []
    for i in range(n_blocks):
        block_max = np.max(np.abs(data[i*n_bins:(i+1)*n_bins]))
        blocks.append(block_max)
    
    blocks = np.array(blocks)
    
    # Fit Gumbel parameters
    # Using method of moments
    mean_blocks = blocks.mean()
    std_blocks = blocks.std()
    
    # Gumbel parameters
    beta = std_blocks * np.sqrt(6) / np.pi
    mu = mean_blocks - beta * 0.5772  # Euler-Mascheroni constant
    
    return blocks, mu, beta

blocks, mu_gumbel, beta_gumbel = gumbel_fit_maxima(fat_tail_returns)

print(f"\n🎯 Extreme Value Theory (Gumbel):")
print(f"Location (μ): {mu_gumbel:.3f}")
print(f"Scale (β): {beta_gumbel:.3f}")

# Predict 1-year maximum (12 blocks of monthly data)
x_predict = np.arange(0, 10, 0.1)
gumbel_cdf = np.exp(-np.exp(-(x_predict - mu_gumbel) / beta_gumbel))
year_cdf = gumbel_cdf ** 12  # Max of 12 months

max_expected_1y = mu_gumbel + beta_gumbel * (np.log(12) - np.log(-np.log(0.95)))
print(f"Expected 1-year max (95% conf): {max_expected_1y:.2f}σ")

# %%
# ## SECCIÓN 5: COPULAS PARA DEPENDENCIA DE COLAS

def clayton_copula_sample(n_samples=1000, theta=2.0):
    """
    Clayton copula: modela dependencia de colas bajas.
    Usado para correlación durante crisis.
    """
    
    u1 = np.random.uniform(0, 1, n_samples)
    u2 = np.random.uniform(0, 1, n_samples)
    
    # Clayton copula
    v = u2 ** (-theta) * (u1 ** (-theta) - 1 + 1)
    v = np.minimum(v, 1)  # Clip a [0,1]
    
    return u1, v

u1, v = clayton_copula_sample(n_samples=5000, theta=2.0)

# Convert to returns
returns_asset1 = norm.ppf(u1)
returns_asset2 = norm.ppf(v)

tail_correlation = np.corrcoef(returns_asset1[returns_asset1 < -1], 
                               returns_asset2[returns_asset2 < -1])[0, 1]

print(f"\n🔗 Clayton Copula (Tail Dependence):")
print(f"Overall correlation: {np.corrcoef(returns_asset1, returns_asset2)[0, 1]:.3f}")
print(f"Lower tail correlation (< -1σ): {tail_correlation:.3f}")
print("⚠️  Tail dependence increases during crises")

# %%
# ## SECCIÓN 6: CONDITIONAL VALUE AT RISK (CVaR)

def cvar_metrics(returns, confidence=0.95):
    """
    CVaR (Conditional VaR): Pérdida promedio si excedate VaR.
    Mejor que VaR porque considera severidad de excepciones.
    """
    
    var = np.percentile(returns, (1 - confidence) * 100)
    exceeds = returns[returns < var]
    
    if len(exceeds) > 0:
        cvar = exceeds.mean()
    else:
        cvar = var
    
    return {
        'var': var,
        'cvar': cvar,
        'n_exceeds': len(exceeds),
        'exceeds_pct': len(exceeds) / len(returns) * 100,
        'severity': cvar / var if var != 0 else 0
    }

cvar_normal = cvar_metrics(normal_returns, confidence=0.95)
cvar_fat = cvar_metrics(fat_tail_returns, confidence=0.95)

print(f"\n⚠️  Value at Risk Metrics (95% confidence):")
print(f"\nNormal Distribution:")
print(f"  VaR: {cvar_normal['var']:.3f}")
print(f"  CVaR: {cvar_normal['cvar']:.3f}")
print(f"  Severity (CVaR/VaR): {cvar_normal['severity']:.2f}x")
print(f"\nFat-tail Distribution:")
print(f"  VaR: {cvar_fat['var']:.3f}")
print(f"  CVaR: {cvar_fat['cvar']:.3f}")
print(f"  Severity (CVaR/VaR): {cvar_fat['severity']:.2f}x")

# %%
# ## SECCIÓN 7: VISUALIZACIÓN

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Normal vs Fat-tail distributions
ax = axes[0, 0]
bins = np.linspace(-8, 8, 100)
ax.hist(normal_returns, bins=bins, density=True, alpha=0.5, label='Normal', edgecolor='black')
ax.hist(fat_tail_returns, bins=bins, density=True, alpha=0.5, label='Fat-tail (t)', edgecolor='black')
x_range = np.linspace(-8, 8, 1000)
ax.plot(x_range, norm.pdf(x_range), 'b-', linewidth=2, label='Normal PDF')
ax.set_xlabel('Returns')
ax.set_ylabel('Density')
ax.set_title('Normal vs Fat-tail Distribution')
ax.set_yscale('log')
ax.legend()
ax.grid(alpha=0.3)

# Q-Q plot
ax = axes[0, 1]
sorted_normal = np.sort(normal_returns)
sorted_fat = np.sort(fat_tail_returns)
quantiles = np.linspace(0.01, 0.99, len(sorted_normal))
ax.scatter(norm.ppf(quantiles), np.percentile(fat_tail_returns, quantiles*100), 
          alpha=0.5, s=10)
ax.plot(sorted_normal, sorted_normal, 'r-', linewidth=2, label='Normal')
ax.set_xlabel('Normal Quantiles')
ax.set_ylabel('Fat-tail Quantiles')
ax.set_title('Q-Q Plot: Deviations in Tails')
ax.legend()
ax.grid(alpha=0.3)

# Copula scatter
ax = axes[1, 0]
ax.scatter(u1, v, alpha=0.3, s=10)
ax.set_xlabel('Asset 1')
ax.set_ylabel('Asset 2')
ax.set_title('Clayton Copula: Tail Concentration')
ax.grid(alpha=0.3)

# Block Maxima (Gumbel)
ax = axes[1, 1]
ax.hist(blocks, bins=15, density=True, alpha=0.6, label='Block Maxima', edgecolor='black')
x_gumbel = np.linspace(0, 5, 1000)
gumbel_pdf = (1/beta_gumbel) * np.exp(-(x_gumbel - mu_gumbel)/beta_gumbel) * \
             np.exp(-np.exp(-(x_gumbel - mu_gumbel)/beta_gumbel))
ax.plot(x_gumbel, gumbel_pdf, 'r-', linewidth=2, label='Gumbel Fit')
ax.set_xlabel('Block Maximum (Monthly)')
ax.set_ylabel('Density')
ax.set_title('Extreme Value Theory: Block Maxima')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('nb_ch06_tail_risks.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Visualization saved: nb_ch06_tail_risks.png")

# %%
# ## SECCIÓN 8: LECCIONES

print("""
🔑 TAIL RISK MANAGEMENT:

1. **Test for Fat Tails**
   ✓ Plot histogram + log scale
   ✓ Check kurtosis > 3
   ✓ Q-Q plot shows deviations in tails
   
2. **Use Appropriate Model**
   ✗ Never assume Normal for financial returns
   ✓ Student-t, Pareto, or mixture models
   ✓ Extreme Value Theory for worst-case scenarios
   
3. **Dependency During Crises**
   ✗ Correlation is not stable
   ✓ Use copulas to model tail dependence
   ✓ Diversification breaks down when needed most
   
4. **Risk Metrics**
   ✗ VaR only (doesn't capture severity)
   ✓ Use CVaR (exceeds VaR)
   ✓ Also report: min loss, expected shortfall
   
5. **Stress Testing**
   ✓ Scenario: 2008-style crash
   ✓ Scenario: Liquidity crisis
   ✓ Scenario: Correlation = 1 across assets
   
6. **Portfolio Protection**
   ✓ Out-of-money puts
   ✓ Tail hedges (VIX futures)
   ✓ Diversification into uncorrelated assets
""")

# %%
if __name__ == "__main__":
    print("✅ Capítulo 6 ejecutable. Próximo: Capítulo 7 (ML en Finanzas)")
