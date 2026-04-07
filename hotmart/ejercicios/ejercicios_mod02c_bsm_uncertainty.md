# Ejercicios Practicos -- Modulo 2C: Black-Scholes y Trinidad de la Incertidumbre
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Pricing con Black-Scholes

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
Implementa la formula de Black-Scholes para una opcion call y put europea.

Parametros:
- S = 100 (precio del activo)
- K = 105 (strike, ligeramente OTM)
- T = 0.5 (6 meses)
- r = 0.04 (tasa libre de riesgo)
- sigma = 0.20 (volatilidad 20%)

1. Calcula el precio del call y del put.
2. Verifica la paridad put-call: C - P = S - K*exp(-rT)
3. Que pasa si sigma sube a 0.40? Y a 0.10?

### Codigo inicial
```python
from scipy import stats
import numpy as np

def bsm_call(S, K, T, r, sigma):
    """Precio call europea Black-Scholes."""
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)

def bsm_put(S, K, T, r, sigma):
    """Precio put europea via paridad put-call."""
    # TODO: implementar
    pass

# TODO: calcular con los parametros dados
# TODO: verificar paridad put-call
# TODO: sensibilidad a sigma
```

### Respuesta esperada
Call ~ $4.89, Put ~ $7.81. Paridad: C - P = S - K*exp(-rT) se cumple
exactamente. Mayor sigma -> mayor precio para ambos (mas incertidumbre).

---

## Ejercicio 2: Normal vs Fat Tails -- El Crash Imposible

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
El 19 de octubre de 1987 (Black Monday), el S&P 500 cayo -22.6% en un dia.
Con una volatilidad diaria tipica de ~1% (anualizada ~16%), bajo distribucion
Normal:

1. Cuantas desviaciones estandar representa una caida de -22.6%?
2. Cual es la probabilidad de ese evento bajo Normal?
3. Cada cuantos anos esperarias un evento asi bajo Normal?
4. Repite los calculos con Student-t (nu=4, misma escala)
5. Cual modelo es mas realista? Por que?

### Codigo inicial
```python
import numpy as np
from scipy import stats

caida = -0.226  # -22.6%
sigma_diaria = 0.01  # 1%

# Normal
z_score = caida / sigma_diaria
prob_normal = stats.norm.cdf(caida, 0, sigma_diaria)

# Student-t(4) con misma escala
# Nota: para Student-t, la escala NO es la desviacion estandar
# sigma_t = sigma * sqrt((nu-2)/nu) para tener misma varianza
nu = 4
sigma_t = sigma_diaria * np.sqrt((nu - 2) / nu)
prob_t = stats.t.cdf(caida, nu, 0, sigma_t)

# TODO: calcular z-score, probabilidades, frecuencia esperada
# TODO: comparar ambos modelos
# TODO: graficar ambas distribuciones con la caida marcada
```

### Respuesta esperada
- z-score: ~22.6 sigmas bajo Normal
- P(Normal): ~10^(-113) -- una vez cada 10^110 anos (universo tiene ~10^10)
- P(Student-t(4)): ~10^(-5) -- una vez cada ~400 anos (raro pero posible)
- Student-t es enormemente mas realista para eventos extremos.

---

## Ejercicio 3: Volatility Smile -- El Mercado vs BSM

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Usa simulacion Monte Carlo con Student-t(nu=4) para generar precios de
opciones call para 15 strikes diferentes, luego extrae la volatilidad
implicita de BSM para cada uno.

Parametros:
- S = 100, T = 0.25, r = 0.03, sigma_base = 0.20
- Strikes: de 80 a 120 (paso de ~2.86)
- n_sim = 200,000

1. Genera precios MCS con Student-t para cada strike
2. Calcula la vol implicita de BSM (biseccion) para cada precio
3. Grafica la vol implicita vs moneyness (K/S)
4. Por que la curva tiene forma de sonrisa/smirk?

### Codigo inicial
```python
from scipy.optimize import brentq

def vol_implicita(precio_mercado, S, K, T, r):
    """Calcula vol implicita por biseccion."""
    try:
        return brentq(
            lambda s: bsm_call(S, K, T, r, s) - precio_mercado,
            0.001, 5.0, xtol=1e-6
        )
    except ValueError:
        return np.nan

# TODO: simular precios con Student-t MCS
# TODO: calcular vol implicita para cada strike
# TODO: graficar el smile
# HINT: deep OTM puts tienen mayor IV porque el mercado
#       asigna mas probabilidad a crashes de lo que BSM predice
```

