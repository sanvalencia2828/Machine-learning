# Capítulo 5: Modelos de Volatilidad Estocástica
#
# Notebook: GARCH, Mean Reversion, Volatility Clustering
# Source: turn0browsertab744690698
# Last Updated: 2026-03-27

# ## SECCIÓN 1: INTRODUCCIÓN

# **Realidades del mercado:**
# 1. Volatilidad NO es constante (rechaza Black-Scholes)
# 2. Volatilidad agrupa: períodos calmos → períodos turbulentos
# 3. Volatilidad sea media-revertida: picos vuelven a normalidad
#
# **Modelos:**
# - GARCH(1,1): Volatilidad depende de choques pasados
# - SV (Stochastic Volatility): Volatilidad es proceso separado
# - Jump diffusions: Permite saltos discretos

# %%
# ## SECCIÓN 2: IMPORTS

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')

print("✅ Chapter 5: Stochastic Volatility Ready")

# %%
# ## SECCIÓN 3: GARCH(1,1) SIMULATION

def garch_11_simulate(
    n_days=1000,
    omega=0.00001,       # Constante de volatilidad base
    alpha=0.05,          # Impacto de shock pasado
    beta=0.94,           # Persistencia de volatilidad
    initial_vol=0.15
):
    """
    GARCH(1,1): σ²_t = ω + α*r²_{t-1} + β*σ²_{t-1}
    
    ω: volatilidad de base
    α: memoria corta (shock actual importa)
    β: persistencia (volatilidad pasada impacta hoy)
    α + β < 1: Volatilidad es estacionaria
    α + β ~ 0.99: Muy persistente
    """
    
    sigma2 = np.zeros(n_days)
    returns = np.zeros(n_days)
    
    sigma2[0] = initial_vol ** 2
    
    for t in range(1, n_days):
        # Innovación
        z_t = np.random.normal(0, 1)
        
        # Retorno
        returns[t] = np.sqrt(sigma2[t-1]) * z_t
        
        # Volatilidad de mañana (GARCH)
        sigma2[t] = omega + alpha * returns[t]**2 + beta * sigma2[t-1]
    
    volatility = np.sqrt(sigma2)
    
    return returns, volatility, sigma2

returns, vol, vol_sq = garch_11_simulate(
    n_days=1000,
    omega=0.00001,
    alpha=0.05,
    beta=0.94
)

print(f"\n📊 GARCH(1,1) Summary:")
print(f"Mean Return: {returns.mean():.6f}")
print(f"Mean Volatility: {vol.mean():.4f}")
print(f"Vol of Vol: {vol.std():.4f}")
print(f"Max Vol: {vol.max():.4f}")
print(f"Min Vol: {vol.min():.4f}")

# %%
# ## SECCIÓN 4: VOLATILITY CLUSTERING

def volatility_clustering_test(returns, window=20):
    """
    Analiza agrupamiento de volatilidad:
    ¿Retornos grandes tienden a ser seguidos por retornos grandes?
    """
    
    abs_returns = np.abs(returns)
    
    # Autocorrelation de |returns|
    acf_values = np.zeros(window)
    mean_abs = abs_returns.mean()
    
    for lag in range(window):
        c0 = np.mean((abs_returns[:-lag or None] - mean_abs) * 
                     (abs_returns[lag:] - mean_abs))
        if lag == 0:
            c0_base = c0
        acf_values[lag] = c0 / c0_base if c0_base != 0 else 0
    
    return acf_values

acf = volatility_clustering_test(returns)

print(f"\n🔗 Volatility Clustering (ACF of |returns|):")
print(f"Lag 1: {acf[1]:.3f}")
print(f"Lag 5: {acf[5]:.3f}")
print(f"Lag 10: {acf[10]:.3f}")
if acf[1] > 0.3:
    print("✅ Strong volatility clustering detected")

# %%
# ## SECCIÓN 5: MEAN REVERSION TEST

def half_life_mean_reversion(volatility, window=20):
    """
    Calcula half-life de volatilidad.
    ¿Cuánto tarda la volatilidad en revertir a media?
    
    Fórmula: HL = ln(2) / (-log(β) del AR(1))
    """
    
    vol_demeaned = volatility - volatility.mean()
    
    # AR(1) regression
    X = vol_demeaned[:-1]
    y = vol_demeaned[1:]
    
    beta_ar = np.cov(X, y)[0, 1] / np.var(X)
    
    if beta_ar >= 1 or beta_ar <= 0:
        hl = np.inf
    else:
        hl = np.log(2) / (-np.log(beta_ar))
    
    return hl, beta_ar

hl, beta_ar = half_life_mean_reversion(vol)

