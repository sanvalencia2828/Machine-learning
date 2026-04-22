# Notebook — Decisiones Probabilísticas: Kelly, VaR y Gestión de Capital

## Propósito
Explorar la toma de decisiones bajo incertidumbre usando funciones de pérdida,
ergodicidad, Value at Risk generativo, Expected Shortfall, y el criterio de Kelly
para asignación óptima de capital. Basado en los conceptos del Capítulo 8.

## Requisitos
Python 3.9+, librerías: numpy, pandas, matplotlib

## source_ref
turn0browsertab744690698

---

## Sección 1: Ergodicidad — Promedio de Ensamble vs Promedio Temporal

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Simulación: 1000 inversores, cada uno con $100, 200 rondas
# Cada ronda: +50% o -40% con igual probabilidad
n_investors = 1000
n_rounds = 200
initial_capital = 100.0

# Resultados del ensamble
wealth = np.full((n_rounds + 1, n_investors), initial_capital)

for t in range(1, n_rounds + 1):
    outcomes = np.where(
        np.random.rand(n_investors) < 0.5,
        1.50,   # +50%
        0.60    # -40%
    )
    wealth[t] = wealth[t - 1] * outcomes

# Promedio de ensamble (ensemble average)
ensemble_avg = wealth.mean(axis=1)

# Trayectoria típica (mediana)
typical_trajectory = np.median(wealth, axis=1)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel izquierdo: trayectorias individuales
for i in range(min(50, n_investors)):
    axes[0].plot(wealth[:, i], alpha=0.1, color='blue')
axes[0].plot(ensemble_avg, 'r-', lw=2, label='Promedio ensamble')
axes[0].plot(typical_trajectory, 'g--', lw=2, label='Mediana (típica)')
axes[0].set_yscale('log')
axes[0].set_xlabel('Rondas')
axes[0].set_ylabel('Capital ($, escala log)')
axes[0].set_title('Trayectorias individuales vs promedios')
axes[0].legend()

# Panel derecho: distribución final
axes[1].hist(wealth[-1], bins=50, density=True, alpha=0.7)
axes[1].axvline(ensemble_avg[-1], color='r', linestyle='-', label=f'Media: ${ensemble_avg[-1]:.0f}')
axes[1].axvline(typical_trajectory[-1], color='g', linestyle='--', label=f'Mediana: ${typical_trajectory[-1]:.2f}')
axes[1].set_xlabel('Capital final ($)')
axes[1].set_ylabel('Densidad')
axes[1].set_title('Distribución de riqueza final')
axes[1].legend()
plt.tight_layout()
plt.show()

print(f"Promedio ensamble final: ${ensemble_avg[-1]:.2f}")
print(f"Mediana (inversor típico) final: ${typical_trajectory[-1]:.2f}")
print(f"% inversores con menos de $100: {(wealth[-1] < 100).mean()*100:.1f}%")
print(f"% inversores arruinados (<$1): {(wealth[-1] < 1).mean()*100:.1f}%")
```

**Salida esperada:** El promedio de ensamble crece exponencialmente, pero la mediana
(inversor típico) converge a cero. Esto demuestra que los procesos multiplicativos
de inversión son NO-ergódicos.

---

## Sección 2: Value at Risk Generativo (GVaR)

```python
# Simular retornos diarios de un activo (Student-t, fat-tailed)
from scipy import stats

np.random.seed(101)
n_samples = 20000
simulated_returns = stats.t.rvs(df=6, loc=0.0, scale=1.5, size=n_samples)

position_size = 100_000  # USD

# GVaR al 99%
probability = 0.99
sorted_returns = np.sort(simulated_returns)
gvar_idx = int(n_samples * (1 - probability))
gvar = sorted_returns[gvar_idx]

# Expected Shortfall (GES): media de las pérdidas más allá del GVaR
tail_returns = sorted_returns[:gvar_idx]
ges = tail_returns.mean()

# Tail Risk (GTR): peor pérdida simulada
gtr = sorted_returns[0]

print(f"GVaR al {probability*100:.0f}%: {gvar:.2f}% → ${gvar/100*position_size:,.0f}")
print(f"GES al {(1-probability)*100:.0f}%: {ges:.2f}% → ${ges/100*position_size:,.0f}")
print(f"GTR (peor caso): {gtr:.2f}% → ${gtr/100*position_size:,.0f}")

