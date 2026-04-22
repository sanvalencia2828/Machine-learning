# Capítulo 4: Simulación Monte Carlo
#
# Notebook: Portfolio Valuation & Path Simulation
# Source: turn0browsertab744690698
# Last Updated: 2026-03-27

# ## SECCIÓN 1: INTRODUCCIÓN

# **Monte Carlo simulation** es el caballo de batalla para valoración.
# Aplicación: Valuación de bonos con opciones, carteras complejas, derivados.
#
# Proceso:
# 1. Defina dinámica de activos (SDE - Stochastic Differential Equation)
# 2. Discretice el SDE (Euler, Milstein)
# 3. Genere N trayectorias
# 4. Compute payoff en vencimiento
# 5. E[payoff] = precio

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

print("✅ Chapter 4: Monte Carlo Simulation Ready")

# %%
# ## SECCIÓN 3: MOVIMIENTO BROWNIANO GEOMÉTRICO

def gbm_paths(
    S0=100,           # Precio inicial
    mu=0.08,          # Drift (rendimiento esperado)
    sigma=0.20,       # Volatilidad
    T=1.0,            # Tiempo a vencimiento (años)
    n_steps=252,      # Pasos por año (trading days)
    n_paths=1000      # Número de simulaciones
):
    """
    Geometric Brownian Motion (GBM):
    dS = μ*S*dt + σ*S*dW
    
    Solución: S_t = S_0 * exp((μ - σ²/2)*t + σ*W_t)
    """
    
    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)
    
    # Matriz de incrementos Brownianos
    dW = np.random.normal(0, np.sqrt(dt), size=(n_paths, n_steps))
    
    # Paths
    paths = np.zeros((n_paths, n_steps + 1))
    paths[:, 0] = S0
    
    for i in range(n_steps):
        paths[:, i+1] = paths[:, i] * np.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * dW[:, i]
        )
    
    return t, paths

# Simular 10 años de precio de acción
t, paths = gbm_paths(S0=100, mu=0.10, sigma=0.25, T=10, n_steps=2520, n_paths=1000)

print(f"\n📈 GBM Simulation Summary:")
print(f"Initial Price: ${paths[:, 0].mean():.2f}")
print(f"Final Price (mean): ${paths[:, -1].mean():.2f}")
print(f"Final Price (5th percentile): ${np.percentile(paths[:, -1], 5):.2f}")
print(f"Final Price (95th percentile): ${np.percentile(paths[:, -1], 95):.2f}")

# %%
# ## SECCIÓN 4: VALUACIÓN DE OPCIÓN CALL

def black_scholes_call(S, K, T, r, sigma):
    """
    Fórmula cerrada Black-Scholes.
    Comparativa con Monte Carlo.
    """
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    call_price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    return call_price

def monte_carlo_call(paths, K, T, r, discount=True):
    """
    Valuación de call por Monte Carlo.
    payoff = max(S_T - K, 0)
    """
    S_T = paths[:, -1]
    payoffs = np.maximum(S_T - K, 0)
    
    if discount:
        price = np.mean(payoffs) * np.exp(-r * T)
    else:
        price = np.mean(payoffs)
    
    return price, payoffs

K = 120  # Strike
r = 0.05  # Risk-free rate

bs_price = black_scholes_call(S=100, K=K, T=10, r=r, sigma=0.25)
mc_price, payoffs = monte_carlo_call(paths, K=K, T=10, r=r)

print(f"\n📊 Call Option Valuation (S₀=100, K=120, T=10y, r=5%, σ=25%):")
print(f"Black-Scholes: ${bs_price:.2f}")
print(f"Monte Carlo: ${mc_price:.2f}")
print(f"Difference: ${abs(bs_price - mc_price):.2f}")

# %%
# ## SECCIÓN 5: VALOR EN RIESGO (VaR) POR MONTE CARLO

def var_monte_carlo(paths, portfolio_value=1000000, confidence=0.95):
    """
    Value at Risk: Pérdida máxima esperada con confianza C.
    
    Uso: Preguntar: ¿Cuánto puedo perder en 1 día con 95% confianza?
    """
    
    returns = (paths[:, -1] - paths[:, 0]) / paths[:, 0]
    losses = -returns * portfolio_value
    
    var = np.percentile(losses, confidence * 100)
    
    return {
        'var': var,
        'cvar': losses[losses > var].mean(),
        'min_loss': losses.min(),
        'max_loss': losses.max(),
        'mean_loss': losses.mean(),
        'std_loss': losses.std()
    }

var_result = var_monte_carlo(paths, portfolio_value=1000000, confidence=0.95)

