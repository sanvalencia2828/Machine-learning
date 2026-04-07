# Script de Video -- Modulo 4B: NHST Aplicado -- OLS, Base Rates e Indicadores
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Indicador que Predijo 9 de las Ultimas 5 Recesiones (8 min)

### [CAMARA]
"Paul Samuelson dijo que el mercado de acciones ha predicho 9 de las
ultimas 5 recesiones. Suena a chiste, pero ilustra un problema real:
un indicador puede ser 'significativo' estadisticamente y aun asi
ser inutil en la practica. Hoy vamos a construir un framework para
evaluar indicadores economicos usando base rates, y vamos a ver por
que un modelo OLS con p < 0.05 puede ser completamente enganoso."

### [SLIDE: Tres casos practicos]
1. **Caso judicial**: falacia del fiscal con ADN + base rates
2. **Indicador de recesion**: P(senal|recesion) vs P(recesion|senal)
3. **Regresion OLS**: Apple vs S&P 500 con Statsmodels

### [SLIDE: El problema central]
- Un indicador con 90% de sensibilidad parece excelente
- Pero si las recesiones ocurren solo 15% del tiempo (base rate)
- Y el indicador tiene 20% de falsos positivos
- P(recesion | senal) = solo 46%, no 90%!
- Ignorar el base rate = tomar decisiones terribles

---

## Segmento 2: Base Rates y el Teorema de Bayes Aplicado (12 min)

### [PIZARRA: Confusion matrix de un indicador]
```
                    Realidad
                  Recesion    No Recesion
Indicador  Senal    TP            FP        -> PPV = TP/(TP+FP)
           Nada     FN            TN        -> NPV = TN/(TN+FN)
                    |             |
                 Sensibilidad  1-Especificidad
```

### [SLIDE: Datos historicos de recesiones USA (NBER)]
- 1945-2024: ~12 recesiones en ~80 anos
- Base rate: ~15% del tiempo en recesion
- Duracion media: ~11 meses
- Expansion media: ~58 meses

### [SCREENCAST: Calcular con Bayes]
```python
# Indicador: yield curve inversion
# Sensibilidad: P(inversion | recesion) ~ 85%
# FPR: P(inversion | no recesion) ~ 25%
# Base rate: P(recesion) ~ 15%
# P(recesion | inversion) = ???
```

### [CAMARA]
"Con Bayes: P(recesion | inversion) = 42%. El indicador que parece
tener 85% de acierto solo tiene 42% de valor predictivo positivo.
Y si usas un umbral NHST de p < 0.05, ni siquiera sabes esto."

---

## Segmento 3: Regresion OLS -- Caso Apple vs S&P 500 (12 min)

### [SCREENCAST: Notebook en vivo con Statsmodels]
```python
import statsmodels.api as sm

# 1. Generar retornos sinteticos tipo Apple y S&P 500
# 2. Modelo de mercado: r_apple = alpha + beta * r_sp500 + epsilon
# 3. sm.OLS(y, X).fit()
# 4. Examinar:
#    - summary() completo
#    - p-values de alpha y beta
#    - R-squared y F-stat
#    - Intervalos de confianza de los parametros
# 5. Tests diagnosticos:
#    - Jarque-Bera (normalidad)
#    - Breusch-Pagan (heterocedasticidad)
#    - Durbin-Watson (autocorrelacion)
#    - Condition number (multicolinealidad)
```

### [SLIDE: Resultados tipicos]
- Alpha ~ 0.02% diario (p ~ 0.70, no significativo)
- Beta ~ 1.25 (p << 0.001, significativo)
- R-squared ~ 0.45
- Jarque-Bera: p << 0.001 (residuales NO normales)
- Conclusion: beta es informativo, pero los p-values son sospechosos

### [CAMARA]
"Fijate: Statsmodels te da 20+ estadisticos. Los que mas importan
no son los p-values de los coeficientes -- son los tests diagnosticos
al final. Si Jarque-Bera rechaza, TODOS los p-values son sospechosos."

---

## Segmento 4: Confusion Matrix de un Indicador Economico (10 min)

### [SCREENCAST: Simulacion interactiva]
```python
# 1. Simular 80 anos de datos economicos (960 meses)
# 2. Generar recesiones con base rate ~ 15%
# 3. Crear indicador con sensibilidad y FPR ajustables
# 4. Construir confusion matrix
# 5. Calcular PPV, NPV, accuracy, F1-score
# 6. Variar FPR de 5% a 30% y ver como cambia PPV
# 7. Plotly interactivo: PPV vs FPR para diferentes base rates
```

### [SLIDE: La leccion]
- Con base rate 15%, incluso sensibilidad 95% y FPR 10%
  da PPV = solo 63%
- Si el base rate baja a 5%: PPV = 33% (1 de cada 3 es falsa alarma)
- NHST ignora el base rate completamente
- Bayes lo incorpora automaticamente

---

## Segmento 5: Cierre -- Framework de Evaluacion (8 min)

### [SLIDE: Checklist para evaluar un indicador/modelo]
1. Cual es el base rate del evento? (P(recesion), P(default), etc.)
2. Cual es la sensibilidad y la especificidad?
3. Calcula el PPV con Bayes -- es suficiente para actuar?
4. Los supuestos del modelo se cumplen? (normalidad, homocedasticidad)
5. Cuantas hipotesis probaste? (correccion por multiple testing)

### [CTA]
"Toma un indicador que uses (RSI, yield curve, PMI, lo que sea).
Calcula su confusion matrix historica. Aplica Bayes con el base rate
correcto. El resultado probablemente te sorprendera."

---

## Notas de Produccion
- Mostrar Statsmodels summary() en pantalla completa
- Confusion matrix como heatmap interactivo
- Slider Plotly para variar FPR y ver PPV en tiempo real
- source_ref: turn0browsertab744690698
