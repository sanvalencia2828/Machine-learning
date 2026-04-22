# Ejercicios Practicos -- Modulo 3B: Conceptos Estadisticos y Volatilidad
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Los 4 Momentos a Mano

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
Dados los retornos diarios de 10 dias: [0.02, -0.01, 0.03, -0.04, 0.01,
0.005, -0.03, 0.015, -0.005, 0.02]:

1. Calcula a mano (o con Python): media, std, skewness, curtosis exceso
2. Es esta serie simetrica o asimetrica?
3. Tiene colas pesadas o normales?
4. Verifica con scipy.stats.describe()

```python
import numpy as np
from scipy import stats

datos = np.array([0.02, -0.01, 0.03, -0.04, 0.01, 0.005, -0.03, 0.015, -0.005, 0.02])
# TODO: calcular los 4 momentos
# TODO: interpretar cada uno
```

---

## Ejercicio 2: Misma Vol, Diferente Riesgo

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera 3 distribuciones de 10,000 retornos con std ~ 1.5%:

- **A**: Normal(0, 0.015)
- **B**: Student-t(nu=3, scale ajustada para std~0.015)
- **C**: 97% Normal(0.001, 0.01) + 3% Normal(-0.05, 0.05)

1. Verifica que las 3 tienen volatilidad similar
2. Calcula VaR 95%, ES 95%, P(r < -5%) para cada una
3. Simula 1000 trayectorias de 252 dias con capital $100K
4. Cual tiene mayor probabilidad de perder >20% en un ano?
5. La volatilidad te hubiera advertido? Conclusion.

```python
# HINT: Para que Student-t tenga std = target:
# scale = target * np.sqrt((nu-2)/nu) para nu > 2
```

---

## Ejercicio 3: Demo de No-Ergodicidad

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Simula el juego: ganas +80% o pierdes -50%, cada uno con p=0.5.

1. Calcula E[R] = 0.5*(+80%) + 0.5*(-50%) = ?
2. Calcula la media geometrica: sqrt(1.8 * 0.5) - 1 = ?
3. Simula 10,000 trayectorias de 50 pasos, capital $100
4. Grafica media del ensamble vs mediana
5. Que % de jugadores pierde dinero?

### Pregunta clave
Si E[R] es claramente positivo, por que la mayoria pierde?
Que implicacion tiene para la evaluacion de inversiones?

---

## Ejercicio 4: QQ-Plot Diagnostico

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Genera 5000 retornos con Student-t(nu=5, loc=0, scale=0.01).

1. Haz un QQ-plot contra la Normal. Que ves en las colas?
2. Haz un QQ-plot contra Student-t(5). Ahora se ajusta?
3. Cambia nu a 3, 4, 10, 30. Cual se parece mas a Normal?
4. A que valor de nu la Student-t es indistinguible de Normal?

```python
from scipy import stats
import matplotlib.pyplot as plt

datos = 0.01 * np.random.standard_t(5, 5000)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
stats.probplot(datos, dist='norm', plot=axes[0])
stats.probplot(datos, dist=stats.t, sparams=(5,), plot=axes[1])
# TODO: completar y comparar
```

---

## Ejercicio 5: VaR, ES y Downside Deviation

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Genera 2 anos de retornos diarios (504 dias) con Student-t(nu=4).

1. Calcula VaR parametrico (asumiendo Normal) al 95% y 99%
2. Calcula VaR historico (percentil directo) al 95% y 99%
3. Calcula Expected Shortfall al 95% y 99%
4. Calcula Downside Deviation y Semi-Varianza
5. Compara: cuanto subestima el VaR Normal vs historico?
6. Si tienes $1M, cual es la perdida maxima esperada en un dia?

```python
# VaR parametrico Normal:
var_param = mu + stats.norm.ppf(0.05) * sigma

# VaR historico:
var_hist = np.percentile(retornos, 5)

# Expected Shortfall:
es = retornos[retornos <= var_hist].mean()

# Downside deviation:
dd = np.sqrt(np.mean(np.minimum(retornos, 0)**2))
```

---

## Ejercicio 6 (Bonus): Construye tu Propio Fat Tails Test

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
Implementa una funcion `fat_tails_report(retornos)` que:

1. Calcule los 4 momentos
2. Ejecute el test de Jarque-Bera para normalidad
3. Cuente eventos > 3, 4, 5 sigma y compare con Normal
4. Genere un QQ-plot
5. Emita un veredicto: "Normal", "Fat tails leves", "Fat tails severas"

Criterio de clasificacion:
- Curtosis exceso < 1 Y Jarque-Bera p > 0.05: "Normal"
- Curtosis exceso 1-5: "Fat tails leves"
- Curtosis exceso > 5: "Fat tails severas"

```python
def fat_tails_report(retornos, nombre=""):
    """Genera reporte de fat tails para una serie de retornos."""
    # TODO: implementar
    pass
```
