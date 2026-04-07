# Capítulo 8: Stress Testing y Regulación
#
# Notebook: VaR, Expected Shortfall, Regulatory Scenarios
# Source: turn0browsertab744690698
# Last Updated: 2026-03-27

# ## SECCIÓN 1: INTRODUCCIÓN

# **Stress testing** es mandatorio post-2008.
# Preguntas:
# - ¿Qué pasa si el S&P500 cae 20%?
# - ¿Qué pasa si tasas suben 200 bps?
# - ¿Qué pasa si las corelaciones van a 1?
#
# Reguladores (Fed, ECB, BIS) requieren:
# - Stress scenarios
# - Capital adequacy ratios
# - Liquidity coverage ratios

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

print("✅ Chapter 8: Stress Testing and Regulation Ready")

# %%
# ## SECCIÓN 3: VALUE AT RISK (VaR)

def var_parametric(returns, confidence=0.95):
    """
    VaR paramétrico: asume returns ~ N(μ, σ²)
    
    VaR(95%) = -1.645*σ + μ  (para percentil inferior)
    """
    
    mu = returns.mean()
    sigma = returns.std()
    
    # Normal quantile
    z_score = norm.ppf(1 - confidence)
    
    var = mu + z_score * sigma
    
    return var

def var_historical(returns, confidence=0.95):
    """
    VaR histórico: usa distribución empírica.
    No asume normalidad.
    """
    
    return np.percentile(returns, (1 - confidence) * 100)

def cvar_historical(returns, confidence=0.95):
    """
    CVaR (Expected Shortfall): promedio de pérdidas > VaR.
    """
    
    var = var_historical(returns, confidence)
    exceeds = returns[returns < var]
    
    return exceeds.mean() if len(exceeds) > 0 else var

# Simular retornos
returns_normal = np.random.normal(0, 0.01, 1000)  # 1% daily vol
returns_crisis = np.concatenate([
    np.random.normal(0, 0.01, 950),
    np.random.normal(-0.05, 0.03, 50)  # 5% crisis days
])

var_99_normal_param = var_parametric(returns_normal, confidence=0.99)
var_99_normal_hist = var_historical(returns_normal, confidence=0.99)
var_99_crisis_hist = var_historical(returns_crisis, confidence=0.99)
cvar_99_crisis = cvar_historical(returns_crisis, confidence=0.99)

print(f"\n📊 Value at Risk Analysis:")
print(f"\nNormal Market Conditions:")
print(f"  Parametric VaR(99%): {var_99_normal_param:.4f} ({var_99_normal_param*100:.2f}%)")
print(f"  Historical VaR(99%): {var_99_normal_hist:.4f} ({var_99_normal_hist*100:.2f}%)")
print(f"\nDuring Crisis (with crisis days):")
print(f"  Historical VaR(99%): {var_99_crisis_hist:.4f} ({var_99_crisis_hist*100:.2f}%)")
print(f"  CVaR(99%): {cvar_99_crisis:.4f} ({cvar_99_crisis*100:.2f}%)")

# %%
# ## SECCIÓN 4: REGULATORY STRESS SCENARIOS

def fed_stress_scenario(portfolio_composition, rate_shock_bps=200):
    """
    Escenario de estrés de la Fed:
    - Interest rates suben 200 bps (típico Fed scenario)
    - Volatilidade increases 25%
    - Credit spreads widen 100 bps
    """
    
    # Portfolio composition
    duration = portfolio_composition.get('duration', 5)  # años
    equity_beta = portfolio_composition.get('equity_beta', 1.0)
    credit_spread = portfolio_composition.get('credit_spread', 100)  # bps
    
    # Shocks
    rate_shock = rate_shock_bps / 10000
    
    # Bond P&L (duration rule)
    bond_pnl = -duration * rate_shock  # -100 bps rate shock → -5% bond price
    
    # Equity P&L (lower growth)
    equity_pnl = -equity_beta * 0.20  # 20% stock market decline
    
    # Credit spread P&L
    spread_pnl = -credit_spread / 10000 * 5  # 5 years, 100 bps widening
    
    return {
        'bond_pnl': bond_pnl,
        'equity_pnl': equity_pnl,
        'credit_pnl': spread_pnl,
        'total_pnl': bond_pnl + equity_pnl + spread_pnl
    }

