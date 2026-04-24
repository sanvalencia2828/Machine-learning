---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# MLE vs Modelos Probabilisticos: Expectativas de Ganancias

<!-- Capitulo 6 del libro "Probabilistic ML for Finance and Investing" -->
<!-- Compara Maximum Likelihood Estimation con el enfoque probabilistico completo -->
<!-- Requisitos: numpy, pandas, scipy, matplotlib -->

```python
# Importaciones
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

np.random.seed(42)
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
```

---

## 1. Modelo MLE para Earnings Expectations (Bernoulli)

<!-- Escenario: empresa reporta earnings beats consecutivos -->
<!-- MLE con Bernoulli: si observamos 3/3 beats, MLE estima theta=1.0 -->
<!-- Esto lleva a 100% de certeza, lo cual es absurdo -->

```python
# --- Estimacion MLE con datos de earnings ---
# Cada trimestre: 1 = earnings beat, 0 = earnings miss
# Observamos 3 trimestres consecutivos de beats

datos_earnings = np.array([1, 1, 1])
n_obs = len(datos_earnings)
n_beats = datos_earnings.sum()

# MLE para Bernoulli: theta_hat = n_exitos / n_total
theta_mle = n_beats / n_obs

print("=== Estimacion MLE de Earnings Beats ===")
print(f"Datos observados: {datos_earnings.tolist()}")
print(f"Numero de beats: {n_beats} de {n_obs}")
print(f"theta_MLE = {theta_mle:.4f}")
print(f"\nEl MLE predice con {theta_mle:.0%} de certeza que el proximo trimestre sera beat.")
print("Esto es claramente una sobreestimacion peligrosa.")

# Prediccion MLE para el proximo trimestre
prob_beat_mle = theta_mle
print(f"\nP(beat proximo | MLE) = {prob_beat_mle:.4f}")
```

```python
# Visualizar el problema del MLE con pocos datos
# Mostrar como cambia theta_MLE con distintas secuencias

secuencias = {
    '1 de 1': [1],
    '2 de 2': [1, 1],
    '3 de 3': [1, 1, 1],
    '5 de 5': [1, 1, 1, 1, 1],
    '0 de 1': [0],
    '0 de 3': [0, 0, 0],
}

fig, ax = plt.subplots(figsize=(10, 5))
nombres = list(secuencias.keys())
mle_vals = [np.mean(v) for v in secuencias.values()]
colores = ['#e74c3c' if v in (0.0, 1.0) else '#3498db' for v in mle_vals]

ax.barh(nombres, mle_vals, color=colores, edgecolor='black')
ax.set_xlabel('theta_MLE')
ax.set_title('MLE con Pocos Datos: Valores Extremos')
ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5, label='theta = 0.5')
ax.set_xlim(-0.05, 1.1)

# Anotar barras problematicas
for i, (nombre, val) in enumerate(zip(nombres, mle_vals)):
    etiqueta = "PELIGRO" if val in (0.0, 1.0) else ""
    ax.text(val + 0.02, i, f'{val:.2f} {etiqueta}', va='center', fontweight='bold',
            color='red' if val in (0.0, 1.0) else 'black')

ax.legend()
plt.tight_layout()
plt.show()
```

---

## 2. Por Que MLE Falla con Datos Escasos

<!-- Analisis formal de las limitaciones del MLE -->

