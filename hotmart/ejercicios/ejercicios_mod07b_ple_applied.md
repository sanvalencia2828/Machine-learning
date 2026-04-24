# Ejercicios Practicos -- Modulo 7B: PLE Aplicado
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Jensen's Alpha para 3 Fondos

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera retornos para 3 fondos con diferentes alphas:
- Fondo A: alpha=0.0003 (positivo leve)
- Fondo B: alpha=0 (sin alpha)
- Fondo C: alpha=-0.0002 (negativo leve)

Para cada uno (252 dias, beta=1.0):
1. Calcula P(alpha > 0) con posterior bayesiano
2. Cual fondo tiene evidencia de alpha real?
3. Con 50 datos en vez de 252, cambia la conclusion?

---

## Ejercicio 2: Cross-Hedging con Incertidumbre

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Tienes $5M en un activo con beta ~ N(1.3, 0.08).
1. Cuanto del indice necesitas vender para cubrir?
2. El rango HDI 95% del hedge es ($X, $Y). Calculalo.
3. Si usas el punto medio, cual es tu riesgo residual?
4. Si usas el limite superior del HDI, sobrecubres?

---

## Ejercicio 3: Market Neutral Test

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Un fondo long-short dice ser market neutral.
Datos: 120 dias, beta estimado = 0.15, SE = 0.08.
1. Posterior con prior N(0, 0.3): P(|beta| < 0.1)?
2. P(|beta| < 0.2)?
3. Es neutral al 90% de confianza?
4. Cuantos datos necesitarias para confirmarlo?

---

## Ejercicio 4: CAPM Probabilistico para DCF

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Valuacion DCF con r_e probabilistico:
- r_f = 4%, ERP = 6%
- beta posterior ~ N(1.15, 0.10)
1. Distribucion de r_e = r_f + beta * ERP
2. HDI 95% de r_e
3. Flujos futuros: $10M/ano por 10 anos
4. Calcula NPV con r_e fijo (OLS) vs distribucion de NPV
5. El rango de NPV cambia la decision de inversion?

---

## Ejercicio 5: ArviZ Completo (si PyMC disponible)

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Con PyMC + ArviZ:
1. `az.plot_trace(trace)` -- las cadenas convergen?
2. `az.plot_posterior(trace, ref_val={"alpha": 0})` -- alpha significativo?
3. `az.plot_forest([trace_aapl, trace_msft])` -- comparar 2 activos
4. `az.summary(trace)` -- Rhat < 1.01? ESS > 400?
5. `az.plot_pair(trace)` -- alpha y beta correlacionados?

---

## Ejercicio 6 (Bonus): R-squared Probabilistico

**Nivel:** Avanzado
**Tiempo estimado:** 20 min

### Enunciado
Para 200 muestras del posterior (alpha_i, beta_i):
1. Calcula R2_i para cada muestra
2. Histograma de R2
3. Media y HDI de R2
4. P(R2 > 0.5)?
5. Es mas informativo que el R2 puntual de OLS?
