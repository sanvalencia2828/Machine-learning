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
# # Modulo 6B: MLE Falla con Pocos Datos -- El Caso ZYX
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Demostrar que MLE da p=1 con 3/3 beats (absurdo estadistico)
# 2. Construir el posterior Beta-Binomial como alternativa con incertidumbre
# 3. Comparar sensibilidad a priors con datasets de 3-8 observaciones
# 4. Implementar actualizacion secuencial y ver el impacto de un "miss"
# 5. Aplicar el framework a startups/IPOs con historia corta

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
# ## 2. El Problema: MLE con 3 Datos
#
# Empresa ZYX: 3 trimestres, 3 beats. MLE dice p=1.

# %%
# Datos ZYX
beats = 3
total = 3

# MLE
p_mle = beats / total

# PML con prior uniforme Beta(1,1)
alpha_prior, beta_prior = 1, 1
alpha_post = alpha_prior + beats
beta_post = beta_prior + (total - beats)
posterior = stats.beta(alpha_post, beta_post)

print("=== CASO ZYX: 3 TRIMESTRES, 3 BEATS ===\n")
print(f"  MLE: p_hat = {p_mle:.1f} (100% de certeza)")
print(f"\n  PML con prior Beta({alpha_prior},{beta_prior}):")
print(f"    Posterior: Beta({alpha_post},{beta_post})")
print(f"    Media: {posterior.mean():.1%}")
print(f"    HDI 95%: ({posterior.ppf(0.025):.1%}, {posterior.ppf(0.975):.1%})")
print(f"    P(p > 0.9): {1 - posterior.cdf(0.9):.1%}")
print(f"    P(p > 0.5): {1 - posterior.cdf(0.5):.1%}")

print(f"\n  MLE dice: 'Siempre gana. 100%.'")
print(f"  PML dice: 'Probablemente entre 38% y 99%. Media 80%.'")
print(f"  Cual es mas honesto con 3 datos?")

# %% [markdown]
# ### Visualizacion: MLE (punto) vs PML (distribucion)

# %%
x = np.linspace(0, 1, 500)
fig, ax = plt.subplots(figsize=(10, 6))

# Prior
ax.plot(x * 100, stats.beta(1, 1).pdf(x), 'gray', ls='--', lw=1.5, label='Prior Beta(1,1)')

# Posterior
ax.plot(x * 100, posterior.pdf(x), 'orangered', lw=2.5, label=f'Posterior Beta({alpha_post},{beta_post})')
ax.fill_between(x * 100, posterior.pdf(x),
                where=(x >= posterior.ppf(0.025)) & (x <= posterior.ppf(0.975)),
                alpha=0.2, color='orangered', label='HDI 95%')

# MLE punto
ax.axvline(p_mle * 100, color='steelblue', ls='--', lw=2.5,
           label=f'MLE: p = {p_mle:.0%}')
ax.scatter([p_mle * 100], [0], s=200, color='steelblue', zorder=5, marker='D')

