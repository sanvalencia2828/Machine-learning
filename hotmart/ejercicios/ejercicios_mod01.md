# Ejercicios Practicos — Modulo 1: La Necesidad del ML Probabilistico
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Modelo Binomial de Tasas de Credito

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Tu tarjeta de credito cobra prime + 10%. La tasa prime actual es 3%.
La Fed se reunira 8 veces este ano. Basado en la economia actual,
estimas que hay un 65% de probabilidad de que suba la tasa 0.25% en
cada reunion.

1. Usa la distribucion binomial para modelar tu tasa de credito en 12 meses.
2. Calcula la tasa esperada (media) y la desviacion estandar.
3. Cual es la probabilidad de que tu tasa supere el 15%?

### Codigo inicial
```python
from scipy.stats import binom
import numpy as np

fed_meetings = 8
p_raise = 0.65
base_rate = 3.0  # prime rate actual
spread = 10.0    # tu spread sobre prime

# Posibles subidas: 0, 1, 2, ..., 8
raises = np.arange(0, fed_meetings + 1)

# TODO: calcular probabilidades con binom.pmf()
# TODO: calcular tasas resultantes
# TODO: calcular media, std, P(tasa > 15%)
```

### Solucion
```python
probs = binom.pmf(raises, fed_meetings, p_raise)
rates = base_rate + spread + raises * 0.25

expected_rate = np.sum(rates * probs)
variance = np.sum(probs * (rates - expected_rate)**2)
std_rate = np.sqrt(variance)
prob_above_15 = probs[rates > 15].sum()

print(f"Tasa esperada: {expected_rate:.2f}%")
print(f"Desviacion estandar: {std_rate:.2f}%")
print(f"P(tasa > 15%): {prob_above_15:.2%}")
```

---

## Ejercicio 2: Cambio Estructural — De Binomial a Trinomial

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Despues de la 5ta reunion, una crisis externa (ej: default de Grecia)
cambia la perspectiva de la Fed. Ahora en cada reunion restante puede:
- Subir 0.25% con probabilidad 0.2
- Mantener con probabilidad 0.3
- Bajar 0.25% con probabilidad 0.5

1. Modifica el modelo para que las primeras 5 reuniones usen binomial
   (p=0.65) y las ultimas 3 usen trinomial.
2. Compara la distribucion de tasas con y sin cambio estructural.
3. Que implicaciones tiene esto para la gestion de riesgo?

### Pista
```python
# Fase 1: 5 reuniones binomiales
# Fase 2: 3 reuniones trinomiales
# Usa simulacion Monte Carlo (10,000 iteraciones) para combinar ambas fases
```

---

## Ejercicio 3: LTCM — Simulacion de Leverage

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Simula un portafolio estilo LTCM con las siguientes caracteristicas:
- Capital inicial: $1,000,000
- Retornos diarios: N(0.05%, 0.8%) en condiciones normales
- Leverage: prueba con 1x, 5x, 10x, 25x
- Crisis (dia 700-750): retornos N(-0.5%, 3%) con dias de panico (-10%)
- Liquidacion por margin call si valor <= 0

1. Ejecuta `python src/ltcm_simulator.py` y analiza los graficos.
2. Cual es el maximo leverage que sobrevive la crisis?
3. Modifica los parametros de crisis para hacerla peor. A que leverage
   sobrevives?
4. Que leccion extraes sobre la relacion entre leverage y riesgo de ruina?

### Reflexion
Conecta tu resultado con la frase del libro: los modelos financieros
"lulled adherents into a false sense of certainty about the accuracy
of their predictive powers."
