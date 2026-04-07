# Script de Video -- Modulo 3B: Conceptos Estadisticos y Critica a la Volatilidad
# Duracion estimada: 45 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- La Mentira de la Volatilidad (7 min)

### [CAMARA]
"Tu broker te dice que un activo tiene 20% de volatilidad. Suena
preciso, cientifico. Pero esa unica cifra esconde mas de lo que revela.
No distingue entre subidas y bajadas, ignora eventos extremos, y asume
que los retornos son simetricos. Hoy vamos a desarmar la volatilidad
y reemplazarla con algo mucho mas honesto: los cuatro momentos de una
distribucion."

### [SLIDE: Que te dice la volatilidad]
- Std de retornos = dispersion alrededor de la media
- Trata +10% y -10% como igualmente "riesgosos"
- Asume simetria y colas delgadas (Normal)
- Es el UNICO input del modelo Black-Scholes

### [SLIDE: Que NO te dice]
- Si las caidas son peores que las subidas (skewness)
- Si los eventos extremos son frecuentes (kurtosis)
- Si tu riesgo real es 5x peor de lo que sigma sugiere
- Si un crash de -22% en un dia es "imposible" o inevitable

### [CAMARA]
"Necesitamos mas que un numero. Necesitamos cuatro."

---

## Segmento 2: Los 4 Momentos de una Distribucion (12 min)

### [PIZARRA: Momento 1 -- Media (mu)]
```
mu = E[X] = (1/N) * sum(x_i)

- Centro de gravedad de la distribucion
- En finanzas: retorno esperado
- PROBLEMA: un promedio puede ser enganoso
  (el rio tiene 1m de profundidad promedio... pero te ahogas)
```

### [PIZARRA: Momento 2 -- Varianza / Desviacion Estandar]
```
sigma^2 = E[(X - mu)^2]
sigma = sqrt(sigma^2)

- Dispersion alrededor de la media
- En finanzas: "volatilidad"
- PROBLEMA: trata subidas y bajadas por igual
  (un activo que sube 50% y baja 50% tiene "alta volatilidad"
   pero los inversores solo temen la bajada!)
```

### [PIZARRA: Momento 3 -- Asimetria (Skewness)]
```
skew = E[((X - mu) / sigma)^3]

- skew = 0: simetrica (Normal)
- skew < 0: cola izquierda mas pesada (caidas extremas mas probables)
- skew > 0: cola derecha mas pesada
- S&P 500: skew ~ -0.5 (las caidas son peores que las subidas)
```

### [PIZARRA: Momento 4 -- Curtosis (Kurtosis)]
```
kurt = E[((X - mu) / sigma)^4]

- Normal: kurt = 3 (o exceso = 0)
- kurt > 3: "leptocurtica" -- colas pesadas, mas eventos extremos
- S&P 500: exceso de curtosis ~ 20-25
- Significa: eventos de 4+ sigma son ~100x mas frecuentes que bajo Normal
```

### [CAMARA]
"Ahora tienes 4 numeros, no 1. Media te dice el centro, volatilidad
la dispersion, skewness si las caidas son peores, y curtosis si los
extremos son frecuentes. Juntos cuentan la historia completa."

---

## Segmento 3: Demostracion -- Retornos NO son Normales (10 min)

### [SCREENCAST: Python demo]
```python
# 1. Generar retornos sinteticos tipo S&P 500 (Student-t nu=4)
# 2. Calcular los 4 momentos
# 3. QQ-plot: retornos vs Normal
# 4. Histograma con zoom en colas
# 5. Contar eventos > 3 sigma: esperados vs observados
```

### [SLIDE: La tabla que cambia todo]
| Metrica | Normal | S&P 500 (sintetico) | Ratio |
|---------|--------|---------------------|-------|
| Curtosis exceso | 0 | ~20 | 20x |
| P(> 3 sigma) | 0.27% | ~2-5% | 10-20x |
| P(> 5 sigma) | 0.00003% | ~0.1% | 3000x |
| Eventos -4 sigma en 50 anos | 0.2 | ~25 | 125x |

