# Ejercicios Practicos -- Modulo 6C: Grid, Markov Chains y MCMC
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Grid Approximation de Cero

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Implementa grid approximation para estimar P(cara) de moneda:
- Prior: Beta(5,5)
- Datos: 8 caras en 15 lanzamientos
1. Grilla de 500 puntos en [0,1]
2. Calcula posterior, compara con Beta(13,12)
3. P(theta > 0.6) desde la grilla
4. Repite con grilla de 50 puntos. Cambia mucho?

---

## Ejercicio 2: Markov Chain de Mercado

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Modifica la matriz de transicion para un mercado mas volatil:
```
         Bear  Stagn  Bull
Bear    [0.4   0.3   0.3]
Stagn   [0.3   0.4   0.3]
Bull    [0.3   0.3   0.4]
```
1. Simula 2000 pasos
2. Calcula distribucion estacionaria (analitica y empirica)
3. Es mas uniforme que la original? Por que?
4. Calcula duracion media en cada estado

---

## Ejercicio 3: Metropolis desde Cero

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Implementa Metropolis para muestrear de una Normal(3, 1):
1. Propuesta: Normal random walk con sigma_prop = 0.5
2. 10,000 iteraciones, burn-in 1000
3. Verifica: media ~3, std ~1
4. Cambia sigma_prop a 0.01 y 10.0. Que pasa con la tasa de aceptacion?
5. Encuentra el sigma_prop optimo (~23% aceptacion)

---

## Ejercicio 4: MCMC para Nu de Student-t

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Genera 300 retornos con Student-t(nu=5, scale=0.015).
1. Implementa Metropolis para estimar nu
2. Prior: Exponential(scale=30)
3. 30,000 iteraciones, burn-in 5,000
4. Trace plot, histograma, autocorrelacion
5. Ejecuta 4 cadenas independientes. Convergen al mismo valor?

---

## Ejercicio 5: Metropolis Bivariado (mu y sigma)

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Estima mu y sigma de datos Normal simultaneamente:
- Prior mu: Normal(0, 0.1)
- Prior sigma: HalfNormal(0.05)
- Datos: 50 retornos diarios
1. Propuesta: Random walk en 2D (sigma_prop = [0.001, 0.002])
2. 20,000 iteraciones
3. Scatter plot de (mu, sigma) muestras
4. Marginal de mu y sigma por separado
5. Tasa de aceptacion? Es adecuada?

---

## Ejercicio 6 (Bonus): Metropolis-Hastings vs Metropolis

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
Metropolis usa propuesta simetrica. Metropolis-Hastings permite
propuestas asimetricas (ej: Log-Normal para parametros positivos).
1. Implementa MH con propuesta Log-Normal para nu
2. Compara tasa de aceptacion vs Metropolis normal
3. La cadena MH converge mas rapido?
