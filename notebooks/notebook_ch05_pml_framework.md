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

# Marco de ML Probabilistico: Inferencia y Prediccion

<!-- Capitulos 5 del libro "Probabilistic ML for Finance and Investing" -->
<!-- Autor del notebook: generado como plantilla de estudio -->
<!-- Requisitos: numpy, pandas, matplotlib -->

```python
# Importaciones principales
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Semilla para reproducibilidad
np.random.seed(42)

# Configuracion de graficos
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
```

---

## 1. Regla de Probabilidad Inversa

<!-- Explicacion del teorema de Bayes como motor del ML probabilistico -->
<!-- P(theta|datos) = P(datos|theta) * P(theta) / P(datos) -->

```python
# --- Componentes del teorema de Bayes ---
# prior:      P(theta)       -> creencia inicial sobre el parametro
# likelihood: P(datos|theta) -> que tan probable es observar los datos dado theta
# marginal:   P(datos)       -> probabilidad total de los datos (constante normalizadora)
# posterior:  P(theta|datos) -> creencia actualizada despues de ver los datos

def calcular_posterior(prior: float, likelihood: float, marginal: float) -> float:
    """
    Calcula la probabilidad posterior usando el teorema de Bayes.

    Parametros
    ----------
    prior : float
        Probabilidad a priori del evento.
    likelihood : float
        Probabilidad de observar la evidencia dado que el evento es verdadero.
    marginal : float
        Probabilidad total de la evidencia bajo todos los escenarios.

    Retorna
    -------
    float
        Probabilidad posterior actualizada.
    """
    posterior = (likelihood * prior) / marginal
    return posterior


# Ejemplo didactico simple: prueba diagnostica
# Un test detecta una condicion con 95% de sensibilidad
# La condicion afecta al 1% de la poblacion
# El test tiene 5% de falsos positivos
prior_condicion = 0.01
sensibilidad = 0.95
tasa_falso_positivo = 0.05

# Probabilidad marginal de un resultado positivo
marginal_positivo = (sensibilidad * prior_condicion) + (tasa_falso_positivo * (1 - prior_condicion))

posterior_condicion = calcular_posterior(prior_condicion, sensibilidad, marginal_positivo)

print("=== Regla de Probabilidad Inversa ===")
print(f"Prior P(condicion)            = {prior_condicion:.4f}")
print(f"Likelihood P(+|condicion)     = {sensibilidad:.4f}")
print(f"P(+|no condicion)             = {tasa_falso_positivo:.4f}")
print(f"Marginal P(+)                 = {marginal_positivo:.4f}")
print(f"Posterior P(condicion|+)      = {posterior_condicion:.4f}")
print(f"\nAun con test positivo, la probabilidad real es solo {posterior_condicion:.1%}")
```

```python
# Visualizacion de las componentes de Bayes
etiquetas = ['Prior', 'Likelihood', 'Marginal', 'Posterior']
valores = [prior_condicion, sensibilidad, marginal_positivo, posterior_condicion]
colores = ['#3498db', '#e74c3c', '#95a5a6', '#2ecc71']

fig, ax = plt.subplots(figsize=(8, 5))
barras = ax.bar(etiquetas, valores, color=colores, edgecolor='black', linewidth=0.8)

# Anotar valores sobre cada barra
for barra, val in zip(barras, valores):
    ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 0.01,
            f'{val:.4f}', ha='center', va='bottom', fontweight='bold')

ax.set_ylabel('Probabilidad')
ax.set_title('Componentes del Teorema de Bayes')
ax.set_ylim(0, 1.1)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## 2. Probabilidad de Default de Deuda: Bonos High-Yield

<!-- Escenario: analista evalua bonos high-yield -->
<!-- Prior: 10% probabilidad de default -->
<!-- Likelihood de senal negativa dado default: 70% -->
<!-- Likelihood de senal negativa dado NO default: 40% -->

```python
# --- Parametros del escenario de bonos ---
prior_default = 0.10          # Creencia inicial: 10% de probabilidad de default
prob_senal_dado_default = 0.70     # Si hay default, 70% de chance de ver senal negativa
prob_senal_dado_no_default = 0.40  # Si NO hay default, 40% de chance de senal negativa

# Calcular marginal: probabilidad total de observar la senal negativa
marginal_senal = (prob_senal_dado_default * prior_default) + \
                 (prob_senal_dado_no_default * (1 - prior_default))

# Posterior: P(default | senal negativa)
posterior_default = calcular_posterior(prior_default, prob_senal_dado_default, marginal_senal)

# Tambien calcular: P(no default | senal negativa)
posterior_no_default = 1 - posterior_default