print(f"\n⚠️  Value at Risk Summary (95% confidence, 1-year):")
print(f"VaR: ${var_result['var']:,.0f}")
print(f"CVaR (Conditional VaR, avg loss if exceed VaR): ${var_result['cvar']:,.0f}")
print(f"Min Loss: ${var_result['min_loss']:,.0f}")
print(f"Max Loss: ${var_result['max_loss']:,.0f}")

# %%
# ## SECCIÓN 6: CONVERGENCIA DE MONTE CARLO

def monte_carlo_convergence(S0=100, K=120, T=1, r=0.05, sigma=0.25, n_simulations_max=10000):
    """
    ¿Cuántas simulaciones necesito para convergencia?
    Más simulaciones = menor error estándar
    """
    
    estimates = []
    n_sims = np.logspace(1, 4, 30).astype(int)
    
    for n in n_sims:
        t_temp, paths_temp = gbm_paths(S0, mu=r, sigma=sigma, T=T, n_steps=100, n_paths=n)
        mc_temp, _ = monte_carlo_call(paths_temp, K, T, r)
        estimates.append(mc_temp)
    
    bs_true = black_scholes_call(S0, K, T, r, sigma)
    errors = np.abs(np.array(estimates) - bs_true)
    
    return n_sims, estimates, errors, bs_true

n_sims, estimates, errors, bs_true = monte_carlo_convergence()

print(f"\n🔄 Monte Carlo Convergence:")
print(f"BS True Price: ${bs_true:.2f}")
print(f"100 simulations error: ${errors[0]:.3f}")
print(f"10,000 simulations error: ${errors[-1]:.3f}")
print(f"Error reduction: {errors[0]/errors[-1]:.1f}x")

# %%
# ## SECCIÓN 7: VISUALIZACIÓN

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Sample paths
ax = axes[0, 0]
ax.plot(t, paths[:100, :].T, alpha=0.3, linewidth=0.5)
ax.set_xlabel('Time (years)')
ax.set_ylabel('Price ($)')
ax.set_title('GBM Sample Paths (100 of 1000)')
ax.grid(alpha=0.3)

# Distribution of final prices
ax = axes[0, 1]
ax.hist(paths[:, -1], bins=50, density=True, alpha=0.6, edgecolor='black')
ax.axvline(np.mean(paths[:, -1]), color='red', linestyle='--', linewidth=2, label='Mean')
ax.axvline(np.percentile(paths[:, -1], 5), color='orange', linestyle='--', label='5th %ile')
ax.axvline(np.percentile(paths[:, -1], 95), color='orange', linestyle='--', label='95th %ile')
ax.set_xlabel('Price ($)')
ax.set_ylabel('Density')
ax.set_title('Distribution of Final Prices')
ax.legend()
ax.grid(alpha=0.3, axis='y')

# Convergence
ax = axes[1, 0]
ax.loglog(n_sims, errors, 'o-', linewidth=2, markersize=6)
ax.loglog(n_sims, 1/np.sqrt(n_sims) * max(errors), '--', alpha=0.5, label='1/√N')
ax.set_xlabel('Number of Simulations')
ax.set_ylabel('|Error|')
ax.set_title('Monte Carlo Convergence')
ax.legend()
ax.grid(alpha=0.3)

# Call payoff distribution
ax = axes[1, 1]
ax.hist(payoffs, bins=50, alpha=0.6, edgecolor='black')
ax.axvline(np.mean(payoffs), color='red', linestyle='--', linewidth=2, label=f'Mean: ${np.mean(payoffs):.2f}')
ax.set_xlabel('Call Payoff ($)')
ax.set_ylabel('Frequency')
ax.set_title('Call Option Payoff Distribution at Maturity')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('nb_ch04_monte_carlo.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Visualization saved: nb_ch04_monte_carlo.png")

# %%
# ## SECCIÓN 8: DECISIÓN PRÁCTICO

print("""
💡 MONTE CARLO EN PRÁCTICA:

✅ Cuándo usar:
- Derivados con payoff complejo
- Carteras con múltiples activos correlacionados
- Opciones multi-periodo
- Volatilidad estocástica
- Jump diffusions

❌ Cuándo NO usar:
- Black-Scholes aplicable (hay fórmula cerrada)
- Necesita baja latencia (muy lento)
- Datos insuficientes para calibración

⚡ Tips de Implementación:
1. Discretización: Euler OK para mayoría; Milstein para volatilidad local
2. Correlación: Use Cholesky decomposition para múltiples activos
3. Antithetic variates: Reduce varianza sin más simulaciones
4. Quasi-random: Sobol/Halton converge más rápido que random
5. Variance reduction: Importance sampling, stratified sampling

""")

# %%
if __name__ == "__main__":
    print("✅ Capítulo 4 ejecutable. Próximo: Capítulo 5 (Volatilidad Estocástica)")
