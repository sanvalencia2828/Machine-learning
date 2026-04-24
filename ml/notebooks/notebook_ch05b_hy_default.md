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
# # Modulo 5B: Inferencia Bayesiana para Default de Bonos High-Yield
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Parametrizar priors Beta segun rating crediticio (BBB, BB, B, CCC)
# 2. Modelar downgrades/upgrades como evidencia que actualiza P(default)
# 3. Implementar actualizacion secuencial paso a paso en Python
# 4. Simular distribucion predictiva de defaults para un portafolio
# 5. Comparar modelo bayesiano vs frecuentista para gestion de riesgo crediticio

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
# ## 2. Priors por Rating Crediticio
#
# Cada rating tiene una tasa historica de default diferente.
# Usamos Beta como prior, parametrizada segun el rating.

# %%
RATING_PRIORS = {
    "AAA": {"alpha": 1, "beta": 199, "media_hist": "0.5%"},
    "AA":  {"alpha": 1, "beta": 99,  "media_hist": "1.0%"},
    "A":   {"alpha": 1, "beta": 49,  "media_hist": "2.0%"},
    "BBB": {"alpha": 2, "beta": 18,  "media_hist": "10%"},
    "BB":  {"alpha": 3, "beta": 12,  "media_hist": "20%"},
    "B":   {"alpha": 4, "beta": 8,   "media_hist": "33%"},
    "CCC": {"alpha": 5, "beta": 5,   "media_hist": "50%"},
}

x = np.linspace(0, 0.7, 300)
fig, ax = plt.subplots(figsize=(12, 6))
for rating, params in RATING_PRIORS.items():
    dist = stats.beta(params["alpha"], params["beta"])
    ax.plot(x * 100, dist.pdf(x), lw=2,
            label=f'{rating}: media={dist.mean()*100:.1f}% ({params["media_hist"]} hist)')

ax.set_xlabel('P(default) %')
ax.set_ylabel('Densidad')
ax.set_title('Priors por Rating Crediticio', fontsize=13)
ax.legend(fontsize=9, ncol=2)
ax.set_xlim(0, 70)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. Modelar Eventos de Rating como Evidencia
#
# Cada evento de rating se traduce en "pseudo-observaciones":
# - **Downgrade**: incrementa alpha (mas evidencia de default)
# - **Upgrade**: incrementa beta (mas evidencia de sobrevivencia)
# - **Neutral**: incrementa beta ligeramente

# %%
RATING_EVIDENCE = {
    "downgrade":     {"d_alpha": 1.0, "d_beta": 0.0},
    "upgrade":       {"d_alpha": 0.0, "d_beta": 2.0},
    "neutral":       {"d_alpha": 0.0, "d_beta": 1.0},
    "double_down":   {"d_alpha": 2.0, "d_beta": 0.0},  # Doble downgrade
    "default_near":  {"d_alpha": 3.0, "d_beta": 0.0},  # Cerca de default
}

print("=== EVIDENCIA POR TIPO DE EVENTO ===\n")
print(f"{'Evento':<20} {'Delta alpha':<15} {'Delta beta':<15} {'Efecto en P(default)'}")
print("-" * 65)
for evento, ev in RATING_EVIDENCE.items():
    efecto = "SUBE" if ev["d_alpha"] > 0 else "BAJA"
    print(f"{evento:<20} +{ev['d_alpha']:<14.1f} +{ev['d_beta']:<14.1f} {efecto}")

# %% [markdown]
# ---
# ## 4. Actualizacion Secuencial: Caso MegaCorp

# %%
def actualizar_secuencial(rating_inicial, eventos, priors=None):
    """Actualiza P(default) secuencialmente con eventos de rating.

    Parametros
    ----------
    rating_inicial : str
        Rating inicial (ej: "BB").
    eventos : list[str]
        Lista de eventos ("downgrade", "upgrade", "neutral").
    priors : dict, optional
        Diccionario de priors por rating.

    Retorna
    -------
    list[dict] con alpha, beta, media, hdi_lo, hdi_hi en cada paso.
    """
    if priors is None:
        priors = RATING_PRIORS

    p = priors[rating_inicial]
    alpha, beta_param = p["alpha"], p["beta"]

    trayectoria = [{
        "paso": 0, "evento": f"Prior ({rating_inicial})",
        "alpha": alpha, "beta": beta_param,
        "media": alpha / (alpha + beta_param),
        "hdi": stats.beta(alpha, beta_param).ppf([0.025, 0.975]),
    }]

    for i, evento in enumerate(eventos):
        ev = RATING_EVIDENCE[evento]
        alpha += ev["d_alpha"]
        beta_param += ev["d_beta"]
        dist = stats.beta(alpha, beta_param)
        trayectoria.append({
            "paso": i + 1, "evento": evento,
            "alpha": alpha, "beta": beta_param,
            "media": dist.mean(),
            "hdi": dist.ppf([0.025, 0.975]),
        })

    return trayectoria


# Caso MegaCorp: BB inicial, 8 trimestres de eventos
eventos_megacorp = [
    "neutral", "downgrade", "neutral", "downgrade",
    "neutral", "neutral", "upgrade", "neutral",
]

tray = actualizar_secuencial("BB", eventos_megacorp)

print("=== MEGACORP: ACTUALIZACION SECUENCIAL ===\n")
print(f"{'Paso':<6} {'Evento':<15} {'Alpha':<8} {'Beta':<8} "
      f"{'P(def)':<10} {'HDI 95%'}")