# Visualización
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(simulated_returns, bins=100, density=True, alpha=0.6, label='Retornos simulados')
ax.axvline(gvar, color='green', lw=2, label=f'GVaR {probability*100:.0f}%: {gvar:.2f}%')
ax.axvline(ges, color='orange', lw=2, ls='--', label=f'GES: {ges:.2f}%')
ax.axvline(gtr, color='red', lw=2, ls=':', label=f'GTR: {gtr:.2f}%')
ax.set_xlabel('Retorno diario (%)')
ax.set_ylabel('Densidad')
ax.set_title('Distribución de retornos con métricas de riesgo generativas')
ax.legend()
plt.show()
```

---

## Sección 3: Ruina del Apostador

```python
def simulate_gamblers_ruin(bankroll, opponent_bankroll, p_win, max_rounds=50000):
    """Simula la ruina del apostador con apuestas de $1."""
    capital = bankroll
    history = [capital]
    for _ in range(max_rounds):
        if capital <= 0 or capital >= bankroll + opponent_bankroll:
            break
        capital += 1 if np.random.rand() < p_win else -1
        history.append(capital)
    return history

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Escenario 1: p < 0.5 (juego desfavorable)
for i in range(10):
    h = simulate_gamblers_ruin(100, 200, p_win=0.48)
    axes[0].plot(h, alpha=0.5)
axes[0].set_title('p=0.48 (desfavorable)')
axes[0].set_xlabel('Rondas')
axes[0].set_ylabel('Capital ($)')

# Escenario 2: p = 0.5 (justo, bankroll menor)
for i in range(10):
    h = simulate_gamblers_ruin(100, 200, p_win=0.50)
    axes[1].plot(h, alpha=0.5)
axes[1].set_title('p=0.50 (justo, bankroll menor)')

# Escenario 3: p > 0.5 (favorable)
for i in range(10):
    h = simulate_gamblers_ruin(100, 200, p_win=0.52)
    axes[2].plot(h, alpha=0.5)
axes[2].set_title('p=0.52 (favorable)')

plt.suptitle('Ruina del Apostador: Trayectorias de Capital')
plt.tight_layout()
plt.show()
```

---

## Sección 4: Ruina del Maximizador de Valor Esperado

```python
# Demostrar que maximizar EV con todo el capital lleva a la ruina
# incluso con probabilidades favorables (p=0.6, pago 2:1)

p_win = 0.6
n_bets = 300
n_gamblers = 50

fig, ax = plt.subplots(figsize=(10, 5))

ruined = 0
for i in range(n_gamblers):
    capital = 100.0
    history = [capital]
    for _ in range(n_bets):
        # Apuesta TODO el capital en cada ronda
        if np.random.rand() < p_win:
            capital *= 2.0  # gana 2x
        else:
            capital *= 0.0  # pierde todo
        history.append(capital)
        if capital < 0.01:
            break
    if capital < 0.01:
        ruined += 1
    ax.plot(history, alpha=0.3)

ax.set_xlabel('Número de apuestas')
ax.set_ylabel('Capital ($)')
ax.set_title(f'Maximizar EV (all-in): {ruined}/{n_gamblers} arruinados ({ruined/n_gamblers*100:.0f}%)')
ax.set_yscale('log')
plt.show()

print(f"EV por apuesta: {p_win * 2 + (1-p_win) * 0 - 1:.1f}x (positivo!)")
print(f"Pero {ruined}/{n_gamblers} inversores terminan arruinados.")
```

---

## Sección 5: Criterio de Kelly

```python
def kelly_simulation(p, odds_win, odds_loss, fraction, n_trials, n_series, initial=100):
    """Simula serie de apuestas con fracción de Kelly dada."""
    wealth = np.zeros((n_trials + 1, n_series))
    wealth[0] = initial
    for t in range(1, n_trials + 1):
        wins = np.random.rand(n_series) < p
        wealth[t] = np.where(
            wins,
            wealth[t-1] * (1 + fraction * odds_win),
            wealth[t-1] * (1 - fraction * odds_loss)
        )
    return wealth

# Parámetros: moneda sesgada p=0.55, pago 1:1
p = 0.55
odds_win = 1.0   # ganas 1x tu apuesta
odds_loss = 1.0  # pierdes 1x tu apuesta

# Kelly optimal: f* = (p*odds_win - (1-p)*odds_loss) / (odds_win * odds_loss)
f_star = (p * odds_win - (1 - p) * odds_loss) / (odds_win * odds_loss)
print(f"Kelly óptimo f* = {f_star:.2%}")

n_trials = 500
n_series = 50

strategies = {
    'Half Kelly': f_star / 2,
    'Kelly': f_star,
    'Triple Kelly': f_star * 3,
    'All-In': 1.0
}

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['green', 'blue', 'purple', 'red']

