# Capítulo 2: Casos de Estudio Históricos - LTCM y Renaissance
#
# Notebook: LTCM Analysis & Crisis Mechanics
# Source: turn0browsertab744690698
# Last Updated: 2026-03-27

# ## SECCIÓN 1: CONTEXTO HISTÓRICO

# **Long-Term Capital Management (LTCM) - 1994-1998**
#
# Fondo de cobertura fundado por:
# - Myron Scholes (Nobel 1997 - Black-Scholes)
# - Robert Merton (Nobel 1997 - Opción Pricing)
# - John Meriwether (trader legendario de Salomon)
#
# **Retornos:** 40%+ anuales → Crisis 1998 → Necesidad rescate $3.6B

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

print("✅ Chapter 2: LTCM Case Study Ready")

# %%
# ## SECCIÓN 3: LTCM STRATEGY SIMULATION

def ltcm_convergence_trade(
    bond_a_initial_spread=2.5,  # bps, US Treasury
    bond_b_initial_spread=3.0,  # bps, Russian Bond
    position_size=100,
    time_periods=252,
    correlation_normal=0.95,
    correlation_crisis=0.99  # "correlations go to 1 in crisis"
):
    """
    Simula la operación de convergencia de LTCM.
    - Compra: Russian bonds (yield más alto)
    - Vende: US Treasuries (yield menor)
    - Apuesta: spreads convergen
    """
    spreads_a = np.full(time_periods, bond_a_initial_spread)
    spreads_b = np.full(time_periods, bond_b_initial_spread)
    
    # Normal times: spreads convergen
    crisis_start = int(time_periods * 0.7)
    for t in range(1, crisis_start):
        # Convergence: spread se empequeñece 0.01 bps/día
        spreads_a[t] = spreads_a[t-1] + np.random.normal(0, 0.1)
        spreads_b[t] = spreads_b[t-1] - np.random.normal(0, 0.1)
    
    # Crisis: divergencia violenta (flight to quality)
    for t in range(crisis_start, time_periods):
        spreads_a[t] = spreads_a[t-1] - np.random.normal(0, 0.5)
        spreads_b[t] = spreads_b[t-1] + np.random.normal(0, 1.0)  # Russian default risk
    
    # P&L
    pnl = (spreads_a[0] - spreads_a) * position_size  # Long treasury, short (implicit)
    pnl -= (spreads_b[0] - spreads_b) * position_size  # Long Russian
    
    return spreads_a, spreads_b, pnl

spreads_a, spreads_b, pnl = ltcm_convergence_trade()

print("\n💰 LTCM Trade Mechanics:")
print(f"Max Profit (normal): +${np.max(pnl):.0f}M")
print(f"Max Loss (crisis): ${np.min(pnl):.0f}M")

# %%
# ## SECCIÓN 4: CORRELATION BREAKDOWN

def correlation_dynamics(n_assets=10, n_days=252, crisis_day=170):
    """
    Muestra cómo correlaciones "go to 1" durante crisis.
    LTCM apostaba a correlaciones estables pero no lo eran.
    """
    normal_corr = 0.3  # Stable in normal times
    crisis_corr = 0.95   # Everything moves together
    
    years = pd.date_range('2000-01-01', periods=n_days, freq='D')
    corr_matrix = np.full(n_days, normal_corr)
    
    # Smooth transition starting at crisis_day
    for t in range(crisis_day, n_days):
        progress = (t - crisis_day) / (n_days - crisis_day)
        corr_matrix[t] = normal_corr + (crisis_corr - normal_corr) * progress
    
    return years, corr_matrix

years, corr_values = correlation_dynamics()

print("\n📈 Correlation Breakdown:")
print(f"Pre-crisis (mean): {corr_values[:150].mean():.3f}")
print(f"Crisis period (mean): {corr_values[170:].mean():.3f}")

# %%
# ## SECCIÓN 5: LEVERAGE & CAPITAL EROSION

def capital_dynamics_with_leverage(initial_capital=4.7, leverage=25, shock_date=170):
    """
    LTCM usaba leverage de ~25x.
    Pequeñas pérdidas → grandes impactos en capital.
    """
    capital = np.full(252, initial_capital)
    losses = np.random.normal(-0.02, 0.5, size=252)
    
    # Pre-crisis: small, steady gains
    losses[:shock_date] = np.random.normal(0.05, 0.1, size=shock_date)
    
    # Crisis: massive losses
    losses[shock_date:] = np.random.normal(-2.0, 1.5, size=252-shock_date)
    
    for t in range(1, 252):
        loss_impact = losses[t] * leverage  # Leverage amplifies
        capital[t] = capital[t-1] + loss_impact
        if capital[t] < 0.5:  # Forced liquidation threshold
            capital[t:] = capital[t]  # Freeze
    
    return capital, losses