print("-" * 65)
for t in tray:
    print(f"{t['paso']:<6} {t['evento']:<15} {t['alpha']:<8.1f} {t['beta']:<8.1f} "
          f"{t['media']:<10.1%} ({t['hdi'][0]:.1%}, {t['hdi'][1]:.1%})")

# %% [markdown]
# ### Visualizacion de la evolucion

# %%
pasos = [t['paso'] for t in tray]
medias = [t['media'] for t in tray]
hdi_lo = [t['hdi'][0] for t in tray]
hdi_hi = [t['hdi'][1] for t in tray]
colores_evento = {'Prior (BB)': 'gray', 'neutral': 'steelblue',
                  'downgrade': 'red', 'upgrade': 'green'}

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(pasos, [m*100 for m in medias], 'orangered', lw=2, marker='o', ms=8)
ax.fill_between(pasos, [h*100 for h in hdi_lo], [h*100 for h in hdi_hi],
                alpha=0.2, color='orangered')

# Colorear puntos por evento
for t in tray:
    color = colores_evento.get(t['evento'], 'gray')
    ax.scatter(t['paso'], t['media']*100, c=color, s=100, zorder=5, edgecolor='black')

ax.set_xlabel('Trimestre')
ax.set_ylabel('P(default) %')
ax.set_title('MegaCorp: P(default) evoluciona con cada evento de rating', fontsize=13)

# Leyenda manual
from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', ms=10, label='Downgrade'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='green', ms=10, label='Upgrade'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue', ms=10, label='Neutral'),
]
ax.legend(handles=legend_elems, fontsize=10)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 5. Portafolio: Distribucion Predictiva de Defaults

# %%
def predictive_portafolio(bonos, n_sim=50000, seed=42):
    """Simula defaults del portafolio usando posteriors individuales.

    Parametros
    ----------
    bonos : list[dict]
        Lista con alpha y beta del posterior de cada bono.
    n_sim : int
        Simulaciones.

    Retorna
    -------
    np.ndarray : numero de defaults por simulacion.
    """
    np.random.seed(seed)
    n_bonos = len(bonos)
    defaults_total = np.zeros(n_sim, dtype=int)

    for bono in bonos:
        theta = np.random.beta(bono["alpha"], bono["beta"], n_sim)
        default = (np.random.random(n_sim) < theta).astype(int)
        defaults_total += default

    return defaults_total


# Portafolio de 15 bonos con diferentes posteriors
np.random.seed(42)
portafolio = []
for i in range(15):
    # Simular historia de ratings aleatoria
    rating = np.random.choice(["BB", "B", "BBB"], p=[0.5, 0.3, 0.2])
    n_eventos = np.random.randint(2, 8)
    eventos = np.random.choice(["neutral", "downgrade", "upgrade"],
                                n_eventos, p=[0.5, 0.35, 0.15]).tolist()
    tray = actualizar_secuencial(rating, eventos)
    final = tray[-1]
    portafolio.append({
        "bono": f"Bono_{i+1}", "rating": rating,
        "alpha": final["alpha"], "beta": final["beta"],
        "p_default": final["media"],
    })

# Mostrar portafolio
print("=== PORTAFOLIO: 15 BONOS HIGH-YIELD ===\n")
print(f"{'Bono':<10} {'Rating':<8} {'P(default)':<12} {'HDI 95%'}")
print("-" * 50)
for b in portafolio:
    hdi = stats.beta(b["alpha"], b["beta"]).ppf([0.025, 0.975])
    print(f"{b['bono']:<10} {b['rating']:<8} {b['p_default']:<12.1%} "
          f"({hdi[0]:.1%}, {hdi[1]:.1%})")

# Distribucion predictiva
defaults = predictive_portafolio(portafolio)

fig, ax = plt.subplots(figsize=(10, 5))
vals = np.arange(0, defaults.max() + 1)
probs = [(defaults == v).mean() for v in vals]
colores = ['#2ecc71' if v <= 2 else '#f39c12' if v <= 4 else '#e74c3c'
           for v in vals]
ax.bar(vals, probs, color=colores, edgecolor='black')
ax.set_xlabel('Numero de defaults')
ax.set_ylabel('Probabilidad')
ax.set_title('Distribucion Predictiva: Defaults en Portafolio de 15 Bonos', fontsize=13)

# Metricas
print(f"\n=== DISTRIBUCION PREDICTIVA DE DEFAULTS ===")
print(f"  Media: {defaults.mean():.1f} defaults")
print(f"  P(0 defaults): {(defaults==0).mean():.1%}")
print(f"  P(3+ defaults): {(defaults>=3).mean():.1%}")
print(f"  P(5+ defaults): {(defaults>=5).mean():.1%}")

# Comparar con frecuentista
p_freq = np.mean([b["p_default"] for b in portafolio])
from scipy.stats import binom
print(f"\n  Frecuentista (p_fija={p_freq:.1%}):")
print(f"    P(3+ defaults): {1-binom.cdf(2, 15, p_freq):.1%}")
print(f"    Bayesiano:      {(defaults>=3).mean():.1%}")

plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 6. Resumen
#
# | Paso | Que hace | Ejemplo |
# |------|---------|---------|
# | Prior | Codifica tasa historica por rating | BB: Beta(3,12) = 20% |
# | Evidencia | Cada evento de rating actualiza | Downgrade: alpha += 1 |
# | Posterior | Distribucion actualizada de P(default) | Beta(5,14) = 26.3% |
# | Predictiva | Defaults esperados en portafolio | P(3+ defaults) = 38% |
# | Decision | Ajustar exposicion si P > umbral | Reducir HY si P(3+) > 25% |
#
# ---
# *source_ref: turn0browsertab744690698*
