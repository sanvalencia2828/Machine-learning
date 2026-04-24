# Script de Video -- Modulo 3C: Normal vs Realidad en Retornos Financieros
# Duracion estimada: 40 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Dia que lo Imposible Ocurrio (7 min)

### [CAMARA]
"El 19 de octubre de 1987 el S&P 500 cayo 22.6% en un solo dia.
Bajo el modelo Normal, la probabilidad de ese evento es 10 a la menos
113. Para ponerlo en perspectiva, el universo tiene 10 a la 10 anos
de antiguedad. Ese evento no solo era improbable -- era mas improbable
que cualquier cosa que haya ocurrido en la historia cosmica. Y sin
embargo, ocurrio. El modelo Gaussiano esta roto."

### [SLIDE: Eventos 'imposibles' que si ocurrieron]
| Evento | Fecha | Magnitud | P bajo Normal |
|--------|-------|----------|---------------|
| Black Monday | Oct 1987 | -22.6% | ~10^-113 |
| Flash Crash | May 2010 | -9.2% (intradiario) | ~10^-14 |
| CHF desvinculacion | Ene 2015 | +30% EURCHF | ~10^-70 |
| COVID crash | Mar 2020 | -12% en un dia | ~10^-23 |

### [CAMARA]
"Todos estos eventos fueron 'imposibles' segun la Normal. Y todos
ocurrieron en tu vida. Hoy vamos a demostrar formalmente que la
Normal no describe retornos financieros, y que la alternativa no
es difusa ni filosofica -- es matematica."

---

## Segmento 2: Anatomia de la No-Normalidad (10 min)

### [SLIDE: 3 formas en que los retornos violan la Normal]
1. **Colas pesadas** (fat tails): curtosis >> 3
2. **Asimetria** (skew): caidas mas extremas que subidas
3. **Clustering de volatilidad**: periodos de calma y crisis

### [PIZARRA: Colas pesadas en numeros]
```
Normal: P(> 4 sigma) = 0.006%  (1 en 16,000 dias = ~60 anos)
S&P 500: P(> 4 sigma) ~ 0.5%  (1 en 200 dias = ~1 ano)
Ratio: los eventos de 4 sigma son ~80x mas frecuentes

Normal: P(> 6 sigma) = 2e-9  (nunca en la historia)
S&P 500: P(> 6 sigma) ~ 0.05%  (varias veces por decada)
```

### [SCREENCAST: Generar datos sinteticos tipo S&P 500]
```python
# 1. Student-t(nu=4): captura curtosis ~25
# 2. Mezcla Normal: 95% calma + 5% crisis
# 3. Normal pura: el modelo convencional
# Comparar los 3 con histogramas y QQ-plots
```

### [SLIDE: QQ-plot -- el diagnostico visual definitivo]
- Si los datos son Normales: puntos sobre la linea de 45 grados
- Si tienen fat tails: puntos se curvan en los extremos
- Si tienen skew: asimetria en las colas

---

## Segmento 3: Tests Formales de Normalidad (8 min)

### [SLIDE: 3 tests que debes conocer]
| Test | Que evalua | Hipotesis nula |
|------|-----------|----------------|
| Jarque-Bera | Skew + curtosis | Datos son Normales |
| Shapiro-Wilk | Forma general | Datos son Normales |
| Anderson-Darling | Colas especificamente | Datos siguen F(x) |

### [SCREENCAST: Ejecutar los 3 tests]
```python
from scipy import stats
# Jarque-Bera: rechaza si p < 0.05
# Shapiro-Wilk: rechaza si p < 0.05
# Anderson-Darling: compara con valores criticos
# Resultado: TODOS rechazan normalidad para retornos financieros
```

### [CAMARA]
"Los tres tests rechazan la Normal con p-values microscopicos.
Esto no es una opinion -- es un resultado estadistico formal.
Usar la Normal para modelar retornos es como usar un mapa plano
para navegar el globo. Funciona localmente, falla globalmente."

---

## Segmento 4: La Alternativa -- Distribuciones con Colas Pesadas (10 min)

### [SLIDE: 3 alternativas a la Normal]
1. **Student-t**: parametro nu controla las colas (nu=4 ~ S&P 500)
2. **Mezcla de Normales**: modela regimenes (calma + crisis)
3. **Distribucion estable**: generaliza Normal (alpha < 2)

### [SCREENCAST: Ajustar Student-t vs Normal a retornos sinteticos]
```python
# 1. Generar 10,000 retornos tipo S&P 500
# 2. Ajustar Normal (MLE)
# 3. Ajustar Student-t (MLE)
# 4. Comparar log-likelihood, AIC, BIC
# 5. Visualizar el ajuste en las colas (log-scale)
```

### [SLIDE: Resultados]
- Student-t con nu ~ 4 ajusta las colas 100x mejor
- Normal subestima P(crash) por ordenes de magnitud
- La diferencia en pricing es enorme (volatility smile)
- AIC/BIC confirman: Student-t es estrictamente superior

### [CAMARA]
"La Student-t no es perfecta. Pero es MUCHO mejor que la Normal
para capturar el riesgo real. Y lo mejor: solo agrega UN parametro
(nu), asi que no estamos sobreajustando."

---

## Segmento 5: Cierre -- Implicaciones Practicas (5 min)

### [SLIDE: Que cambiar en tu practica]
1. NUNCA asumas normalidad sin testar formalmente
2. Usa QQ-plot como diagnostico visual rapido
3. Ajusta Student-t o mezcla como alternativa
4. Recalcula VaR/ES con la distribucion correcta
5. MCS con fat tails > MCS con Normal

### [SLIDE: Conexion con el curso]
- Modulo 2C: BSM falla porque asume Normal
- Modulo 3: MCS propaga la distribucion completa
- Modulo 3B: 4 momentos revelan la no-normalidad
- Modulo 7: PyMC usa Student-t como likelihood

### [CTA]
"Ejecuta el QQ-plot con retornos de cualquier activo de tu portafolio.
Si las colas se desvian, tu modelo Normal esta mintiendo. Cuanto?
Calcula el ratio de eventos extremos observados vs esperados."

---

## Notas de Produccion
- Tabla de eventos 'imposibles' como slide animado
- QQ-plot interactivo con zoom en colas
- Comparacion visual Normal vs Student-t en log-scale
- source_ref: turn0browsertab744690698
