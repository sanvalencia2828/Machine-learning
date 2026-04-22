# Script de Video -- Modulo 8: Decisiones Probabilisticas y Gestion de Capital
# Duracion estimada: 60 minutos (6 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Juego que Arruina al 86% (8 min)

### [CAMARA]
"Un juego te ofrece +50% o -40% con igual probabilidad. El valor
esperado es +5%. Parece buen negocio. Pero si juegas 100 veces,
el 86% de los jugadores pierde casi todo. Por que? Porque el valor
esperado es una mentira en procesos no-ergodicos. Hoy aprendemos
a tomar decisiones que funcionan para TU trayectoria individual,
no para un promedio ficticio."

### [SLIDE: Del ensamble a la decision]
```
Modulos 1-7: construir distribuciones predictivas
Modulo 8: USAR esas distribuciones para decidir

Decisiones clave:
  1. Cuanto capital asignar? (Kelly criterion)
  2. Cual es mi riesgo real? (GVaR, GES, GTR)
  3. Por que el valor esperado no funciona? (ergodicidad)
  4. Por que Markowitz falla? (ruina del inversor)
```

---

## Segmento 2: Ergodicidad -- Por Que E[R] Miente (10 min)

### [PIZARRA: Procesos ergodicos vs no-ergodicos]
```
Ergodico: promedio del ensamble = promedio temporal
  -> Lanzar dado muchas veces: media converge a 3.5

No-ergodico: promedio del ensamble != promedio temporal
  -> Juego +50%/-40%: E[R]=+5% pero mediana temporal = -5.1%
  -> La MAYORIA pierde, unos pocos ganan enormemente
  -> El promedio sube por los outliers, no por la experiencia tipica
```

### [SLIDE: 3 tipos de ruina]
1. **Ruina del apostador**: apuesta fija, capital finito, ruina segura
2. **Ruina del maximizador de E[R]**: apuesta todo, ruina rapida
3. **Ruina del inversor Markowitz**: optimiza varianza, ignora colas

---

## Segmento 3: GVaR, GES y GTR desde Distribuciones Predictivas (12 min)

### [SLIDE: Metricas generativas de riesgo]
```
FRECUENTISTA:
  VaR = percentil(retornos_historicos, alpha)
  ES = media(retornos < VaR)
  Problema: usa datos pasados, no propaga incertidumbre

GENERATIVO (PML):
  GVaR = percentil(posterior_predictive, alpha)
  GES = media(posterior_predictive < GVaR)
  GTR = P(retorno < umbral) desde posterior_predictive
  Ventaja: propaga TODA la incertidumbre parametrica + aleatoria
```

### [SCREENCAST: Calcular GVaR/GES]
```python
# 1. Generar 50,000 retornos desde posterior predictive
# 2. GVaR 95% = percentil 5% de retornos simulados
# 3. GES 95% = media de retornos < GVaR
# 4. GTR = P(retorno < -5%)
# Comparar con VaR/ES frecuentista clasico
```

---

## Segmento 4: Criterio de Kelly -- Asignacion Optima (15 min)

### [PIZARRA: Kelly criterion]
```
Kelly clasico (2 resultados):
  f* = (p * b - q) / b
  f* = fraccion optima del capital a apostar
  p = probabilidad de ganar
  b = ratio ganancia/perdida
  q = 1 - p

Kelly generalizado (distribucion continua):
  f* = argmax E[log(1 + f * R)]
  Maximiza la tasa de crecimiento GEOMETRICA
  No el retorno esperado (aritmetico)
```

### [SCREENCAST: Kelly con posterior predictive]
```python
# 1. Generar retornos desde posterior predictive
# 2. Para cada f (0 a 2 en pasos de 0.01):
#    calcular E[log(1 + f * R)]
# 3. f* = el que maximiza la tasa geometrica
# 4. Comparar: Kelly f* vs Markowitz optimo
# 5. Simular 1000 trayectorias con cada estrategia
```

### [SLIDE: Kelly vs Markowitz]
| Propiedad | Markowitz | Kelly |
|-----------|-----------|-------|
| Optimiza | Varianza (cuadratica) | Tasa geometrica (log) |
| Considera ergodicidad | NO | SI |
| Riesgo de ruina | Posible | Minimizado |
| Con fat tails | Subestima riesgo | Reduce asignacion |
| Horizonte | 1 periodo | Largo plazo |

---

## Segmento 5: Demo Completa -- Portafolio con PML (10 min)

### [SCREENCAST: Pipeline completo]
```python
# Datos: retornos sinteticos tipo S&P 500 (fat tails)
# 1. Posterior predictive: 50,000 retornos simulados
# 2. GVaR, GES, GTR
# 3. Kelly f*
# 4. Simular trayectorias: Kelly vs full invest vs Markowitz
# 5. Resultado: Kelly sobrevive, los otros no siempre
```

---

## Segmento 6: Cierre -- El Curso Completo (5 min)

### [SLIDE: Recorrido del curso]
```
Cap 1-2: Por que las finanzas necesitan PML
Cap 3: MCS propaga incertidumbre
Cap 4: NHST esta roto
Cap 5: La regla inversa (Bayes)
Cap 6: MLE falla, MCMC rescata
Cap 7: Ensambles generativos con PyMC
Cap 8: Decisiones con distribuciones completas
```

### [CTA]
"Toma tu portafolio. Genera la posterior predictive. Calcula GVaR.
Calcula Kelly f*. Compara con tu asignacion actual.
Si Kelly dice menos, probablemente estas asumiendo demasiado riesgo."

---

## Notas de Produccion
- Animar trayectorias: Kelly (verde) vs full invest (rojo)
- Mostrar el "abanico" de trayectorias divergentes
- GVaR vs VaR como lineas en histograma
- source_ref: turn0browsertab744690698
