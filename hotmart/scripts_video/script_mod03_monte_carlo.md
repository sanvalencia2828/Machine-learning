# Script de Video -- Modulo 3: Simulacion Monte Carlo para Incertidumbre
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- Pi con Dardos Aleatorios (8 min)

### [CAMARA]
"Voy a estimar Pi lanzando dardos al azar. Suena absurdo, pero este
mismo metodo se usa para valorar derivados financieros, evaluar
proyectos de inversion y cuantificar riesgo de portafolio. Se llama
simulacion Monte Carlo y es la herramienta mas versatil de las finanzas
cuantitativas."

### [SCREENCAST: Demo en vivo]
```python
# Estimar Pi con 10, 100, 1000, 10000 puntos aleatorios
# Graficar convergencia a 3.14159...
# Mostrar que MCS funciona aunque NO conozcas la formula analitica
```

### [SLIDE: Que es MCS]
- Generar miles de escenarios aleatorios
- Propagar incertidumbre a traves de un modelo
- Obtener una DISTRIBUCION de resultados, no un numero
- Fundado por Von Neumann y Ulam (Proyecto Manhattan, 1940s)

### [CAMARA]
"MCS no predice EL futuro. Simula MUCHOS futuros posibles y te dice
cuales son probables y cuales no. Eso es infinitamente mas util que
una prediccion puntual."

---

## Segmento 2: Fundamentos Estadisticos (12 min)

### [SLIDE: Los 4 momentos de una distribucion]
1. **Media** (mu): centro de la distribucion
2. **Varianza/Std** (sigma): dispersion alrededor de la media
3. **Asimetria** (skewness): cola izquierda vs derecha
4. **Curtosis** (kurtosis): peso de las colas

### [PIZARRA: Por que la volatilidad es absurda como medida de riesgo]
```
Volatilidad (sigma):
  - Trata subidas y bajadas como igualmente "riesgosas"
  - Asume distribucion simetrica
  - No distingue entre colas leves y pesadas
  - Un activo con +10% y -10% tiene "mismo riesgo" que +1% y -1%

Realidad:
  - Los inversores solo temen las BAJADAS
  - Retornos financieros son ASIMETRICOS (skew negativo)
  - Las colas son PESADAS (curtosis >> 3)
  - La volatilidad subestima el riesgo real
```

### [SLIDE: S&P 500 no es Normal]
- Curtosis historica: ~25 (Normal = 3)
- Skewness: negativa (caidas son mas extremas que subidas)
- Black Monday 1987: -22% (imposible bajo Normal)
- Implicacion: cualquier modelo que asuma normalidad subestima riesgo

### [SCREENCAST: QQ-plot]
```python
# Generar QQ-plot de retornos sinteticos
# Mostrar como las colas se desvian de la linea de 45 grados
# Comparar Normal vs Student-t
```

---

## Segmento 3: Ley de Grandes Numeros y Teorema Central del Limite (10 min)

### [SLIDE: LGN -- Fundamento de MCS]
- Promedio muestral converge al valor esperado con mas muestras
- MCS funciona PORQUE la LGN garantiza convergencia
- Mas simulaciones = mejor estimacion (tasa: 1/sqrt(N))
- 10,000 sims: error ~ 1%; 1,000,000 sims: error ~ 0.1%

### [PIZARRA: TLC -- Por que funciona con cualquier distribucion]
```
Promedios de N observaciones ~ Normal
  INDEPENDIENTEMENTE de la distribucion original

Esto significa:
  - Puedes usar MCS con Student-t, Log-normal, mezclas...
  - Los intervalos de confianza del promedio son validos
  - PERO: el TLC NO dice que los datos individuales son normales!
  - Error comun: confundir "promedios normales" con "datos normales"
```

### [SCREENCAST: Convergencia MCS]
```python
# Simular media con 10, 100, 1000, 10000 iteraciones
# Mostrar como el error baja con sqrt(N)
# Verificar TLC: histograma de medias muestrales es Normal
```

### [CAMARA]
"LGN dice: con suficientes simulaciones, tu estimacion converge.
TLC dice: el error de tu estimacion es Normal. Juntas te dan la
garantia teorica de que MCS funciona."

---

## Segmento 4: MCS Aplicado -- Valoracion de Proyecto de Software (12 min)

### [SCREENCAST: Abrir notebook]
```python
# notebook_ch03_monte_carlo_finance.md
# 1. Definir factores de riesgo del proyecto:
#    - Costo de desarrollo: Triangular(50K, 80K, 120K)
#    - Tiempo al mercado: LogNormal(12 meses, 4 meses)
#    - Tasa de adopcion: Beta(2, 5) -- sesgo optimista
#    - Ingreso por usuario: Normal(50, 15)
# 2. Simular 50,000 escenarios
# 3. Calcular distribucion de NPV
# 4. P(NPV > 0) = probabilidad de exito del proyecto
# 5. VaR del proyecto = peor escenario al 95%
```

### [SLIDE: Resultados clave]
- NPV medio: $X (pero un solo numero NO es util)
- P(NPV > 0): Y% -- probabilidad real de exito
- VaR 95%: -$Z -- peor caso razonable
- La distribucion completa > cualquier estimacion puntual

### [SLIDE: Sensibilidad -- Que factor importa mas?]
- Correlation plot: NPV vs cada factor de riesgo
- El factor con mayor correlacion = el que mas impacta
- Ejemplo tipico: tiempo al mercado domina (delay kills startups)

### [CAMARA]
"Mira lo que acabamos de hacer: en vez de un numero magico de NPV,
tenemos una DISTRIBUCION. Podemos decir 'hay 65% de probabilidad de
que el proyecto sea rentable, pero un 10% de probabilidad de perder
mas de $200K.' Eso es MCS."

---

## Segmento 5: Cierre + Conexion con PML (8 min)

### [SLIDE: MCS como forward propagation]
- MCS propaga incertidumbre HACIA ADELANTE:
  parametros inciertos --> distribucion de resultados
- PML (regla inversa) propaga HACIA ATRAS:
  datos observados --> distribucion de parametros
- MCS = forward | PML = inverse
- Juntos forman el ciclo completo de inferencia probabilistica

### [SLIDE: Resumen]
1. MCS simula miles de escenarios para obtener distribuciones
2. La volatilidad es insuficiente -- usa los 4 momentos
3. Los retornos financieros NO son normales (fat tails, skew)
4. LGN + TLC garantizan que MCS converge
5. MCS da distribuciones completas, no estimaciones puntuales

### [SLIDE: Conexion con el resto del curso]
- Modulo 2C: BSM asume normalidad -- MCS la reemplaza
- Modulo 5: MCS como generador de distribuciones predictivas
- Modulo 7: PyMC usa MCS (MCMC) para inferencia inversa
- Modulo 8: Kelly criterion usa MCS para simular trayectorias

### [CAMARA]
"MCS es la navaja suiza de las finanzas cuantitativas. Si hay
un solo metodo que deberias dominar, es este. Todo lo que sigue
en el curso lo usa."

### [CTA]
"Ejercicio: elige un proyecto o inversion que estes evaluando.
Define 3 factores de riesgo con distribuciones. Simula 10,000
escenarios. Cual es la probabilidad de exito? Comparte en la comunidad."

---

## Notas de Produccion
- Demo de Pi con animacion de puntos cayendo
- Graficos en vivo: convergencia, QQ-plot, histograma NPV
- Usar datos sinteticos -- no datos con copyright
- Mostrar codigo en VS Code/Colab (tema oscuro, fuente 16pt)
- source_ref: turn0browsertab744690698