```python
# --- Analisis de las fallas del MLE ---

# Problema 1: Sobreajuste - MLE memoriza los datos
# Con pocos datos, theta_MLE esta en los extremos (0 o 1)
print("=== Fallas del MLE con Datos Escasos ===\n")
print("1. SOBREAJUSTE EXTREMO:")
print("   Con n pequeno, theta_MLE solo puede tomar valores {0/n, 1/n, ..., n/n}")
print(f"   Con n=3: valores posibles = {[round(k/3, 4) for k in range(4)]}")

# Problema 2: No cuantifica incertidumbre
print("\n2. SIN CUANTIFICACION DE INCERTIDUMBRE:")
print("   MLE da un punto, no una distribucion")
print("   No sabemos si theta=1.0 es confiable o no")

# Problema 3: Predicciones degeneradas
print("\n3. PREDICCIONES DEGENERADAS:")
print("   Si theta_MLE=1.0, predice beats para siempre")
print("   Si theta_MLE=0.0, predice misses para siempre")
print("   Ambos son imposibles en mercados reales")

# Simulacion: variabilidad del MLE con muestras repetidas
n_repeticiones = 10_000
verdadero_theta = 0.65  # Tasa real de beats

mle_n3 = np.array([np.random.binomial(3, verdadero_theta) / 3 for _ in range(n_repeticiones)])
mle_n50 = np.array([np.random.binomial(50, verdadero_theta) / 50 for _ in range(n_repeticiones)])

print(f"\n--- Variabilidad del MLE (theta verdadero = {verdadero_theta}) ---")
print(f"Con n=3:  media={mle_n3.mean():.3f}, std={mle_n3.std():.3f}, "
      f"P(MLE=1.0)={np.mean(mle_n3==1.0):.3f}")
print(f"Con n=50: media={mle_n50.mean():.3f}, std={mle_n50.std():.3f}, "
      f"P(MLE=1.0)={np.mean(mle_n50==1.0):.3f}")
```

```python
# Distribucion muestral del MLE con distintos tamanios de muestra
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(mle_n3, bins=np.arange(-0.05, 1.15, 1/3) - 1/6,
             density=True, color='#e74c3c', alpha=0.7, edgecolor='black', rwidth=0.8)
axes[0].axvline(x=verdadero_theta, color='black', linestyle='--', linewidth=2,
                label=f'theta real = {verdadero_theta}')
axes[0].set_title('Distribucion de theta_MLE con n=3')
axes[0].set_xlabel('theta_MLE')
axes[0].set_ylabel('Densidad')
axes[0].legend()
axes[0].grid(alpha=0.3)

axes[1].hist(mle_n50, bins=30, density=True, color='#2ecc71', alpha=0.7, edgecolor='black')
axes[1].axvline(x=verdadero_theta, color='black', linestyle='--', linewidth=2,
                label=f'theta real = {verdadero_theta}')
axes[1].set_title('Distribucion de theta_MLE con n=50')
axes[1].set_xlabel('theta_MLE')
axes[1].set_ylabel('Densidad')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.suptitle(f'Variabilidad del MLE (theta verdadero = {verdadero_theta})', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

---

## 3. Modelo Probabilistico: Prior Uniforme + Likelihood Bernoulli

<!-- Solucion bayesiana: poner un prior y calcular el posterior -->
<!-- Prior uniforme Beta(1,1) = no preferencia inicial -->
<!-- Likelihood Bernoulli con datos observados -->

```python
# --- Modelo probabilistico completo ---
# Prior: Beta(1, 1) = distribucion uniforme en [0, 1]
# Equivale a decir "no tengo preferencia sobre theta"
alfa_prior = 1
beta_prior = 1

# Datos: 3 beats de 3
n_total = 3
n_beats = 3
n_misses = n_total - n_beats

# Posterior analitico: Beta(alfa + beats, beta + misses)
alfa_post = alfa_prior + n_beats
beta_post = beta_prior + n_misses

# Estadisticas del posterior
media_post = alfa_post / (alfa_post + beta_post)
moda_post = (alfa_post - 1) / (alfa_post + beta_post - 2) if (alfa_post > 1 and beta_post > 1) else None
varianza_post = (alfa_post * beta_post) / ((alfa_post + beta_post)**2 * (alfa_post + beta_post + 1))
ic_95 = stats.beta.ppf([0.025, 0.975], alfa_post, beta_post)

