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

# Peligros de NHST, p-values e Intervalos de Confianza

## Proposito

Demostrar por que la inferencia estadistica clasica (NHST) puede conducir a
conclusiones erroneas en finanzas. Se analizan la falacia del fiscal, el
descuido de la tasa base, los errores en intervalos de confianza y la
no-normalidad de residuos en modelos de mercado.

## Requisitos

```python
# Importar librerias necesarias
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.api as sm

# Semilla para reproducibilidad
np.random.seed(42)
```

---

## 1. Falacia inversa: ejemplo del fiscal con tipos sanguineos

Un fiscal argumenta: "Solo el 10% de la poblacion tiene sangre tipo B. La sangre
en la escena es tipo B. El acusado tiene tipo B. Por lo tanto, hay un 90%
de probabilidad de que sea culpable."

Esto confunde P(evidencia | inocente) con P(inocente | evidencia).

```python
# Parametros del escenario
poblacion_ciudad = 500_000
proporcion_tipo_b = 0.10
personas_tipo_b = int(poblacion_ciudad * proporcion_tipo_b)

# Probabilidad real de culpabilidad (suponiendo que cualquier persona tipo B
# pudo haber estado en la escena)
p_culpable_dado_tipo_b = 1 / personas_tipo_b

print("=== Falacia del fiscal: tipos sanguineos ===")
print(f"Poblacion de la ciudad:     {poblacion_ciudad:,}")
print(f"Proporcion tipo B:          {proporcion_tipo_b:.0%}")
print(f"Personas con tipo B:        {personas_tipo_b:,}")
print(f"P(tipo B | inocente):       {proporcion_tipo_b:.2f}")
print(f"P(culpable | tipo B):       {p_culpable_dado_tipo_b:.8f}")
print(f"\nEl fiscal dice 90% de culpabilidad.")
print(f"La probabilidad real es:    {p_culpable_dado_tipo_b:.8f} = 1/{personas_tipo_b:,}")
```

**Salida esperada**: La probabilidad real es infima (~0.00002%), no 90%.

```python
# Visualizacion: comparar lo que dice el fiscal vs la realidad
fig, ax = plt.subplots(figsize=(8, 5))

categorias = ['Argumento del fiscal\n(falacia inversa)', 'Probabilidad real\n(Bayes)']
valores = [0.90, p_culpable_dado_tipo_b]
colores = ['#e74c3c', '#2ecc71']

barras = ax.bar(categorias, valores, color=colores, width=0.5, edgecolor='black')

# Anotar valores sobre las barras
for barra, val in zip(barras, valores):
    ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.02,
            f'{val:.6f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Probabilidad de culpabilidad')
ax.set_title('Falacia del fiscal: confusion de probabilidades condicionales')
ax.set_ylim(0, 1.1)
plt.tight_layout()
plt.savefig('../data/fig_ch04_falacia_fiscal.png', dpi=100)
plt.show()
```

---

## 2. Indicador de recesion: descuido de la tasa base

Un indicador economico "predice recesiones con 95% de precision". Pero si las
recesiones ocurren solo el 8% del tiempo, las alertas falsas dominan.

```python
# Parametros del indicador con datos sinteticos
n_meses = 10_000  # Meses simulados

# Tasa base de recesion
p_recesion = 0.08
recesion_real = np.random.random(n_meses) < p_recesion

# Indicador con sensibilidad=0.95 y especificidad=0.90
sensibilidad = 0.95  # P(alerta | recesion)
especificidad = 0.90  # P(sin alerta | no recesion)

alerta = np.zeros(n_meses, dtype=bool)
for i in range(n_meses):
    if recesion_real[i]:
        alerta[i] = np.random.random() < sensibilidad
    else:
        alerta[i] = np.random.random() > especificidad  # Falsa alarma

# Calcular metricas
verdaderos_positivos = np.sum(alerta & recesion_real)
falsos_positivos = np.sum(alerta & ~recesion_real)
total_alertas = np.sum(alerta)

precision_observada = verdaderos_positivos / total_alertas if total_alertas > 0 else 0

# Calculo analitico con Bayes
p_alerta = sensibilidad * p_recesion + (1 - especificidad) * (1 - p_recesion)
p_recesion_dado_alerta = (sensibilidad * p_recesion) / p_alerta

print("=== Indicador de recesion: descuido de tasa base ===")
print(f"Meses simulados:          {n_meses:,}")
print(f"Recesiones reales:        {np.sum(recesion_real):,} ({np.mean(recesion_real):.2%})")
print(f"Alertas emitidas:         {total_alertas:,}")
print(f"Verdaderos positivos:     {verdaderos_positivos:,}")
print(f"Falsos positivos:         {falsos_positivos:,}")
print(f"Precision observada:      {precision_observada:.4f}")
print(f"Precision analitica:      {p_recesion_dado_alerta:.4f}")
print(f"\nA pesar del 95% de sensibilidad, solo ~{p_recesion_dado_alerta:.0%} de las alertas son correctas.")
```