print("=== Default de Bonos High-Yield ===")
print(f"Prior P(default)                    = {prior_default:.2f}")
print(f"P(senal negativa | default)         = {prob_senal_dado_default:.2f}")
print(f"P(senal negativa | no default)      = {prob_senal_dado_no_default:.2f}")
print(f"Marginal P(senal negativa)          = {marginal_senal:.4f}")
print(f"Posterior P(default | senal neg.)    = {posterior_default:.4f}")
print(f"Posterior P(no default | senal neg.) = {posterior_no_default:.4f}")
```

```python
# Comparacion visual: prior vs posterior del default
categorias = ['Default', 'No Default']
priors = [prior_default, 1 - prior_default]
posteriors = [posterior_default, posterior_no_default]

x_pos = np.arange(len(categorias))
ancho = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(x_pos - ancho/2, priors, ancho, label='Prior', color='#3498db', edgecolor='black')
ax.bar(x_pos + ancho/2, posteriors, ancho, label='Posterior (tras senal negativa)',
       color='#e74c3c', edgecolor='black')

ax.set_ylabel('Probabilidad')
ax.set_title('Bonos High-Yield: Prior vs Posterior de Default')
ax.set_xticks(x_pos)
ax.set_xticklabels(categorias)
ax.legend()
ax.set_ylim(0, 1.05)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## 3. Actualizacion Iterativa de Probabilidades con Nuevos Datos

<!-- El posterior de una iteracion se convierte en el prior de la siguiente -->
<!-- Esto demuestra el aprendizaje secuencial bayesiano -->

```python
def actualizacion_secuencial(prior_inicial, observaciones, likelihood_positiva, likelihood_negativa):
    """
    Actualiza la probabilidad de forma secuencial con cada nueva observacion.

    Parametros
    ----------
    prior_inicial : float
        Creencia inicial antes de cualquier observacion.
    observaciones : list of int
        Secuencia de observaciones (1 = senal negativa, 0 = senal positiva).
    likelihood_positiva : float
        P(senal | hipotesis verdadera).
    likelihood_negativa : float
        P(senal | hipotesis falsa).

    Retorna
    -------
    list of float
        Lista de posteriors acumulados incluyendo el prior inicial.
    """
    historial = [prior_inicial]
    prior_actual = prior_inicial

    for obs in observaciones:
        if obs == 1:  # Senal negativa observada
            lik_h1 = likelihood_positiva
            lik_h0 = likelihood_negativa
        else:  # Senal positiva (sin alarma)
            lik_h1 = 1 - likelihood_positiva
            lik_h0 = 1 - likelihood_negativa

        # Marginal para esta observacion
        marginal = (lik_h1 * prior_actual) + (lik_h0 * (1 - prior_actual))

        # Nuevo posterior
        posterior = (lik_h1 * prior_actual) / marginal

        historial.append(posterior)
        prior_actual = posterior  # El posterior se vuelve el nuevo prior

    return historial


# Simular 12 meses de senales para el bono
# 1 = senal negativa (alarma), 0 = senal positiva (sin problema)
np.random.seed(7)
senales_mensuales = np.random.choice([0, 1], size=12, p=[0.55, 0.45])

historial_default = actualizacion_secuencial(
    prior_inicial=prior_default,
    observaciones=senales_mensuales,
    likelihood_positiva=prob_senal_dado_default,
    likelihood_negativa=prob_senal_dado_no_default
)

print("=== Actualizacion Secuencial ===")
print(f"Senales observadas: {senales_mensuales.tolist()}")
print(f"  (1=senal negativa, 0=senal positiva)\n")
for i, p in enumerate(historial_default):
    marcador = " <-- prior inicial" if i == 0 else f" tras senal={'NEG' if senales_mensuales[i-1]==1 else 'POS'}"
    print(f"  Paso {i:2d}: P(default) = {p:.4f}{marcador}")
```

```python
# Graficar la evolucion de la probabilidad de default
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

# Panel superior: evolucion del posterior
pasos = range(len(historial_default))
ax1.plot(pasos, historial_default, 'o-', color='#e74c3c', linewidth=2, markersize=6)
ax1.axhline(y=prior_default, color='#3498db', linestyle='--', alpha=0.7, label=f'Prior inicial ({prior_default})')
ax1.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, label='Umbral 50%')
ax1.set_ylabel('P(Default)')
ax1.set_title('Actualizacion Secuencial de Probabilidad de Default')
ax1.legend(loc='upper left')
ax1.grid(alpha=0.3)
ax1.set_xlim(-0.5, len(historial_default) - 0.5)

# Panel inferior: senales observadas
colores_senal = ['#2ecc71' if s == 0 else '#e74c3c' for s in senales_mensuales]
ax2.bar(range(1, len(senales_mensuales) + 1), senales_mensuales, color=colores_senal, edgecolor='black')
ax2.set_xlabel('Observacion (mes)')
ax2.set_ylabel('Senal')
ax2.set_yticks([0, 1])
ax2.set_yticklabels(['Positiva', 'Negativa'])
ax2.set_xlim(0.5, len(senales_mensuales) + 0.5)

plt.tight_layout()
plt.show()
```

