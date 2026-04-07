# Script de Video -- Modulo 6B: MLE Falla con Pocos Datos -- El Caso ZYX
# Duracion estimada: 40 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- 100% de Certeza con 3 Datos (7 min)

### [CAMARA]
"Una empresa tiene solo 3 trimestres de historia. Los 3 supero
estimaciones de earnings. Un modelo MLE concluye: la probabilidad
de superar estimaciones es 100%. Para siempre. Con total certeza.
Con solo 3 datos. Eso no es ciencia -- es alucinacion estadistica.
Hoy vamos a ver exactamente por que MLE produce esta absurdez y
como PML da una respuesta mucho mas honesta."

### [SLIDE: El caso ZYX]
```
Datos: 3 trimestres, 3 earnings beats
  Beat = 1, Miss = 0
  Datos = [1, 1, 1]

MLE: p_hat = 3/3 = 1.0
  "100% de probabilidad de beat futuro"
  Sin incertidumbre. Sin matices.

Problema: con 3 datos, hay ENORME incertidumbre
  que MLE ignora completamente
```

### [CAMARA]
"Es como lanzar una moneda 3 veces, sacar 3 caras, y concluir
que SIEMPRE sale cara. Nadie haria eso con una moneda. Pero los
modelos MLE lo hacen con datos financieros todo el tiempo."

---

## Segmento 2: Por Que MLE Da p=1 (8 min)

### [PIZARRA: MLE para Bernoulli]
```
Datos: X1, X2, ..., Xn ~ Bernoulli(p)

Likelihood: L(p) = p^k * (1-p)^(n-k)
  donde k = beats, n = total

MLE: p_hat = argmax L(p) = k/n

Con k=3, n=3: p_hat = 3/3 = 1.0

El likelihood se maximiza EXACTAMENTE en p=1.
No hay espacio para incertidumbre en MLE.
Es un PUNTO, no una distribucion.
```

### [SLIDE: El problema en 4 lineas]
1. MLE busca el MEJOR punto
2. Con 3/3 beats, p=1 es el mejor punto
3. Pero p=0.8 tambien es muy compatible con 3/3
4. MLE ignora todo lo que no sea el maximo

---

## Segmento 3: PML Rescata -- Prior + Posterior (10 min)

### [SCREENCAST: Notebook en vivo]
```python
# 1. Prior: Beta(1, 1) = Uniforme (no asumimos nada)
# 2. Likelihood: Binomial(3, 3, p)
# 3. Posterior: Beta(1+3, 1+0) = Beta(4, 1)
# 4. Media posterior: 4/5 = 80% (NO 100%)
# 5. HDI 95%: (38%, 99%)
# 6. P(p > 0.9) = solo 34%
# 7. P(p = 1.0) = 0% (imposible exactamente 1)
```

### [SLIDE: Comparacion directa]
| Metrica | MLE | PML (prior uniforme) |
|---------|-----|---------------------|
| Estimacion p | 1.000 | 0.800 |
| Incertidumbre | NINGUNA | HDI (0.38, 0.99) |
| P(p > 0.9) | 100% | 34% |
| P(beat proximo) | 100% | 80% |

### [CAMARA]
"Con prior uniforme, PML dice 80% con un rango enorme. Con prior
esceptico Beta(2, 2), dice 71%. El prior no es un sesgo -- es
HONESTIDAD sobre lo poco que sabemos con 3 datos."

---

## Segmento 4: Actualizacion con Mas Datos (10 min)

### [SCREENCAST: Actualizacion secuencial]
```python
# Q4: beat  -> Beta(5, 1), media 83%
# Q5: beat  -> Beta(6, 1), media 86%
# Q6: MISS  -> Beta(6, 2), media 75%
# Q7: beat  -> Beta(7, 2), media 78%
# Q8: beat  -> Beta(8, 2), media 80%
# Graficar: evolucion de media + HDI por trimestre
# Mostrar: MLE ajustaria bruscamente con el miss
#   (de 100% a 83% instantaneamente)
```

### [SLIDE: El miss del Q6 en dos frameworks]
```
MLE antes del miss:  p = 5/5 = 100%
MLE despues del miss: p = 5/6 = 83%
  Caida: 17 puntos porcentuales de golpe

PML antes del miss:  media = 86%, HDI (55%, 99%)
PML despues del miss: media = 75%, HDI (44%, 94%)
  Caida: 11 puntos. Mas suave. El prior amortigua.
```

---

## Segmento 5: Cierre -- Datasets Pequenos y la Trampa MLE (5 min)

### [SLIDE: Cuando MLE es peligroso]
1. **n < 20**: MLE sobreajusta severamente
2. **Eventos binarios**: p=k/n puede ser 0 o 1 facilmente
3. **Datos financieros**: trimestres escasos, eventos raros
4. **Startups/IPOs**: 2-4 trimestres de historia

### [SLIDE: Cuando PML rescata]
1. Prior absorbe lo poco que sabemos
2. Posterior refleja incertidumbre real
3. Con mas datos, prior pierde influencia
4. Distribucion predictiva es honesta

### [CTA]
"Toma una accion que tenga < 8 trimestres de historia.
Calcula p(beat) con MLE y con PML. La diferencia te
dira cuanto riesgo estas ignorando."

---

## Notas de Produccion
- Animar MLE como "unico punto" vs PML como "distribucion completa"
- Mostrar el posterior Beta evolucionando trimestre a trimestre
- Enfatizar el momento del "miss" como punto de quiebre
- source_ref: turn0browsertab744690698