print(f"\n⏱️  Mean Reversion Dynamics:")
print(f"AR(1) coefficient: {beta_ar:.4f}")
print(f"Half-life (days): {hl:.1f}")
if hl < 100:
    print(f"✅ Volatilidad revierte a media en aprox {hl:.0f} días")
else:
    print("⚠️  Volatilidad es muy persistente (weak mean reversion)")

# %%
# ## SECCIÓN 6: LEVERAGE EFFECT

def leverage_effect(returns, volatility, window=20):
    """
    Leverage effect (assymetric volatilidad):
    ¿Shocks negativos causan mayor incremento de volatilidad?
    """
    
    correlations = []
    for t in range(window, len(returns)):
        returns_window = returns[t-window:t]
        vol_change = (volatility[t] - volatility[t-window]) / volatility[t-window]
        corr = np.corrcoef(returns_window, [vol_change]*window)[0, 1]
        correlations.append(corr)
    
    return np.array(correlations)

lev_effect = leverage_effect(returns, vol)

print(f"\n⚡ Leverage Effect:")
print(f"Mean Leverage Effect: {lev_effect.mean():.3f}")
if lev_effect.mean() < -0.2:
    print("✅ Fuerte leverage effect: retornos negativos → volatilidad aumenta más")
else:
    print("ℹ️  Leverage effect débil")

# %%
# ## SECCIÓN 7: VISUALIZACIÓN

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Returns y Volatilidad
ax = axes[0, 0]
ax2 = ax.twinx()
ax.plot(returns, alpha=0.5, linewidth=0.5, label='Returns', color='blue')
ax2.plot(vol, alpha=0.7, linewidth=1.5, label='Volatility', color='red')
ax.set_xlabel('Days')
ax.set_ylabel('Returns', color='blue')
ax2.set_ylabel('Volatility', color='red')
ax.set_title('GARCH(1,1): Returns & Volatility Over Time')
ax.grid(alpha=0.3)

# Volatility Clustering (ACF)
ax = axes[0, 1]
ax.bar(range(len(acf)), acf, alpha=0.6, edgecolor='black')
ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('Lag (days)')
ax.set_ylabel('Autocorrelation')
ax.set_title('Volatility Clustering: ACF of |Returns|')
ax.grid(alpha=0.3, axis='y')

# Distribution of Returns (vs Normal)
ax = axes[1, 0]
ax.hist(returns, bins=50, density=True, alpha=0.6, label='Observed', edgecolor='black')
x_range = np.linspace(returns.min(), returns.max(), 100)
ax.plot(x_range, norm.pdf(x_range, returns.mean(), returns.std()), 
        'r-', linewidth=2, label='Normal Distribution')
ax.set_xlabel('Returns')
ax.set_ylabel('Density')
ax.set_title('Return Distribution vs Normal (GARCH features fatter tails)')
ax.legend()
ax.grid(alpha=0.3, axis='y')

# Volatility vs Lagged Returns
ax = axes[1, 1]
scatter = ax.scatter(returns[:-1], vol[1:] - vol[:-1], alpha=0.3, s=20)
ax.axvline(0, color='red', linestyle='--', alpha=0.5)
ax.set_xlabel('Lagged Returns')
ax.set_ylabel('Change in Volatility')
ax.set_title('Leverage Effect: Negative Returns → Volatility Spikes')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('nb_ch05_volatility.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Visualization saved: nb_ch05_volatility.png")

# %%
# ## SECCIÓN 8: APLICACIÓN - OPCIÓN PRICING

def garch_option_price_simulation(S0=100, K=100, T=1, r=0.05, n_paths=5000):
    """
    Usa GARCH para generar paths, luego valúa opción.
    Resultado: precio diferente a Black-Scholes (que asume vol constante).
    """
    
    dt = 1/252
    n_steps = int(T * 252)
    
    paths = np.zeros((n_paths, n_steps + 1))
    paths[:, 0] = S0
    
    for path in range(n_paths):
        sigma2 = 0.15 ** 2
        for step in range(n_steps):
            z = np.random.normal(0, 1)
            sigma = np.sqrt(sigma2)
            paths[path, step + 1] = paths[path, step] * np.exp(
                (r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z
            )
            # GARCH update
            sigma2 = 0.00001 + 0.05*((paths[path, step+1] - paths[path, step])/paths[path, step])**2 + 0.94*sigma2
    
    payoffs = np.maximum(paths[:, -1] - K, 0)
    price = np.mean(payoffs) * np.exp(-r * T)
    
    return price

garch_call_price = garch_option_price_simulation()

print(f"\n💰 Option Pricing with GARCH:")
print(f"GARCH Call Price (S₀=100, K=100, T=1y): ${garch_call_price:.2f}")
print(f"(Compare to Black-Scholes with constant vol)")

# %%
if __name__ == "__main__":
    print("✅ Capítulo 5 ejecutable. Próximo: Capítulo 6 (Tail Risks)")