print("=== Modelo Probabilistico ===")
print(f"Prior: Beta({alfa_prior}, {beta_prior})")
print(f"Datos: {n_beats} beats, {n_misses} misses")
print(f"Posterior: Beta({alfa_post}, {beta_post})")
print(f"\nEstadisticas del Posterior:")
print(f"  Media:    {media_post:.4f}")
print(f"  Moda:     {moda_post if moda_post else 'No definida (esquina)'}")
print(f"  Varianza: {varianza_post:.4f}")
print(f"  Std:      {np.sqrt(varianza_post):.4f}")
print(f"  IC 95%:   [{ic_95[0]:.4f}, {ic_95[1]:.4f}]")
print(f"\nComparacion:")
print(f"  MLE dice theta = {theta_mle:.2f} (certeza absoluta)")
print(f"  Bayes dice theta ~ Beta({alfa_post},{beta_post}) con media {media_post:.2f} e incertidumbre")
```

```python
# Visualizar prior, likelihood y posterior
x = np.linspace(0, 1, 500)

# Prior
prior_pdf = stats.beta.pdf(x, alfa_prior, beta_prior)

# Likelihood (proporcional): theta^k * (1-theta)^(n-k) para k=3, n=3
likelihood_proporcional = x**n_beats * (1 - x)**n_misses
# Normalizar para visualizacion
likelihood_normalizada = likelihood_proporcional / np.trapz(likelihood_proporcional, x)

# Posterior
posterior_pdf = stats.beta.pdf(x, alfa_post, beta_post)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, prior_pdf, 'b--', linewidth=2, label=f'Prior: Beta({alfa_prior},{beta_prior})')
ax.plot(x, likelihood_normalizada, 'g:', linewidth=2, label='Likelihood (normalizada)')
ax.plot(x, posterior_pdf, 'r-', linewidth=2.5, label=f'Posterior: Beta({alfa_post},{beta_post})')
ax.fill_between(x, posterior_pdf, alpha=0.15, color='red')

# Marcar MLE
ax.axvline(x=theta_mle, color='black', linestyle='-.', alpha=0.7, label=f'MLE = {theta_mle:.2f}')

ax.set_xlabel('theta (probabilidad de beat)')
ax.set_ylabel('Densidad')
ax.set_title('Actualizacion Bayesiana: Prior x Likelihood -> Posterior')
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
ax.set_xlim(0, 1)
plt.tight_layout()
plt.show()
```

---

## 4. Grid Approximation: 9 Puntos, Posterior Paso a Paso

<!-- Aproximacion discreta del posterior usando una grilla -->
<!-- Util para entender mecanicamente como funciona Bayes -->

```python
# --- Grid approximation con 9 puntos ---
n_puntos = 9
grilla_theta = np.linspace(0.1, 0.9, n_puntos)  # Evitar 0 y 1 exactos

# Paso 1: Prior en cada punto (uniforme => todos iguales)
prior_grilla = np.ones(n_puntos) / n_puntos

# Paso 2: Likelihood en cada punto: P(datos | theta) = theta^3 * (1-theta)^0
likelihood_grilla = grilla_theta**n_beats * (1 - grilla_theta)**n_misses

# Paso 3: Producto no normalizado
producto = prior_grilla * likelihood_grilla

# Paso 4: Normalizar para obtener posterior
posterior_grilla = producto / producto.sum()

# Construir tabla detallada
tabla_grid = pd.DataFrame({
    'theta': grilla_theta,
    'Prior': prior_grilla,
    'Likelihood': likelihood_grilla,
    'Prior x Likelihood': producto,
    'Posterior': posterior_grilla
})

print("=== Grid Approximation: 9 Puntos ===\n")
print(tabla_grid.to_string(index=False, float_format='{:.6f}'.format))
print(f"\nSuma de posteriors: {posterior_grilla.sum():.6f} (debe ser 1.0)")
print(f"\nMedia del posterior (grid): {np.sum(grilla_theta * posterior_grilla):.4f}")
print(f"Media del posterior (exacto): {media_post:.4f}")
```

```python
# Visualizacion paso a paso de grid approximation
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# (a) Prior
axes[0, 0].bar(grilla_theta, prior_grilla, width=0.07, color='#3498db', edgecolor='black')
axes[0, 0].set_title('Paso 1: Prior (Uniforme)')
axes[0, 0].set_xlabel('theta')
axes[0, 0].set_ylabel('P(theta)')
axes[0, 0].set_ylim(0, max(prior_grilla) * 1.3)
axes[0, 0].grid(alpha=0.3)