**Salida esperada**: La precision real del indicador es ~45%, no 95%.

---

## 3. NHST y falacia del fiscal: ejemplo de test medico

```python
# Test medico: enfermedad rara con prevalencia 1 en 1,000
prevalencia = 0.001
sensibilidad_test = 0.99
especificidad_test = 0.95

# Bayes
p_positivo = sensibilidad_test * prevalencia + (1 - especificidad_test) * (1 - prevalencia)
p_enfermo_dado_positivo = (sensibilidad_test * prevalencia) / p_positivo

# Simulacion con poblacion de 100,000
poblacion = 100_000
enfermos = int(poblacion * prevalencia)
sanos = poblacion - enfermos

vp = int(enfermos * sensibilidad_test)  # Verdaderos positivos
fp = int(sanos * (1 - especificidad_test))  # Falsos positivos

print("=== Test medico: NHST puede enganiar ===")
print(f"Poblacion:               {poblacion:,}")
print(f"Enfermos reales:         {enfermos:,}")
print(f"Verdaderos positivos:    {vp:,}")
print(f"Falsos positivos:        {fp:,}")
print(f"Total positivos:         {vp + fp:,}")
print(f"P(enfermo | positivo):   {p_enfermo_dado_positivo:.4f}")
print(f"\nEl p-value del test es {1-sensibilidad_test:.2f}, pero P(enfermo|+) = {p_enfermo_dado_positivo:.2%}")

# Visualizacion con diagrama de Venn simplificado (barras apiladas)
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(['Positivos'], [vp], color='green', label=f'Verdaderos positivos ({vp})')
ax.barh(['Positivos'], [fp], left=[vp], color='red', label=f'Falsos positivos ({fp})')
ax.set_xlabel('Numero de personas')
ax.set_title('Resultado del test: la mayoria de positivos son falsos')
ax.legend()
plt.tight_layout()
plt.savefig('../data/fig_ch04_test_medico.png', dpi=100)
plt.show()
```

---

## 4. Intervalos de confianza: tres tipos de errores

Los intervalos de confianza son frecuentemente malinterpretados.

```python
# Generar datos sinteticos de retornos
np.random.seed(42)
n_muestra = 50
mu_real = 0.08  # Retorno anual real (desconocido en la practica)
sigma_real = 0.20
retornos_anuales = np.random.normal(mu_real, sigma_real, n_muestra)

# Calcular IC al 95% clasico
media_muestral = np.mean(retornos_anuales)
error_estandar = np.std(retornos_anuales, ddof=1) / np.sqrt(n_muestra)
t_critico = stats.t.ppf(0.975, df=n_muestra - 1)
ic_inferior = media_muestral - t_critico * error_estandar
ic_superior = media_muestral + t_critico * error_estandar

print("=== Intervalo de confianza al 95% ===")
print(f"Media muestral:    {media_muestral:.4f}")
print(f"Error estandar:    {error_estandar:.4f}")
print(f"IC 95%:            [{ic_inferior:.4f}, {ic_superior:.4f}]")
print(f"Valor real de mu:  {mu_real:.4f}")
print(f"El IC contiene mu: {ic_inferior <= mu_real <= ic_superior}")

# Error comun 1: "Hay 95% de probabilidad de que mu este en el IC"
# FALSO: mu es fijo, el intervalo es aleatorio.

# Error comun 2: "El 95% de los datos cae en el IC"
# FALSO: el IC es para la media, no para los datos.

# Error comun 3: "Si repetimos el experimento, el nuevo IC sera similar"
# NO NECESARIAMENTE: depende de la muestra.
```

