# Ejercicios Practicos — Modulo 2B: Probabilidades Relativas y Riesgo vs Incertidumbre
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Moneda Sesgada — Frecuentista vs Epistemico

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Tienes una moneda que sospechas esta sesgada. Realizas 20 lanzamientos
y obtienes 14 caras.

1. Calcula la estimacion MLE (frecuentista) de P(cara) y su IC 95%.
2. Usando un prior Beta(2,2), calcula la media posterior y HDI 95%.
3. Repite con solo 5 lanzamientos (4 caras). ¿Que enfoque cambia mas?
4. ¿Cual de los dos enfoques responde la pregunta "¿cual es la probabilidad
   de que la moneda tenga sesgo > 0.6?"

### Codigo inicial
```python
from scipy import stats
import numpy as np

def comparar_enfoques(n_lanzamientos, n_caras, alpha_prior=2, beta_prior=2):
    """Compara estimacion frecuentista vs epistemica."""
    # Frecuentista
    p_hat = n_caras / n_lanzamientos
    se = np.sqrt(p_hat * (1 - p_hat) / n_lanzamientos)
    ic_95 = (p_hat - 1.96 * se, p_hat + 1.96 * se)

    # Epistemico
    alpha_post = alpha_prior + n_caras
    beta_post = beta_prior + (n_lanzamientos - n_caras)
    posterior = stats.beta(alpha_post, beta_post)
    hdi_95 = posterior.ppf([0.025, 0.975])

    # TODO: completar con P(sesgo > 0.6) usando 1 - posterior.cdf(0.6)

    return {"p_hat": p_hat, "ic_95": ic_95,
            "media_post": posterior.mean(), "hdi_95": hdi_95}

# TODO: probar con (20, 14) y (5, 4)
# TODO: graficar ambas distribuciones posterior
```

### Respuesta esperada
Con n=20: ambos enfoques dan resultados similares.
Con n=5: el bayesiano es mas conservador (el prior "encoge" hacia 0.5).
Solo el bayesiano responde P(sesgo > 0.6) directamente: ~76% con n=20.

---

## Ejercicio 2: ¿Riesgo o Incertidumbre? — Clasificacion Critica

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Clasifica cada evento segun Knight (riesgo vs incertidumbre), luego
argumenta por que la clasificacion falla. Asigna un score de 0 a 1
indicando tu confianza en poder estimar probabilidades.

| Evento | Knight diria | Tu score (0-1) | Por que la frontera es difusa |
|--------|-------------|-----------------|-------------------------------|
| Retorno del S&P 500 manana | | | |
| Tesla quiebra en 5 anos | | | |
| Inflacion > 5% proximo ano | | | |
| IA reemplaza tu trabajo en 10 anos | | | |
| Moneda justa sale cara | | | |
| China invade Taiwan este ano | | | |

### Reflexion
1. ¿Hay algun evento que sea PURAMENTE riesgo (probabilidad perfectamente conocida)?
2. ¿Hay algun evento que sea PURAMENTE incertidumbre (sin base para estimar)?
3. Si la respuesta a ambos es "no", ¿que nos dice sobre la utilidad de la distincion?

```python
# Genera el espectro como barplot horizontal
import matplotlib.pyplot as plt

eventos = ["Moneda justa", "S&P 500 manana", "Inflacion >5%",
           "Tesla quiebra", "IA reemplaza trabajo", "China invade Taiwan"]

# TODO: asignar tus scores y graficar
# scores = [?, ?, ?, ?, ?, ?]
```

---

## Ejercicio 3: Valor de la Informacion — ¿Cuanto Vale Saber Mas?

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Un fondo de cobertura evalua si invertir en bonos de una empresa.
Necesita estimar P(default).

- Prior: Beta(2, 18) → media 10%, basado en rating BBB historico
- Dato 1: La empresa reporta ingresos record → 0 defaults en 1 "trial"
- Dato 2: Analista descubre deuda oculta → 1 default en 1 "trial"
- Dato 3: Fed baja tasas → 0 defaults en 3 "trials" (entorno favorable)

1. Actualiza la posterior secuencialmente con cada dato.
2. Grafica como cambia P(default) y el ancho del HDI.
3. ¿Cuanto redujo la incertidumbre cada dato? (mide en ancho de HDI)
4. Si contratar un analista cuesta $50,000 y el fondo invierte $10M,
   ¿vale la pena la informacion adicional?

