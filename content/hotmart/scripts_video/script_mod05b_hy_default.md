# Script de Video -- Modulo 5B: Inferencia Bayesiana para Default de Bonos High-Yield
# Duracion estimada: 45 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- $200 Millones en 90 Dias (7 min)

### [CAMARA]
"En 2020, un fondo de bonos high-yield perdio $200 millones cuando
3 de sus 15 posiciones hicieron default en 90 dias. Su modelo de
riesgo decia que la probabilidad era 2%. La realidad: 20%. La diferencia
entre modelos que ignoran la informacion y modelos que aprenden de ella
es, literalmente, cientos de millones de dolares. Hoy construimos
el modelo que aprende."

### [SLIDE: El problema]
- Bonos high-yield: mayor rendimiento, mayor riesgo de default
- Las agencias de rating dan senales (upgrades, downgrades, neutrales)
- Pregunta clave: P(default | secuencia de ratings)?
- NHST no puede responder. El framework bayesiano si.

---

## Segmento 2: Setup del Modelo Beta-Binomial con Ratings (10 min)

### [PIZARRA: Estructura del modelo]
```
theta = P(default en proximo ano)

Prior: theta ~ Beta(alpha, beta)
  - Rating BBB: Beta(2, 18) -> media 10%
  - Rating BB:  Beta(3, 12) -> media 20%
  - Rating B:   Beta(4, 8)  -> media 33%
  - Rating CCC: Beta(5, 5)  -> media 50%

Evidencia de ratings:
  - Downgrade: equivale a observar ~1 "cuasi-default" y 0 "sobrevivencias"
  - Upgrade: equivale a observar 0 "cuasi-defaults" y ~2 "sobrevivencias"
  - Neutral: equivale a 0 "cuasi-defaults" y 1 "sobrevivencia"

Posterior: theta ~ Beta(alpha + d, beta + s)
  donde d = cuasi-defaults observados, s = sobrevivencias
```

### [CAMARA]
"Los ratings de agencias (Moody's, S&P, Fitch) son senales ruidosas.
No te dicen directamente P(default). Pero cada downgrade AUMENTA tu
estimacion, y cada upgrade la BAJA. El modelo bayesiano formaliza esto."

---

## Segmento 3: Actualizacion Dinamica con Secuencia de Ratings (12 min)

### [SCREENCAST: Notebook en vivo]
```python
# Empresa: "MegaCorp"
# Rating inicial: BB (prior Beta(3, 12), media 20%)
#
# Trimestre 1: Rating neutral -> Beta(3, 13), media 18.8%
# Trimestre 2: Downgrade a B  -> Beta(4, 13), media 23.5%
# Trimestre 3: Downgrade a CCC -> Beta(5, 13), media 27.8%
# Trimestre 4: Rating neutral -> Beta(5, 14), media 26.3%
#
# Graficar: evolucion de P(default) con HDI 95% por trimestre
# Comparar: P(default > 30%) en cada paso
```

### [SLIDE: La magia de la actualizacion secuencial]
- No necesitas re-entrenar: solo actualizas alpha y beta
- Cada rating NUEVO mueve el posterior
- Downgrades consecutivos: efecto ACUMULATIVO
- El modelo "recuerda" toda la historia de ratings

---

## Segmento 4: Multiples Bonos -- Portafolio Completo (10 min)

### [SCREENCAST: Simulacion de portafolio]
```python
# 20 bonos high-yield con diferentes historiales de ratings
# Para cada bono: prior -> secuencia de ratings -> posterior
# Distribucion predictiva: cuantos defaults en el portafolio?
# P(3+ defaults) = ??? P(5+ defaults) = ???
# Comparar con modelo frecuentista (tasa historica fija)
```

### [SLIDE: Resultados]
- Modelo frecuentista: P(3+ defaults) = 7% (usa tasa historica fija)
- Modelo bayesiano: P(3+ defaults) = 18% (incorpora downgrades recientes)
- Diferencia: 2.5x -- el bayesiano es mas conservador Y mas preciso
- El frecuentista ignora que 5 bonos fueron downgraded recientemente

---

## Segmento 5: Cierre (6 min)

### [SLIDE: Framework completo para credit risk]
1. **Prior por rating**: Beta parametrizada segun rating inicial
2. **Likelihood por evento**: downgrades, upgrades, neutrales
3. **Posterior secuencial**: se actualiza con cada evento
4. **Predictive del portafolio**: distribucion de defaults futuros
5. **Decision**: ajustar exposicion basado en P(defaults > umbral)

### [CTA]
"Toma un bono de tu watchlist. Define su prior segun el rating.
Mira los ultimos 4 trimestres de eventos. Actualiza el posterior.
P(default > 20%) cambio?"

---

## Notas de Produccion
- Animar la evolucion del posterior con cada rating como timeline
- Color-code: verde (upgrade), rojo (downgrade), gris (neutral)
- Mostrar portafolio como heatmap de P(default) por bono
- source_ref: turn0browsertab744690698