```python
# Demostrar que el 95% se refiere a la cobertura en repeticiones
n_repeticiones = 200
intervalos = []
contiene_mu = 0

for _ in range(n_repeticiones):
    muestra = np.random.normal(mu_real, sigma_real, n_muestra)
    m = np.mean(muestra)
    se = np.std(muestra, ddof=1) / np.sqrt(n_muestra)
    tc = stats.t.ppf(0.975, df=n_muestra - 1)
    lo, hi = m - tc * se, m + tc * se
    cubre = lo <= mu_real <= hi
    intervalos.append((lo, hi, cubre))
    contiene_mu += cubre

print(f"De {n_repeticiones} intervalos, {contiene_mu} contienen mu ({contiene_mu/n_repeticiones:.1%})")

# Visualizar los primeros 50 intervalos
fig, ax = plt.subplots(figsize=(10, 8))
for i, (lo, hi, cubre) in enumerate(intervalos[:50]):
    color = 'blue' if cubre else 'red'
    ax.plot([lo, hi], [i, i], color=color, linewidth=1.5, alpha=0.7)
    ax.plot([(lo+hi)/2], [i], 'o', color=color, markersize=3)

ax.axvline(mu_real, color='green', linestyle='--', linewidth=2, label=f'mu real = {mu_real}')
ax.set_xlabel('Valor del parametro')
ax.set_ylabel('Numero de repeticion')
ax.set_title(f'Intervalos de confianza al 95%: {contiene_mu} de {n_repeticiones} contienen mu')
ax.legend()
plt.tight_layout()
plt.savefig('../data/fig_ch04_intervalos_confianza.png', dpi=100)
plt.show()
```

---

## 5. Modelo de mercado OLS: regresion lineal con datos sinteticos

Simular un activo cuyo retorno depende del mercado (modelo CAPM simplificado).

```python
# Generar retornos sinteticos de mercado y activo
n_obs = 252  # Un anio de datos diarios

# Retornos del mercado (con colas gruesas para ser realista)
retorno_mercado = stats.t.rvs(df=5, loc=0.0004, scale=0.012, size=n_obs)

# Retornos del activo: beta=1.3, alpha=0.0002, con ruido no-normal
beta_real = 1.3
alpha_real = 0.0002
ruido = stats.t.rvs(df=4, loc=0, scale=0.008, size=n_obs)
retorno_activo = alpha_real + beta_real * retorno_mercado + ruido

# Ajustar regresion OLS con statsmodels
X = sm.add_constant(retorno_mercado)  # Agregar intercepto
modelo_ols = sm.OLS(retorno_activo, X).fit()

print(modelo_ols.summary())
```

**Salida esperada**: Resumen del modelo OLS con beta cercano a 1.3 y alpha
cercano a 0. Los p-values pueden enganiar si los residuos no son normales.

```python
# Visualizar la regresion
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter con linea de regresion
axes[0].scatter(retorno_mercado, retorno_activo, alpha=0.4, s=15)
x_linea = np.linspace(retorno_mercado.min(), retorno_mercado.max(), 100)
y_linea = modelo_ols.params[0] + modelo_ols.params[1] * x_linea
axes[0].plot(x_linea, y_linea, 'r-', linewidth=2,
             label=f'y = {modelo_ols.params[0]:.4f} + {modelo_ols.params[1]:.2f}x')
axes[0].set_xlabel('Retorno del mercado')
axes[0].set_ylabel('Retorno del activo')
axes[0].set_title('Modelo de mercado OLS')
axes[0].legend()

# Residuos vs valores ajustados
residuos = modelo_ols.resid
axes[1].scatter(modelo_ols.fittedvalues, residuos, alpha=0.4, s=15)
axes[1].axhline(0, color='red', linestyle='--')
axes[1].set_xlabel('Valores ajustados')
axes[1].set_ylabel('Residuos')
axes[1].set_title('Residuos vs ajustados (buscar patrones)')

plt.tight_layout()
plt.savefig('../data/fig_ch04_ols_mercado.png', dpi=100)
plt.show()
```

---

## 6. Diagnostico: Jarque-Bera, curtosis y no-normalidad de residuos

