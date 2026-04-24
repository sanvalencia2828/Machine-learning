# Ejercicios Practicos -- Modulo 7: Ensambles Generativos con PyMC
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: OLS vs Posterior -- Comparar Estimaciones

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Genera 100 retornos sinteticos (AAPL vs SP500, beta=1.2, alpha=0).
1. Ajusta OLS: obtiene alpha, beta, IC 95%
2. Calcula posterior bayesiano (Normal conjugado) con priors:
   alpha ~ N(0, 0.001), beta ~ N(1, 0.5)
3. Compara IC frecuentista vs HDI bayesiano
4. Calcula P(beta > 1.0) con el posterior
5. OLS puede responder esa pregunta?

---

## Ejercicio 2: Spaghetti Plot -- Ensamble de Lineas

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Del posterior de alpha y beta (ejercicio 1):
1. Muestrea 100 pares (alpha_i, beta_i)
2. Grafica las 100 lineas de regresion
3. Donde convergen? Donde divergen?
4. Agrega la linea OLS en rojo. Esta dentro del ensamble?
5. Que pasa en x = 2*max(r_mkt)? (extrapolacion)

---

## Ejercicio 3: Retrodiction Check

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Con el modelo ajustado:
1. Para cada dato de entrenamiento, simula 1000 retornos posibles
2. Los datos reales caen dentro del HDI 95%?
3. Calcula cobertura: deberia ser ~95%
4. Si la cobertura es < 90%, que indica sobre el modelo?
5. Grafica: datos reales vs bandas de retrodiction

---

## Ejercicio 4: Prediction con Incertidumbre

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Predice el retorno de AAPL para 3 escenarios de mercado:
- r_SP500 = -3% (crash)
- r_SP500 = 0% (neutral)
- r_SP500 = +2% (rally)

Para cada escenario:
1. Calcula media y HDI 95% de la prediccion
2. Cuanto mas ancho es el HDI para el crash vs neutral?
3. Haz un grafico con las 3 distribuciones predictivas
4. Que decision de portafolio tomarias en cada caso?

---

## Ejercicio 5: PyMC Mini-Proyecto (si PyMC disponible)

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Si tienes PyMC instalado (`pip install pymc`):
```python
import pymc as pm

with pm.Model() as model:
    alpha = pm.Normal("alpha", mu=0, sigma=0.001)
    beta = pm.Normal("beta", mu=1, sigma=0.5)
    sigma = pm.HalfStudentT("sigma", nu=4, sigma=0.02)
    mu = alpha + beta * r_mkt
    y = pm.StudentT("y", nu=6, mu=mu, sigma=sigma, observed=r_asset)
    trace = pm.sample(2000, tune=1000)
```
1. Ejecuta y examina `pm.summary(trace)`
2. Rhat < 1.01 para todos los parametros?
3. Trace plots: las cadenas convergen?
4. Compara HDI de PyMC vs conjugado manual
5. Prior predictive check: los datos simulados son plausibles?

---

## Ejercicio 6 (Bonus): R-squared Probabilistico

**Nivel:** Avanzado
**Tiempo estimado:** 20 min

### Enunciado
OLS da R2 = 0.45 (punto unico).
1. Para 200 pares (alpha_i, beta_i) del posterior:
   calcula R2_i = 1 - Var(residuales_i) / Var(Y)
2. Histograma de R2: es una distribucion, no un punto
3. Media y HDI 95% de R2
4. P(R2 > 0.5)? P(R2 < 0.3)?
5. El R2 probabilistico es mas informativo que el puntual?