for (name, f), color in zip(strategies.items(), colors):
    wealth = kelly_simulation(p, odds_win, odds_loss, f, n_trials, n_series)
    mean_wealth = wealth.mean(axis=1)
    ax.plot(mean_wealth, color=color, lw=2, label=f'{name} (f={f:.2%})')

ax.set_xlabel('Número de apuestas')
ax.set_ylabel('Capital promedio ($)')
ax.set_title('Criterio de Kelly: Crecimiento de capital por estrategia')
ax.legend()
ax.set_yscale('log')
plt.show()
```

**Salida esperada:** Kelly domina a largo plazo. Half-Kelly crece más lento pero con menos
volatilidad. Triple Kelly y All-In convergen a cero.

---

## Sección 6: Ruina del Inversor Markowitz

```python
# 100 inversores, cada uno asigna diferente fracción de capital (1%-100%)
# a una serie de 20,000 apuestas con EV positivo pero asimétrico

p_beat = 0.755  # probabilidad de ganar (posterior predictive mean del Ch6)
profit_pct = 0.05   # +5% si gana
loss_pct = 0.15     # -15% si pierde

n_bets = 20000
fractions = np.arange(0.01, 1.01, 0.01)  # 1% a 100%
initial = 100_000

# Generar secuencia de resultados
outcomes = np.random.binomial(1, p_beat, size=n_bets)

final_capitals = []
for f in fractions:
    capital = initial
    for outcome in outcomes:
        if outcome == 1:
            capital *= (1 + profit_pct * f)
        else:
            capital *= (1 - loss_pct * f)
    final_capitals.append(capital)

# Kelly óptimo general
f_kelly = (profit_pct * p_beat - loss_pct * (1 - p_beat)) / (profit_pct * loss_pct)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(fractions * 100, final_capitals, 'b-', lw=2)
ax.axvline(f_kelly * 100, color='red', ls='--', lw=2, label=f'Kelly óptimo: {f_kelly*100:.1f}%')
ax.axhline(initial, color='gray', ls=':', alpha=0.5, label='Capital inicial')
ax.set_xlabel('Fracción del capital invertida (%)')
ax.set_ylabel('Capital final ($)')
ax.set_title('Crecimiento de capital vs tamaño de posición (20,000 apuestas)')
ax.set_yscale('log')
ax.legend()
plt.show()

optimal_idx = np.argmax(final_capitals)
print(f"Kelly óptimo teórico: {f_kelly*100:.1f}%")
print(f"Fracción óptima simulada: {fractions[optimal_idx]*100:.0f}%")
print(f"Capital máximo: ${final_capitals[optimal_idx]:,.0f}")
print(f"Inversores arruinados (>40% capital): {sum(1 for fc in final_capitals if fc < 1)}")
```

---

## Sección 7: Ejercicio

**Ejercicio:** Usando los parámetros del modelo de mercado del Capítulo 7 (alpha=-0.05,
beta=1.33, residual=0.79), calcular:
1. El Kelly position size para una posición larga en Apple dado el retorno esperado
2. El GVaR al 95% y 99% usando 10,000 simulaciones de la distribución predictiva posterior
3. Comparar el capital terminal después de 252 días (1 año) usando Kelly vs Half-Kelly vs MPT (100% invertido)

```python
# Esqueleto para el ejercicio
# TODO: completar con los valores del Ch7

alpha_post = -0.05  # media posterior de alpha
beta_post = 1.33    # media posterior de beta
residual_post = 0.79  # media posterior del residual

# Simular retornos del mercado (Student-t, df=6)
# market_returns = stats.t.rvs(df=6, loc=..., scale=..., size=10000)
# apple_returns = alpha_post + beta_post * market_returns + residual

# Calcular Kelly f* = E[r] / Var[r] para distribución continua
# ...

print("Completar ejercicio con datos del Capítulo 7")
```

---

## Conclusiones
- Los procesos de inversión son NO-ergódicos: el promedio de ensamble difiere del promedio temporal
- Maximizar el valor esperado lleva a la ruina en apuestas secuenciales
- El criterio de Kelly optimiza el crecimiento de capital sin riesgo de ruina
- Half-Kelly es preferible en la práctica por la incertidumbre en los parámetros
- VaR y Expected Shortfall son mejores medidas de riesgo que la volatilidad

## Referencias
- Peters, O. "The Ergodicity Problem in Economics" Nature Physics 15, 2019
- Kelly, J.L. "A New Interpretation of Information Rate" Bell System Technical Journal, 1956
- Thorp, E.O. "A Man for All Markets" Random House, 2017
- Poundstone, W. "Fortune's Formula" Hill and Wang, 2006