### [CAMARA]
"Mira esos numeros. El modelo Normal dice que un evento de 5 sigmas
ocurre una vez cada 14,000 anos. En mercados reales, ocurre cada
pocos anos. Confiar en la volatilidad es como usar un mapa que dice
que los acantilados no existen."

---

## Segmento 4: Valor Esperado vs Promedio -- No son lo Mismo (8 min)

### [SLIDE: Diferencia crucial]
```
Promedio muestral: x_bar = sum(x_i) / N
  -> Lo que calculaste con datos observados
  -> Depende de la muestra

Valor esperado: E[X] = integral(x * f(x) dx)
  -> Lo que obtendrias con infinitas observaciones
  -> Propiedad de la distribucion, no de la muestra
```

### [PIZARRA: El problema de la ergodicidad]
```
Ejemplo: lanzar moneda justa, +50% o -40%

Valor esperado de un lanzamiento: E[R] = 0.5*(+50%) + 0.5*(-40%) = +5%
Parece buen negocio!

Pero despues de 2 lanzamientos:
  +50% seguido de -40%: 1.5 * 0.6 = 0.90 (PERDISTE 10%)
  -40% seguido de +50%: 0.6 * 1.5 = 0.90 (PERDISTE 10%)

El valor esperado es positivo, pero el resultado REAL es negativo.
Esto es no-ergodicidad: el promedio del ensamble no es el promedio temporal.
```

### [CAMARA]
"Este ejemplo destruye la intuicion de que 'valor esperado positivo =
buena inversion'. En finanzas, TU recorres UNA trayectoria, no el
promedio de todas. Por eso necesitas distribuciones completas."

---

## Segmento 5: Cierre -- De Sigma a Distribuciones Completas (8 min)

### [SLIDE: Resumen de los 4 momentos]
| Momento | Nombre | Que mide | Normal asume |
|---------|--------|----------|-------------|
| 1 | Media | Centro | Cualquier valor |
| 2 | Varianza | Dispersion | Unico parametro de riesgo |
| 3 | Skewness | Asimetria | = 0 (simetrica) |
| 4 | Curtosis | Colas | = 3 (delgadas) |

### [SLIDE: Por que la volatilidad es insuficiente]
1. Ignora asimetria (skew < 0 en mercados reales)
2. Ignora colas pesadas (curtosis >> 3)
3. Trata subidas y bajadas como iguales
4. Subestima riesgo de eventos extremos por ordenes de magnitud

### [SLIDE: Alternativas a sigma]
- Distribucion completa (via MCS)
- VaR y Expected Shortfall (capturan colas)
- Downside deviation (solo cuenta perdidas)
- Distribuciones Student-t o de mezcla (capturan fat tails)

### [SLIDE: Conexion con el curso]
- Modulo 3: MCS propaga la distribucion completa, no solo sigma
- Modulo 2C: BSM falla porque usa sigma como unico input
- Modulo 7: Ensambles generativos producen distribuciones completas
- Modulo 8: Kelly usa la distribucion, no solo E[R]

### [CAMARA]
"La volatilidad no esta mal por ser imprecisa. Esta mal por ser
INCOMPLETA. Es como medir la salud de un paciente solo con la
temperatura. Necesitas el cuadro completo."

### [CTA]
"Ejercicio: descarga retornos historicos de un activo que tengas.
Calcula los 4 momentos. Si la curtosis es > 5, tu modelo Normal
esta mintiendo. Comparte tus numeros en la comunidad."

---

## Notas de Produccion
- Animar los 4 momentos como "capas" que se agregan
- Zoom interactivo en las colas del histograma
- Demo de ergodicidad con animacion de trayectorias
- source_ref: turn0browsertab744690698