capital, daily_losses = capital_dynamics_with_leverage()

print("\n💔 Capital Erosion:")
print(f"Initial: $4.7B")
print(f"After crisis: ${capital[-1]:.2f}B")
print(f"Loss: ${4.7 - capital[-1]:.2f}B ({(1 - capital[-1]/4.7)*100:.1f}%)")

# %%
# ## SECCIÓN 6: VISUALIZACIÓN DEL COLAPSO

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# P&L del trade
ax = axes[0, 0]
ax.plot(pnl, linewidth=2, label='Convergence Trade P&L')
ax.axvline(170, color='red', linestyle='--', linewidth=2, label='Russian Default')
ax.fill_between(range(len(pnl)), 0, pnl, where=(pnl > 0), alpha=0.3, color='green', label='Profit')
ax.fill_between(range(len(pnl)), 0, pnl, where=(pnl < 0), alpha=0.3, color='red', label='Loss')
ax.set_xlabel('Days')
ax.set_ylabel('P&L ($M)')
ax.set_title('LTCM Convergence Trade - Aug 1998 Crisis')
ax.legend()
ax.grid(alpha=0.3)

# Correlation breakdown
ax = axes[0, 1]
ax.plot(corr_values, linewidth=2, color='darkblue')
ax.axvline(170, color='red', linestyle='--', alpha=0.7)
ax.fill_between(range(len(corr_values)), 0, corr_values, alpha=0.2)
ax.set_xlabel('Days')
ax.set_ylabel('Asset Correlation')
ax.set_ylim([0, 1])
ax.set_title('Correlation Breakdown: "Goes to 1 in Crisis"')
ax.grid(alpha=0.3)

# Capital erosion
ax = axes[1, 0]
ax.plot(capital, linewidth=2.5, color='darkgreen')
ax.axhline(0.5, color='red', linestyle='--', alpha=0.5, label='Liquidation Threshold')
ax.fill_between(range(len(capital)), 0, capital, alpha=0.2, color='green')
ax.set_xlabel('Days')
ax.set_ylabel('Capital ($B)')
ax.set_title('LTCM Capital Dynamics (25x Leverage)')
ax.legend()
ax.grid(alpha=0.3)

# Daily losses
ax = axes[1, 1]
ax.bar(range(len(daily_losses)), daily_losses, width=0.8, alpha=0.6)
ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
ax.axvline(170, color='red', linestyle='--', linewidth=2)
ax.set_xlabel('Days')
ax.set_ylabel('Daily Return (%)')
ax.set_title('Daily P&L - Losses Amplified by Leverage')
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('nb_ch02_ltcm_crisis.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Visualization saved: nb_ch02_ltcm_crisis.png")

# %%
# ## SECCIÓN 7: LECCIONES

print("""
🔑 LECCIONES DE LTCM:

1. **Correlation Stability Assumption**
   ✗ LTCM: "Correlations are stable, diversification is certain"
   ✓ Reality: Correlations jump to 1 during crises
   
2. **Leverage Risk**
   ✗ LTCM: 25x leverage amplified small losses into capital destruction
   ✓ Safe practice: 3-5x leverage with regular stress testing

3. **Model Fragility**
   ✗ Model tuned to "normal" market conditions
   ✓ Test under extreme scenarios BEFORE deployment

4. **Liquidity Assumption**
   ✗ Assumed ability to unwind positions gracefully
   ✓ Liquidity evaporates when you NEED it

5. **Hubris**
   ✗ Nobel laureates = "model is right" = removed risk controls
   ✓ Even brilliant minds can be wrong about markets

""")

# %%
# ## SECCIÓN 8: CONTRAPUNTO - RENAISSANCE TECHNOLOGIES

print("""
✅ RENAISSANCE TECHNOLOGIES (Opposite Approach):

Fundada 1982 por Jim Simons (matemático, criptógrafo)

**Strategy:** Enfoque empírico "data first, theory second"
- Busca patrones estadísticos en datos brutos
- NO asume distribuciones previas
- Holding period corto → menor riesgo de correlación breakdown
- Rigorous backtesting & parameter uncertainty

**Resultado:** 30%+ anuales (post-fees), sin crisis de 1998

**Philosophy:** "Markets are not efficient, but they ARE learnable"

Key Difference: LTCM = Nobel theory
            Renaissance = Empirical pattern recognition
""")

# %%
if __name__ == "__main__":
    print("✅ Capítulo 2 ejecutable. Próximo: Capítulo 3 (Inferencia Bayesiana)")
