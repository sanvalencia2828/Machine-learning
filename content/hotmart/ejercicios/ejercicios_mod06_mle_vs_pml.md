# Ejercicios Practicos -- Modulo 6: MLE vs PML
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: MLE vs PML con 5 Datos

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Earnings trimestrales: [1.8, 2.1, 1.9, 2.3, 2.0].
1. Calcula estimacion MLE (media, std)
2. Calcula posterior PML con prior Normal(2.0, 0.3)
3. Agrega un outlier (3.5). Como cambia cada estimacion?
4. Cual es mas robusto y por que?

---

## Ejercicio 2: Correlaciones Espurias

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera 100 series temporales aleatorias (252 dias, independientes).
1. Calcula la matriz de correlacion (4950 pares)
2. Cuantas tienen |r| > 0.15? > 0.20? > 0.25?
3. Selecciona las top 5 y graficalas. Parecen "reales"?
4. Un modelo de ML entrenado con estas 100 features: que haria?
5. Como PML mitiga este problema?

---

## Ejercicio 3: Grid Approximation

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Estima P(cara) de una moneda con grid approximation:
- Prior: Beta(5, 5)
- Datos: 12 caras en 20 lanzamientos
1. Crea grilla de 500 puntos en [0, 1]
2. Calcula prior * likelihood para cada punto
3. Normaliza para obtener posterior discretizado
4. Compara con posterior analitico Beta(17, 13)
5. Calcula P(theta > 0.6) desde la grilla

---

## Ejercicio 4: MCMC Metropolis para Student-t

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Genera 300 retornos con Student-t(nu=5, scale=0.015).
Implementa MCMC Metropolis para estimar nu:
1. Prior: nu ~ Exponential(1/30)
2. Likelihood: datos ~ Student-t(nu, 0, scale)
3. Propuesta: nu_nuevo = nu_actual + Normal(0, 0.5)
4. Corre 30,000 iteraciones, burn-in 5,000
5. Reporta: media, mediana, HDI 95% de nu
6. Grafica la cadena y el histograma posterior

### Pregunta
Que tasa de aceptacion es optima? (Regla: ~23-44% para 1 parametro)

---

## Ejercicio 5: MLE Falla con Datasets Pequenos

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Genera datasets de tamano n = 5, 10, 20, 50, 100, 500 con Normal(2.0, 0.5).
Para cada n:
1. Calcula MLE de mu y su IC 95%
2. Calcula posterior PML con prior Normal(2.0, 1.0)
3. Repite 1000 veces. Mide: MSE de MLE vs MSE de PML
4. En que n el MLE se vuelve competitivo con PML?
5. Grafica MSE vs n para ambos metodos

---

## Ejercicio 6 (Bonus): Deep Learning vs PML Conceptual

**Nivel:** Conceptual
**Tiempo estimado:** 15 min

### Enunciado
Para cada escenario, argumenta cual enfoque es mejor:

| Escenario | MLE/DL | PML | Por que? |
|-----------|--------|-----|----------|
| 10M imagenes de gatos | | | |
| 20 trimestres de earnings | | | |
| Prediccion de retorno manana | | | |
| Deteccion de fraude (1M transacciones) | | | |
| Probabilidad de default (50 bonos) | | | |
| Modelo regulatorio (Basilea) | | | |