# (b) Likelihood
axes[0, 1].bar(grilla_theta, likelihood_grilla, width=0.07, color='#2ecc71', edgecolor='black')
axes[0, 1].set_title('Paso 2: Likelihood P(datos|theta)')
axes[0, 1].set_xlabel('theta')
axes[0, 1].set_ylabel('P(datos|theta)')
axes[0, 1].grid(alpha=0.3)

# (c) Producto sin normalizar
axes[1, 0].bar(grilla_theta, producto, width=0.07, color='#f39c12', edgecolor='black')
axes[1, 0].set_title('Paso 3: Prior x Likelihood (sin normalizar)')
axes[1, 0].set_xlabel('theta')
axes[1, 0].set_ylabel('Producto')
axes[1, 0].grid(alpha=0.3)

# (d) Posterior normalizado
axes[1, 1].bar(grilla_theta, posterior_grilla, width=0.07, color='#e74c3c', edgecolor='black')
axes[1, 1].set_title('Paso 4: Posterior (normalizado)')
axes[1, 1].set_xlabel('theta')
axes[1, 1].set_ylabel('P(theta|datos)')
axes[1, 1].grid(alpha=0.3)

plt.suptitle('Grid Approximation Paso a Paso (3 beats de 3)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

---

## 5. Distribuciones Predictivas Prior y Posterior

<!-- Distribucion predictiva: probabilidad del proximo resultado -->
<!-- Prior predictive: integra sobre el prior -->
<!-- Posterior predictive: integra sobre el posterior -->

```python
# --- Distribucion predictiva ---
n_sim = 100_000

# Predictiva Prior: muestrear theta del prior, luego muestrear dato
theta_prior_samples = np.random.beta(alfa_prior, beta_prior, size=n_sim)
pred_prior = np.random.binomial(1, theta_prior_samples)

# Predictiva Posterior: muestrear theta del posterior, luego muestrear dato
theta_post_samples = np.random.beta(alfa_post, beta_post, size=n_sim)
pred_posterior = np.random.binomial(1, theta_post_samples)

# Para comparar: prediccion MLE (deterministico)
pred_mle = np.ones(n_sim)  # MLE dice siempre beat

print("=== Distribuciones Predictivas ===\n")
print(f"P(beat proximo | prior):     {pred_prior.mean():.4f}")
print(f"P(beat proximo | posterior): {pred_posterior.mean():.4f}")
print(f"P(beat proximo | MLE):       {pred_mle.mean():.4f}")
print(f"\nEl prior es agnostico (50/50), el posterior es mas informado,")
print(f"y el MLE es absurdamente confiado.")
```

```python
# Grafico comparativo de predicciones
metodos = ['Prior\nPredictive', 'Posterior\nPredictive', 'MLE']
prob_beat = [pred_prior.mean(), pred_posterior.mean(), pred_mle.mean()]
prob_miss = [1 - p for p in prob_beat]

x_pos = np.arange(len(metodos))
ancho = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x_pos - ancho/2, prob_beat, ancho, label='Beat', color='#2ecc71', edgecolor='black')
ax.bar(x_pos + ancho/2, prob_miss, ancho, label='Miss', color='#e74c3c', edgecolor='black')

for i, (pb, pm) in enumerate(zip(prob_beat, prob_miss)):
    ax.text(i - ancho/2, pb + 0.02, f'{pb:.2f}', ha='center', fontweight='bold')
    ax.text(i + ancho/2, pm + 0.02, f'{pm:.2f}', ha='center', fontweight='bold')

ax.set_ylabel('Probabilidad')
ax.set_title('Prediccion del Proximo Trimestre: Tres Metodos')
ax.set_xticks(x_pos)
ax.set_xticklabels(metodos)
ax.legend()
ax.set_ylim(0, 1.15)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## 6. MCMC: Concepto de Metropolis Sampling

<!-- MCMC permite muestrear de distribuciones complicadas -->
<!-- Implementamos Metropolis-Hastings para muestrear de una Student-t con df=6 -->

```python
def metropolis_hastings(target_log_pdf, n_muestras, inicio=0.0, sigma_propuesta=1.0):
    """
    Implementacion basica de Metropolis-Hastings.

    Parametros
    ----------
    target_log_pdf : callable
        Funcion que retorna el log de la densidad objetivo (no necesita estar normalizada).
    n_muestras : int
        Numero de muestras a generar.
    inicio : float
        Valor inicial de la cadena.
    sigma_propuesta : float
        Desviacion estandar de la distribucion propuesta (normal).

    Retorna
    -------
    muestras : np.ndarray
        Cadena de muestras MCMC.
    tasa_aceptacion : float
        Proporcion de propuestas aceptadas.
    """
    muestras = np.zeros(n_muestras)
    muestras[0] = inicio
    aceptadas = 0

    for i in range(1, n_muestras):
        actual = muestras[i - 1]

        # Proponer nuevo valor desde una normal centrada en el actual
        propuesta = actual + np.random.normal(0, sigma_propuesta)

        # Calcular ratio de aceptacion (en escala log)
        log_ratio = target_log_pdf(propuesta) - target_log_pdf(actual)

        # Aceptar o rechazar
        if np.log(np.random.uniform()) < log_ratio:
            muestras[i] = propuesta
            aceptadas += 1
        else:
            muestras[i] = actual

    tasa_aceptacion = aceptadas / (n_muestras - 1)
    return muestras, tasa_aceptacion


# Objetivo: muestrear de una Student-t con df=6
df_objetivo = 6

def log_pdf_student_t(x, df=df_objetivo):
    """Log-densidad de una Student-t (sin constante normalizadora)."""
    return -(df + 1) / 2 * np.log(1 + x**2 / df)


# Ejecutar Metropolis-Hastings
n_muestras_mcmc = 50_000
burn_in = 5_000

cadena, tasa = metropolis_hastings(
    target_log_pdf=log_pdf_student_t,
    n_muestras=n_muestras_mcmc,
    inicio=0.0,
    sigma_propuesta=2.5
)

# Descartar burn-in
muestras_finales = cadena[burn_in:]

print("=== Metropolis-Hastings: Student-t(df=6) ===")
print(f"Muestras totales:   {n_muestras_mcmc:,}")
print(f"Burn-in descartado: {burn_in:,}")
print(f"Muestras utiles:    {len(muestras_finales):,}")
print(f"Tasa de aceptacion: {tasa:.2%}")
print(f"\nEstadisticas de la cadena:")
print(f"  Media:  {muestras_finales.mean():.4f} (teorico: 0.0)")
print(f"  Std:    {muestras_finales.std():.4f} (teorico: {np.sqrt(df_objetivo/(df_objetivo-2)):.4f})")
print(f"  Min:    {muestras_finales.min():.4f}")
print(f"  Max:    {muestras_finales.max():.4f}")
```

```python
# Visualizar la cadena MCMC y comparar con distribucion analitica
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (a) Traceplot completo
axes[0, 0].plot(cadena[:3000], linewidth=0.3, color='#3498db', alpha=0.8)
axes[0, 0].axvline(x=burn_in, color='red', linestyle='--', label=f'Burn-in ({burn_in})')
axes[0, 0].set_title('Traceplot (primeras 3000 muestras)')
axes[0, 0].set_xlabel('Iteracion')
axes[0, 0].set_ylabel('Valor')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# (b) Histograma vs densidad analitica
x_rango = np.linspace(-8, 8, 500)
densidad_analitica = stats.t.pdf(x_rango, df_objetivo)

axes[0, 1].hist(muestras_finales, bins=80, density=True, alpha=0.6,
                color='#3498db', edgecolor='black', linewidth=0.3, label='MCMC')
axes[0, 1].plot(x_rango, densidad_analitica, 'r-', linewidth=2.5, label=f'Student-t(df={df_objetivo})')
axes[0, 1].set_title('Histograma MCMC vs Densidad Analitica')
axes[0, 1].set_xlabel('Valor')
axes[0, 1].set_ylabel('Densidad')
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# (c) Autocorrelacion
lags = 50
autocorr = np.correlate(muestras_finales - muestras_finales.mean(),
                        muestras_finales - muestras_finales.mean(), mode='full')
autocorr = autocorr[len(autocorr)//2:]
autocorr = autocorr[:lags] / autocorr[0]

axes[1, 0].bar(range(lags), autocorr, color='#2ecc71', edgecolor='black', linewidth=0.3)
axes[1, 0].set_title('Autocorrelacion de la Cadena')
axes[1, 0].set_xlabel('Lag')
axes[1, 0].set_ylabel('Autocorrelacion')
axes[1, 0].axhline(y=0, color='black', linewidth=0.5)
axes[1, 0].grid(alpha=0.3)

# (d) Media acumulada (convergencia)
media_acumulada = np.cumsum(muestras_finales) / np.arange(1, len(muestras_finales) + 1)
axes[1, 1].plot(media_acumulada, color='#e74c3c', linewidth=1)
axes[1, 1].axhline(y=0, color='black', linestyle='--', alpha=0.7, label='Media teorica (0)')
axes[1, 1].set_title('Convergencia de la Media')
axes[1, 1].set_xlabel('Muestra')
axes[1, 1].set_ylabel('Media acumulada')
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)

plt.suptitle('Metropolis-Hastings: Muestreo de Student-t(df=6)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

---

## 7. Ejercicio: Comparar MLE vs PML con 1, 3, 10, 50 Observaciones

<!-- EJERCICIO PROPUESTO -->
<!-- Evaluar como MLE y Bayes responden a distintos tamanios de muestra -->

```python
# =============================================================
# EJERCICIO: MLE vs PML con diferentes tamanios de muestra
# =============================================================
#
# ESCENARIO:
# - La tasa real de earnings beats es theta_real = 0.65
# - Observamos n = {1, 3, 10, 50} trimestres
# - Comparar:
#   a) theta_MLE vs media del posterior bayesiano
#   b) Incertidumbre: MLE no tiene IC, Bayes tiene IC del posterior
#   c) Prediccion del proximo beat
#
# TAREAS:
# 1. Para cada n, generar datos con np.random.binomial(1, 0.65, size=n)
# 2. Calcular theta_MLE = media de datos
# 3. Calcular posterior Beta(1 + beats, 1 + misses)
# 4. Calcular IC 95% del posterior
# 5. Calcular distribucion predictiva posterior
# 6. Graficar 4 paneles: uno por cada n
#    - Mostrar prior, posterior y MLE
# 7. Tabla resumen con columnas:
#    n | theta_MLE | media_post | IC_95_low | IC_95_high | pred_beat_MLE | pred_beat_Bayes
#
# PISTAS:
# - stats.beta.ppf([0.025, 0.975], alfa, beta) para IC
# - La predictiva posterior integra sobre la incertidumbre en theta

theta_real = 0.65
tamanos = [1, 3, 10, 50]
prior_a, prior_b = 1, 1

# --- Tu codigo aqui ---
# resultados = []
# for n in tamanos:
#     datos = np.random.binomial(1, theta_real, size=n)
#     beats = datos.sum()
#     misses = n - beats
#     ...
#     resultados.append({...})
#
# df_resultados = pd.DataFrame(resultados)
# print(df_resultados)
#
# Graficar 4 paneles:
# fig, axes = plt.subplots(2, 2, figsize=(14, 10))
# ...

print("Completar el ejercicio arriba ^")
```
