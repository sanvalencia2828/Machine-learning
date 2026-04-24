# Script de Video -- Modulo 4: Peligros de la Estadistica Convencional
# Duracion estimada: 55 minutos (6 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- La Ciencia Rota (7 min)

### [CAMARA]
"En 2005, John Ioannidis publico un paper titulado 'Why Most Published
Research Findings Are False'. No fue una opinion -- fue una demostracion
matematica. La mayoria de la investigacion cientifica que usa p-values
esta equivocada. Y si la ciencia medica tiene este problema, imaginate
las finanzas, donde los datos son mas ruidosos, las muestras mas
pequenas, y los incentivos para manipular resultados son enormes."

### [SLIDE: El problema en numeros]
- Mas del 50% de hallazgos publicados con NHST no se replican
- En finanzas: la mayoria de "anomalias" desaparecen fuera de muestra
- El p-value de 0.05 NO significa lo que la gente cree que significa

### [SLIDE: Que aprenderemos]
1. La falacia inversa que subyace en NHST
2. La falacia del fiscal: confundir P(datos|H0) con P(H0|datos)
3. La falacia del abogado defensor: ignorar la tasa base
4. Por que los intervalos de confianza no significan lo que dicen
5. Como construir un modelo OLS para Apple y por que los tests fallan

---

## Segmento 2: La Falacia Inversa (10 min)

### [PIZARRA: El error fundamental de NHST]
```
NHST calcula:  P(datos | H0 es cierta)
Tu preguntas:  P(H0 es cierta | datos)

Estas NO son lo mismo!

Ejemplo:
  P(llueve | hay nubes) = 0.30
  P(hay nubes | llueve) = 0.99

  Confundir estas dos es la FALACIA INVERSA
```

### [SLIDE: En NHST]
```
H0: "No hay efecto" (el medicamento no funciona, el alpha es 0)
p-value = P(datos tan extremos | H0 cierta) = 0.03

Error comun: "Hay solo 3% de probabilidad de que H0 sea cierta"
Correcto: "Si H0 fuera cierta, estos datos tendrian 3% de prob"

La diferencia es ENORME y tiene consecuencias devastadoras
```

### [CAMARA]
"El p-value responde una pregunta que NADIE hizo. Tu quieres saber
si tu estrategia funciona. El p-value te dice que tan raro seria
ver estos resultados si la estrategia NO funcionara. Son preguntas
completamente diferentes."

---

## Segmento 3: Falacias del Fiscal y del Abogado Defensor (10 min)

### [SLIDE: Falacia del fiscal (Prosecutor's fallacy)]
```
Escenario: un sospechoso tiene un perfil de ADN raro (1 en 1,000,000)
Fiscal: "La probabilidad de que sea inocente es 1 en 1,000,000"

INCORRECTO. Si la ciudad tiene 10 millones de personas:
  - ~10 personas tienen ese perfil
  - P(inocente | match ADN) = 9/10 = 90%

El fiscal confunde P(match | inocente) con P(inocente | match)
```

### [SLIDE: En finanzas]
```
Backtesting una estrategia:
  p-value = 0.01 (parece muy significativa)

Pero si probaste 100 estrategias diferentes:
  P(al menos una con p<0.01 | todas nulas) = 1 - 0.99^100 = 63%

¡63% de probabilidad de encontrar un "hallazgo" por azar!
Esto es data mining / p-hacking
```

### [SLIDE: Falacia del abogado defensor (Defense attorney's fallacy)]
```
Abogado: "El match de ADN ocurre en 10 de 10M personas.
          Mi cliente es solo 1 de 10. No es evidencia."

INCORRECTO: ignora toda la evidencia adicional
  (motivo, oportunidad, testimonio)

En finanzas: ignorar la tasa base de estrategias que funcionan
  Si solo 1% de estrategias generan alpha real,
  incluso un p-value de 0.01 da solo 50-50
```

