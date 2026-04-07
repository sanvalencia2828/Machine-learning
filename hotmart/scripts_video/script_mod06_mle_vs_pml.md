# Script de Video -- Modulo 6: Peligros de la IA Convencional (MLE vs PML)
# Duracion estimada: 55 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- La IA que Predice con Total Confianza y se Equivoca (8 min)

### [CAMARA]
"Un modelo de deep learning predice que las ganancias de Tesla el
proximo trimestre seran exactamente $2.47 por accion. Sin barra de
error, sin incertidumbre, sin 'puede ser entre X e Y'. Solo un numero
con total confianza. Eso no es inteligencia -- es arrogancia
computacional. Hoy vamos a ver por que los modelos MLE y deep learning
fallan en finanzas, y que los hace peligrosos: no es que se equivoquen,
es que no SABEN que se equivocan."

### [SLIDE: MLE vs PML en una imagen]
```
MLE (Maximum Likelihood Estimation):
  Datos --> UN punto optimo de parametros --> UNA prediccion
  "El mejor ajuste posible" (pero sin incertidumbre)

PML (Probabilistic ML):
  Datos + Prior --> DISTRIBUCION de parametros --> DISTRIBUCION de predicciones
  "Muchos ajustes posibles, ponderados por plausibilidad"
```

### [SLIDE: 3 problemas de la IA convencional en finanzas]
1. **Predicciones puntuales sin incertidumbre** (sobreconfianza)
2. **Correlaciones espurias** (confunde correlacion con causalidad)
3. **Datasets pequenos** (MLE se sobreajusta con pocos datos)

---

## Segmento 2: MLE -- El Mejor Punto que Ignora Todo lo Demas (12 min)

### [PIZARRA: Que es MLE]
```
MLE busca: theta_hat = argmax P(datos | theta)

Solo maximiza el likelihood. No usa prior. No reporta incertidumbre.

Ejemplo: earnings de 5 trimestres = [2.1, 2.3, 2.0, 2.5, 2.2]
  MLE: mu_hat = 2.22, sigma_hat = 0.17
  Prediccion: "El proximo trimestre sera 2.22"
  Sin barra de error. Sin "podria ser entre 1.8 y 2.6".

PML con prior Normal(2.0, 0.5):
  Posterior: mu ~ Normal(2.18, 0.14)
  Prediccion: "El proximo trimestre sera 2.18 +/- 0.35 (HDI 95%)"
```

### [SCREENCAST: Demo MLE vs PML]
```python
# 1. Generar earnings sinteticos (5 trimestres)
# 2. MLE: punto unico
# 3. PML: distribucion posterior + predictive
# 4. Agregar un outlier (earnings surprise)
# 5. MLE se mueve drasticamente. PML es robusto.
```

### [CAMARA]
"Con 5 datos, MLE es un accidente esperando pasar. Un solo
trimestre anomalo mueve la estimacion 30%. PML con un prior
razonable se mueve solo 10%. El prior no es un sesgo --
es proteccion contra el ruido."

---

## Segmento 3: Correlaciones Espurias y Falta de Causalidad (10 min)

### [SLIDE: Correlaciones espurias reales]
- Divorcios en Maine vs consumo de margarina: r = 0.99
- Ahogamientos en piscina vs peliculas de Nicolas Cage: r = 0.67
- Gasto en ciencia vs suicidios: r = 0.99

### [SLIDE: En finanzas]
```
Con 100 variables y 252 dias de datos:
  Correlaciones posibles: 100*99/2 = 4,950
  Esperadas con |r| > 0.20 por azar: ~500
  Esperadas con |r| > 0.30 por azar: ~100
  Esperadas con |r| > 0.50 por azar: ~10

Un modelo de ML entrenado en estas 100 variables
ENCONTRARA patrones. Pero no seran reales.
```

### [SCREENCAST: Demo correlaciones espurias]
```python
# 1. Generar 50 series temporales aleatorias (sin relacion)
# 2. Calcular todas las correlaciones
# 3. Encontrar las "mejores" correlaciones
# 4. Graficar: parecen relaciones reales
# 5. Son COMPLETAMENTE espurias
```

### [CAMARA]
"El deep learning es un buscador de patrones. En datos financieros
ruidosos, encuentra patrones en el RUIDO. Sin un framework causal,
no puede distinguir senal de ruido. PML al menos te dice:
'la incertidumbre es enorme, no confies en esto'."

---

## Segmento 4: Grid Approximation y MCMC Metropolis (15 min)

### [SCREENCAST: Grid approximation]
```python
# Alternativa numerica a conjugados analiticos:
# 1. Definir grilla de valores para theta (0 a 1, paso 0.001)
# 2. Para cada theta: calcular prior * likelihood
# 3. Normalizar
# 4. Resultado: posterior discretizado
# Ventaja: funciona con cualquier prior y likelihood
# Desventaja: escala mal a >2 parametros
```

### [SCREENCAST: MCMC Metropolis]
```python
# Cuando grid no escala, usamos MCMC:
# 1. Empezar en theta_0 aleatorio
# 2. Proponer theta_nuevo = theta_actual + ruido
# 3. Calcular ratio = posterior(nuevo) / posterior(actual)
# 4. Si ratio > 1: aceptar siempre
# 5. Si ratio < 1: aceptar con probabilidad = ratio
# 6. Repetir 10,000+ veces
# 7. Las muestras aceptadas SON el posterior
```

### [SLIDE: MCMC para Student-t con colas pesadas]
```
Problema: estimar nu (grados de libertad) de retornos financieros
  Prior: nu ~ Exponential(1/30) -> media 30
  Likelihood: datos ~ Student-t(nu, mu, sigma)
  Posterior: no tiene forma cerrada -> MCMC!

Resultado: nu ~ 4-5 (confirma fat tails)
```

---

## Segmento 5: Cierre -- Por Que PML es Superior (10 min)

### [SLIDE: MLE vs PML -- tabla final]
| Dimension | MLE / Deep Learning | PML |
|-----------|-------------------|-----|
| Prediccion | Punto unico | Distribucion completa |
| Incertidumbre | No reporta | Cuantifica siempre |
| Datos pequenos | Overfitting severo | Prior regulariza |
| Correlaciones | Las encuentra (espurias o no) | Las pondera con incertidumbre |
| Causalidad | No distingue | Prior puede codificar estructura causal |
| Transparencia | Caja negra (DL) | Cada supuesto es explicito |

### [SLIDE: Conexion con el curso]
- Modulo 4: NHST/MLE comparten los mismos problemas
- Modulo 5: PML framework resuelve la pregunta correcta
- Modulo 7: PyMC automatiza MCMC para modelos complejos
- Modulo 8: Decisiones financieras usan distribuciones, no puntos

### [CTA]
"La proxima vez que alguien te de una prediccion puntual sin
incertidumbre, preguntale: que distribucion genero ese numero?
Si no puede responder, no es ML probabilistico."

---

## Notas de Produccion
- Animar MLE como "pico de una montana" vs PML como "toda la montana"
- Mostrar correlaciones espurias con humor (graficos absurdos)
- Demo MCMC en vivo: ver las cadenas converger
- source_ref: turn0browsertab744690698
