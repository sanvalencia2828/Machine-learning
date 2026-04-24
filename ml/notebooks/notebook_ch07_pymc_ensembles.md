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

# Ensambles Generativos con PyMC y ArviZ

<!-- Capitulo 7 del libro "Probabilistic ML for Finance and Investing" -->
<!-- Modelo de mercado bayesiano completo usando PyMC -->
<!-- Requisitos: numpy, pandas, matplotlib, pymc, arviz -->

```python
# pip install pymc arviz

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# PyMC y ArviZ se importan dentro de cada seccion para claridad
# import pymc as pm
# import arviz as az

np.random.seed(42)
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
```

---

## 1. Modelo de Mercado: Y = alpha + beta*X + epsilon

<!-- Regresion lineal bayesiana aplicada a retornos de mercado -->
<!-- Y = retorno del activo, X = retorno del mercado -->
<!-- Generamos datos sinteticos para portabilidad -->

```python
# --- Generar datos sinteticos de retornos ---
# Simulamos retornos mensuales de un activo vs un indice de mercado
# Parametros "verdaderos" que queremos recuperar
alpha_verdadero = 0.003   # Alpha mensual del 0.3% (exceso de retorno)
beta_verdadero = 1.15     # Beta ligeramente agresivo
sigma_verdadero = 0.025   # Volatilidad residual mensual

n_meses = 60  # 5 anios de datos mensuales

# Retornos del mercado: simulados como normal
retornos_mercado = np.random.normal(loc=0.007, scale=0.045, size=n_meses)

# Retornos del activo: modelo lineal con ruido
ruido = np.random.normal(0, sigma_verdadero, size=n_meses)
retornos_activo = alpha_verdadero + beta_verdadero * retornos_mercado + ruido

# Crear DataFrame
df_retornos = pd.DataFrame({
    'mes': range(1, n_meses + 1),
    'retorno_mercado': retornos_mercado,
    'retorno_activo': retornos_activo
})

print("=== Datos Sinteticos de Retornos ===")
print(f"Periodos: {n_meses} meses")
print(f"Parametros verdaderos: alpha={alpha_verdadero}, beta={beta_verdadero}, sigma={sigma_verdadero}")
print(f"\nEstadisticas descriptivas:")
print(df_retornos[['retorno_mercado', 'retorno_activo']].describe().round(4))
```

```python
# Visualizar la relacion entre retornos
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter plot con regresion OLS para referencia
from numpy.polynomial.polynomial import polyfit
coefs_ols = np.polyfit(retornos_mercado, retornos_activo, 1)
x_linea = np.linspace(retornos_mercado.min(), retornos_mercado.max(), 100)
y_linea = coefs_ols[0] * x_linea + coefs_ols[1]

axes[0].scatter(retornos_mercado, retornos_activo, alpha=0.6, color='#3498db', edgecolor='black', s=40)
axes[0].plot(x_linea, y_linea, 'r--', linewidth=2,
             label=f'OLS: y = {coefs_ols[1]:.4f} + {coefs_ols[0]:.3f}x')
axes[0].set_xlabel('Retorno Mercado')
axes[0].set_ylabel('Retorno Activo')
axes[0].set_title('Retornos: Activo vs Mercado')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Series temporales
axes[1].plot(df_retornos['mes'], df_retornos['retorno_mercado'], 'b-o', markersize=3,
             alpha=0.7, label='Mercado')
axes[1].plot(df_retornos['mes'], df_retornos['retorno_activo'], 'r-s', markersize=3,
             alpha=0.7, label='Activo')
axes[1].axhline(y=0, color='black', linewidth=0.5)
axes[1].set_xlabel('Mes')
axes[1].set_ylabel('Retorno')
axes[1].set_title('Series Temporales de Retornos')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
```

---

## 2. Especificar Priors: alpha~Normal, beta~Normal, residual~HalfStudentT

<!-- Eleccion de priors informativos pero no restrictivos -->
<!-- alpha ~ Normal(0, 0.05): alpha mensual raramente supera 5% -->
<!-- beta ~ Normal(1, 0.5): la mayoria de activos tienen beta cercano a 1 -->
<!-- sigma ~ HalfStudentT(nu=4, sigma=0.05): residual positivo, colas pesadas -->