### Codigo inicial
```python
from scipy import stats
import numpy as np

def actualizar_default(alpha, beta, exitos, trials):
    """Actualiza posterior Beta con nuevos datos.

    Parametros
    ----------
    alpha, beta : float
        Parametros actuales de la posterior.
    exitos : int
        Numero de defaults observados.
    trials : int
        Numero de observaciones.

    Retorna
    -------
    tuple : (alpha_nuevo, beta_nuevo)
    """
    return alpha + exitos, beta + (trials - exitos)

# Prior
alpha, beta = 2, 18

# TODO: actualizar con cada dato
# TODO: calcular HDI en cada paso
# TODO: graficar la evolucion
# TODO: calcular el valor monetario de la reduccion de incertidumbre
```

### Pista
El valor de la informacion se puede aproximar como:
```
valor_info = inversion * (ancho_hdi_antes - ancho_hdi_despues) / ancho_hdi_antes
```
Si `valor_info > costo_analista`, vale la pena.

---

## Ejercicio 4: Portafolio bajo Dos Paradigmas

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Simula 2 anos de retornos diarios de un activo con colas pesadas
(Student-t, nu=4) y compara las decisiones de asignacion de capital
bajo dos frameworks:

**Framework A (Frecuentista):**
- Asume retornos normales
- Calcula VaR parametrico al 95%
- Asigna capital: max_allocation = capital / |VaR|

**Framework B (Epistemico):**
- Ajusta Student-t a los datos
- Calcula VaR desde la distribucion ajustada
- Asigna capital: max_allocation = capital / |VaR_t|

1. Genera 504 retornos diarios con mu=0.0003, sigma=0.012, nu=4
2. Calcula VaR y Expected Shortfall bajo ambos frameworks
3. Simula 1000 trayectorias de portafolio (252 dias) con cada asignacion
4. ¿Cual framework tiene menor probabilidad de ruina (valor < 0)?

### Codigo inicial
```python
import numpy as np
from scipy import stats

def simular_retornos(n=504, mu=0.0003, sigma=0.012, nu=4, seed=42):
    """Genera retornos diarios con colas pesadas."""
    np.random.seed(seed)
    return mu + sigma * np.random.standard_t(nu, size=n)

def var_frecuentista(retornos, nivel=0.05):
    """VaR parametrico normal."""
    mu = retornos.mean()
    sigma = retornos.std()
    return mu + stats.norm.ppf(nivel) * sigma

def var_epistemico(retornos, nivel=0.05):
    """VaR con Student-t ajustada."""
    nu, mu, sigma = stats.t.fit(retornos)
    return stats.t.ppf(nivel, nu, mu, sigma)

# TODO: generar retornos
# TODO: calcular VaR y ES bajo ambos frameworks
# TODO: simular trayectorias de portafolio
# TODO: comparar probabilidad de ruina
# TODO: graficar distribucion de riqueza final
```

### Respuesta esperada
- VaR frecuentista subestima el riesgo de cola ~20-40%
- Asignacion frecuentista es ~20-40% mas agresiva
- Probabilidad de ruina frecuentista > epistemico
- El epistemico "pierde" retornos esperados pero "gana" supervivencia

---

## Ejercicio 5 (Bonus): Replicar el Debate Knight-Keynes

**Nivel:** Conceptual / Investigacion
**Tiempo estimado:** 20 min

### Enunciado
Lee las siguientes afirmaciones y argumenta a favor o en contra:

1. "No puedo asignar una probabilidad a que la Fed suba tasas porque
    es un evento unico, no repetible." (Argumento frecuentista)

2. "La probabilidad de un cisne negro es exactamente cero porque nunca
    ha ocurrido." (Argumento inductivo)

3. "Si no puedo medir la probabilidad con datos historicos, la
    incertidumbre es irreducible." (Argumento Knight)

4. "Toda probabilidad es una declaracion sobre mi informacion, no
    sobre el mundo." (Argumento epistemico)

### Para reflexionar
- ¿Es posible que un evento tenga probabilidad 0 y aun asi ocurra?
- ¿Que herramienta usarias para cada tipo de incertidumbre?
  - Aleatoria → distribuciones parametricas + MCS
  - Epistemica → priors + regla inversa
  - Ontologica → stress testing + escenarios extremos
