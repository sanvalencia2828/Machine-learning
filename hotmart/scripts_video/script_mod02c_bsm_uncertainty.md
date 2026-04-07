# Script de Video -- Modulo 2C: Black-Scholes y la Trinidad de la Incertidumbre
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Nobel que Quebro un Hedge Fund (8 min)

### [CAMARA]
"En 1997, Scholes y Merton recibieron el Nobel por resolver el problema
de pricing de opciones. Un ano despues, su fondo LTCM colapso y casi
llevo al sistema financiero global con el. La formula que les dio el Nobel
es la misma que no vio venir la crisis. Hoy vamos a entender POR QUE
fallo, y que tipo de incertidumbre ignoro."

### [SLIDE: Black-Scholes-Merton: la formula]
- Publicada en 1973 por Black, Scholes y Merton
- Precio de una opcion europea: C = S*N(d1) - K*e^(-rT)*N(d2)
- Revoluciono los mercados de derivados
- Aun se usa como "benchmark" (pero nadie la usa literalmente)

### [SLIDE: Los 5 supuestos criticos de BSM]
1. Retornos log-normales (distribucion Gaussiana)
2. Volatilidad constante en el tiempo
3. Trading continuo sin costos de transaccion
4. No hay saltos ni discontinuidades
5. Tasa libre de riesgo constante

### [CAMARA]
"Cada uno de estos supuestos es falso en mercados reales. Y no son
aproximaciones inofensivas -- cada uno esconde un tipo diferente de
incertidumbre que la formula ignora. Veamos cual."

---

## Segmento 2: Black-Scholes -- Que Asume y Por Que Falla (12 min)

### [PIZARRA DIGITAL: La formula paso a paso]
```
C = S * N(d1) - K * e^(-rT) * N(d2)

d1 = [ln(S/K) + (r + sigma^2/2)*T] / (sigma * sqrt(T))
d2 = d1 - sigma * sqrt(T)

Donde:
  S = precio del activo
  K = strike
  T = tiempo al vencimiento
  r = tasa libre de riesgo
  sigma = volatilidad (CONSTANTE)
  N() = CDF de la Normal estandar
```

### [SLIDE: Evidencia contra BSM]
1. **Fat tails**: retornos reales tienen curtosis >> 3
   - S&P 500: curtosis historica ~25 (Normal = 3)
   - Crash de Oct 1987: -22% en un dia (25+ sigmas bajo Normal)
2. **Volatility smile**: el mercado NO usa una sola sigma
   - Opciones deep out-of-the-money son mas caras que BSM predice
   - El mercado "sabe" que las colas son pesadas
3. **Saltos**: gaps overnight, flash crashes
   - BSM asume paths continuos (movimiento Browniano)
   - Realidad: los precios saltan sin pasar por valores intermedios

### [SCREENCAST: Python demo rapida]
```python
# Comparar distribucion Normal vs retornos reales del S&P 500
# Mostrar que las colas pesadas generan eventos "imposibles" bajo BSM
# El crash de 1987 tendria probabilidad ~10^(-150) bajo Normal
```

### [CAMARA]
"El mercado de opciones ya sabe que BSM esta mal. Por eso existe la
volatility smile. Pero en vez de arreglar el modelo, la industria lo
parchea. Es como usar un mapa equivocado y corregir la ruta a mano.
Funciona... hasta que no funciona."

---

## Segmento 3: La Trinidad de la Incertidumbre (12 min)

### [SLIDE: Tres tipos de incertidumbre]
| Tipo | Descripcion | Ejemplo financiero | BSM la captura? |
|------|-------------|-------------------|-----------------|
| **Aleatoria** | Variabilidad de datos, irreducible | Retorno diario del S&P 500 | Parcialmente (asume Normal) |
| **Epistemica** | Ignorancia reducible con informacion | Volatilidad real vs estimada | NO (asume sigma conocida) |
| **Ontologica** | Cambio estructural, el mundo cambia | Flash crash, pandemia, default soberano | NO (asume estacionariedad) |

### [PIZARRA: Como BSM falla en cada tipo]
```
ALEATORIA:
  BSM dice: retornos ~ Normal(mu, sigma)
  Realidad: retornos ~ Student-t(nu~4) con colas pesadas
  Consecuencia: subestima riesgo de eventos extremos

EPISTEMICA:
  BSM dice: sigma es conocida y constante
  Realidad: sigma cambia con el tiempo (GARCH, regimenes)
  Consecuencia: el modelo no sabe lo que no sabe

ONTOLOGICA:
  BSM dice: el proceso generador de datos no cambia
  Realidad: crisis, regulacion, tecnologia cambian las reglas
  Consecuencia: el modelo no puede anticipar lo que nunca ha visto
```

