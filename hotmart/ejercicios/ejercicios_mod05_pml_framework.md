# Ejercicios Practicos -- Modulo 5: Framework PML
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Prior, Likelihood y Posterior a Mano

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Un analista evalua un nuevo fondo con prior Beta(2,8) para P(outperform).
Observa que el fondo supera al benchmark 7 de 10 trimestres.

1. Identifica alpha_prior, beta_prior
2. Calcula alpha_post = alpha_prior + 7, beta_post = beta_prior + 3
3. Calcula media prior y media posterior
4. Grafica prior y posterior superpuestos
5. Calcula P(outperform > 50%) con el posterior
6. El dato movio significativamente la creencia?

```python
from scipy import stats
prior = stats.beta(2, 8)
posterior = stats.beta(2+7, 8+3)
# TODO: medias, graficos, P(theta > 0.5)
```

---

## Ejercicio 2: Sensibilidad al Prior

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Mismos datos (7 de 10 outperform). Prueba 3 priors:
1. Esceptico: Beta(1, 9) (media 10%)
2. Neutro: Beta(1, 1) (media 50%)
3. Optimista: Beta(9, 1) (media 90%)

Para cada uno:
1. Calcula el posterior
2. Grafica los 3 posteriors juntos
3. Con cual prior la conclusion cambia mas?
4. Con 100 datos en vez de 10, importa el prior?

---

## Ejercicio 3: Actualizacion Secuencial de Default

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Un fondo de bonos high-yield monitorea defaults trimestralmente:
- Prior: Beta(2, 18) (tasa historica ~10%)
- Q1: 20 bonos, 2 defaults
- Q2: 20 bonos, 1 default
- Q3: 20 bonos, 0 defaults
- Q4: 20 bonos, 3 defaults

1. Actualiza secuencialmente el posterior despues de cada trimestre
2. Grafica la evolucion de la media posterior y HDI 95%
3. En que trimestre la estimacion cambia mas?
4. Calcula P(default_rate > 15%) despues de cada trimestre
5. Deberia el fondo reducir exposicion a high-yield?

---

## Ejercicio 4: Distribuciones Predictivas

**Nivel:** Avanzado
**Tiempo estimado:** 30 min

### Enunciado
Usando el posterior Beta(5, 25) del caso de bonos:

1. Genera 50,000 muestras de theta ~ Beta(5, 25)
2. Para cada theta, simula defaults en 20 bonos: d ~ Binomial(20, theta)
3. Histograma de d = posterior predictive
4. Repite con el prior Beta(2, 8) = prior predictive
5. Compara: la posterior predictive es mas concentrada?
6. P(5+ defaults en proximos 20 bonos) = ???

```python
theta_post = np.random.beta(5, 25, 50000)
defaults_sim = np.array([np.random.binomial(20, t) for t in theta_post])
# TODO: histograma y calcular P(defaults >= 5)
```

---

## Ejercicio 5: Mini-Proyecto -- Modelo Bayesiano para Retorno de Activo

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Modela el retorno mensual de un activo con Normal-Normal conjugado:

Prior: mu ~ Normal(0.005, 0.003) [retorno 0.5% mensual +/- 0.3%]
Datos: 12 meses con media 0.008 y std 0.04

1. Calcula el posterior de mu (Normal conjugado)
2. Calcula HDI 95% del posterior
3. P(retorno mensual > 0) = ???
4. Genera posterior predictive: r_nuevo ~ Normal(mu_post, sigma_obs)
5. Compara con IC frecuentista de la media

```python
# Normal-Normal conjugado:
tau_prior = 1 / 0.003**2
tau_data = 12 / 0.04**2  # n / sigma^2
tau_post = tau_prior + tau_data
mu_post = (tau_prior * 0.005 + tau_data * 0.008) / tau_post
sigma_post = 1 / np.sqrt(tau_post)
```

---

## Ejercicio 6 (Bonus): Monty Hall como Introduccion a Bayes

**Nivel:** Basico-Conceptual
**Tiempo estimado:** 15 min

### Enunciado
El problema de Monty Hall:
- 3 puertas: 1 auto, 2 cabras
- Eliges puerta 1
- Monty abre puerta 3 (cabra)
- Cambias o te quedas?

1. Define priors: P(auto_puerta_i) = 1/3 para cada puerta
2. Calcula likelihood: P(Monty abre 3 | auto en 1, 2, 3)
3. Aplica Bayes para P(auto en 2 | Monty abrio 3)
4. Resultado: cambiar duplica la probabilidad de ganar
5. Conecta con finanzas: nueva informacion SIEMPRE actualiza priors
