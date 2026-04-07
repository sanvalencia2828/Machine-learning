# Script de Video -- Modulo 6C: Grid Approximation, Markov Chains y MCMC
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- Cuando No Hay Formula Cerrada (7 min)

### [CAMARA]
"Hasta ahora usamos Beta-Binomial, que tiene formula cerrada. Pero
la mayoria de modelos financieros reales NO la tienen. No puedes
calcular el posterior con papel y lapiz. Necesitas un algoritmo que
EXPLORE la distribucion posterior por ti. Ese algoritmo es MCMC --
y es el motor detras de PyMC, Stan, y toda la inferencia probabilistica
moderna."

### [SLIDE: El camino de Beta-Binomial a MCMC]
```
Nivel 1: Conjugados analiticos (Beta-Binomial, Normal-Normal)
  -> Rapido, exacto, limitado a modelos simples

Nivel 2: Grid Approximation
  -> Funciona con cualquier modelo, pero no escala a >2 parametros

Nivel 3: MCMC (Markov Chain Monte Carlo)
  -> Funciona con CUALQUIER modelo, escala a miles de parametros
  -> Es lo que PyMC, Stan, JAGS usan internamente
```

---

## Segmento 2: Grid Approximation -- La Idea y sus Limites (10 min)

### [PIZARRA: Grid approximation]
```
1. Definir grilla de valores para theta
2. Para cada theta: calcular prior(theta) * likelihood(theta|datos)
3. Normalizar: posterior = valores / sum(valores)

Ejemplo ZYX (3/3 beats):
  theta = [0.01, 0.02, ..., 0.99] (99 puntos)
  Para cada theta: Beta(2,2).pdf(theta) * Binom(3,3,theta)
  Normalizar -> posterior discretizado
```

### [SLIDE: Limitacion: maldicion de la dimensionalidad]
```
1 parametro: 100 puntos -> 100 evaluaciones
2 parametros: 100 x 100 -> 10,000 evaluaciones
5 parametros: 100^5 -> 10 BILLONES de evaluaciones
10 parametros: 100^10 -> 10^20 (imposible)

Modelos reales tienen 10-1000+ parametros
Grid es IMPOSIBLE para modelos reales
```

---

## Segmento 3: Markov Chains -- Estados de Mercado (12 min)

### [SLIDE: Que es un Markov Chain]
```
Un proceso donde el estado futuro solo depende del estado actual:
  P(estado_t+1 | estado_t, estado_t-1, ...) = P(estado_t+1 | estado_t)

"El futuro solo depende del presente, no del pasado"
```

### [SCREENCAST: Ejemplo de mercado]
```python
# 3 estados: Bear (-), Stagnant (0), Bull (+)
# Matriz de transicion:
#              Bear  Stagn  Bull
# Desde Bear  [0.6   0.3   0.1]
# Desde Stagn [0.2   0.5   0.3]
# Desde Bull  [0.1   0.3   0.6]
#
# Simular 1000 pasos
# Verificar: la cadena converge a distribucion estacionaria
# Aplicar: clasificar regimenes de mercado
```

### [SLIDE: Propiedades clave]
1. **Estacionariedad**: despues de suficientes pasos, la cadena converge
2. **Distribucion estacionaria**: la proporcion de tiempo en cada estado
3. **Ergodicidad**: el promedio temporal = promedio del ensamble
4. MCMC EXPLOTA estas propiedades para muestrear posteriors

---

## Segmento 4: MCMC Metropolis -- El Algoritmo (13 min)

### [PIZARRA: Metropolis paso a paso]
```
Objetivo: muestrear de P(theta | datos) sin calcularla explicitamente

1. Empezar en theta_0 (cualquier punto)
2. Proponer theta* = theta_actual + ruido Normal(0, sigma)
3. Calcular ratio = P(datos|theta*)*P(theta*) / P(datos|theta_actual)*P(theta_actual)
4. Si ratio >= 1: ACEPTAR theta*
5. Si ratio < 1: ACEPTAR con probabilidad = ratio, sino QUEDAR
6. Repetir 10,000+ veces
7. Despues de burn-in: las muestras SON la distribucion posterior

MAGIA: nunca calculas P(datos) (marginal likelihood)!
  El ratio la cancela automaticamente
```

### [SCREENCAST: MCMC para Student-t fat tails]
```python
# Datos: 500 retornos financieros con colas pesadas
# Objetivo: estimar nu (grados de libertad)
# Prior: nu ~ Exponential(1/30)
# Likelihood: datos ~ Student-t(nu, mu, sigma)
# MCMC Metropolis: 20,000 iteraciones
# Resultado: posterior de nu ~ 4 (confirma fat tails)
```

### [SLIDE: Diagnosticos de MCMC]
- **Tasa de aceptacion**: ideal 23-44% (1 parametro)
- **Trace plot**: la cadena debe "explorar" sin quedarse pegada
- **Autocorrelacion**: baja = bueno (muestras independientes)
- **Rhat**: convergencia entre multiples cadenas

---

## Segmento 5: Cierre (8 min)

### [SLIDE: Resumen del pipeline]
```
Modelo simple (1-2 parametros) -> Conjugados o Grid
Modelo complejo (3+ parametros) -> MCMC
Modelo muy complejo (100+) -> HMC (Hamiltonian MC, usado por PyMC)
```

### [CTA]
"Implementa MCMC para tu propio modelo. Elige un activo,
define prior para mu y sigma, usa Metropolis para muestrear
la posterior conjunta. Visualiza las cadenas."

---

## Notas de Produccion
- Animar Markov chain como "caminata" entre estados
- Metropolis como "exploracion de montana" (sube mas, baja a veces)
- Trace plots en vivo mostrando convergencia
- source_ref: turn0browsertab744690698