### [SLIDE: Analogia -- los tres tipos en la vida real]
- **Aleatoria**: no sabes que carta sale del mazo (pero conoces el mazo)
- **Epistemica**: no sabes si el mazo esta completo (pero puedes revisarlo)
- **Ontologica**: alguien cambio el mazo por uno de Tarot a media partida

### [CAMARA]
"Los modelos financieros convencionales solo manejan incertidumbre
aleatoria -- y mal. La epistemica la ignoran pretendiendo que los
parametros son conocidos. Y la ontologica? Ni siquiera tienen un
framework para pensarla. El ML probabilistico aborda las tres."

---

## Segmento 4: Demo Interactiva -- BSM vs Realidad (12 min)

### [SCREENCAST: Abrir notebook]
```python
# notebook_ch02c_bsm_uncertainty_trinity.md / .ipynb
# 1. Implementar BSM pricing
# 2. Generar paths con Normal vs Student-t
# 3. Comparar precios de opciones bajo ambos modelos
# 4. Construir volatility smile sintetica
# 5. Mostrar como la incertidumbre epistemica amplifica el error
```

### [SLIDE: Resultados clave de la demo]
- BSM subprecia opciones OTM hasta 50% (colas pesadas)
- La volatility smile emerge naturalmente con Student-t
- Incertidumbre en sigma amplifica el error de pricing 2-3x
- Bajo cambio de regimen, BSM colapsa completamente

### [CAMARA]
"Fijate: no estamos diciendo que BSM es inutil. Es un benchmark.
Pero usarlo sin entender sus limitaciones es como conducir con GPS
en un camino que ya no existe. El ML probabilistico te da el mapa
actualizado Y te dice donde el mapa es menos confiable."

### [SLIDE: Visualizacion Plotly interactiva]
- Panel 1: BSM Normal vs Student-t (densidades + pricing)
- Panel 2: Volatility smile BSM vs mercado
- Panel 3: Trinidad de incertidumbre -- impacto en pricing

---

## Segmento 5: Cierre -- Implicaciones para tu Trading (6 min)

### [SLIDE: Resumen conceptual]
1. BSM asume normalidad, volatilidad constante y mercados continuos
2. Las tres fallas corresponden a tres tipos de incertidumbre
3. Aleatoria: reemplazar Normal por distribuciones con colas pesadas
4. Epistemica: tratar sigma como variable, no constante
5. Ontologica: stress testing y escenarios contrafactuales

### [SLIDE: Que hacer en la practica]
- NO uses BSM literalmente para pricing real
- USA distribuciones completas (Student-t, mezclas)
- CUANTIFICA tu incertidumbre sobre los parametros
- PREPARA escenarios para cambios de regimen
- El modelo probabilistico hace todo esto automaticamente

### [SLIDE: Conexion con el resto del curso]
- Modulo 3: MCS para propagar incertidumbre aleatoria
- Modulo 5: Regla inversa para reducir incertidumbre epistemica
- Modulo 7: Ensambles generativos que cuantifican las tres
- Modulo 8: Kelly criterion para decisiones bajo incertidumbre total

### [CAMARA]
"La proxima vez que alguien te cite un precio de BSM como si fuera
verdad revelada, preguntale: que tipo de incertidumbre estas ignorando?
Esa pregunta vale mas que cualquier formula."

### [CTA]
"Ejercicio: toma una opcion de tu watchlist. Calcula su precio con BSM
y luego con Student-t (nu=4). Cual es la diferencia? Eso mide cuanto
riesgo de cola estas ignorando. Comparte tu resultado en la comunidad."

---

## Notas de Produccion
- Insertar grafico de volatility smile real (CBOE) como referencia visual
- Animar la trinidad como diagrama de Venn con build progresivo
- Mostrar codigo en vivo con VS Code (tema oscuro, fuente 16pt)
- Usar datos sinteticos -- NO datos con copyright
- Mencionar crash de 1987 y LTCM como ejemplos historicos (sin citas largas)
- source_ref: turn0browsertab744690698