---

## 4. Distribucion Predictiva Prior: Simulacion Antes de Entrenar

<!-- Antes de ver datos, simulamos predicciones usando solo el prior -->
<!-- Esto nos dice que rango de resultados esperamos a priori -->

```python
# --- Distribucion predictiva prior ---
# Escenario: modelar retornos de un bono con prior sobre tasa de default
# Si default ocurre: perdida del 60% del principal
# Si no: ganancia del cupon (8% anual)

n_simulaciones = 50_000
cupon_anual = 0.08
perdida_default = -0.60

# Muestrear tasas de default del prior (Beta difusa centrada en 10%)
# Usamos Beta(2, 18) que tiene media ~0.10 y varianza razonable
alfa_prior, beta_prior = 2, 18
tasas_default_prior = np.random.beta(alfa_prior, beta_prior, size=n_simulaciones)

# Para cada tasa simulada, generar un resultado binario
ocurre_default = np.random.binomial(1, tasas_default_prior)

# Retorno segun si hubo default o no
retornos_prior = np.where(ocurre_default == 1, perdida_default, cupon_anual)

print("=== Distribucion Predictiva Prior ===")
print(f"Simulaciones: {n_simulaciones:,}")
print(f"Prior sobre tasa de default: Beta({alfa_prior}, {beta_prior})")
print(f"  Media prior: {alfa_prior/(alfa_prior+beta_prior):.2f}")
print(f"Retorno esperado prior: {retornos_prior.mean():.4f}")
print(f"Prob. de default en simulacion: {ocurre_default.mean():.4f}")
print(f"Percentil 5 de retorno: {np.percentile(retornos_prior, 5):.4f}")
print(f"Percentil 95 de retorno: {np.percentile(retornos_prior, 95):.4f}")
```

```python
# Visualizar la distribucion predictiva prior
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Izquierda: distribucion prior de la tasa de default
axes[0].hist(tasas_default_prior, bins=60, density=True, color='#3498db', alpha=0.7, edgecolor='black')
axes[0].set_xlabel('Tasa de Default')
axes[0].set_ylabel('Densidad')
axes[0].set_title(f'Prior: Beta({alfa_prior}, {beta_prior})')
axes[0].axvline(x=tasas_default_prior.mean(), color='red', linestyle='--',
                label=f'Media = {tasas_default_prior.mean():.3f}')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Derecha: distribucion predictiva de retornos (prior)
conteo_default = (retornos_prior == perdida_default).sum()
conteo_cupon = (retornos_prior == cupon_anual).sum()
axes[1].bar(['Default\n(perdida 60%)', 'No Default\n(cupon 8%)'],
            [conteo_default / n_simulaciones, conteo_cupon / n_simulaciones],
            color=['#e74c3c', '#2ecc71'], edgecolor='black')
axes[1].set_ylabel('Proporcion')
axes[1].set_title('Distribucion Predictiva Prior de Retornos')
axes[1].set_ylim(0, 1.05)
axes[1].grid(axis='y', alpha=0.3)

plt.suptitle('Simulacion ANTES de Entrenar (Solo Prior)', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
```

---

## 5. Distribucion Predictiva Posterior: Simulacion Despues de Entrenar

<!-- Despues de observar datos, actualizamos el prior y simulamos de nuevo -->
<!-- Comparamos como cambia la incertidumbre predictiva -->

