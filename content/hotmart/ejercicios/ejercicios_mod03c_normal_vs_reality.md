# Ejercicios Practicos -- Modulo 3C: Normal vs Realidad
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Tu Primer QQ-Plot

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
1. Genera 5000 retornos con Student-t(nu=4, scale=0.01)
2. Genera 5000 retornos con Normal(0, 0.01) como control
3. Haz un QQ-plot de cada uno contra la Normal
4. Cual muestra desviacion en las colas? Por que?

```python
from scipy import stats
import matplotlib.pyplot as plt

datos_t = 0.01 * np.random.standard_t(4, 5000)
datos_n = np.random.normal(0, 0.01, 5000)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
stats.probplot(datos_t, dist='norm', plot=axes[0])
stats.probplot(datos_n, dist='norm', plot=axes[1])
# TODO: titular y comparar
```

---

## Ejercicio 2: Tests de Normalidad -- 3 en 1

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Aplica Jarque-Bera, Shapiro-Wilk y Anderson-Darling a:
1. Normal pura (1000 datos)
2. Student-t(nu=5) (1000 datos)
3. Mezcla: 90% N(0,0.01) + 10% N(-0.03, 0.04) (1000 datos)

Para cada distribucion, reporta: estadistico, p-value, conclusion.
Cual test es mas sensible a fat tails? Cual a asimetria?

```python
from scipy.stats import jarque_bera, shapiro, anderson
# TODO: generar las 3 muestras
# TODO: aplicar los 3 tests
# TODO: reportar resultados en tabla
```

---

## Ejercicio 3: Ajuste Normal vs Student-t con AIC

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera 10000 retornos con Student-t(nu=3.5, scale=0.012).

1. Ajusta Normal MLE (2 parametros)
2. Ajusta Student-t MLE (3 parametros)
3. Calcula log-likelihood, AIC y BIC para ambos
4. Cual modelo es mejor? Por cuanto?
5. Cambia nu a 10, 20, 50. A partir de que nu la Normal
   empieza a ser competitiva?

```python
# AIC = 2k - 2*loglik
# BIC = k*ln(n) - 2*loglik
# Menor AIC/BIC = mejor modelo
```

---

## Ejercicio 4: Tabla de Eventos Extremos

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Genera 50000 retornos con Student-t(nu=4, scale=0.01).

1. Cuenta eventos > 2, 3, 4, 5, 6 sigma
2. Calcula cuantos esperarias bajo Normal
3. Construye la tabla de ratios
4. Si un crash es un evento de 5 sigma, cada cuantos anos
   ocurre bajo Normal? Y bajo Student-t(4)?

```python
# Normal: P(>k*sigma) = 2 * stats.norm.sf(k)
# Frecuencia esperada = P * n_dias
# Anos = n_dias / (252 * frecuencia_por_dia)
```

---

## Ejercicio 5: Error de VaR por Asumir Normalidad

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Un banco calcula VaR 99% para su portafolio asumiendo Normal.
Los retornos reales siguen Student-t(nu=4).

1. Con capital $10M, calcula VaR 99% parametrico Normal
2. Calcula VaR 99% usando la Student-t ajustada
3. Calcula VaR 99% historico (percentil directo)
4. Cuanto capital ADICIONAL necesita el banco si usa el modelo correcto?
5. Si el regulador exige VaR 99% + buffer de 3x, cual modelo
   cumple el requisito? Cual lo subestima?

---

## Ejercicio 6 (Bonus): Genera tu Propio Dataset Realista

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
Construye un generador de retornos que capture 3 propiedades:
1. Colas pesadas (curtosis > 10)
2. Asimetria negativa (skew < -0.5)
3. Clustering de volatilidad (periodos de alta y baja vol)

Opciones de implementacion:
- Mezcla de Normales con pesos asimetricos
- Student-t + cambio de regimen GARCH-like
- Mezcla con componente de saltos

```python
def generador_realista(n, seed=42):
    """Genera retornos con fat tails, skew y clustering."""
    np.random.seed(seed)
    # TODO: implementar
    # Verificar: skew < -0.5, curtosis > 10
    pass
```