---

## Ejercicio 4: Clasificacion -- Trinidad de Incertidumbre en Opciones

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Para cada escenario, clasifica el tipo de incertidumbre dominante
(aleatoria, epistemica, ontologica) y explica que herramienta usarias.

| Escenario | Tipo | Herramienta |
|-----------|------|-------------|
| El retorno diario de Apple es impredecible | | |
| No sabes si la volatilidad de Tesla es 30% o 50% | | |
| La Fed cambia la politica monetaria sin aviso previo | | |
| Un flash crash reduce el mercado 10% en 5 minutos | | |
| Tu modelo BSM usa sigma = 0.25 pero la real es 0.35 | | |
| China prohibe las criptomonedas (cambio regulatorio) | | |
| El LIBOR deja de existir y es reemplazado por SOFR | | |

### Reflexion
1. Puede un mismo evento tener mas de un tipo de incertidumbre?
2. Que tipo de incertidumbre es la MAS peligrosa para un trader?
3. BSM trata toda la incertidumbre como aleatoria. Por que es un problema?

```python
# No se necesita codigo, pero si quieres formalizar:
clasificacion = {
    "Retorno diario Apple": {
        "tipo": "???",
        "herramienta": "???"
    },
    # TODO: completar para cada escenario
}
```

---

## Ejercicio 5: Stress Test -- BSM bajo Cambio de Regimen

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Simula un portafolio de opciones bajo dos regimenes:

**Regimen 1 (Normal, dias 1-180):**
- sigma = 0.18, sin saltos, retornos ~ Normal

**Regimen 2 (Crisis, dias 181-252):**
- sigma = 0.45, saltos negativos (lambda=0.05, mu_jump=-0.08)
- Retornos ~ Student-t(nu=3)

1. Pricing con BSM usando sigma constante de todo el periodo
2. Pricing con MCS usando los parametros correctos de cada regimen
3. Cuanto pierde un trader que usa BSM si vende opciones en el Regimen 1
   y la crisis llega en el Regimen 2?
4. Como protegerias el portafolio si reconocieras la incertidumbre
   ontologica?

### Codigo inicial
```python
import numpy as np
from scipy import stats

def simular_regimenes(S0=100, n_paths=50000, seed=42):
    """Simula precios con cambio de regimen."""
    np.random.seed(seed)
    n_dias = 252
    S = np.full(n_paths, S0, dtype=float)

    for d in range(n_dias):
        if d < 180:
            # Regimen 1: calma
            ret = np.random.normal(0.0003, 0.18/np.sqrt(252), n_paths)
        else:
            # Regimen 2: crisis
            sigma_d = 0.45 / np.sqrt(252)
            ret = sigma_d * np.random.standard_t(3, n_paths)
            # Saltos
            jumps = np.random.binomial(1, 0.05, n_paths)
            ret += jumps * np.random.normal(-0.08, 0.03, n_paths)
        S *= np.exp(ret)

    return S

# TODO: simular
# TODO: comparar precio de call K=100 con BSM vs MCS
# TODO: calcular P&L del vendedor de opciones
# TODO: proponer estrategia de cobertura
```

### Respuesta esperada
- BSM subprecia las opciones ~30-60% cuando llega la crisis
- El vendedor de opciones pierde significativamente
- Cobertura: comprar puts OTM profundos (tail risk hedging),
  usar modelos con regimen-switching, o reservar capital para ontologica

---

## Ejercicio 6 (Bonus): Las Griegas bajo Incertidumbre

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Las "griegas" de BSM (Delta, Gamma, Vega, Theta) asumen sigma constante.

1. Calcula Delta y Vega para un call ATM (S=K=100, T=0.25, r=0.03, sigma=0.25)
2. Si sigma es incierta (sigma ~ Normal(0.25, 0.05)), calcula el
   "Delta efectivo" y "Vega efectivo" promediando sobre la distribucion
   de sigma (1000 muestras)
3. Cuanto se desvian del valor puntual de BSM?
4. Que implicacion tiene para hedging dinamico?

### Pistas
```python
def bsm_delta(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    return stats.norm.cdf(d1)

def bsm_vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    return S * stats.norm.pdf(d1) * np.sqrt(T)

# TODO: calcular griegas puntuales vs promediadas sobre incertidumbre en sigma
```
