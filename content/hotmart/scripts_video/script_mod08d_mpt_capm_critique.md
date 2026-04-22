# Script de Video -- Modulo 8D: MPT, CAPM y su Critica Probabilistica
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Nobel que Pierde Dinero (8 min)

### [CAMARA]
"Harry Markowitz gano el Nobel por la Modern Portfolio Theory. Pero
cuando le preguntaron como invertia su propio dinero, admitio que
usaba 50/50 -- la mitad en acciones, la mitad en bonos. No su propia
teoria. Hoy vamos a entender POR QUE el creador de MPT no la usa,
y que la reemplaza."

### [SLIDE: MPT en 30 segundos]
```
Inputs:  retornos esperados (mu), covarianza (Sigma)
Output:  pesos optimos que minimizan varianza dado un retorno objetivo
Magia:   la "frontera eficiente" -- el conjunto de portafolios optimos

Problema: TODO depende de mu y Sigma estimados
  -> Basura entra, basura sale
  -> Pequenos errores en mu -> cambios enormes en pesos
  -> En crisis: correlaciones cambian, mu se invierte
```

---

## Segmento 2: 5 Razones por las que MPT Falla (12 min)

### [SLIDE: Razon 1 -- Retornos NO son normales]
- MPT asume normalidad (media + varianza lo describe todo)
- Realidad: fat tails, skewness, curtosis >> 3
- Una crisis de -30% es "imposible" bajo Normal pero ocurre regularmente

### [SLIDE: Razon 2 -- Covarianzas NO son estables]
- En calma: correlacion acciones-bonos ~ -0.3
- En crisis: TODAS las correlaciones van a 1
- La diversificacion desaparece exactamente cuando mas la necesitas

### [SLIDE: Razon 3 -- Sensibilidad extrema a inputs]
- Cambiar mu de un activo en 0.1% puede cambiar su peso de 5% a 40%
- "Estimation error maximizer" (Michaud)
- Los pesos de MPT son tan ruidosos como los datos de entrada

### [SLIDE: Razon 4 -- Volatilidad es mala medida de riesgo]
- Trata +10% y -10% como igualmente "riesgosos"
- No captura fat tails ni skewness
- Ya lo vimos en Modulo 3B

### [SLIDE: Razon 5 -- Ignora ergodicidad]
- MPT optimiza para 1 periodo (estatico)
- No considera crecimiento geometrico a largo plazo
- Kelly > Markowitz para inversores individuales (Modulo 8)

---

## Segmento 3: CAPM -- Util como Benchmark, Peligroso como Verdad (10 min)

### [PIZARRA: CAPM]
```
E[r_i] = r_f + beta_i * (E[r_m] - r_f)

beta = Cov(r_i, r_m) / Var(r_m)

Implicaciones:
  - Solo riesgo sistematico (beta) es recompensado
  - Riesgo idiosincratico se diversifica
  - Un solo factor (mercado) explica todo

Problemas:
  - Beta NO es estable en el tiempo
  - Alpha "no existe" segun CAPM (pero fondos cobran por buscarlo)
  - Un solo factor es insuficiente (Fama-French usa 3-5)
```

---

## Segmento 4: Alternativas -- 1/N y Ensambles Probabilisticos (12 min)

### [SCREENCAST: Naive diversification vs MPT]
```python
# 1. Generar retornos sinteticos de 5 activos (fat tails)
# 2. Calcular frontera eficiente de MPT
# 3. Calcular portafolio 1/N (pesos iguales)
# 4. Simular 1000 trayectorias de 252 dias con cada estrategia
# 5. Comparar: Sharpe ratio, max drawdown, P(ruina)
# Resultado: 1/N frecuentemente SUPERA a MPT fuera de muestra
```

### [SLIDE: Por que 1/N funciona]
- No estima mu (la fuente de mayor error en MPT)
- Diversificacion real sin optimizacion ruidosa
- DeMiguel et al. (2009): 1/N supera a 14 estrategias de optimizacion

### [SLIDE: Ensambles probabilisticos para portafolios]
```
En vez de UN set de pesos optimos (MPT):
  1. Posterior de mu y Sigma (desde PyMC)
  2. Para cada muestra del posterior: calcular pesos optimos
  3. Resultado: DISTRIBUCION de pesos, no un solo punto
  4. El "ensamble" de portafolios captura la incertidumbre
```

---

## Segmento 5: Cierre (8 min)

### [SLIDE: MPT vs Kelly vs 1/N vs PML Ensemble]
| Criterio | MPT | Kelly | 1/N | PML Ensemble |
|----------|-----|-------|-----|-------------|
| Asume Normal | SI | No | No | No |
| Estima mu | SI (fragil) | SI (via posterior) | NO | SI (robusto) |
| Ergodicidad | Ignora | Central | N/A | Via posterior |
| Crisis | Falla | Reduce asignacion | Estable | Se adapta |
| Incertidumbre | Ignora | En distribucion | N/A | Cuantifica |

### [CTA]
"Toma 5 activos. Calcula pesos MPT y 1/N. Simula 1 ano fuera de
muestra 1000 veces. Cual Sharpe es mejor? Cual drawdown es peor?"

---

## Notas de Produccion
- Frontera eficiente como grafico interactivo
- Animar pesos MPT cambiando con pequenas variaciones en mu
- Correlaciones en crisis como heatmap que se vuelve "todo rojo"
- source_ref: turn0browsertab744690698
