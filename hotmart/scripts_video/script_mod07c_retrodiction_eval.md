# Script de Video -- Modulo 7C: Retrodiccion, HMC y Evaluacion de PLEs
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Modelo que Sabe lo que No Sabe (7 min)

### [CAMARA]
"Un modelo OLS predice con la misma confianza si Apple sube 1% o 50%.
Un PLE de PyMC ensancha sus intervalos cuando le pides predecir algo
que no ha visto. Eso se llama 'el modelo conoce sus limitaciones'.
Hoy vamos a construir todo el pipeline: retrodiccion para verificar
que el modelo funciona, HMC para entrenamiento eficiente, y evaluacion
probabilistica para medir que tan bueno es realmente."

### [SLIDE: Pipeline completo del PLE]
```
1. Prior Predictive Check (retrodiccion previa)
   -> Los datos simulados desde los priors son plausibles?

2. Entrenamiento con HMC/NUTS
   -> Muestrear el posterior eficientemente

3. Posterior Predictive Check (retrodiccion posterior)
   -> Los datos de entrenamiento son plausibles bajo el posterior?

4. Prediction con incertidumbre
   -> Extrapolar con intervalos que se ensanchan

5. Evaluacion: R2 probabilistico + HDI
   -> Cuantificar que tan bueno es el modelo
```

---

## Segmento 2: Prior Predictive Check (10 min)

### [SCREENCAST]
```python
# ANTES de ver datos, simular del modelo:
with model:
    prior_pred = pm.sample_prior_predictive(500)

# Pregunta: los datos simulados son PLAUSIBLES?
# Si el prior genera retornos de +1000%: prior es malo
# Si genera retornos de -50% a +50%: prior es razonable
# Esto es RETRODICCION PREVIA
```

### [SLIDE: Por que importa]
- Un prior malo = modelo que aprende cosas erroneas
- La retrodiccion ANTES del entrenamiento detecta priors absurdos
- Es como "pre-vuelo" antes de despegar
- OLS no tiene equivalente: no tiene priors que verificar

---

## Segmento 3: HMC y Entrenamiento (12 min)

### [SLIDE: Metropolis vs HMC/NUTS]
```
Metropolis: camina aleatoriamente, acepta/rechaza
  -> Funciona pero es LENTO (alta autocorrelacion)

HMC (Hamiltonian MC): usa el GRADIENTE del log-posterior
  -> "Fisica de la pelota en el potencial"
  -> La pelota rueda hacia zonas de alta probabilidad
  -> Saltos grandes, baja autocorrelacion

NUTS (No-U-Turn Sampler): HMC que se ajusta solo
  -> Elige automaticamente cuantos pasos dar
  -> Es lo que PyMC usa por defecto
  -> No necesitas ajustar nada manualmente
```

### [SCREENCAST: Entrenamiento PyMC]
```python
with model:
    trace = pm.sample(
        draws=2000,      # Muestras por cadena
        tune=1000,       # Adaptacion (descartado)
        chains=4,        # 4 cadenas independientes
        target_accept=0.95,  # Tasa de aceptacion objetivo
    )
# Diagnosticos automaticos:
# - Rhat (convergencia entre cadenas)
# - ESS (tamano efectivo de muestra)
# - Divergencias (problemas geometricos)
```

---

## Segmento 4: Posterior Predictive y Extrapolacion (12 min)

### [SCREENCAST: Retrodiccion posterior]
```python
with model:
    post_pred = pm.sample_posterior_predictive(trace)

# Comparar datos reales vs datos simulados desde posterior
# Cobertura: ~95% de datos reales dentro del HDI 95%
# Si cobertura << 95%: modelo no ajusta bien
# Si cobertura >> 95%: modelo es demasiado conservador
```

### [SLIDE: El modelo reconoce sus limitaciones]
```
Prediccion en r_mkt = 0% (zona conocida):
  HDI: (-1.5%, +1.8%) -> ancho 3.3%

Prediccion en r_mkt = +5% (fuera de muestra):
  HDI: (-3.2%, +8.5%) -> ancho 11.7%  (3.5x mas ancho!)

Prediccion en r_mkt = +10% (extrapolacion extrema):
  HDI: (-6.1%, +15.2%) -> ancho 21.3% (6.5x mas ancho!)

El modelo ENSANCHA sus intervalos cuando extrapola
OLS mantiene el mismo ancho -> falsa confianza
```

---

## Segmento 5: Evaluacion y Cierre (9 min)

### [SLIDE: R2 probabilistico]
```python
# Para cada muestra del posterior:
#   R2_i = 1 - Var(residuales_i) / Var(Y)
# Resultado: distribucion de R2, no punto unico

# OLS: R2 = 0.62
# PLE: R2 ~ N(0.61, 0.02), HDI (0.57, 0.65)
# P(R2 > 0.5) = 100%
# P(R2 > 0.7) = 0.3%
```

### [SLIDE: Checklist de evaluacion PLE]
1. Prior predictive: datos simulados plausibles?
2. Diagnosticos HMC: Rhat < 1.01, ESS > 400, 0 divergencias?
3. Posterior predictive: cobertura ~95%?
4. Extrapolacion: intervalos se ensanchan correctamente?
5. R2 probabilistico: distribucion razonable?

### [CTA]
"Construye tu PLE para un activo. Ejecuta las 5 verificaciones.
Si alguna falla, tienes un problema que OLS NUNCA te hubiera dicho."

---

## Notas de Produccion
- Prior predictive como "spaghetti plot antes de datos"
- Posterior predictive como "spaghetti plot despues de datos"
- Extrapolacion: zoom en los extremos mostrando ensanchamiento
- source_ref: turn0browsertab744690698