```python
import pymc as pm
import arviz as az

print("=== Especificacion de Priors ===\n")

# Definir el modelo bayesiano
with pm.Model() as modelo_mercado:

    # --- Priors ---
    # Alpha: intercepto, retorno excedente mensual
    # Normal(0, 0.05) permite alphas entre -10% y +10% mensual (amplio)
    alpha = pm.Normal('alpha', mu=0.0, sigma=0.05)

    # Beta: sensibilidad al mercado
    # Normal(1, 0.5) centrado en 1 (mercado neutral) con flexibilidad
    beta = pm.Normal('beta', mu=1.0, sigma=0.5)

    # Sigma: volatilidad residual
    # HalfStudentT con colas pesadas para permitir volatilidad alta
    sigma = pm.HalfStudentT('sigma', nu=4, sigma=0.05)

    # --- Modelo lineal ---
    mu = alpha + beta * retornos_mercado

    # --- Likelihood ---
    # Retornos observados siguen una normal con media mu y desviacion sigma
    retorno_obs = pm.Normal('retorno_obs', mu=mu, sigma=sigma,
                            observed=retornos_activo)

print("Modelo especificado correctamente.")
print(f"\nVariables del modelo:")
for var in modelo_mercado.free_RVs:
    print(f"  - {var.name}")
print(f"\nDatos observados: {modelo_mercado.observed_RVs[0].name} ({n_meses} puntos)")
```

```python
# Visualizar los priors elegidos
from scipy import stats as sp_stats

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Prior de alpha
x_alpha = np.linspace(-0.15, 0.15, 300)
axes[0].plot(x_alpha, sp_stats.norm.pdf(x_alpha, 0, 0.05), 'b-', linewidth=2)
axes[0].fill_between(x_alpha, sp_stats.norm.pdf(x_alpha, 0, 0.05), alpha=0.2, color='blue')
axes[0].axvline(x=alpha_verdadero, color='red', linestyle='--', label=f'Verdadero ({alpha_verdadero})')
axes[0].set_title('Prior: alpha ~ Normal(0, 0.05)')
axes[0].set_xlabel('alpha')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Prior de beta
x_beta = np.linspace(-0.5, 2.5, 300)
axes[1].plot(x_beta, sp_stats.norm.pdf(x_beta, 1.0, 0.5), 'b-', linewidth=2)
axes[1].fill_between(x_beta, sp_stats.norm.pdf(x_beta, 1.0, 0.5), alpha=0.2, color='blue')
axes[1].axvline(x=beta_verdadero, color='red', linestyle='--', label=f'Verdadero ({beta_verdadero})')
axes[1].set_title('Prior: beta ~ Normal(1.0, 0.5)')
axes[1].set_xlabel('beta')
axes[1].legend()
axes[1].grid(alpha=0.3)

# Prior de sigma (HalfStudentT)
x_sigma = np.linspace(0.001, 0.15, 300)
# Aproximar HalfStudentT: tomar abs de StudentT
pdf_sigma = 2 * sp_stats.t.pdf(x_sigma, df=4, loc=0, scale=0.05)
axes[2].plot(x_sigma, pdf_sigma, 'b-', linewidth=2)
axes[2].fill_between(x_sigma, pdf_sigma, alpha=0.2, color='blue')
axes[2].axvline(x=sigma_verdadero, color='red', linestyle='--', label=f'Verdadero ({sigma_verdadero})')
axes[2].set_title('Prior: sigma ~ HalfStudentT(nu=4, sigma=0.05)')
axes[2].set_xlabel('sigma')
axes[2].legend()
axes[2].grid(alpha=0.3)

plt.suptitle('Distribuciones Prior del Modelo de Mercado', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()
```

---

## 3. Prior Predictive Check con Datos Sinteticos

<!-- Simular datos del modelo ANTES de entrenar -->
<!-- Verificar que los priors generan datos razonables -->

```python
# --- Prior predictive check ---
with modelo_mercado:
    prior_predictive = pm.sample_prior_predictive(samples=1000, random_seed=42)

# Extraer simulaciones del prior
retornos_simulados_prior = prior_predictive.prior_predictive['retorno_obs'].values

print("=== Prior Predictive Check ===")
print(f"Forma de simulaciones: {retornos_simulados_prior.shape}")
print(f"  (cadenas x muestras x observaciones)")

# Aplanar para analisis
retornos_planos = retornos_simulados_prior.reshape(-1, n_meses)
print(f"\nEstadisticas de retornos simulados del prior:")
print(f"  Media de medias:  {np.mean([r.mean() for r in retornos_planos]):.4f}")
print(f"  Media de stds:    {np.mean([r.std() for r in retornos_planos]):.4f}")
print(f"  Rango tipico:     [{np.percentile(retornos_planos, 2.5):.4f}, "
      f"{np.percentile(retornos_planos, 97.5):.4f}]")
```

