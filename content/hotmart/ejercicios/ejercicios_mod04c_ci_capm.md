# Ejercicios Practicos -- Modulo 4C: IC, CAPM y la Trampa de Alpha
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: IC de Alpha y Beta con Statsmodels

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Genera retornos sinteticos: r_asset = 0 + 1.0 * r_mkt + ruido Normal.
(Alpha real = 0, Beta real = 1.0)

1. Ajusta OLS con `sm.OLS(y, sm.add_constant(x)).fit()`
2. Lee `modelo.conf_int()` para alpha y beta
3. El IC de alpha incluye 0? (Deberia, alpha real = 0)
4. Repite 100 veces. En cuantas el IC de alpha NO incluye 0? (~5%)
5. Esas ~5 veces son "falsos descubrimientos de alpha"

---

## Ejercicio 2: IC Parametro vs IC Prediccion

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Con el mismo modelo OLS de AAPL vs SPY:
1. Calcula `modelo.get_prediction(X).conf_int()` (IC parametro)
2. Calcula `modelo.get_prediction(X).conf_int(obs=True)` (IC prediccion)
3. Grafica ambos sobre el scatter
4. Calcula el ancho medio de cada uno
5. El IC de prediccion es util para trading? Por que no?

### Pregunta clave
Si el IC de prediccion del retorno de manana es (-3.5%, +3.8%),
que decision de inversion tomarias? Que te dice eso sobre la
utilidad practica de este modelo?

---

## Ejercicio 3: Cobertura Empirica de IC

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Simula el "experimento repetido" que define un IC:
1. Fija mu_real = 8% (retorno anual esperado)
2. Genera 10,000 muestras de n=20 retornos anuales (sigma=15%)
3. Para cada muestra, calcula IC 95% para mu
4. Cuenta: que % de los ICs contiene mu_real?
5. Repite con n=5. Cambia la cobertura? Por que?

```python
# Con n pequeno y datos no-normales (Student-t),
# la cobertura del IC clasico puede ser < 95%
# Prueba con np.random.standard_t(5, n) * sigma + mu
```

---

## Ejercicio 4: Bayesiano vs Frecuentista para Alpha

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Implementa el modelo bayesiano Normal-Normal para estimar alpha:

Prior: alpha ~ N(0, sigma_prior)
Datos: alpha_MLE ~ N(alpha, SE_alpha)
Posterior: Normal conjugada

1. Con sigma_prior = 0.001 (esceptico): calcula posterior y HDI
2. Con sigma_prior = 0.01 (no informativo): calcula posterior
3. Con sigma_prior = 0.0001 (muy esceptico): calcula posterior
4. Cual prior da un resultado mas "honesto"?
5. Calcula P(alpha > 0) para cada prior

```python
# Normal-Normal conjugado:
tau_prior = 1 / sigma_prior**2
tau_data = 1 / SE_alpha**2
tau_post = tau_prior + tau_data
mu_post = (tau_prior * 0 + tau_data * alpha_MLE) / tau_post
sigma_post = 1 / np.sqrt(tau_post)
```

---

## Ejercicio 5: Mini-Proyecto -- Compara Betas de AAPL, MSFT, TSLA

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Genera retornos sinteticos para 3 activos con betas diferentes:
- AAPL: beta = 1.2
- MSFT: beta = 0.9
- TSLA: beta = 1.8

Para cada uno:
1. Estima OLS y obtiene IC 95% de beta
2. Los IC se solapan? Puedes distinguir las betas?
3. Cuantos dias de datos necesitas para que los IC NO se solapen?
4. Grafifica los 3 IC en un forest plot

---

## Ejercicio 6 (Bonus): IC con Bootstrap

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
El IC clasico asume normalidad de residuales.
Bootstrap no asume nada sobre la distribucion.

1. Ajusta OLS a datos con fat tails (Student-t residuales)
2. Bootstrap: resample 1000 veces, reajusta OLS cada vez
3. IC bootstrap = percentiles 2.5% y 97.5% de las estimaciones
4. Compara IC bootstrap vs IC clasico
5. Cual es mas ancho? Cual es mas honesto?

```python
betas_bootstrap = []
for _ in range(1000):
    idx = np.random.choice(n, n, replace=True)
    X_boot = sm.add_constant(r_spy[idx])
    modelo_boot = sm.OLS(r_aapl[idx], X_boot).fit()
    betas_bootstrap.append(modelo_boot.params[1])
ci_boot = np.percentile(betas_bootstrap, [2.5, 97.5])
```
