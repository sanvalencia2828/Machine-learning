# Ejercicios Practicos -- Modulo 3D: LGN, TLC y Monte Carlo
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Convergencia de la Media (LGN)

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
Genera muestras de dado justo para N = 10, 100, 1000, 10000.
1. Para cada N, calcula la media y el error vs 3.5
2. Grafica error vs N. Que forma tiene?
3. Verifica que error ~ C/sqrt(N) ajustando una recta en log-log

```python
np.random.seed(42)
ns = [10, 100, 1000, 10000]
errores = [abs(np.random.choice([1,2,3,4,5,6], n).mean() - 3.5) for n in ns]
# TODO: graficar y ajustar 1/sqrt(N)
```

---

## Ejercicio 2: TLC Visual -- 4 Distribuciones

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Para cada distribucion, genera 10,000 medias muestrales de tamano n=30:
1. Uniforme(0,1)
2. Exponencial(3)
3. Bernoulli(0.2)
4. Student-t(5)

Haz histogramas. Todas se ven Normales a pesar de que las
distribuciones originales son muy diferentes.

### Pregunta clave
Que pasa con n=2? Y con n=100?

---

## Ejercicio 3: Cauchy -- Cuando TLC Falla

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
1. Genera medias de Cauchy para n = 5, 50, 500, 5000
2. Calcula std de las medias para cada n
3. Se reduce la std con n? (Deberia si TLC funciona)
4. Haz QQ-plot de medias(n=500) vs Normal. Es Normal?
5. Explica por que TLC falla con Cauchy

---

## Ejercicio 4: IC para Estimacion MCS

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Estima E[max(S_T - K, 0)] con MCS para una opcion call.
S=100, K=110, T=0.5, r=0.03, sigma=0.30.

1. Simula con N = 100, 1000, 10000, 100000
2. Para cada N: precio MCS, SE, IC 95%
3. Compara con BSM analitico
4. Con que N el IC es < $0.10 de ancho?

---

## Ejercicio 5: Eficiencia de MCS

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
La "maldicion de Monte Carlo": error ~ 1/sqrt(N).

1. Si necesitas precision de 1%: cuantas sims?
2. Si necesitas precision de 0.1%: cuantas sims?
3. Si cada simulacion toma 1ms: cuanto tiempo para 0.1%?
4. Compara con "antithetic variates": genera (Z, -Z) en pares.
   Reduce el numero de sims necesarias? Por cuanto?

```python
# Antithetic variates:
z = np.random.normal(0, 1, N//2)
z_anti = np.concatenate([z, -z])  # Correlacion -1
# Estima con z_anti en vez de z independientes
# Compara la varianza del estimador
```

---

## Ejercicio 6 (Bonus): TLC con Datos Dependientes

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
El TLC clasico asume datos iid. Los retornos financieros
tienen autocorrelacion en volatilidad (clustering).

1. Genera 10000 retornos con volatilidad que cambia:
   sigma[t] = 0.01 si |ret[t-1]| < 0.02, else 0.03
2. Calcula medias muestrales de tamano 50 (10000 repeticiones)
3. Son Normales? (test Jarque-Bera)
4. Compara con datos iid de misma distribucion marginal
5. Que pasa con el ancho del IC? Es mayor o menor que iid?

### Pista
Con dependencia, el TLC aun funciona pero la tasa de convergencia
es MAS LENTA. El IC "ingenuo" (sin corregir) subestima el error.