```python
# Graficar prior predictive vs datos reales
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribucion de retornos simulados vs observados
muestras_aleatorias = retornos_planos[np.random.choice(len(retornos_planos), 200, replace=False)]
for muestra in muestras_aleatorias:
    axes[0].hist(muestra, bins=20, density=True, alpha=0.02, color='blue', histtype='step')
axes[0].hist(retornos_activo, bins=20, density=True, alpha=0.8, color='red',
             edgecolor='black', label='Datos reales')
axes[0].set_title('Prior Predictive: Distribuciones Simuladas vs Reales')
axes[0].set_xlabel('Retorno')
axes[0].set_ylabel('Densidad')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Scatter de media vs std de cada simulacion
medias_sim = [r.mean() for r in retornos_planos]
stds_sim = [r.std() for r in retornos_planos]
axes[1].scatter(medias_sim, stds_sim, alpha=0.1, s=10, color='blue', label='Simulaciones prior')
axes[1].scatter(retornos_activo.mean(), retornos_activo.std(),
                color='red', s=200, marker='*', zorder=5, edgecolor='black',
                label='Datos reales')
axes[1].set_xlabel('Media del retorno')
axes[1].set_ylabel('Std del retorno')
axes[1].set_title('Prior Predictive: Media vs Volatilidad')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
```

---

## 4. Entrenamiento: pm.sample() con HMC/NUTS

<!-- NUTS (No-U-Turn Sampler) es la variante mas eficiente de HMC -->
<!-- Muestreamos del posterior de los parametros -->

```python
# --- Entrenar el modelo con NUTS ---
with modelo_mercado:
    # NUTS es el sampler por defecto para variables continuas
    traza = pm.sample(
        draws=2000,        # Muestras por cadena
        tune=1000,         # Muestras de tuning (descartadas)
        chains=4,          # 4 cadenas paralelas
        target_accept=0.9, # Tasa de aceptacion objetivo
        random_seed=42,
        return_inferencedata=True
    )

print("=== Entrenamiento Completado ===")
print(f"Cadenas: {traza.posterior.dims['chain']}")
print(f"Muestras por cadena: {traza.posterior.dims['draw']}")
print(f"Total muestras posterior: {traza.posterior.dims['chain'] * traza.posterior.dims['draw']}")
```

```python
# Resumen de los parametros estimados
resumen = az.summary(traza, var_names=['alpha', 'beta', 'sigma'],
                     hdi_prob=0.95, round_to=5)
print("=== Resumen del Posterior ===\n")
print(resumen)

print(f"\n--- Comparacion con Valores Verdaderos ---")
print(f"{'Parametro':<10} {'Verdadero':>10} {'Media Post':>12} {'HDI 95%':>20}")
print("-" * 55)
for param, verdadero in [('alpha', alpha_verdadero), ('beta', beta_verdadero), ('sigma', sigma_verdadero)]:
    media = resumen.loc[param, 'mean']
    hdi_low = resumen.loc[param, 'hdi_2.5%']
    hdi_high = resumen.loc[param, 'hdi_97.5%']
    contiene = "SI" if hdi_low <= verdadero <= hdi_high else "NO"
    print(f"{param:<10} {verdadero:>10.4f} {media:>12.5f} [{hdi_low:.5f}, {hdi_high:.5f}] {contiene}")
```

---

## 5. Posterior Analysis: Trazas, Densidades e Intervalos Credibles

<!-- ArviZ ofrece herramientas de diagnostico y visualizacion -->

```python
# --- Diagnosticos de la cadena ---

# Traceplot: verificar convergencia y mixing
az.plot_trace(traza, var_names=['alpha', 'beta', 'sigma'],
              figsize=(14, 8), compact=True)
plt.suptitle('Traceplots: Convergencia de las Cadenas MCMC', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

```python
# Distribuciones posteriores con intervalos credibles
az.plot_posterior(traza, var_names=['alpha', 'beta', 'sigma'],
                 hdi_prob=0.95, figsize=(14, 4),
                 ref_val=[alpha_verdadero, beta_verdadero, sigma_verdadero])
