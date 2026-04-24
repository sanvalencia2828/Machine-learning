# Ejercicios Practicos -- Modulo 3: Simulacion Monte Carlo
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Estimar Pi con Monte Carlo

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
Estima Pi lanzando puntos aleatorios en un cuadrado de lado 2 centrado
en el origen. Un punto esta dentro del circulo si x^2 + y^2 <= 1.

1. Genera N = 100, 1000, 10000, 100000 puntos
2. Estima Pi = 4 * (puntos dentro / total)
3. Calcula el error absoluto |Pi_est - Pi_real| para cada N
4. Grafica la convergencia. A que tasa baja el error?

### Codigo inicial
```python
import numpy as np

def estimar_pi(n, seed=42):
    np.random.seed(seed)
    x = np.random.uniform(-1, 1, n)
    y = np.random.uniform(-1, 1, n)
    dentro = (x**2 + y**2) <= 1
    return 4 * dentro.mean()

# TODO: probar con diferentes N
# TODO: graficar convergencia
# TODO: verificar que error ~ 1/sqrt(N)
```

### Respuesta esperada
Error ~ 1/sqrt(N). Con N=100000, error < 0.01.

---

## Ejercicio 2: Los 4 Momentos de Retornos Financieros

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera 10000 retornos diarios con 3 distribuciones diferentes:
- Normal(0.0004, 0.012)
- Student-t(nu=4, loc=0.0004, scale=0.008)
- Mezcla: 95% Normal(0.0004, 0.010) + 5% Normal(-0.005, 0.04)

Para cada distribucion, calcula y compara:
1. Media, Std, Skewness, Curtosis (exceso)
2. P(retorno < -3%) -- probabilidad de evento extremo
3. VaR 95% y Expected Shortfall 95%
4. Cual distribucion es mas "peligrosa" segun cada metrica?

### Codigo inicial
```python
import numpy as np
from scipy import stats

np.random.seed(42)
n = 10000

ret_normal = np.random.normal(0.0004, 0.012, n)
ret_t = 0.0004 + 0.008 * np.random.standard_t(4, n)

# Mezcla
mask = np.random.binomial(1, 0.95, n)
ret_mezcla = np.where(mask,
    np.random.normal(0.0004, 0.010, n),
    np.random.normal(-0.005, 0.04, n))

# TODO: calcular 4 momentos para cada distribucion
# TODO: calcular P(r < -3%), VaR, ES
# TODO: comparar y graficar
```

---

## Ejercicio 3: LGN y TLC en Accion

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Demuestra la LGN y el TLC con retornos Student-t(nu=3):

**LGN:**
1. Para cada N en [10, 50, 100, 500, 1000, 5000]:
   calcula la media muestral de N retornos
2. Repite 1000 veces y grafica la dispersion de medias
3. Verifica que la dispersion baja con 1/sqrt(N)

**TLC:**
1. Para N=50, genera 10000 medias muestrales
2. Haz un histograma. Es Normal a pesar de que los datos son Student-t?
3. Haz un QQ-plot contra la Normal
4. Si los datos fueran Cauchy (nu=1), el TLC funcionaria? Prueba.

```python
# HINT: Cauchy tiene varianza infinita -> TLC NO aplica
# Esto demuestra que TLC tiene condiciones (varianza finita)
```

---

## Ejercicio 4: MCS para Valoracion de Startup

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Valora una startup fintech con MCS (50,000 simulaciones):

**Factores de riesgo:**
- Inversion inicial: $200,000 (fijo)
- Costo operativo mensual: Triangular($15K, $25K, $40K)
- Meses hasta break-even: LogNormal(mu=2.5, sigma=0.4) [~12 meses]
- Usuarios al ano 1: Poisson(lambda=500)
- Revenue por usuario/mes: Gamma(shape=3, scale=10) [$30 promedio]
- Churn rate mensual: Beta(2, 18) [~10%]

1. Simula 3 anos de operacion
2. Calcula NPV con tasa de descuento 15%
3. Reporta: NPV medio, P(NPV>0), VaR 95%, Expected Shortfall
4. Sensibilidad: cual factor impacta mas el NPV?
5. Que decisiones tomarias basado en la distribucion completa?

### Codigo inicial
```python
import numpy as np

def simular_startup(n_sim=50000, seed=42):
    np.random.seed(seed)
    # Inversion
    inversion = 200_000

    # TODO: generar cada factor de riesgo
    # TODO: calcular flujos de caja mensuales por 36 meses
    # TODO: calcular NPV con descuento mensual
    # TODO: retornar array de NPVs

    pass

# TODO: ejecutar simulacion
# TODO: calcular metricas de riesgo
# TODO: graficar distribucion de NPV
# TODO: analisis de sensibilidad (correlacion NPV vs cada factor)
```

---

## Ejercicio 5: Volatilidad vs Riesgo Real

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Genera dos activos con la MISMA volatilidad (std=1.5%) pero
comportamiento muy diferente:

- **Activo A**: Normal(0.05%, 1.5%) -- simetrico
- **Activo B**: Mezcla: 97% Normal(0.1%, 0.8%) + 3% Normal(-5%, 4%)

1. Verifica que ambos tienen volatilidad similar
2. Calcula VaR 95% y ES 95% para ambos
3. Simula 1000 trayectorias de 252 dias con capital $100K
4. Cual activo tiene mayor probabilidad de perder >20%?
5. La volatilidad te hubiera dicho esto? Conclusion.

```python
# Este ejercicio demuestra por que la volatilidad es una
# medida ABSURDA de riesgo (concepto clave del capitulo 3)
```

---

## Ejercicio 6 (Bonus): MCS con Correlacion entre Factores

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
En el ejercicio 4, asumimos factores independientes. Pero en la
realidad, los factores estan correlacionados (ej: si el costo sube,
el break-even se retrasa).

1. Define una matriz de correlacion entre 3 factores:
   ```
   costo  break_even  churn
   1.0    0.5         0.3
   0.5    1.0         0.2
   0.3    0.2         1.0
   ```
2. Usa la descomposicion de Cholesky para generar factores correlacionados
3. Compara NPV con y sin correlacion
4. La correlacion hace el proyecto MAS o MENOS riesgoso?

### Pista
```python
from scipy.linalg import cholesky

corr = np.array([[1.0, 0.5, 0.3],
                 [0.5, 1.0, 0.2],
                 [0.3, 0.2, 1.0]])
L = cholesky(corr, lower=True)

# Z = variables normales independientes
Z = np.random.normal(0, 1, (n_sim, 3))
# Z_corr = variables normales correlacionadas
Z_corr = Z @ L.T
```