# Example portfolio: 50% bonds (duration 5), 40% equities (beta 1), 10% credit
portfolio = {'duration': 5, 'equity_beta': 1.0, 'credit_spread': 100}
stress_result = fed_stress_scenario(portfolio, rate_shock_bps=200)

print(f"\n🏦 Fed Stress Scenario (Rates +200 bps):")
print(f"Bond Impact: {stress_result['bond_pnl']*100:.2f}%")
print(f"Equity Impact: {stress_result['equity_pnl']*100:.2f}%")
print(f"Credit Impact: {stress_result['credit_pnl']*100:.2f}%")
print(f"Total Portfolio Impact: {stress_result['total_pnl']*100:.2f}%")

# %%
# ## SECCIÓN 5: REVERSE STRESS TESTING

def reverse_stress_test(initial_capital=10000000, loss_threshold=0.20):
    """
    Reverse stress testing: ¿Qué eventos causarían 20% loss?
    Usado para identificar vulnerabilidades.
    """
    
    scenarios = {
        'Market Crash (-30%)': {'prob': 0.05, 'impact': -0.30},
        'Rate Shock (+300 bps)': {'prob': 0.02, 'impact': -0.15},
        'Credit Crisis': {'prob': 0.03, 'impact': -0.25},
        'Liquidity Crisis': {'prob': 0.01, 'impact': -0.40},
        'Correlation → 1': {'prob': 0.04, 'impact': -0.20},
    }
    
    results = {}
    for scenario, details in scenarios.items():
        loss = initial_capital * details['impact']
        results[scenario] = {
            'loss': loss,
            'probability': details['prob'],
            'expected_loss': loss * details['prob']
        }
    
    return results

capital = 10_000_000
reverse_stress = reverse_stress_test(capital, loss_threshold=0.20)

print(f"\n⚠️  Reverse Stress Test (Starting Capital: ${capital:,.0f}):")
print(f"{'Scenario':<25} {'Loss':<15} {'Prob':<10} {'Expected':<15}")
print("-" * 65)
for scenario, details in reverse_stress.items():
    print(f"{scenario:<25} ${details['loss']:>12,.0f} {details['probability']:>9.1%} ${details['expected_loss']:>13,.0f}")

total_expected_loss = sum(d['expected_loss'] for d in reverse_stress.values())
print(f"\nTotal Expected Loss: ${total_expected_loss:,.0f}")
print(f"As % of Capital: {total_expected_loss/capital:.2%}")

# %%
# ## SECCIÓN 6: CAPITAL ADEQUACY (BASEL III)

def required_capital_basel3(trading_positions, credit_exposure, operational_risk_charge=0.10):
    """
    Basel III: Minimum capital requirement = 10.5% of risk-weighted assets
    
    Components:
    - Market Risk (trading book)
    - Credit Risk (loans, bonds)
    - Operational Risk
    """
    
    # Market risk (VaR-based, simplified)
    var_99_1day = 0.025 * trading_positions['equity_notional']
    market_risk_charge = var_99_1day * 3  # Standard multiplier
    
    # Credit risk (probability of default approach)
    credit_risk_charge = credit_exposure['principal'] * credit_exposure['pd'] * credit_exposure['lgd']
    
    # Operational risk
    operational_risk_charge = (trading_positions['equity_notional'] + credit_exposure['principal']) * operational_risk_charge
    
    total_rwa = market_risk_charge + credit_risk_charge + operational_risk_charge
    required_capital = total_rwa * 0.105  # 10.5% minimum
    
    return {
        'market_risk_charge': market_risk_charge,
        'credit_risk_charge': credit_risk_charge,
        'operational_risk_charge': operational_risk_charge,
        'total_rwa': total_rwa,
        'required_capital': required_capital
    }

# Example bank
trading_book = {'equity_notional': 50_000_000}
credit_book = {'principal': 200_000_000, 'pd': 0.02, 'lgd': 0.45}

capital_req = required_capital_basel3(trading_book, credit_book)

print(f"\n📋 Basel III Capital Requirement:")
print(f"Market Risk Charge: ${capital_req['market_risk_charge']:,.0f}")
print(f"Credit Risk Charge: ${capital_req['credit_risk_charge']:,.0f}")
print(f"Operational Risk Charge: ${capital_req['operational_risk_charge']:,.0f}")
print(f"Total RWA: ${capital_req['total_rwa']:,.0f}")
print(f"Required Capital (10.5%): ${capital_req['required_capital']:,.0f}")