plt.suptitle('Distribuciones Posteriores con HDI 95%', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

```python
# Grafico forest para comparar entre cadenas
az.plot_forest(traza, var_names=['alpha', 'beta', 'sigma'],
               hdi_prob=0.95, combined=False, figsize=(10, 5))
plt.title('Forest Plot: Estimaciones por Cadena')
plt.tight_layout()
plt.show()
```

```python
# Correlaciones entre parametros
az.plot_pair(traza, var_names=['alpha', 'beta', 'sigma'],
             kind='kde', figsize=(10, 10),
             marginals=True)
plt.suptitle('Distribuciones Conjuntas de los Parametros', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
```

---

## 6. Posterior Predictive Check y Retrodictions

<!-- Generar datos simulados desde el posterior para comparar con los reales -->
<!-- "Retrodictions": predicciones sobre los datos de entrenamiento -->

```python
# --- Posterior predictive check ---
with modelo_mercado:
    posterior_predictive = pm.sample_posterior_predictive(traza, random_seed=42)

retornos_post_pred = posterior_predictive.posterior_predictive['retorno_obs'].values
# Forma: (cadenas, muestras, n_obs)

print("=== Posterior Predictive Check ===")
print(f"Forma de predicciones: {retornos_post_pred.shape}")
```

```python
# Comparar distribuciones: predicciones del posterior vs datos reales
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histograma agregado
retornos_post_planos = retornos_post_pred.reshape(-1, n_meses)
muestras_idx = np.random.choice(len(retornos_post_planos), 300, replace=False)
for idx in muestras_idx:
    axes[0].hist(retornos_post_planos[idx], bins=20, density=True,
                 alpha=0.01, color='blue', histtype='step')
axes[0].hist(retornos_activo, bins=20, density=True, alpha=0.8,
             color='red', edgecolor='black', label='Datos reales')
axes[0].set_title('Posterior Predictive vs Datos Reales')
axes[0].set_xlabel('Retorno')
axes[0].set_ylabel('Densidad')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Retrodictions: mediana y bandas para cada observacion
mediana_pred = np.median(retornos_post_planos, axis=0)
p05 = np.percentile(retornos_post_planos, 5, axis=0)
p95 = np.percentile(retornos_post_planos, 95, axis=0)

meses = range(1, n_meses + 1)
axes[1].fill_between(meses, p05, p95, alpha=0.3, color='blue', label='IC 90%')
axes[1].plot(meses, mediana_pred, 'b-', linewidth=1.5, label='Mediana posterior')
axes[1].plot(meses, retornos_activo, 'ro', markersize=4, label='Datos reales')
axes[1].set_xlabel('Mes')
axes[1].set_ylabel('Retorno')
axes[1].set_title('Retrodictions: Predicciones sobre Datos de Entrenamiento')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
```

```python
# Metricas cuantitativas del posterior predictive check
# Que proporcion de datos reales cae dentro del IC 90%?
dentro_ic = np.sum((retornos_activo >= p05) & (retornos_activo <= p95))
cobertura = dentro_ic / n_meses

# Bayesian p-value: proporcion de simulaciones con estadistico >= observado
media_real = retornos_activo.mean()
medias_simuladas = retornos_post_planos.mean(axis=1)
p_value_bayesiano = np.mean(medias_simuladas >= media_real)

print("=== Metricas de Calibracion ===")
print(f"Cobertura del IC 90%: {cobertura:.1%} ({dentro_ic}/{n_meses} observaciones)")
print(f"  (esperado: ~90%)")
print(f"Bayesian p-value (media): {p_value_bayesiano:.3f}")
print(f"  (valores cercanos a 0.5 indican buen ajuste)")
```

---

## 7. Test con Datos Out-of-Sample

<!-- Evaluar el modelo en datos que no uso para entrenar -->

```python
# --- Generar datos out-of-sample ---
n_oos = 12  # 12 meses adicionales

retornos_mercado_oos = np.random.normal(loc=0.007, scale=0.045, size=n_oos)
ruido_oos = np.random.normal(0, sigma_verdadero, size=n_oos)
retornos_activo_oos = alpha_verdadero + beta_verdadero * retornos_mercado_oos + ruido_oos

# Extraer muestras del posterior para hacer predicciones
alpha_muestras = traza.posterior['alpha'].values.flatten()
beta_muestras = traza.posterior['beta'].values.flatten()
sigma_muestras = traza.posterior['sigma'].values.flatten()

n_posterior = len(alpha_muestras)

# Para cada punto OOS, generar distribucion predictiva
predicciones_oos = np.zeros((n_posterior, n_oos))
for i in range(n_oos):
    mu_i = alpha_muestras + beta_muestras * retornos_mercado_oos[i]
    predicciones_oos[:, i] = np.random.normal(mu_i, sigma_muestras)

mediana_oos = np.median(predicciones_oos, axis=0)
p05_oos = np.percentile(predicciones_oos, 5, axis=0)
p95_oos = np.percentile(predicciones_oos, 95, axis=0)
p25_oos = np.percentile(predicciones_oos, 25, axis=0)
p75_oos = np.percentile(predicciones_oos, 75, axis=0)

# Cobertura OOS
dentro_ic_oos = np.sum((retornos_activo_oos >= p05_oos) & (retornos_activo_oos <= p95_oos))
cobertura_oos = dentro_ic_oos / n_oos

print("=== Evaluacion Out-of-Sample ===")
print(f"Meses OOS: {n_oos}")
print(f"Cobertura IC 90%: {cobertura_oos:.1%} ({dentro_ic_oos}/{n_oos})")
print(f"MAE mediana: {np.mean(np.abs(retornos_activo_oos - mediana_oos)):.5f}")
print(f"RMSE mediana: {np.sqrt(np.mean((retornos_activo_oos - mediana_oos)**2)):.5f}")
```

```python
# Graficar predicciones OOS
fig, ax = plt.subplots(figsize=(12, 6))

meses_oos = range(1, n_oos + 1)
ax.fill_between(meses_oos, p05_oos, p95_oos, alpha=0.2, color='blue', label='IC 90%')
ax.fill_between(meses_oos, p25_oos, p75_oos, alpha=0.3, color='blue', label='IC 50%')
ax.plot(meses_oos, mediana_oos, 'b-o', linewidth=2, markersize=5, label='Mediana predictiva')
ax.plot(meses_oos, retornos_activo_oos, 'rs', markersize=8, label='Datos reales (OOS)')
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_xlabel('Mes (Out-of-Sample)')
ax.set_ylabel('Retorno')
ax.set_title(f'Prediccion Out-of-Sample (Cobertura 90%: {cobertura_oos:.0%})')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## 8. Ejercicio: Agregar Segundo Feature (Volumen) al Modelo

<!-- EJERCICIO PROPUESTO -->
<!-- Extender el modelo de mercado con un segundo predictor -->

```python
# =============================================================
# EJERCICIO: Modelo de mercado con dos features
# =============================================================
#
# ESCENARIO:
# Extender el modelo Y = alpha + beta*X + epsilon a:
# Y = alpha + beta_mercado * X_mercado + beta_volumen * X_volumen + epsilon
#
# DATOS SINTETICOS:
# - X_mercado: retornos del indice (ya generados arriba)
# - X_volumen: cambio porcentual en volumen de trading (generar con np.random.normal)
# - Parametros verdaderos: beta_volumen = -0.02 (mas volumen -> menos retorno)
#
# TAREAS:
# 1. Generar X_volumen sintetico (60 meses, media=0.05, std=0.15)
# 2. Generar Y = alpha + beta_mercado*X_mercado + beta_volumen*X_volumen + epsilon
# 3. Especificar modelo PyMC con priors para los 4 parametros
# 4. Hacer prior predictive check
# 5. Entrenar con pm.sample()
# 6. Comparar posteriors de beta_mercado y beta_volumen
# 7. Posterior predictive check
# 8. Comparar metricas con el modelo de 1 feature
#
# PISTAS:
# - beta_volumen ~ Normal(0, 0.1) como prior
# - Usar az.compare() para comparar modelos si se desea
# - El volumen puede tener efecto pequeno; verificar si el IC incluye 0

# --- Tu codigo aqui ---
# beta_volumen_verdadero = -0.02
# volumen_cambio = np.random.normal(0.05, 0.15, size=n_meses)
# ...
#
# with pm.Model() as modelo_2features:
#     alpha = pm.Normal('alpha', mu=0, sigma=0.05)
#     beta_m = pm.Normal('beta_mercado', mu=1, sigma=0.5)
#     beta_v = pm.Normal('beta_volumen', mu=0, sigma=0.1)
#     sigma = pm.HalfStudentT('sigma', nu=4, sigma=0.05)
#     ...

print("Completar el ejercicio arriba ^")
```
