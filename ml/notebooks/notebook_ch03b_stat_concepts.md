# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .md
#       format_name: markdown
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Modulo 3B: Conceptos Estadisticos y Critica a la Volatilidad
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Calcular e interpretar los 4 momentos: media, varianza, skewness, curtosis
# 2. Demostrar por que la volatilidad es insuficiente como medida de riesgo
# 3. Distinguir entre valor esperado y promedio muestral (ergodicidad)
# 4. Comparar distribuciones Normal vs Student-t vs mezcla con datos sinteticos
# 5. Aplicar medidas de riesgo alternativas: VaR, ES, downside deviation

# %% [markdown]
# ---
# ## 1. Setup

# %%
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
plt.rcParams.update({
    'figure.figsize': (10, 6), 'font.size': 12,
    'axes.grid': True, 'grid.alpha': 0.3,
})
print("Entorno listo.")

# %% [markdown]
# ---
# ## 2. Los 4 Momentos de una Distribucion

# %%
def calcular_4_momentos(datos, nombre=""):
    """Calcula y muestra los 4 momentos de una serie de datos.

    Parametros
    ----------
    datos : array-like
        Serie de retornos o valores.
    nombre : str
        Etiqueta para la serie.

    Retorna
    -------
    dict con media, std, skew, curtosis_exceso.
    """
    mu = np.mean(datos)
    sigma = np.std(datos, ddof=1)
    skew = float(stats.skew(datos))
    kurt_exc = float(stats.kurtosis(datos))  # exceso (Normal=0)

    if nombre:
        print(f"  {nombre}:")
        print(f"    Media:             {mu:>10.6f}")
        print(f"    Std (volatilidad): {sigma:>10.6f}")
        print(f"    Skewness:          {skew:>10.3f}  "
              f"({'simetrica' if abs(skew) < 0.5 else 'asimetrica'})")
        print(f"    Curtosis exceso:   {kurt_exc:>10.2f}  "
              f"({'colas normales' if kurt_exc < 1 else 'colas pesadas'})")

    return {"media": mu, "std": sigma, "skew": skew, "kurt_exc": kurt_exc}


# Generar 3 distribuciones con ~misma media y ~misma std
n = 50000

# 1. Normal pura
ret_normal = np.random.normal(0.0004, 0.012, n)

# 2. Student-t (fat tails)
ret_t = 0.0004 + 0.0085 * np.random.standard_t(4, n)

# 3. Mezcla (cola izquierda pesada)
mask = np.random.binomial(1, 0.95, n).astype(bool)
ret_mezcla = np.where(mask,
    np.random.normal(0.0006, 0.009, n),
    np.random.normal(-0.008, 0.04, n))

print("=== 4 MOMENTOS: 3 distribuciones con ~misma media y ~misma std ===\n")
m1 = calcular_4_momentos(ret_normal, "Normal(0.04%, 1.2%)")
m2 = calcular_4_momentos(ret_t, "Student-t(nu=4)")
m3 = calcular_4_momentos(ret_mezcla, "Mezcla 95/5")

# %% [markdown]
# ### Visualizacion: las 3 distribuciones

# %%
fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
bins = np.linspace(-0.08, 0.08, 100)
datos_list = [(ret_normal, 'Normal', 'steelblue'),
              (ret_t, 'Student-t(4)', 'orangered'),
              (ret_mezcla, 'Mezcla 95/5', 'forestgreen')]

for i, (datos, nombre, color) in enumerate(datos_list):
    axes[i].hist(datos, bins=bins, density=True, alpha=0.6, color=color)
    # Normal de referencia
    x = np.linspace(-0.08, 0.08, 300)
    axes[i].plot(x, stats.norm.pdf(x, datos.mean(), datos.std()),
                 'k--', lw=1.5, label='Normal ref')
    m = calcular_4_momentos(datos)
    axes[i].set_title(f'{nombre}\nskew={m["skew"]:.2f}, kurt_exc={m["kurt_exc"]:.1f}',
                       fontsize=11)
    axes[i].set_xlabel('Retorno')
    axes[i].legend(fontsize=9)