# %%
# ## SECCIÓN 7: VISUALIZACIÓN

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# VaR Comparison
ax = axes[0, 0]
portfolio_values = np.linspace(-0.1, 0.05, 1000)
ax.hist(returns_normal, bins=50, density=True, alpha=0.5, label='Normal', edgecolor='black')
ax.hist(returns_crisis, bins=50, density=True, alpha=0.5, label='With Crisis', edgecolor='black')
ax.axvline(var_99_normal_hist, color='blue', linestyle='--', linewidth=2, label=f'Normal VaR(99%)')
ax.axvline(var_99_crisis_hist, color='red', linestyle='--', linewidth=2, label=f'Crisis VaR(99%)')
ax.set_xlabel('Daily Returns')
ax.set_ylabel('Density')
ax.set_title('VaR: Normal vs Crisis')
ax.legend()
ax.grid(alpha=0.3)

# Stress Scenario Results
ax = axes[0, 1]
scenarios_names = list(reverse_stress.keys())
losses = [abs(reverse_stress[s]['loss']) for s in scenarios_names]
colors_stress = plt.cm.Reds(np.linspace(0.3, 0.9, len(scenarios_names)))
ax.barh(scenarios_names, losses, color=colors_stress, edgecolor='black')
ax.set_xlabel('Loss ($)')
ax.set_title('Reverse Stress Test: Potential Losses')
ax.ticklabel_format(style='plain', axis='x')

# Capital Allocation
ax = axes[1, 0]
risk_components = ['Market Risk', 'Credit Risk', 'Operational Risk']
risk_charges = [
    capital_req['market_risk_charge'],
    capital_req['credit_risk_charge'],
    capital_req['operational_risk_charge']
]
colors_capital = ['blue', 'green', 'red']
ax.bar(risk_components, risk_charges, color=colors_capital, alpha=0.7, edgecolor='black')
ax.set_ylabel('Risk-Weighted Assets ($)')
ax.set_title('Basel III: Capital Required by Risk Type')
ax.ticklabel_format(style='plain', axis='y')
ax.grid(alpha=0.3, axis='y')

# Fed Stress Impact by Component
ax = axes[1, 1]
components = ['Bonds\n(Duration)', 'Equities\n(Beta)', 'Credit\n(Spreads)']
impacts = [
    stress_result['bond_pnl'] * 100,
    stress_result['equity_pnl'] * 100,
    stress_result['credit_pnl'] * 100
]
colors_impact = ['green' if x > 0 else 'red' for x in impacts]
ax.bar(components, impacts, color=colors_impact, alpha=0.7, edgecolor='black')
ax.axhline(0, color='black', linewidth=0.5)
ax.set_ylabel('Impact (%)')
ax.set_title('Fed Stress Scenario: Portfolio Impact (+200 bps rates)')
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('nb_ch08_stress_testing.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Visualization saved: nb_ch08_stress_testing.png")

# %%
# ## SECCIÓN 8: REGULACIÓN Y LECCIONES

print("""
🏦 REGULACIÓN Y STRESS TESTING:

**Mandatos Regulatorios:**

1. **Dodd-Frank Act (USA)**
   ✓ Annual stress test for large banks
   ✓ Scenario: Customer Portfolio Analysis and Reporting (CCAR)
   ✓ Report capital plans quarterly

2. **Basel III (Global)**
   ✓ Capital adequacy: 10.5% RWA minimum
   ✓ Liquidity coverage: 100% daily outflow coverage
   ✓ Leverage ratio: 3% unweighted

3. **European Banking Authority (EBA)**
   ✓ Biennial comprehensive stress tests
   ✓ Adverse scenarios: recession, asset price shock
   ✓ Publication of results → market discipline

4. **Scenarios Used:**
   ✓ Baseline: economic forecasts
   ✓ Adverse: recession (-4% GDP, rates fall)
   ✓ Severely Adverse: depression (-6% GDP, spreads +300 bps)

**Best Practices:**

✓ Run multiple scenarios (deterministic + stochastic)
✓ Include correlation breakdowns
✓ Test liquidity, not just solvency
✓ Back-test historical scenarios
✓ Validate with P&L data
✓ Report to board quarterly
✓ Use results for position limits
✓ Communicate with regulators

""")

# %%
if __name__ == "__main__":
    print("✅ Chapter 8 completo. MVP Ready!")