```python
# Prueba de Jarque-Bera sobre los residuos
jb_stat, jb_pvalue = stats.jarque_bera(residuos)

# Curtosis y sesgo de los residuos
curtosis_residuos = stats.kurtosis(residuos)
sesgo_residuos = stats.skew(residuos)

# Test de Shapiro-Wilk (complementario)
sw_stat, sw_pvalue = stats.shapiro(residuos)

print("=== Diagnostico de normalidad de residuos ===")
print(f"Sesgo:              {sesgo_residuos:.4f}  (normal=0)")
print(f"Curtosis (exceso):  {curtosis_residuos:.4f}  (normal=0)")
print(f"Jarque-Bera stat:   {jb_stat:.4f}")
print(f"Jarque-Bera p-val:  {jb_pvalue:.6f}")
print(f"Shapiro-Wilk stat:  {sw_stat:.4f}")
print(f"Shapiro-Wilk p-val: {sw_pvalue:.6f}")

if jb_pvalue < 0.05:
    print("\n>> Se RECHAZA normalidad de residuos (Jarque-Bera, alpha=0.05)")
    print(">> Los p-values y los IC del modelo OLS NO son confiables.")
else:
    print("\n>> No se rechaza normalidad (pero esto no significa que sean normales).")
```

```python
# Visualizacion de diagnostico de residuos
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Histograma de residuos con normal superpuesta
x_r = np.linspace(residuos.min(), residuos.max(), 200)
axes[0, 0].hist(residuos, bins=40, density=True, alpha=0.6)
axes[0, 0].plot(x_r, stats.norm.pdf(x_r, np.mean(residuos), np.std(residuos)),
                'r-', linewidth=2, label='Normal teorica')
axes[0, 0].set_title('Histograma de residuos')
axes[0, 0].legend()

# QQ-Plot de residuos
stats.probplot(residuos, dist="norm", plot=axes[0, 1])
axes[0, 1].set_title('QQ-Plot de residuos')

# ACF de residuos (autocorrelacion)
from statsmodels.graphics.tsaplots import plot_acf
plot_acf(residuos, lags=30, ax=axes[1, 0], alpha=0.05)
axes[1, 0].set_title('Autocorrelacion de residuos')

# ACF de residuos al cuadrado (heterocedasticidad / ARCH)
plot_acf(residuos**2, lags=30, ax=axes[1, 1], alpha=0.05)
axes[1, 1].set_title('ACF de residuos^2 (efecto ARCH)')

plt.suptitle('Diagnostico completo de residuos OLS', fontsize=13)
plt.tight_layout()
plt.savefig('../data/fig_ch04_diagnostico_residuos.png', dpi=100)
plt.show()
```

**Salida esperada**: El QQ-plot mostrara desviaciones en las colas. La curtosis
sera elevada. Si hay efecto ARCH, la ACF de residuos^2 mostrara correlaciones.

---

## 7. Ejercicio: intervalos credibles vs intervalos de confianza

Comparar el intervalo de confianza frecuentista con el intervalo credible
bayesiano para la media de retornos.

Tareas:
1. Usar los retornos del modelo de mercado generados en la seccion 5.
2. Calcular el IC frecuentista al 95% (ya hecho arriba como referencia).
3. Implementar un intervalo credible bayesiano al 95% usando un prior
   conjugado normal: prior N(0, 0.05^2) para la media, y calcular el
   posterior dado los datos.
4. Graficar ambos intervalos y el prior/posterior.
5. Responder: en que condiciones el intervalo credible es mas estrecho?

```python
# Espacio para la solucion del ejercicio
# Pista: con prior N(mu_0, sigma_0^2) y likelihood N(mu, sigma^2/n),
# el posterior es N(mu_post, sigma_post^2) donde:
# sigma_post^2 = 1 / (1/sigma_0^2 + n/sigma^2)
# mu_post = sigma_post^2 * (mu_0/sigma_0^2 + n*x_bar/sigma^2)

# Parametros del prior
mu_0 = 0.0  # Creencia previa: media cero
sigma_0 = 0.05  # Incertidumbre del prior

# Completar la implementacion aqui
# ...
```

---

## Referencias

- Gigerenzer, G. (2004). *Mindless statistics*. Journal of Socio-Economics.
- Wasserstein, R. & Lazar, N. (2016). *ASA Statement on Statistical Significance and P-Values*.
- Taleb, N.N. (2007). *The Black Swan*.
- Nuzzo, R. (2014). *Scientific method: Statistical errors*. Nature.
