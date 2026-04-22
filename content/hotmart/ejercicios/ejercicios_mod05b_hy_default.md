# Ejercicios Practicos -- Modulo 5B: Default de Bonos High-Yield
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Priors por Rating

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
1. Define priors Beta para 4 ratings: BBB, BB, B, CCC
2. Grafica las 4 distribuciones prior superpuestas
3. Para cada rating, calcula P(default > 20%)
4. Cual rating tiene mayor incertidumbre (ancho HDI)?

---

## Ejercicio 2: Actualizacion con 1 Evento

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Bono rating BB (prior Beta(3,12)).
1. Calcula posterior despues de un downgrade: Beta(4, 12)
2. Calcula posterior despues de un upgrade: Beta(3, 14)
3. Grafica prior y ambos posteriors
4. Cuanto movio el downgrade vs el upgrade?

---

## Ejercicio 3: Secuencia de 6 Trimestres

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Empresa "RiskyCorp": rating B, eventos:
T1: neutral, T2: downgrade, T3: downgrade, T4: neutral, T5: upgrade, T6: neutral

1. Actualiza paso a paso
2. Grafica P(default) con HDI en cada trimestre
3. En que trimestre P(default) fue maxima?
4. El upgrade del T5 compensa los 2 downgrades?

---

## Ejercicio 4: Portafolio de 10 Bonos

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Genera 10 bonos con ratings aleatorios y 4 eventos cada uno.
1. Calcula posterior para cada bono
2. Simula 50,000 escenarios de defaults
3. Histograma de defaults totales
4. P(3+ defaults), P(5+ defaults)
5. Si tu limite de riesgo es P(3+) < 20%, ajustas posiciones?

---

## Ejercicio 5: Sensibilidad al Prior

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
Mismos datos (bono BB, 4 downgrades). Prueba 3 priors:
1. Optimista: Beta(1, 19) (media 5%)
2. Neutro: Beta(3, 12) (media 20%)
3. Pesimista: Beta(5, 5) (media 50%)

Con 10 datos, el posterior converge al mismo valor?
Con 50 datos? En que punto el prior deja de importar?

---

## Ejercicio 6 (Bonus): Rating Transition Matrix Bayesiana

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Las agencias publican matrices de transicion de ratings anuales.
Usa una matriz simplificada:
```
           BBB   BB    B    CCC   Default
BBB       0.85  0.10  0.03  0.01  0.01
BB        0.05  0.75  0.12  0.05  0.03
B         0.01  0.05  0.70  0.15  0.09
CCC       0.00  0.02  0.10  0.50  0.38
```

1. Simula la trayectoria de 20 bonos a 5 anos usando MCS
2. Cuantos hacen default en 5 anos?
3. Compara con la prediccion bayesiana del portafolio
4. Cual metodo captura mejor el riesgo?