axes[0].set_ylabel('Densidad')
plt.suptitle('3 distribuciones: misma media y std, pero MUY diferente riesgo',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. Por que la Volatilidad es Absurda como Medida de Riesgo

# %%
def comparar_riesgo(datos_list, capital=100000):
    """Compara metricas de riesgo para varias distribuciones."""
    print(f"{'Metrica':<30}", end="")
    for nombre, _, _ in datos_list:
        print(f"{nombre:<18}", end="")
    print()
    print("-" * (30 + 18 * len(datos_list)))

    metricas = [
        ("Std (volatilidad)", lambda d: d.std()),
        ("Skewness", lambda d: float(stats.skew(d))),
        ("Curtosis exceso", lambda d: float(stats.kurtosis(d))),
        ("VaR 95%", lambda d: np.percentile(d, 5)),
        ("VaR 99%", lambda d: np.percentile(d, 1)),
        ("Expected Shortfall 95%", lambda d: d[d <= np.percentile(d, 5)].mean()),
        ("P(retorno < -3%)", lambda d: (d < -0.03).mean()),
        ("P(retorno < -5%)", lambda d: (d < -0.05).mean()),
        ("Downside deviation", lambda d: np.sqrt(np.mean(np.minimum(d, 0)**2))),
        ("Peor retorno", lambda d: d.min()),
    ]

    for nombre_m, func in metricas:
        print(f"{nombre_m:<30}", end="")
        for _, datos, _ in datos_list:
            val = func(datos)
            if isinstance(val, float) and abs(val) < 0.01:
                print(f"{val:<18.6f}", end="")
            elif isinstance(val, float):
                print(f"{val:<18.4f}", end="")
            else:
                print(f"{val:<18}", end="")
        print()


comparar_riesgo([
    ("Normal", ret_normal, None),
    ("Student-t", ret_t, None),
    ("Mezcla", ret_mezcla, None),
])

print("\n--> Las 3 distribuciones tienen volatilidad SIMILAR")
print("--> Pero el riesgo real (VaR, ES, eventos extremos) es DRAMATICAMENTE diferente")
print("--> La volatilidad te miente sobre el riesgo de cola")

# %% [markdown]
# ---
# ## 4. QQ-Plot: Diagnostico Visual de No-Normalidad

# %%
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for i, (nombre, datos, color) in enumerate(datos_list):
    stats.probplot(datos, dist='norm', plot=axes[i])
    axes[i].set_title(f'QQ-Plot: {nombre}', fontsize=11)
    axes[i].get_lines()[0].set_markerfacecolor(color)
    axes[i].get_lines()[0].set_markersize(2)
    axes[i].get_lines()[0].set_alpha(0.5)

plt.suptitle('QQ-Plot vs Normal: desviacion en colas = fat tails',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

print("Si los puntos siguen la linea de 45 grados -> Normal")
print("Si se desvian en los extremos -> colas pesadas")

# %% [markdown]
# ---
# ## 5. Valor Esperado vs Promedio: Ergodicidad

# %%
def demo_ergodicidad(n_pasos=100, n_trayectorias=1000, seed=42):
    """Demuestra no-ergodicidad: E[R] > 0 pero trayectoria individual pierde.

    Juego: +50% o -40% con p=0.5 cada uno.
    E[R] = 0.5*1.5 + 0.5*0.6 = 1.05 -> positivo!
    Pero la media geometrica: sqrt(1.5*0.6) = 0.949 -> negativo!
    """
    np.random.seed(seed)
    capital_inicial = 100

    # Factores: +50% = 1.5, -40% = 0.6
    factores = np.where(
        np.random.binomial(1, 0.5, (n_trayectorias, n_pasos)),
        1.5, 0.6)

    # Trayectorias
    riqueza = capital_inicial * np.cumprod(factores, axis=1)

    # Estadisticas
    media_ensamble = riqueza.mean(axis=0)  # Promedio en cada paso
    mediana = np.median(riqueza, axis=0)

    return riqueza, media_ensamble, mediana


riqueza, media_ens, mediana = demo_ergodicidad()

fig, ax = plt.subplots(figsize=(12, 6))

# Algunas trayectorias individuales
for i in range(min(50, riqueza.shape[0])):
    ax.plot(riqueza[i], alpha=0.1, color='gray', lw=0.5)

ax.plot(media_ens, 'steelblue', lw=2.5, label=f'Media del ensamble (final: ${media_ens[-1]:,.0f})')
ax.plot(mediana, 'orangered', lw=2.5, label=f'Mediana (final: ${mediana[-1]:.2f})')
ax.axhline(100, color='black', ls=':', lw=1, label='Capital inicial: $100')

ax.set_xlabel('Paso (lanzamiento)')
ax.set_ylabel('Riqueza ($)')
ax.set_title('No-Ergodicidad: E[R] > 0 pero la mayoria pierde', fontsize=13)
ax.set_yscale('log')
ax.legend(fontsize=10)
plt.tight_layout()
plt.show()

prob_perdida = (riqueza[:, -1] < 100).mean()
print(f"Valor esperado por paso: +5% (parece buen negocio)")
print(f"Media geometrica por paso: -5.1% (realidad)")
print(f"Despues de 100 pasos:")
print(f"  Media del ensamble: ${media_ens[-1]:,.0f} (engano)")
print(f"  Mediana: ${mediana[-1]:.2f} (realidad)")
print(f"  P(perder dinero): {prob_perdida:.0%}")
print(f"\n--> El valor esperado MIENTE sobre tu experiencia individual")
print(f"--> Necesitas la distribucion completa, no solo E[R]")

# %% [markdown]
# ---
# ## 6. Eventos Extremos: Esperados vs Observados

# %%
def tabla_eventos_extremos(retornos, nombre="Datos"):
    """Compara frecuencia de eventos extremos: observados vs Normal."""
    mu = retornos.mean()
    sigma = retornos.std()
    n = len(retornos)

    print(f"\n=== Eventos extremos: {nombre} (n={n:,}) ===\n")
    print(f"{'Umbral':<15} {'Normal predice':<18} {'Observados':<15} {'Ratio'}")
    print("-" * 60)

    for k in [2, 3, 4, 5]:
        umbral = k * sigma
        p_normal = 2 * stats.norm.sf(k)  # Dos colas
        esperados = p_normal * n
        observados = ((retornos - mu).abs() > umbral).sum() if hasattr(retornos, 'abs') \
            else np.sum(np.abs(retornos - mu) > umbral)
        ratio = observados / max(esperados, 0.01)
        print(f"  {k} sigma      {esperados:>12.1f}      {observados:>10d}     {ratio:>6.1f}x")

    return


tabla_eventos_extremos(ret_normal, "Normal")
tabla_eventos_extremos(ret_t, "Student-t(4)")
tabla_eventos_extremos(ret_mezcla, "Mezcla 95/5")

print("\n--> Normal: eventos observados ~ esperados (modelo correcto)")
print("--> Student-t y Mezcla: eventos extremos 5-100x mas frecuentes")
print("--> Si usas Normal, subestimas riesgo de cola drasticamente")

# %% [markdown]
# ---
# ## 7. Medidas Alternativas de Riesgo

# %%
def calcular_metricas_alternativas(retornos, nombre="", nivel=0.05):
    """Calcula VaR, ES, downside deviation y semi-varianza."""
    var = np.percentile(retornos, nivel * 100)
    es = retornos[retornos <= var].mean()
    downside = np.sqrt(np.mean(np.minimum(retornos, 0)**2))
    semi_var = np.mean(np.minimum(retornos - retornos.mean(), 0)**2)

    if nombre:
        print(f"  {nombre}:")
        print(f"    VaR {1-nivel:.0%}:              {var:>10.5f}  "
              f"(peor retorno con {1-nivel:.0%} confianza)")
        print(f"    Expected Shortfall {1-nivel:.0%}: {es:>10.5f}  "
              f"(media de perdidas peores que VaR)")
        print(f"    Downside deviation:    {downside:>10.5f}  "
              f"(solo volatilidad de bajadas)")
        print(f"    Semi-varianza:         {semi_var:>10.8f}")

    return {"var": var, "es": es, "downside_dev": downside, "semi_var": semi_var}


print("=== METRICAS ALTERNATIVAS DE RIESGO ===\n")
calcular_metricas_alternativas(ret_normal, "Normal")
calcular_metricas_alternativas(ret_t, "Student-t(4)")
calcular_metricas_alternativas(ret_mezcla, "Mezcla 95/5")

# %% [markdown]
# ---
# ## 8. Resumen y Conclusiones
#
# | Momento | Nombre | Que mide | Normal asume |
# |---------|--------|----------|-------------|
# | 1 | Media | Centro de la distribucion | Cualquier valor |
# | 2 | Varianza | Dispersion | Unico parametro de riesgo |
# | 3 | Skewness | Asimetria | = 0 |
# | 4 | Curtosis | Peso de las colas | = 3 (exceso = 0) |
#
# ### Takeaways
# 1. La **volatilidad** solo mide el momento 2 -- ignora skew y curtosis
# 2. Distribuciones con misma std tienen **riesgo real muy diferente**
# 3. El **valor esperado** puede ser positivo aunque la mayoria pierda (no-ergodicidad)
# 4. Eventos de 4+ sigma son **100x mas frecuentes** que la Normal predice
# 5. Usa **distribuciones completas** (VaR, ES, MCS), no solo sigma
#
# ---
# *source_ref: turn0browsertab744690698*
