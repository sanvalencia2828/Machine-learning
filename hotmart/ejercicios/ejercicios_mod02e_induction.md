# Ejercicios Practicos -- Modulo 2E: El Problema de la Induccion
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Simula tu Propio Pavo de Russell

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Simula una estrategia de carry trade que genera retornos estables
(mu=0.0008, sigma=0.003) durante 2 anos (504 dias) y luego colapsa
cuando la moneda se devalua (mu=-0.05, sigma=0.08, 20 dias).

1. Genera los retornos y grafica el precio acumulado
2. Calcula el retorno total pre-crisis y post-crisis
3. Cuantos dias de ganancias se necesitan para recuperar la crisis?
4. Cual es la relacion entre "confianza" y "fragilidad"?

### Codigo inicial
```python
import numpy as np

np.random.seed(42)
ret_calma = np.random.normal(0.0008, 0.003, 504)
ret_crisis = np.random.normal(-0.05, 0.08, 20)
retornos = np.concatenate([ret_calma, ret_crisis])

precios = 100 * np.exp(np.cumsum(retornos))

# TODO: graficar precios
# TODO: calcular retornos por periodo
# TODO: calcular dias necesarios para recuperar
```

### Respuesta esperada
La crisis de 20 dias destruye ~2 anos de ganancias.
Dias para recuperar: mu_calma * n_dias = perdida_crisis.

---

## Ejercicio 2: Frecuentista vs Bayesiano -- Ancho del IC/HDI

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera 300 retornos de calma (mu=0.001, sigma=0.01) seguidos de
100 retornos de crisis (mu=-0.02, sigma=0.03).

1. Calcula el IC 95% frecuentista acumulado (dia por dia)
2. Calcula el HDI 95% bayesiano con prior N(0, 0.005)
3. Grafica ambos. En que dia el frecuentista "se engana"?
4. En que dia el bayesiano "reacciona" a la crisis?

### Preguntas clave
- Por que el IC frecuentista sigue estrecho durante la crisis?
- El bayesiano es "mejor"? O solo es "menos confiado"?
- Que prior elegiras si NO supieras que viene una crisis?

```python
# HINT: IC frecuentista = mu +/- 1.96 * std/sqrt(n)
# HINT: Bayesiano Normal-Normal: tau_post = tau_prior + n*tau_like
```

---

## Ejercicio 3: Detector de Cambio de Regimen

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Implementa un detector de cambio de regimen con ventana deslizante.

1. Genera datos del pavo (500 calma + 50 crisis)
2. Prueba con ventanas de 10, 20, 50, 100 dias
3. Para cada ventana, registra: dia de deteccion y falsos positivos
4. Grafica el tradeoff: ventana mas corta = deteccion rapida pero mas falsos positivos

### Codigo inicial
```python
def detectar_cambio(retornos, ventana, umbral_z=3.0):
    """Detecta cambio de regimen con z-score deslizante."""
    detecciones = []
    for i in range(ventana * 2, len(retornos)):
        hist = retornos[:i - ventana]
        reciente = retornos[i - ventana:i]
        z = (reciente.mean() - hist.mean()) / (hist.std() / (ventana**0.5))
        if abs(z) > umbral_z:
            detecciones.append(i)
    return detecciones

# TODO: probar con diferentes ventanas
# TODO: contar falsos positivos (detecciones antes del quiebre real)
# TODO: graficar tradeoff
```

---

## Ejercicio 4: Stress Test de tu Portafolio

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Toma un portafolio hipotetico con capital $500,000 invertido en
una estrategia con retornos historicos mu=0.0005, sigma=0.01.

Simula 4 escenarios de falla inductiva (10,000 iteraciones cada uno):

| Escenario | mu_crisis | sigma_crisis | Duracion |
|-----------|-----------|-------------|----------|
| Correccion suave | -0.005 | 0.02 | 60 dias |
| Bear market | -0.015 | 0.03 | 120 dias |
| Crisis aguda | -0.04 | 0.06 | 30 dias |
| Flash crash | -0.10 | 0.15 | 5 dias |

1. Para cada escenario: calcula perdida media, P95, max, y P(ruina>30%)
2. Cual escenario es mas peligroso: lento-gradual o rapido-agudo?
3. Cuanto capital deberas reservar como "colchon inductivo"?

```python
# TODO: simular cada escenario
# TODO: calcular metricas de riesgo
# TODO: determinar capital de reserva
```

---

## Ejercicio 5: Falsacionismo Aplicado

**Nivel:** Avanzado
**Tiempo estimado:** 25 min

### Enunciado
Tienes una estrategia de momentum que ha funcionado 3 anos (756 dias).
Aplica el enfoque falsacionista de Popper:

1. Divide los datos en ventanas de 60 dias (12+ ventanas)
2. Para cada ventana, haz un test t: "la media es > 0?"
3. Cuenta cuantas ventanas REFUTAN la hipotesis (p < 0.05, media < 0)
4. Si mas del 20% de las ventanas refutan, la estrategia es fragil

### Pregunta clave
Una estrategia que NUNCA es refutada en 3 anos... deberia darte
mas confianza o MENOS? (Pista: piensa en el pavo.)

```python
from scipy import stats

# Generar datos de estrategia "exitosa"
np.random.seed(42)
retornos = np.random.normal(0.0003, 0.015, 756)

ventana = 60
n_ventanas = len(retornos) // ventana

refutaciones = 0
for i in range(n_ventanas):
    sub = retornos[i * ventana:(i + 1) * ventana]
    t_stat, p_val = stats.ttest_1samp(sub, 0)
    # TODO: contar refutaciones
    # TODO: analizar la tasa de refutacion
```

---

## Ejercicio 6 (Bonus): El Cisne Negro de Taleb

**Nivel:** Conceptual
**Tiempo estimado:** 15 min

### Enunciado
Para cada evento historico, explica:
(a) Que "indujo" el mercado antes del evento
(b) Por que la induccion fallo
(c) Que senales (si alguna) existian

| Evento | Induccion previa | Por que fallo | Senales ignoradas |
|--------|-----------------|---------------|-------------------|
| Black Monday 1987 | | | |
| Crisis asiatica 1997 | | | |
| Dot-com 2000 | | | |
| Lehman 2008 | | | |
| Flash crash 2010 | | | |
| COVID 2020 | | | |

### Reflexion
Taleb argumenta que los cisnes negros son "predecibles en retrospectiva
pero impredecibles en prospectiva". Si esto es cierto:
1. Tiene sentido hacer predicciones puntuales?
2. Que rol juegan los priors bayesianos ante lo impredecible?
3. Como cambia tu filosofia de inversion si aceptas la induccion?
