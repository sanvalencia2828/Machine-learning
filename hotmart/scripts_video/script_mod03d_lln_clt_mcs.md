# Script de Video -- Modulo 3D: LGN, TLC y los Fundamentos de Monte Carlo
# Duracion estimada: 45 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- Por que Monte Carlo Funciona (7 min)

### [CAMARA]
"Cuando lanzas un dado 10 veces, el promedio puede ser 2.8 o 4.3.
Cuando lo lanzas 10 millones de veces, el promedio es 3.500000.
Esto no es magia -- es la Ley de los Grandes Numeros. Y es la razon
por la que Monte Carlo funciona. Hoy vamos a entender los dos
teoremas que hacen posible toda simulacion financiera."

### [SLIDE: Los dos pilares de MCS]
1. **LGN** (Ley de Grandes Numeros): el promedio converge al valor real
2. **TLC** (Teorema del Limite Central): el error es Normal y medible
3. Juntos garantizan: MCS converge y puedes medir QUE TAN RAPIDO

### [SLIDE: Sin LGN y TLC, MCS seria...]
- Solo "tirar numeros al azar y rezar"
- Sin garantia de convergencia
- Sin forma de medir el error
- Sin intervalo de confianza para las estimaciones

---

## Segmento 2: Ley de Grandes Numeros -- Convergencia (10 min)

### [PIZARRA: LGN debil]
```
Sea X1, X2, ..., Xn variables iid con E[Xi] = mu
Entonces: X_bar_n = (1/n) * sum(Xi) --> mu  (en probabilidad)

Traduccion: el promedio muestral converge al valor esperado
```

### [SCREENCAST: Demo interactiva]
```python
# Dado justo: E[X] = 3.5
# Moneda sesgada: E[X] = p
# Student-t(4): E[X] = 0 (pero con colas pesadas)
# Para cada caso: graficar convergencia de X_bar vs n
```

### [SLIDE: LGN en finanzas]
- Retorno medio: converge al retorno esperado con mas datos
- VaR por MCS: converge al VaR real con mas simulaciones
- Precio de opcion por MCS: converge al precio real
- Tasa de convergencia: error ~ 1/sqrt(N)

### [PIZARRA: La tasa importa]
```
N = 100:     error ~ 10%
N = 10,000:  error ~ 1%
N = 1,000,000: error ~ 0.1%

Para ir de 1% a 0.1% necesitas 100x mas simulaciones
Esto es la "maldicion de Monte Carlo"
```

---

## Segmento 3: Teorema del Limite Central -- El Error es Normal (10 min)

### [PIZARRA: TLC]
```
Sea X1, ..., Xn iid con E[Xi] = mu, Var(Xi) = sigma^2
Entonces: sqrt(n) * (X_bar - mu) / sigma --> N(0,1)

Traduccion: el error del promedio es Normal
  INDEPENDIENTEMENTE de la distribucion original
```

### [SCREENCAST: Demo visual]
```python
# 1. Generar datos de Exponencial (muy asimetrica)
# 2. Calcular 10,000 medias muestrales de tamano n=5, 20, 50, 200
# 3. Histograma de medias: se vuelve Normal
# 4. Repetir con Student-t(3): tambien funciona
# 5. Repetir con Cauchy (nu=1): TLC FALLA (varianza infinita)
```

### [SLIDE: TLC en MCS]
- Permite calcular intervalos de confianza para estimaciones MCS
- Error estandar de MCS: SE = sigma / sqrt(N)
- IC 95% = estimacion +/- 1.96 * SE
- Ejemplo: si MCS estima VaR = -2.5%, IC = (-2.7%, -2.3%)

### [CAMARA]
"TLC no dice que los DATOS son normales. Dice que los PROMEDIOS
de datos son normales. Error numero uno en finanzas: confundir los
dos. Tus retornos tienen fat tails, pero la ESTIMACION del retorno
medio converge a Normal."

---

## Segmento 4: Demo -- LGN + TLC = MCS Garantizado (12 min)

### [SCREENCAST: Notebook en vivo]
```python
# Aplicacion completa: estimar P(perdida > 5%) para un portafolio
# 1. Generar retornos con Student-t (fat tails)
# 2. Simular N = 100, 1000, 10000, 100000
# 3. Medir: estimacion de P(perdida > 5%) para cada N
# 4. Calcular IC 95% usando TLC
# 5. Verificar que IC se estrecha con sqrt(N)
# 6. Graficar convergencia con bandas de confianza
```

### [SLIDE: Resultados clave]
- Con N=100: P(loss>5%) = 3.0% +/- 3.3% (inutil)
- Con N=1000: P(loss>5%) = 2.8% +/- 1.0% (aceptable)
- Con N=10000: P(loss>5%) = 2.73% +/- 0.32% (bueno)
- Con N=100000: P(loss>5%) = 2.71% +/- 0.10% (excelente)

### [SLIDE: Cuando TLC falla]
1. Varianza infinita (Cauchy, Levy): NO converge a Normal
2. Datos dependientes (autocorrelacion): converge MAS LENTO
3. N muy pequeno: la aproximacion Normal es pobre
4. Colas extremas: el promedio converge pero los extremos no

---

## Segmento 5: Cierre -- Distribucion Financiera Correcta + MCS (6 min)

### [SLIDE: El pipeline correcto]
```
1. Testar normalidad (Mod 3C) --> RECHAZADA
2. Ajustar Student-t u otra fat-tailed --> nu ~ 4
3. Simular con la distribucion correcta (no Normal)
4. LGN garantiza convergencia
5. TLC da intervalos de confianza
6. Resultado: MCS robusto con incertidumbre cuantificada
```

### [SLIDE: Resumen]
| Concepto | Que garantiza | Condicion |
|----------|--------------|-----------|
| LGN | Promedio converge a E[X] | E[X] existe |
| TLC | Error del promedio es Normal | Var(X) finita |
| MCS | Simular distribucion completa | LGN + TLC |

### [CTA]
"Ejercicio: simula el precio de una opcion call con MCS.
Usa N=100, 1000, 10000. Para cada N, calcula el IC 95%.
Cuando el IC es lo suficientemente estrecho para una decision?"

---

## Notas de Produccion
- Animar convergencia de la media con grafico en tiempo real
- Histograma de medias muestrales como build progresivo
- Demo Cauchy como "contra-ejemplo" (TLC falla)
- source_ref: turn0browsertab744690698