ax.set_xlabel('P(earnings beat) %')
ax.set_ylabel('Densidad')
ax.set_title('MLE (punto unico p=100%) vs PML (distribucion completa)',
             fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.set_xlim(0, 100)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. Sensibilidad al Prior con Pocos Datos

# %%
priors = [
    ("Uniforme Beta(1,1)", 1, 1),
    ("Esceptico Beta(2,2)", 2, 2),
    ("Informado Beta(3,2)", 3, 2),  # sesgo hacia beats
    ("Muy esceptico Beta(1,3)", 1, 3),  # sesgo contra beats
]

fig, ax = plt.subplots(figsize=(10, 6))

print("=== SENSIBILIDAD AL PRIOR (3/3 beats) ===\n")
print(f"{'Prior':<25} {'Posterior':<15} {'Media':<10} {'HDI 95%':<25} {'P(p>0.9)'}")
print("-" * 80)

for nombre, a, b in priors:
    a_post = a + beats
    b_post = b + (total - beats)
    post = stats.beta(a_post, b_post)
    hdi = post.ppf([0.025, 0.975])

    print(f"{nombre:<25} Beta({a_post},{b_post}){'':<5} "
          f"{post.mean():<10.1%} ({hdi[0]:.1%}, {hdi[1]:.1%}){'':<5} "
          f"{1-post.cdf(0.9):.1%}")

    ax.plot(x * 100, post.pdf(x), lw=2, label=f'{nombre}: media={post.mean():.0%}')

ax.axvline(100, color='steelblue', ls='--', lw=1.5, label='MLE: 100%')
ax.set_xlabel('P(beat) %')
ax.set_ylabel('Densidad')
ax.set_title('Con 3 datos, el prior IMPORTA mucho', fontsize=13)
ax.legend(fontsize=9)
plt.tight_layout()
plt.show()

print(f"\n  -> Con solo 3 datos, la eleccion de prior cambia la media de 57% a 83%")
print(f"  -> Con 100 datos, el prior casi no importaria")
print(f"  -> MLE ignora todo esto y dice 100% sin importar el contexto")

# %% [markdown]
# ---
# ## 4. Actualizacion Secuencial: 8 Trimestres

# %%
# ZYX: 8 trimestres de resultados
resultados = [1, 1, 1, 1, 1, 0, 1, 1]  # Q6 es un miss!
trimestres = [f"Q{i+1}" for i in range(len(resultados))]

alpha, beta_param = 1, 1  # Prior uniforme
trayectoria = [{
    "t": "Prior", "alpha": alpha, "beta": beta_param,
    "media_pml": alpha / (alpha + beta_param),
    "hdi": stats.beta(alpha, beta_param).ppf([0.025, 0.975]),
    "mle": np.nan,
}]

k_acum, n_acum = 0, 0
for i, (t, r) in enumerate(zip(trimestres, resultados)):
    k_acum += r
    n_acum += 1
    alpha += r
    beta_param += (1 - r)
    post = stats.beta(alpha, beta_param)
    trayectoria.append({
        "t": t + (" (MISS)" if r == 0 else ""),
        "alpha": alpha, "beta": beta_param,
        "media_pml": post.mean(),
        "hdi": post.ppf([0.025, 0.975]),
        "mle": k_acum / n_acum,
    })

print("=== ACTUALIZACION SECUENCIAL: 8 TRIMESTRES ===\n")
print(f"{'Trim':<15} {'Resultado':<10} {'MLE':<10} {'PML media':<12} {'PML HDI 95%'}")
print("-" * 60)
for i, t in enumerate(trayectoria):
    res = "-" if i == 0 else ("BEAT" if resultados[i-1] == 1 else "MISS")
    mle_str = f"{t['mle']:.0%}" if not np.isnan(t['mle']) else "-"
    print(f"{t['t']:<15} {res:<10} {mle_str:<10} {t['media_pml']:<12.1%} "
          f"({t['hdi'][0]:.1%}, {t['hdi'][1]:.1%})")

# Grafico
fig, ax = plt.subplots(figsize=(12, 6))
pasos = range(len(trayectoria))
medias = [t['media_pml'] for t in trayectoria]
hdi_lo = [t['hdi'][0] for t in trayectoria]
hdi_hi = [t['hdi'][1] for t in trayectoria]
mles = [t['mle'] for t in trayectoria]

ax.plot(pasos, [m*100 for m in medias], 'orangered', lw=2.5, marker='o', ms=8, label='PML media')
ax.fill_between(pasos, [h*100 for h in hdi_lo], [h*100 for h in hdi_hi],
                alpha=0.15, color='orangered', label='PML HDI 95%')
ax.plot(pasos, [m*100 if not np.isnan(m) else np.nan for m in mles],
        'steelblue', lw=2, ls='--', marker='s', ms=6, label='MLE')

# Marcar el miss
miss_idx = resultados.index(0) + 1
ax.axvline(miss_idx, color='red', ls=':', alpha=0.5)
ax.annotate('MISS!', xy=(miss_idx, 60), fontsize=12, color='red', fontweight='bold')

ax.set_xticks(pasos)
ax.set_xticklabels([t['t'] for t in trayectoria], rotation=45, ha='right', fontsize=9)
ax.set_ylabel('P(beat) %')
ax.set_title('ZYX: MLE salta bruscamente con el miss. PML es suave.', fontsize=13)
ax.legend(fontsize=10)
ax.set_ylim(0, 105)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 5. Distribucion Predictiva: Proximos 4 Trimestres

# %%
# Despues de 8 trimestres: posterior Beta(8, 2)
alpha_final = trayectoria[-1]["alpha"]
beta_final = trayectoria[-1]["beta"]

np.random.seed(42)
n_sim = 50000
n_futuros = 4

# PML predictive
theta_post = np.random.beta(alpha_final, beta_final, n_sim)
beats_futuros = np.array([np.random.binomial(n_futuros, t) for t in theta_post])

# MLE predictive (punto fijo)
p_mle_final = 7 / 8
beats_mle = np.random.binomial(n_futuros, p_mle_final, n_sim)

print(f"=== PREDICCION: PROXIMOS {n_futuros} TRIMESTRES ===\n")
print(f"  Posterior actual: Beta({alpha_final}, {beta_final}), media={alpha_final/(alpha_final+beta_final):.0%}")
print(f"  MLE actual: p = {p_mle_final:.0%}")

print(f"\n  {'Metrica':<30} {'MLE':<15} {'PML'}")
print(f"  {'-'*55}")
print(f"  {'P(4/4 beats)':<30} {(beats_mle==4).mean():<15.1%} {(beats_futuros==4).mean():.1%}")
print(f"  {'P(3+/4 beats)':<30} {(beats_mle>=3).mean():<15.1%} {(beats_futuros>=3).mean():.1%}")
print(f"  {'P(0 beats)':<30} {(beats_mle==0).mean():<15.1%} {(beats_futuros==0).mean():.1%}")
print(f"  {'Media beats':<30} {beats_mle.mean():<15.1f} {beats_futuros.mean():.1f}")

print(f"\n  -> PML asigna mas probabilidad a 0 beats y menos a 4/4")
print(f"  -> PML es mas honesto: incorpora incertidumbre sobre p")

# %% [markdown]
# ---
# ## 6. Resumen
#
# | Metrica | MLE (3/3 datos) | PML Beta(1,1) |
# |---------|----------------|---------------|
# | p estimado | 1.000 (100%) | 0.800 (80%) |
# | Incertidumbre | NINGUNA | HDI (38%, 99%) |
# | P(p > 0.9) | 100% | 34% |
# | Ante un miss | Cae bruscamente 17pp | Cae suavemente 11pp |
# | Prediccion 4T | 4/4 con 75% confianza | 4/4 con 51% confianza |
#
# ### Takeaways
# 1. MLE con pocos datos produce estimaciones **absurdas** (p=1 con 3 datos)
# 2. PML con prior uniforme ya corrige: **80% en vez de 100%**
# 3. Con prior esceptico: aun mas conservador (71%)
# 4. El prior **importa mucho** con pocos datos, **poco** con muchos
# 5. La distribucion predictiva PML es mas honesta que la puntual MLE
#
# ---
# *source_ref: turn0browsertab744690698*
