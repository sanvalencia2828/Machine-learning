# Script de Video -- Modulo 7: Ensambles Generativos con PyMC
# Duracion estimada: 65 minutos (6 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- La Linea que Duda (8 min)

### [CAMARA]
"En OLS, obtienes UNA linea de regresion. En PML, obtienes MILES
de lineas, cada una igualmente plausible, y todas juntas forman
un ensamble generativo. Donde las lineas convergen, el modelo esta
seguro. Donde divergen, esta confesando su ignorancia. Eso es
infinitamente mas util que una sola linea con falsa precision."

### [SLIDE: OLS vs Probabilistic Linear Ensemble (PLE)]
```
OLS: Y = alpha + beta*X + epsilon
  -> UNA alpha, UNA beta, UN epsilon estimado
  -> IC via formulas asumiendo normalidad

PLE (PyMC):
  alpha ~ Normal(0, prior_sigma_alpha)
  beta ~ Normal(0, prior_sigma_beta)
  sigma ~ HalfStudentT(nu=4, sigma=prior_sigma)
  Y ~ StudentT(nu=6, mu=alpha + beta*X, sigma=sigma)
  -> DISTRIBUCION de alpha, beta, sigma
  -> Miles de lineas de regresion plausibles
```

---

## Segmento 2: OLS/MLE -- Lo que Ya Sabes y sus Limites (10 min)

### [SLIDE: Market Model OLS]
```
r_AAPL = alpha + beta * r_SP500 + epsilon

OLS da: alpha_hat, beta_hat, sigma_hat (puntos unicos)
IC 95%: asumen normalidad de residuales
R-squared: proporcion de varianza explicada

Problemas:
1. Residuales financieros NO son normales (fat tails)
2. IC son invalidos si residuales violan supuestos
3. No hay forma de incorporar conocimiento previo
4. Predicciones sin incertidumbre sobre parametros
```

### [SCREENCAST: OLS rapido con datos sinteticos]
```python
# Generar AAPL vs SP500 sinteticos
# Ajustar OLS
# Mostrar: IC clasicos, diagnosticos que fallan
# "Ya vimos esto en Modulo 4C. Ahora la alternativa."
```

---

## Segmento 3: Regresion Probabilistica con PyMC (15 min)

### [SCREENCAST: Construir el modelo PLE paso a paso]
```python
import pymc as pm

with pm.Model() as market_model:
    # Priors
    alpha = pm.Normal("alpha", mu=0, sigma=0.001)
    beta = pm.Normal("beta", mu=1, sigma=0.5)
    sigma = pm.HalfStudentT("sigma", nu=4, sigma=0.02)

    # Likelihood (Student-t para fat tails)
    mu = alpha + beta * X_data
    likelihood = pm.StudentT("returns", nu=6, mu=mu, sigma=sigma,
                             observed=Y_data)

    # Inferencia via NUTS (HMC)
    trace = pm.sample(2000, tune=1000, cores=2)
```

### [SLIDE: Que produce PyMC]
1. **Trace**: miles de muestras de (alpha, beta, sigma)
2. **Posterior summary**: media, HDI, Rhat, ESS
3. **Retrodiction**: genera datos sinteticos desde el posterior
4. **Prediction**: distribucion de retornos futuros
5. **Prior/Posterior predictive checks**: verificar el modelo

### [CAMARA]
"Fijate: en 10 lineas de codigo, PyMC te da todo lo que OLS no puede:
distribucion de parametros, incertidumbre propagada, likelihood con
fat tails, y diagnosticos automaticos. Eso es el poder de PML."

---

## Segmento 4: Intervalos Creibles vs Intervalos de Confianza (10 min)

### [SLIDE: Comparacion directa]
| Propiedad | IC Frecuentista | HDI Bayesiano |
|-----------|----------------|---------------|
| Interpretacion | Cobertura repetida | P(param en intervalo) |
| Con n=20 | Ancho por formula | Prior lo acota |
| Fat tails | Invalido | Usa Student-t likelihood |
| P(beta > 1) | No calculable | Directo: 1-CDF(1) |

### [SCREENCAST: Comparar lado a lado]
```python
# Posterior de beta: media, HDI
# OLS IC de beta: formula clasica
# Superponer ambos en un grafico
# Mostrar: P(beta > 1.0) directo del posterior
```

---

## Segmento 5: Ensambles Generativos -- Miles de Lineas (12 min)

### [SCREENCAST: Visualizar el ensamble]
```python
# 1. Extraer 200 pares (alpha_i, beta_i) del posterior
# 2. Para cada par: graficar la linea Y = alpha_i + beta_i * X
# 3. Resultado: "spaghetti plot" de 200 lineas
# 4. Donde convergen: alta certeza
# 5. Donde divergen: baja certeza (extrapolacion!)
# 6. El ensamble SABE que no sabe en los extremos
```

### [SLIDE: Retrodiction vs Prediction]
```
Retrodiction: P(Y_train | modelo ajustado)
  -> "Los datos de entrenamiento son plausibles bajo mi modelo?"
  -> Posterior Predictive Check sobre datos observados

Prediction: P(Y_nuevo | modelo, datos)
  -> "Que retorno espero manana?"
  -> Propaga TODA la incertidumbre (parametros + ruido)
  -> El intervalo se ENSANCHA en extrapolaciones
```

---

## Segmento 6: Cierre (10 min)

### [SLIDE: R-squared probabilistico]
```
R2_bayesiano = 1 - Var(residuales) / Var(Y)
  Pero con una DISTRIBUCION de R2, no un solo numero

Ejemplo:
  OLS: R2 = 0.45 (punto unico)
  PyMC: R2 ~ Normal(0.44, 0.03), HDI (0.38, 0.50)
  -> El R2 real podria ser tan bajo como 0.38
```

### [SLIDE: Conexion con Modulo 8]
- Modulo 8 usa las distribuciones predictivas de PyMC
  para calcular GVaR, GES, GTR y criterio de Kelly
- El ensamble generativo es el INPUT de las decisiones
- Sin PML: decisiones basadas en puntos. Con PML: basadas en distribuciones.

### [CTA]
"Instala PyMC (pip install pymc). Toma tu modelo OLS favorito.
Reescribelo como modelo PyMC. Compara los HDI con los IC clasicos."

---

## Notas de Produccion
- Mostrar spaghetti plot como animacion progresiva
- Prior predictive vs posterior predictive lado a lado
- PyMC summary con colores en Rhat y ESS
- source_ref: turn0browsertab744690698
