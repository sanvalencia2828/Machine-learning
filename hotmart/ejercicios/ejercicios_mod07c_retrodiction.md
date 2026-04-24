# Ejercicios Practicos -- Modulo 7C: Retrodiccion y Evaluacion
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Prior Predictive Check

**Nivel:** Basico  |  **Tiempo:** 20 min

Simula 200 datasets desde tus priors. Los retornos simulados
caen en (-10%, +10%)? Si no, ajusta los priors.

---

## Ejercicio 2: Posterior Predictive Check

**Nivel:** Intermedio  |  **Tiempo:** 25 min

Calcula cobertura: que % de datos reales cae dentro del HDI 95%
simulado desde el posterior. Si < 90%, el modelo no ajusta.

---

## Ejercicio 3: Extrapolacion y Ensanchamiento

**Nivel:** Intermedio  |  **Tiempo:** 25 min

Predice para r_mkt = 0%, +3%, +7%, +15%. Grafica el ancho del HDI
vs r_mkt. Es lineal? Exponencial?

---

## Ejercicio 4: R2 Probabilistico

**Nivel:** Avanzado  |  **Tiempo:** 25 min

Calcula distribucion de R2 con 2000 muestras del posterior.
P(R2 > 0.5)? P(R2 > 0.7)? Compara con R2 puntual de OLS.

---

## Ejercicio 5: Comparar Prior vs Posterior Predictive

**Nivel:** Avanzado  |  **Tiempo:** 30 min

Grafica lado a lado: datos simulados desde prior vs posterior.
El posterior es mas concentrado? Cuanto aprendio el modelo?

---

## Ejercicio 6 (Bonus): Checklist Completa

**Nivel:** Avanzado  |  **Tiempo:** 35 min

Ejecuta las 5 verificaciones del PLE para un activo de tu eleccion.
Reporta: prior check OK? Rhat? ESS? Cobertura? Extrapolacion? R2?
