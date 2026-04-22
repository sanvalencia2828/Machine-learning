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

# Trifecta de Errores en Modelos Financieros

## Proposito

Explorar los tres tipos fundamentales de error que afectan a todo modelo financiero:
especificacion, parametros y adaptacion estructural. Se usan datos sinteticos y
distribuciones de scipy para ilustrar cada caso sin depender de datos externos.

## Requisitos

```python
# Importar librerias necesarias
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Semilla para reproducibilidad
np.random.seed(42)
```

---

## 1. Introduccion: por que todos los modelos financieros son erroneos

Los modelos financieros son simplificaciones de la realidad. George Box lo resumio:
"Todos los modelos son erroneos, pero algunos son utiles." En finanzas, este axioma
cobra especial importancia porque las decisiones basadas en modelos defectuosos
pueden generar perdidas catastroficas.

La **trifecta de errores** clasifica las fuentes de fallo en tres categorias:

1. **Error de especificacion**: elegir la distribucion o estructura equivocada.
2. **Error de parametros**: estimar mal los valores que alimentan un modelo correcto.
3. **Error de adaptacion estructural**: el mundo cambia y el modelo no se adapta.

---

## 2. Error de especificacion: normal vs fat-tailed

Muchos modelos financieros asumen retornos normales. En la practica, los retornos
presentan colas gruesas y asimetria.

```python
# Generar retornos sinteticos: normales vs colas gruesas (t de Student con 3 gl)
n_observaciones = 5000

retornos_normales = np.random.normal(loc=0.0005, scale=0.02, size=n_observaciones)
retornos_cola_gruesa = stats.t.rvs(df=3, loc=0.0005, scale=0.015, size=n_observaciones)

# Calcular estadisticos descriptivos para comparar
resumen = pd.DataFrame({
    'Normal': pd.Series(retornos_normales).describe(),
    'Cola Gruesa (t, df=3)': pd.Series(retornos_cola_gruesa).describe()
})

# Agregar curtosis y sesgo
resumen.loc['curtosis'] = [
    stats.kurtosis(retornos_normales),
    stats.kurtosis(retornos_cola_gruesa)
]
resumen.loc['sesgo'] = [
    stats.skew(retornos_normales),
    stats.skew(retornos_cola_gruesa)
]

print("Comparacion de distribuciones:")
print(resumen.round(6))
```

**Salida esperada**: La distribucion t mostrara curtosis mucho mayor (~6 o mas)
frente a la normal (~0), y valores extremos mas frecuentes.

```python
# Visualizar ambas distribuciones superpuestas
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histograma comparativo
axes[0].hist(retornos_normales, bins=80, alpha=0.6, density=True, label='Normal')
axes[0].hist(retornos_cola_gruesa, bins=80, alpha=0.6, density=True, label='t (df=3)')
axes[0].set_title('Distribucion de retornos sinteticos')
axes[0].set_xlabel('Retorno diario')
axes[0].set_ylabel('Densidad')
axes[0].legend()

# QQ-plot de los retornos de cola gruesa contra la normal teorica
stats.probplot(retornos_cola_gruesa, dist="norm", plot=axes[1])
axes[1].set_title('QQ-Plot: retornos cola gruesa vs normal teorica')

plt.tight_layout()
plt.savefig('../data/fig_ch01_especificacion.png', dpi=100)
plt.show()
```

**Salida esperada**: El histograma muestra colas mas pesadas para la t de Student.
El QQ-plot revela desviaciones claras en los extremos.

---

## 3. Error de parametros: modelo binomial de tasas de credito

Un modelo puede tener la estructura correcta pero parametros equivocados.
Simulamos un portafolio de creditos con distribucion binomial usando 4 tasas
de incumplimiento distintas.

```python
# Parametros del portafolio de creditos
n_creditos = 100  # numero de creditos en el portafolio
probabilidades_default = [0.02, 0.05, 0.10, 0.20]  # tasas de incumplimiento

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for i, p in enumerate(probabilidades_default):
    # Distribucion binomial: numero de incumplimientos dado n y p
    x = np.arange(0, n_creditos + 1)
    pmf = stats.binom.pmf(x, n_creditos, p)

    # Graficar la funcion de masa de probabilidad
    axes[i].bar(x, pmf, color=f'C{i}', alpha=0.7)
    axes[i].set_title(f'Tasa de default = {p:.0%}')
    axes[i].set_xlabel('Numero de incumplimientos')
    axes[i].set_ylabel('Probabilidad')

    # Calcular y mostrar media y desviacion estandar
    media = n_creditos * p
    desv = np.sqrt(n_creditos * p * (1 - p))
    axes[i].axvline(media, color='red', linestyle='--', label=f'Media={media:.1f}')
    axes[i].axvline(media + 2*desv, color='orange', linestyle=':', label=f'+2σ={media+2*desv:.1f}')
    axes[i].legend(fontsize=8)

plt.suptitle('Error de parametros: PMF binomial con distintas tasas', fontsize=13)
plt.tight_layout()
plt.savefig('../data/fig_ch01_parametros.png', dpi=100)
plt.show()
```

