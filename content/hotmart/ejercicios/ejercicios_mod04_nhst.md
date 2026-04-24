# Ejercicios Practicos -- Modulo 4: Peligros de NHST
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Falacia Inversa con Test Medico

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
Un test de embarazo tiene sensibilidad 97% y especificidad 99%.
La prevalencia de embarazo en una poblacion es 3%.

1. Calcula P(embarazada | test positivo) usando Bayes
2. Calcula P(NO embarazada | test positivo)
3. Si el test da positivo, deberas confiar ciegamente?
4. Que pasa si la prevalencia sube a 30%?

```python
def bayes_test(sensibilidad, especificidad, prevalencia):
    p_pos = sensibilidad * prevalencia + (1 - especificidad) * (1 - prevalencia)
    p_enfermo_dado_pos = (sensibilidad * prevalencia) / p_pos
    return p_enfermo_dado_pos

# TODO: calcular para prevalencia 3% y 30%
```

---

## Ejercicio 2: P-Hacking -- Encuentra tu "Alpha"

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera 50 estrategias aleatorias (retornos Normal(0, 0.01), 252 dias).
NINGUNA tiene alpha real.

1. Para cada estrategia, calcula p-value del test t (H0: mu=0)
2. Cuantas tienen p < 0.05? p < 0.01?
3. Grafica la distribucion de p-values. Es uniforme? Por que?
4. Ahora prueba con 500 estrategias. Cual es el mejor p-value?
5. Si publicas SOLO la mejor, que conclusion sacaria el lector?

```python
np.random.seed(42)
p_values = []
for _ in range(50):
    ret = np.random.normal(0, 0.01, 252)
    _, p = stats.ttest_1samp(ret, 0)
    p_values.append(p)
# TODO: analizar distribucion de p-values
```

---

## Ejercicio 3: Falacia del Fiscal en Matching de ADN

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Un perfil de ADN coincide con frecuencia 1 en 500,000.
La ciudad tiene 2 millones de habitantes.

1. Cuantas personas en la ciudad tienen ese perfil? (~4)
2. P(inocente | match) = ?
3. El fiscal dice "1 en 500,000 de probabilidad de inocencia". Correcto?
4. Que informacion ADICIONAL necesitas para calcular P(culpable | match)?
5. Conecta con backtesting: si probaste 500 estrategias y una tiene p=1/500,000...

---

## Ejercicio 4: IC -- Los 3 Errores en Practica

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera 1000 muestras de 30 retornos cada una, con mu_real = 0.05.
Para cada muestra, calcula el IC 95%.

1. Que % de los ICs contiene mu_real? (deberia ser ~95%)
2. Toma UN solo IC. Cual es P(mu esta en este IC)?
   (Pista: es 0% o 100%, no 95%)
3. Si tu IC es (0.02, 0.12), que puedes decir sobre mu?
4. Genera muestras de tamano 5 en vez de 30. Cambia la cobertura?
   Por que podria no ser 95%?

---

## Ejercicio 5: Modelo OLS -- Cuando los Tests Mienten

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Genera un modelo de mercado sintetico:
`r_asset = 0.0001 + 1.3 * r_market + epsilon`

Donde epsilon tiene fat tails (Student-t, nu=3).

1. Ajusta OLS y reporta alpha, beta, p-values
2. Ejecuta Jarque-Bera sobre residuales. Son normales?
3. Calcula Durbin-Watson. Hay autocorrelacion?
4. Si los residuales NO son normales, son validos los p-values? Por que?
5. Repite con epsilon ~ Normal. Ahora los tests pasan?

```python
from scipy import stats

np.random.seed(42)
n = 500
r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
epsilon = 0.008 * np.random.standard_t(3, n)  # Fat tails!
r_asset = 0.0001 + 1.3 * r_mkt + epsilon

# TODO: OLS manual
# TODO: tests diagnosticos
# TODO: comparar con epsilon Normal
```

---

## Ejercicio 6 (Bonus): Correccion de Bonferroni y Tasa de Descubrimiento Falso

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
Has probado 200 estrategias y 12 tienen p < 0.05.

1. Aplica correccion de Bonferroni: nuevo umbral = 0.05/200
   Cuantas sobreviven?
2. Aplica Benjamini-Hochberg (FDR): ordena p-values, compara
   con i/200 * 0.05. Cuantas sobreviven?
3. Cual correccion es mas conservadora?
4. Si 3 estrategias sobreviven ambas correcciones,
   cual es tu estimacion de cuantas son reales?

```python
from scipy.stats import false_discovery_control

# Bonferroni
umbral_bonf = 0.05 / 200
sobreviven_bonf = (p_values < umbral_bonf).sum()

# Benjamini-Hochberg (FDR)
# TODO: implementar o usar scipy
```
