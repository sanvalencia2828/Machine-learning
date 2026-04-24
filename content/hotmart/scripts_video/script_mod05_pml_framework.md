# Script de Video -- Modulo 5: El Framework de ML Probabilistico
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- La Pregunta que NHST No Puede Responder (8 min)

### [CAMARA]
"Un fondo de cobertura evalua un bono corporativo. Necesita saber:
cual es la probabilidad de que este bono haga default? NHST no puede
responder. Los intervalos de confianza no pueden responder. Pero la
regla de probabilidad inversa si. Hoy vamos a construir, paso a paso,
el framework que responde la pregunta correcta en finanzas."

### [SLIDE: La regla de probabilidad inversa (Bayes)]
```
P(theta | datos) = P(datos | theta) * P(theta) / P(datos)

posterior = likelihood * prior / marginal likelihood

Cada termino tiene un significado financiero:
  prior:      lo que sabes ANTES de ver datos
  likelihood: que tan compatibles son los datos con cada theta
  posterior:  lo que sabes DESPUES de ver datos
  marginal:   normalizacion (promedio sobre todos los theta posibles)
```

### [SLIDE: Comparacion con NHST]
| NHST | Bayesiano |
|------|-----------|
| P(datos \| H0) | P(theta \| datos) |
| Responde pregunta equivocada | Responde la pregunta correcta |
| No incorpora priors | Priors explicitos |
| Binario (acepta/rechaza) | Distribucion continua |

---

## Segmento 2: Cada Termino de la Regla Inversa (12 min)

### [PIZARRA: Prior -- P(theta)]
```
Lo que sabes ANTES de ver datos:
  - Conocimiento personal del analista
  - Datos historicos del sector
  - Consenso del mercado
  - Restricciones fisicas/logicas

Ejemplo bonos:
  Prior para P(default): Beta(2, 18) -> media 10%
  Basado en: tasa historica de default BBB ~ 10% en 10 anos
```

### [PIZARRA: Likelihood -- P(datos | theta)]
```
Que tan probable es observar estos datos si theta = X:
  - Funcion del modelo elegido
  - Conecta parametros con observaciones

Ejemplo bonos:
  12 bonos BBB, 1 hizo default:
  Likelihood: Binomial(k=1, n=12, p=theta)
```

### [PIZARRA: Posterior -- P(theta | datos)]
```
Lo que sabes DESPUES de ver datos:
  posterior = likelihood * prior / marginal

Ejemplo bonos:
  Prior: Beta(2, 18)
  Likelihood: Binomial(1, 12)
  Posterior: Beta(2+1, 18+11) = Beta(3, 29)
  Media posterior: 3/32 = 9.4%
  HDI 95%: (2.3%, 21.4%)
```

### [CAMARA]
"Fijate: empezamos con un prior de 10% de default. Vimos 1 default
en 12 bonos (8.3%). El posterior se mueve a 9.4% -- un compromiso
entre lo que sabiamos y lo que vimos. Esto es aprendizaje bayesiano."

---

## Segmento 3: Distribuciones Predictivas (10 min)

### [SLIDE: Dos tipos de prediccion]
```
Prior Predictive: P(datos_nuevos) = integral P(datos|theta) * P(theta) d(theta)
  "Que datos esperarias ANTES de ver evidencia?"
  -> Sanity check del modelo: los datos simulados son plausibles?

Posterior Predictive: P(datos_nuevos | datos_obs) = integral P(datos|theta) * P(theta|datos) d(theta)
  "Que datos esperarias DESPUES de ver evidencia?"
  -> Prediccion que PROPAGA incertidumbre parametrica
  -> Es lo que realmente necesitas para decisiones
```

### [SCREENCAST: Demo predictivas]
```python
# 1. Prior predictive: simular defaults con theta ~ Beta(2, 18)
# 2. Observar 1 default en 12 bonos
# 3. Posterior predictive: simular defaults con theta ~ Beta(3, 29)
# 4. Comparar las distribuciones
# 5. La posterior predictive es mas concentrada (aprendio de datos)
```

### [CAMARA]
"La distribucion predictiva posterior NO es un solo numero. Es una
distribucion completa de posibles futuros. Cada futuro viene con su
probabilidad. Eso es infinitamente mas util que un punto."

---

## Segmento 4: Caso Completo -- Default de Bonos Corporativos (12 min)

### [SCREENCAST: Notebook en vivo]
```python
# Escenario: fondo de cobertura evaluando cartera de bonos high-yield
#
# 1. Prior: Beta(2, 8) -> media 20% (high-yield default rate)
# 2. Datos: portafolio de 20 bonos, 3 defaults observados
# 3. Posterior: Beta(2+3, 8+17) = Beta(5, 25) -> media 16.7%
# 4. HDI 95%: ~(5.8%, 31.5%)
# 5. P(default > 25%) = ??? (respuesta directa!)
# 6. Prior predictive vs posterior predictive
# 7. Actualizacion secuencial: agregar mas datos
```

### [SLIDE: Actualizacion secuencial]
```
Trimestre 1: 3/20 defaults -> Beta(5, 25), media 16.7%
Trimestre 2: 1/20 mas     -> Beta(6, 44), media 12.0%
Trimestre 3: 0/20 mas     -> Beta(6, 64), media 8.6%
Trimestre 4: 2/20 mas     -> Beta(8, 82), media 8.9%

El modelo APRENDE trimestralmente.
No necesitas re-entrenar desde cero.
```

---

## Segmento 5: Cierre -- Conexion con el Curso (8 min)

### [SLIDE: El framework PML completo]
1. **Prior**: codifica conocimiento financiero
2. **Likelihood**: conecta parametros con datos
3. **Posterior**: distribucion de parametros actualizada
4. **Predictive**: distribucion de futuros observables
5. **Decision**: usa la predictive para tomar decisiones

### [SLIDE: Conexion con modulos]
- Modulo 6: MLE = posterior sin prior (varianza maxima)
- Modulo 7: PyMC automatiza todo esto (MCMC)
- Modulo 8: Kelly criterion usa la posterior predictive

### [CTA]
"Elige un activo de tu portafolio. Define un prior para su retorno
esperado. Observa 30 dias de datos. Actualiza tu posterior. Como
cambio tu estimacion? Comparte."

---

## Notas de Produccion
- Animar la regla de Bayes como flujo: prior -> datos -> posterior
- Mostrar la actualizacion secuencial como animacion
- Graficos prior vs posterior superpuestos
- source_ref: turn0browsertab744690698
