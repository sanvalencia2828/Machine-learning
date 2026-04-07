# Script de Video -- Modulo 4C: Intervalos de Confianza, CAPM y la Trampa de Alpha
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Alpha que No Existia (8 min)

### [CAMARA]
"Un gestor de fondos te muestra que su alpha es 0.05% diario con un
intervalo de confianza del 95% de (0.01%, 0.09%). Parece significativo
porque el IC no incluye cero. Pero ese IC tiene tres errores de
interpretacion que la mayoria de profesionales desconoce. Hoy vamos
a desarmar esos errores, estimar el alpha y beta de Apple frente
al S&P 500, y ver por que los intervalos de confianza frecuentistas
son mucho menos informativos de lo que parecen."

### [SLIDE: 3 errores de interpretacion de un IC 95%]
1. NO significa "95% de probabilidad de que el parametro este aqui"
2. NO es una declaracion sobre ESTE intervalo especifico
3. NO incorpora conocimiento previo sobre alpha y beta

### [SLIDE: Lo que realmente significa]
"Si repitiera el experimento infinitas veces y calculara un IC cada vez,
el 95% de esos intervalos contendrian el valor real del parametro."
-> Responde una pregunta hipotetica, no la tuya.

---

## Segmento 2: CAPM -- Alpha y Beta con OLS (12 min)

### [SLIDE: Modelo de mercado (CAPM de un factor)]
```
r_AAPL = alpha + beta * r_SP500 + epsilon

alpha = retorno excedente (skill del gestor o anomalia)
beta = sensibilidad al mercado (riesgo sistematico)
epsilon = ruido idiosincratico
```

### [SCREENCAST: OLS con Statsmodels]
```python
import statsmodels.api as sm

# 1. Generar retornos sinteticos tipo AAPL vs SPY
# 2. sm.OLS(r_aapl, sm.add_constant(r_spy)).fit()
# 3. Leer summary():
#    - alpha: valor, SE, t-stat, p-value, IC 95%
#    - beta: valor, SE, t-stat, p-value, IC 95%
#    - R-squared, F-stat, Durbin-Watson
# 4. Graficar: scatter + linea OLS + banda de IC
```

### [SLIDE: Interpretacion practica del IC de alpha]
```
Alpha estimado: 0.020% diario
IC 95%: (-0.050%, 0.090%)

Pregunta: Tiene este activo alpha real?
NHST dice: "IC incluye 0 -> no significativo (p > 0.05)"
Realidad: el IC es ENORME comparado con el alpha
  (ancho = 0.14%, alpha = 0.02%)
  La senal es 7x mas chica que la incertidumbre
```

### [CAMARA]
"Mira ese IC. Incluye valores negativos (-0.05%) y positivos (0.09%).
Es como decir 'el gestor tal vez gana, tal vez pierde, no tenemos idea'.
Y sin embargo, muchos reportes financieros usan exactamente este
framework para declarar que un fondo 'tiene alpha'."

---

## Segmento 3: IC de la Prediccion vs IC del Parametro (10 min)

### [SLIDE: Dos tipos de IC en OLS]
```
IC del parametro (confidence interval):
  beta esta en (1.10, 1.40) con 95% de cobertura
  -> Precision de la estimacion de beta

IC de la prediccion (prediction interval):
  El proximo retorno de Apple estara en (-3.5%, +3.8%)
  -> Rango de donde puede caer la proxima observacion

El IC de prediccion es MUCHO mas ancho que el del parametro
porque incluye la incertidumbre del ruido (epsilon)
```

### [SCREENCAST: Visualizar ambos]
```python
# Grafico: scatter + linea OLS
# Banda estrecha: IC del parametro (beta)
# Banda ancha: IC de la prediccion
# La prediccion es practicamente inutil (banda gigante)
```

### [CAMARA]
"El IC del parametro te dice que beta es ~1.25 con buena precision.
Pero el IC de la prediccion te dice que el retorno de manana puede
ser cualquier cosa entre -3.5% y +3.8%. Es una prediccion? No.
Es una confesion de ignorancia disfrazada de precision."

---

## Segmento 4: La Alternativa -- Intervalos Credibles (12 min)

### [SLIDE: IC frecuentista vs intervalo credible bayesiano]
| Propiedad | IC frecuentista | Intervalo credible |
|-----------|----------------|-------------------|
| Interpretacion | Cobertura en repeticiones | P(parametro en intervalo) |
| Incorpora prior | NO | SI |
| Con 5 datos | Muy ancho pero "valido" | Se encoge con prior |
| Responde | "Que pasaria si repito" | "Que creo dado lo que vi" |

### [SCREENCAST: Comparar con datos financieros]
```python
# Mismo dataset: AAPL vs SPY sintetico
# 1. IC frecuentista de alpha y beta
# 2. Intervalo credible bayesiano con prior N(0, 0.001) para alpha
# 3. El prior "encoge" alpha hacia 0 (escepticismo razonable)
# 4. Resultado: el bayesiano es mas honesto con poca evidencia
```

### [CAMARA]
"El intervalo credible responde TU pregunta: 'dado lo que vi, donde
probablemente esta beta?' El IC frecuentista responde una pregunta
hipotetica sobre repeticiones infinitas. En finanzas, tu tomas UNA
decision. Necesitas la respuesta bayesiana."

---

## Segmento 5: Cierre -- La Trampa de Alpha (8 min)

### [SLIDE: Por que la busqueda de alpha es una trampa estadistica]
1. El alpha real es probablemente cercano a 0 (eficiencia de mercado)
2. Los IC frecuentistas son demasiado anchos para detectar alphas reales
3. Si pruebas muchos activos, la falacia del fiscal garantiza falsos positivos
4. Los diagnosticos OLS fallan con datos financieros (fat tails)
5. Sin ajustar por base rate, "alpha significativo" es espejismo

### [SLIDE: Checklist anti-trampa]
1. Ejecuta diagnosticos ANTES de confiar en p-values
2. Reporta IC de prediccion (no solo de parametro) para honestidad
3. Ajusta por multiple testing si evaluaste multiples activos
4. Usa priors escepticos: alpha ~ N(0, sigma_pequena)
5. El IC no te dice P(alpha > 0) -- el intervalo credible SI

### [CTA]
"Toma un activo que crees que tiene alpha. Calcula el OLS vs S&P 500.
Mira el IC de alpha. Incluye 0? Ahora calcula el IC de PREDICCION.
Es util? Comparte tus resultados."

---

## Notas de Produccion
- Mostrar Statsmodels summary() con zoom en IC
- Animar las dos bandas (parametro vs prediccion)
- Comparacion lado a lado: IC vs intervalo credible
- source_ref: turn0browsertab744690698
