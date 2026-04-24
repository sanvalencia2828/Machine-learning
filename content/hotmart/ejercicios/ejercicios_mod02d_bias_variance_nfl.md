# Ejercicios Practicos -- Modulo 2D: Bias-Variance Tradeoff y No Free Lunch
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Descomposicion Bias-Variance Manual

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Dados 3 modelos que predicen el retorno de un activo:

| Dia | Retorno real | Modelo A | Modelo B | Modelo C |
|-----|-------------|----------|----------|----------|
| 1   | 0.02        | 0.01     | 0.03     | 0.02     |
| 2   | -0.01       | 0.01     | -0.03    | -0.01    |
| 3   | 0.03        | 0.01     | 0.05     | 0.04     |
| 4   | -0.02       | 0.01     | -0.04    | -0.03    |
| 5   | 0.01        | 0.01     | 0.02     | 0.00     |

1. Calcula el MSE de cada modelo
2. El Modelo A siempre predice 0.01. Tiene bias alto o varianza alta?
3. El Modelo B exagera los movimientos. Tiene bias alto o varianza alta?
4. El Modelo C es cercano pero no perfecto. Donde esta su error?

### Codigo inicial
```python
import numpy as np

real = np.array([0.02, -0.01, 0.03, -0.02, 0.01])
modelo_a = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
modelo_b = np.array([0.03, -0.03, 0.05, -0.04, 0.02])
modelo_c = np.array([0.02, -0.01, 0.04, -0.03, 0.00])

# TODO: calcular MSE para cada modelo
# TODO: clasificar el tipo de error dominante
```

### Respuesta esperada
- A: MSE alto, bias alto (siempre predice lo mismo = underfitting)
- B: MSE moderado, varianza alta (amplifica senales)
- C: MSE bajo, equilibrado (el mejor de los tres)

---

## Ejercicio 2: Overfitting en Backtesting de Estrategias

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Genera 500 retornos diarios sinteticos con un patron debil:
`retorno = 0.001 * factor + ruido(0, 0.02)`

1. Divide en train (350) y test (150)
2. Ajusta polinomios de grado 1, 3, 5, 10, 20 al train
3. Calcula MSE en train y test para cada grado
4. Grafica ambas curvas. Donde se separan?
5. Si estuvieras haciendo backtesting de una estrategia,
   que grado elegiras? Por que?

### Codigo inicial
```python
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

np.random.seed(42)
n = 500
factor = np.random.normal(0, 1, n)
retorno = 0.001 * factor + np.random.normal(0, 0.02, n)

# TODO: split train/test
# TODO: ajustar polinomios de diferentes grados
# TODO: graficar MSE train vs test
# TODO: identificar el punto de overfitting
```

### Pista
El MSE de train siempre baja con mas complejidad. El MSE de test
baja y luego SUBE. El punto donde se separan es donde empieza
el overfitting -- equivalente a una estrategia que "funciona" en
backtest pero falla en vivo.

---

## Ejercicio 3: No Free Lunch -- Tu Propio Experimento

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Crea 4 problemas de regresion sinteticos con diferentes estructuras:

1. **Lineal**: y = 3x + 1 + ruido
2. **Cuadratico**: y = x^2 - 0.5 + ruido
3. **Escalonado**: y = 1 si x > 0.5, else 0 + ruido
4. **Periodico**: y = sin(6*pi*x) + ruido

Prueba 4 algoritmos: LinearRegression, Ridge(alpha=1),
DecisionTree(max_depth=5), KNN(k=7).

1. Cual algoritmo gana en cada problema?
2. Hay algun algoritmo que gane en los 4?
3. Que pasa si no sabes nada sobre la estructura?

### Codigo inicial
```python
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor

# TODO: definir 4 funciones generadoras
# TODO: para cada problema, probar 4 algoritmos (30 repeticiones)
# TODO: construir tabla de MSE promedio
# TODO: identificar el ganador por problema
# TODO: verificar que ningun algoritmo domina en todos
```

---

## Ejercicio 4: Regularizacion como Prior -- OLS vs Ridge

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Genera datos de una funcion sinusoidal con ruido fuerte (sigma=0.4).
Ajusta un polinomio de grado 12 con:

1. OLS (sin regularizacion)
2. Ridge con alpha = 0.001, 0.01, 0.1, 1.0, 10.0
3. Para cada alpha, calcula MSE train y MSE test
4. Grafica las curvas de ajuste para OLS y el mejor Ridge

### Preguntas
- Ridge con alpha alto es equivalente a que tipo de prior?
- Por que Ridge mejora el MSE test aunque empeora el MSE train?
- Como se conecta esto con priors bayesianos?

```python
from sklearn.linear_model import Ridge

# Prior bayesiano equivalente:
# Ridge(alpha) <=> Prior N(0, sigma^2 / alpha) sobre los coeficientes
# alpha grande = prior fuerte hacia 0 (modelo simple)
# alpha pequeno = prior debil (casi OLS)

# TODO: implementar la comparacion
# TODO: graficar ajustes
# TODO: encontrar alpha optimo por validacion cruzada
```

---

## Ejercicio 5: Aplicacion -- Modelo CAPM vs Red Neuronal

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Simula retornos de un activo que sigue un CAPM no lineal:
`r_asset = 0.005 + 1.2 * r_market + 0.5 * r_market^2 + ruido(0, 0.01)`

1. Genera 1000 observaciones (700 train, 300 test)
2. Ajusta: (a) CAPM lineal, (b) Polinomio grado 2,
   (c) Polinomio grado 10, (d) Arbol profundidad 10
3. Calcula MSE train y test. Cual es el tradeoff?
4. Repite con solo 50 datos de train. Como cambia el ranking?
5. Que modelo recomendarias a un portfolio manager? Por que?

### Codigo inicial
```python
import numpy as np

np.random.seed(42)
n = 1000
r_market = np.random.normal(0.001, 0.015, n)
r_asset = (0.005 + 1.2 * r_market + 0.5 * r_market**2
           + np.random.normal(0, 0.01, n))

# TODO: split train/test
# TODO: ajustar 4 modelos
# TODO: comparar MSE
# TODO: repetir con n_train = 50
# TODO: explicar como NFL y bias-variance guian la eleccion
```

### Respuesta esperada
- Con n=700: polinomio grado 2 gana (captura la no linealidad sin overfitting)
- Con n=50: CAPM lineal gana (menos varianza, bias aceptable con pocos datos)
- NFL: no hay respuesta universal; depende de n y estructura
- Recomendacion: empezar simple, agregar complejidad solo si los datos lo permiten

---

## Ejercicio 6 (Bonus): Visualiza tu Propio Tradeoff

**Nivel:** Conceptual
**Tiempo estimado:** 15 min

### Enunciado
Para cada situacion financiera, indica si priorizarias reducir bias
o reducir varianza. Justifica.

| Situacion | Bias o Varianza? | Por que? |
|-----------|-----------------|----------|
| 100 anos de datos del S&P 500 | | |
| 10 dias de datos de un IPO reciente | | |
| Prediccion intradiaria de alta frecuencia | | |
| Estimacion de probabilidad de default | | |
| Modelo de riesgo regulatorio (Basilea) | | |

### Reflexion
El bias-variance tradeoff en finanzas no es solo tecnico:
- Reguladores prefieren modelos con bias alto (conservadores)
- Traders prefieren modelos con varianza controlada (estables)
- El costo del error no es simetrico (perder > no ganar)