**Salida esperada**: Cuatro graficos de barras mostrando como la distribucion
de incumplimientos cambia drasticamente al variar la probabilidad p.

```python
# Tabla resumen de impacto financiero
# Suponemos perdida promedio por credito = $50,000
perdida_por_credito = 50_000

resumen_parametros = []
for p in probabilidades_default:
    media_defaults = n_creditos * p
    var_defaults = n_creditos * p * (1 - p)
    perdida_esperada = media_defaults * perdida_por_credito
    peor_caso_95 = stats.binom.ppf(0.95, n_creditos, p) * perdida_por_credito

    resumen_parametros.append({
        'Prob. Default': f'{p:.0%}',
        'Defaults esperados': media_defaults,
        'Perdida esperada ($)': f'{perdida_esperada:,.0f}',
        'Peor caso 95% ($)': f'{peor_caso_95:,.0f}'
    })

df_resumen = pd.DataFrame(resumen_parametros)
print("Impacto financiero por error en la tasa de default:")
print(df_resumen.to_string(index=False))
```

---

## 4. Error de adaptacion estructural: cambio de regimen

El modelo se construyo para un mundo que ya no existe. Simulamos un mercado
que pasa de un regimen binomial (sube/baja) a uno trinomial (sube/baja/lateral).

```python
# Regimen 1: binomial (primeros 500 dias)
n_dias_r1 = 500
subida = 0.01
bajada = -0.01
prob_subida_r1 = 0.55

movimientos_r1 = np.random.choice(
    [subida, bajada],
    size=n_dias_r1,
    p=[prob_subida_r1, 1 - prob_subida_r1]
)

# Regimen 2: trinomial (siguientes 500 dias) — el modelo no contempla esto
n_dias_r2 = 500
lateral = 0.0
prob_subida_r2 = 0.35
prob_lateral = 0.30
prob_bajada_r2 = 0.35

movimientos_r2 = np.random.choice(
    [subida, lateral, bajada],
    size=n_dias_r2,
    p=[prob_subida_r2, prob_lateral, prob_bajada_r2]
)

# Unir ambos periodos y calcular precio acumulado
movimientos_total = np.concatenate([movimientos_r1, movimientos_r2])
precio = 100 * np.exp(np.cumsum(movimientos_total))

# Visualizar el cambio de regimen
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

axes[0].plot(precio, linewidth=0.8)
axes[0].axvline(n_dias_r1, color='red', linestyle='--', label='Cambio de regimen')
axes[0].set_title('Precio sintetico con cambio de regimen')
axes[0].set_ylabel('Precio')
axes[0].legend()

# Histogramas por regimen
axes[1].hist(movimientos_r1, bins=30, alpha=0.6, label='Regimen binomial', density=True)
axes[1].hist(movimientos_r2, bins=30, alpha=0.6, label='Regimen trinomial', density=True)
axes[1].set_title('Distribucion de movimientos por regimen')
axes[1].set_xlabel('Retorno diario')
axes[1].set_ylabel('Densidad')
axes[1].legend()

plt.tight_layout()
plt.savefig('../data/fig_ch01_adaptacion.png', dpi=100)
plt.show()
```

**Salida esperada**: Un grafico de precio con comportamiento distinto antes y
despues del dia 500, y dos histogramas que evidencian la diferencia estructural.

---

## 5. Ejercicio: modelo con distribucion Student-t

Disenar un modelo de retornos usando `scipy.stats.t` con distintos grados de
libertad (3, 5, 10, 30) y comparar:

1. Generar 10,000 muestras para cada valor de df.
2. Calcular VaR al 99% para cada caso.
3. Graficar las cuatro distribuciones superpuestas.
4. Responder: a partir de que df la t se aproxima a la normal?

```python
# Espacio para la solucion del ejercicio
# Pista: usar stats.t.rvs(df=..., size=...) y np.percentile(...)
grados_libertad = [3, 5, 10, 30]
n_muestras = 10_000

# Completar la implementacion aqui
# ...
```

---

## Referencias

- Orrell, D. & Wilmott, P. (2017). *The Money Formula*.
- Sekerke, M. (2015). *Bayesian Risk Management*.
- Thompson, S. et al. (2006). *The Source of Financial Innovation*.
- Simons, K. (1997). *Model Error*. New England Economic Review.