### [CAMARA]
"Ambas falacias son caras opuestas del mismo error: ignorar la
tasa base. En finanzas, la tasa base de estrategias que REALMENTE
funcionan es probablemente menor al 1%. Tu p-value tiene que
superar ese umbral, y 0.05 no es ni remotamente suficiente."

---

## Segmento 4: Intervalos de Confianza -- 3 Errores (8 min)

### [SLIDE: Lo que la gente CREE que es un IC 95%]
"Hay 95% de probabilidad de que el parametro real este en este intervalo"

### [SLIDE: Lo que REALMENTE es un IC 95%]
"Si repitiera el experimento infinitas veces y calculara un IC cada vez,
el 95% de esos intervalos contendrian el parametro real"

### [PIZARRA: 3 errores de interpretacion]
```
Error 1: "El parametro tiene 95% de prob de estar en el IC"
  -> FALSO. El parametro es fijo; el IC es aleatorio.

Error 2: "Si el IC no incluye 0, el efecto es significativo"
  -> Equivale a NHST. Mismos problemas.

Error 3: "El ancho del IC mide mi incertidumbre"
  -> Solo mide la precision de la estimacion puntual.
  -> NO incorpora conocimiento previo ni modelo uncertainty.
```

### [CAMARA]
"El intervalo de confianza es una herramienta frecuentista que
responde una pregunta contrafactual: 'que pasaria si repitiera
infinitas veces?' Pero tu NO vas a repetir. Necesitas una respuesta
para ESTA vez. Eso requiere intervalos credibles, no de confianza."

---

## Segmento 5: Demo -- Modelo OLS para Apple y Tests Diagnosticos (12 min)

### [SCREENCAST: Notebook en vivo]
```python
# 1. Generar retornos sinteticos tipo Apple vs S&P 500
# 2. Ajustar modelo de mercado OLS: r_apple = alpha + beta * r_sp500
# 3. Examinar:
#    - p-value de alpha (¿hay alpha estadisticamente significativo?)
#    - p-value de beta
#    - R-squared
# 4. Tests diagnosticos:
#    - Jarque-Bera (normalidad de residuales)
#    - Breusch-Pagan (heterocedasticidad)
#    - Durbin-Watson (autocorrelacion)
# 5. TODOS los supuestos de OLS se violan -> los p-values no son validos
```

### [SLIDE: Resultados]
- Alpha parece "significativo" (p < 0.05)
- Pero residuales NO son normales (Jarque-Bera rechaza)
- Heterocedasticidad presente (Breusch-Pagan rechaza)
- Autocorrelacion en volatilidad (Durbin-Watson marginal)
- Los p-values asumen todo OK -> si los supuestos fallan, p-values mienten

---

## Segmento 6: Cierre -- La Alternativa Bayesiana (8 min)

### [SLIDE: NHST vs Bayesiano]
| Pregunta | NHST | Bayesiano |
|----------|------|-----------|
| Que calcula | P(datos \| H0) | P(hipotesis \| datos) |
| Incorpora prior | NO | SI |
| Resultado | Acepta/rechaza binario | Distribucion de plausibilidad |
| Incertidumbre | IC frecuentista | Intervalo credible |
| Multiple testing | Requiere correccion | Incorporado naturalmente |

### [SLIDE: Conexion con el curso]
- Modulo 5: La regla de probabilidad inversa (lo que NHST deberia usar)
- Modulo 6: MLE vs enfoque probabilistico (MLE = NHST extendido)
- Modulo 7: PyMC produce intervalos credibles, no de confianza

### [CTA]
"La proxima vez que alguien te muestre un p-value de 0.05, preguntale:
cuantas hipotesis probaste? Cual es la tasa base? Los residuales
son normales? Si no puede responder, el p-value no significa nada."

---

## Notas de Produccion
- Animar la falacia del fiscal con dados/urnas
- Mostrar p-hacking en vivo: probar 100 estrategias hasta que una sea p<0.05
- Tabla NHST vs Bayesiano como build progresivo
- source_ref: turn0browsertab744690698