```python
# --- Simular datos observados ---
# Supongamos que observamos 20 bonos similares: 3 hicieron default
n_observados = 20
defaults_observados = 3

# Actualizar el prior Beta(2,18) con los datos observados
# Posterior: Beta(alfa + defaults, beta + no_defaults)
alfa_posterior = alfa_prior + defaults_observados
beta_posterior = beta_prior + (n_observados - defaults_observados)

print(f"=== Actualizacion del Prior con Datos ===")
print(f"Datos observados: {defaults_observados} defaults en {n_observados} bonos")
print(f"Prior:     Beta({alfa_prior}, {beta_prior})  -> media = {alfa_prior/(alfa_prior+beta_prior):.4f}")
print(f"Posterior: Beta({alfa_posterior}, {beta_posterior}) -> media = {alfa_posterior/(alfa_posterior+beta_posterior):.4f}")

# Muestrear del posterior
tasas_default_posterior = np.random.beta(alfa_posterior, beta_posterior, size=n_simulaciones)

# Generar predicciones del posterior
ocurre_default_post = np.random.binomial(1, tasas_default_posterior)
retornos_posterior = np.where(ocurre_default_post == 1, perdida_default, cupon_anual)

print(f"\n=== Distribucion Predictiva Posterior ===")
print(f"Retorno esperado posterior: {retornos_posterior.mean():.4f}")
print(f"Prob. de default posterior: {ocurre_default_post.mean():.4f}")
print(f"Percentil 5: {np.percentile(retornos_posterior, 5):.4f}")
print(f"Percentil 95: {np.percentile(retornos_posterior, 95):.4f}")
```

```python
# Comparar prior vs posterior
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribucion de tasas de default: prior vs posterior
from scipy.stats import beta as beta_dist  # Solo para densidad continua
x_vals = np.linspace(0, 0.5, 300)
axes[0].plot(x_vals, beta_dist.pdf(x_vals, alfa_prior, beta_prior),
             'b-', linewidth=2, label=f'Prior Beta({alfa_prior},{beta_prior})')
axes[0].plot(x_vals, beta_dist.pdf(x_vals, alfa_posterior, beta_posterior),
             'r-', linewidth=2, label=f'Posterior Beta({alfa_posterior},{beta_posterior})')
axes[0].set_xlabel('Tasa de Default')
axes[0].set_ylabel('Densidad')
axes[0].set_title('Prior vs Posterior sobre Tasa de Default')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Comparar predicciones
categorias = ['Default\n(perdida 60%)', 'No Default\n(cupon 8%)']
prior_probs = [ocurre_default.mean(), 1 - ocurre_default.mean()]
post_probs = [ocurre_default_post.mean(), 1 - ocurre_default_post.mean()]

x_pos = np.arange(len(categorias))
ancho = 0.3
axes[1].bar(x_pos - ancho/2, prior_probs, ancho, label='Predictiva Prior', color='#3498db', edgecolor='black')
axes[1].bar(x_pos + ancho/2, post_probs, ancho, label='Predictiva Posterior', color='#e74c3c', edgecolor='black')
axes[1].set_ylabel('Proporcion')
axes[1].set_title('Distribucion Predictiva: Prior vs Posterior')
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(categorias)
axes[1].legend()
axes[1].set_ylim(0, 1.05)
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()
```

---

## 6. Ejercicio: Aplicar PML a Deteccion de Fraude en Tarjetas de Credito

<!-- EJERCICIO PROPUESTO -->
<!-- Contexto: un banco quiere detectar fraude usando inferencia bayesiana -->
<!-- El estudiante debe implementar la solucion completa -->

```python
# =============================================================
# EJERCICIO: Deteccion de fraude con ML probabilistico
# =============================================================
#
# ESCENARIO:
# - La tasa base de fraude es 0.5% (prior)
# - El sistema de deteccion tiene sensibilidad del 98%
#   (P(alerta | fraude) = 0.98)
# - La tasa de falso positivo es del 3%
#   (P(alerta | no fraude) = 0.03)
#
# TAREAS:
# 1. Calcular P(fraude | alerta) usando Bayes
# 2. Simular 100 transacciones con tasas de fraude
#    muestreadas de un prior Beta(1, 199)
# 3. Suponer que de 500 transacciones reales, 4 fueron fraude.
#    Actualizar el prior y recalcular.
# 4. Graficar: prior vs posterior de la tasa de fraude
# 5. Calcular la distribucion predictiva posterior para
#    las proximas 100 transacciones
#
# PISTAS:
# - Usar actualizacion_secuencial() de la seccion 3
# - Beta(a, b) se actualiza a Beta(a + exitos, b + fracasos)
# - np.random.beta() para muestrear del posterior

# --- Tu codigo aqui ---
prior_fraude = 0.005
sensibilidad_fraude = 0.98
falso_positivo_fraude = 0.03

# Paso 1: Bayes puntual
# marginal_alerta = ...
# posterior_fraude = ...

# Paso 2: Simulacion con prior Beta(1, 199)
# ...

# Paso 3: Actualizar con datos reales
# ...

# Paso 4: Graficar
# ...

# Paso 5: Prediccion posterior
# ...

print("Completar el ejercicio arriba ^")
```
