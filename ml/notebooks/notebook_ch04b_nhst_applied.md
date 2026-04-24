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
# # Modulo 4B: NHST Aplicado -- OLS, Base Rates e Indicadores Economicos
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Construir un modelo OLS con Statsmodels e interpretar su summary correctamente
# 2. Ejecutar tests diagnosticos (JB, BP, DW) y saber cuando los p-values mienten
# 3. Calcular base rates de recesiones y aplicar Bayes a indicadores economicos
# 4. Construir y analizar la confusion matrix de un indicador financiero
# 5. Cuantificar el impacto del base rate en el valor predictivo positivo (PPV)

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

# Verificar Statsmodels
try:
    import statsmodels.api as sm
    from statsmodels.stats.diagnostic import het_breuschpagan
    print("Statsmodels disponible:", sm.__version__)
except ImportError:
    print("Instala statsmodels: pip install statsmodels")
    sm = None

print("Entorno listo.")

# %% [markdown]
# ---
# ## 2. Regresion OLS: Modelo de Mercado para Apple
#
# r_apple = alpha + beta * r_market + epsilon
#
# Generamos datos sinteticos que simulan la relacion Apple-S&P 500
# con fat tails para demostrar que los diagnosticos OLS fallan.

# %%
def generar_datos_mercado(n=504, beta_real=1.25, alpha_real=0.0002,
                           sigma_epsilon=0.01, nu=4, seed=42):
    """Genera retornos sinteticos tipo Apple vs S&P 500.

    Parametros
    ----------
    n : int
        Numero de dias de trading.
    beta_real : float
        Beta real del activo.
    alpha_real : float
        Alpha real (retorno excedente diario).
    sigma_epsilon : float
        Escala del ruido idiosincratico.
    nu : float
        Grados de libertad Student-t (fat tails).
    seed : int
        Semilla aleatoria.

    Retorna
    -------
    tuple : (r_market, r_asset, r_asset_real)
    """
    np.random.seed(seed)
    r_market = 0.0003 + 0.012 * np.random.standard_t(nu, n)
    epsilon = sigma_epsilon * np.random.standard_t(nu, n)
    r_asset = alpha_real + beta_real * r_market + epsilon
    r_asset_real = alpha_real + beta_real * r_market  # Sin ruido
    return r_market, r_asset, r_asset_real


r_mkt, r_apple, r_apple_real = generar_datos_mercado()

print(f"Datos generados: {len(r_mkt)} dias")
print(f"r_market: media={r_mkt.mean():.5f}, std={r_mkt.std():.5f}")
print(f"r_apple:  media={r_apple.mean():.5f}, std={r_apple.std():.5f}")

# %% [markdown]
# ### OLS con Statsmodels

# %%
if sm is not None:
    X = sm.add_constant(r_mkt)
    modelo = sm.OLS(r_apple, X).fit()
    print(modelo.summary())
else:
    # Fallback: OLS manual
    X = np.column_stack([np.ones(len(r_mkt)), r_mkt])
    beta_hat = np.linalg.lstsq(X, r_apple, rcond=None)[0]
    residuals = r_apple - X @ beta_hat
    rss = np.sum(residuals**2)
    tss = np.sum((r_apple - r_apple.mean())**2)
    r_sq = 1 - rss / tss
    print(f"Alpha: {beta_hat[0]:.6f}")
    print(f"Beta:  {beta_hat[1]:.4f}")
    print(f"R-sq:  {r_sq:.4f}")

# %% [markdown]
# ### Tests Diagnosticos

# %%
if sm is not None:
    residuals = modelo.resid

    # Jarque-Bera
    jb_stat, jb_p, jb_skew, jb_kurt = sm.stats.stattools.jarque_bera(residuals)
    print(f"Jarque-Bera: stat={jb_stat:.1f}, p={jb_p:.2e}")
    print(f"  -> {'RECHAZA normalidad' if jb_p < 0.05 else 'OK'}")

    # Breusch-Pagan
    bp_stat, bp_p, _, _ = het_breuschpagan(residuals, modelo.model.exog)
    print(f"\nBreusch-Pagan: stat={bp_stat:.1f}, p={bp_p:.4f}")
    print(f"  -> {'RECHAZA homocedasticidad' if bp_p < 0.05 else 'OK'}")

    # Durbin-Watson
    from statsmodels.stats.stattools import durbin_watson
    dw = durbin_watson(residuals)
    print(f"\nDurbin-Watson: {dw:.3f}")
    print(f"  -> {'Autocorrelacion positiva' if dw < 1.5 else 'Autocorrelacion negativa' if dw > 2.5 else 'OK'}")

    # Conclusion
    print(f"\n{'='*50}")
    if jb_p < 0.05:
        print("ADVERTENCIA: residuales no son normales.")
        print("Los p-values de la regresion son SOSPECHOSOS.")
        print("No confies ciegamente en alpha p-value = "
              f"{modelo.pvalues[0]:.4f}")
else:
    residuals = r_apple - X @ beta_hat
    jb_stat, jb_p = stats.jarque_bera(residuals)
    print(f"Jarque-Bera: stat={jb_stat:.1f}, p={jb_p:.2e}")
    print(f"  -> {'RECHAZA normalidad' if jb_p < 0.05 else 'OK'}")

# %% [markdown]
# ### Visualizacion: Regresion con IC

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter + linea de regresion
axes[0].scatter(r_mkt * 100, r_apple * 100, s=8, alpha=0.3, color='steelblue')
x_line = np.linspace(r_mkt.min(), r_mkt.max(), 100)
if sm is not None:
    y_line = modelo.params[0] + modelo.params[1] * x_line
    # IC de prediccion
    X_pred = sm.add_constant(x_line)
    pred = modelo.get_prediction(X_pred)
    ci = pred.conf_int(alpha=0.05)
    axes[0].fill_between(x_line * 100, ci[:, 0] * 100, ci[:, 1] * 100,
                         alpha=0.15, color='orangered', label='IC 95%')
else:
    y_line = beta_hat[0] + beta_hat[1] * x_line

axes[0].plot(x_line * 100, y_line * 100, 'orangered', lw=2, label='OLS fit')
axes[0].set_xlabel('Retorno S&P 500 (%)')
axes[0].set_ylabel('Retorno Apple (%)')
axes[0].set_title('Modelo de Mercado: Apple vs S&P 500', fontsize=12)
axes[0].legend()

# QQ-plot de residuales
stats.probplot(residuals, dist='norm', plot=axes[1])
axes[1].set_title('QQ-Plot Residuales (deberia ser linea recta)', fontsize=12)

plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. Base Rates de Recesiones (Datos Sinteticos tipo NBER/FRED)
#
# Simulamos datos historicos de recesiones para calcular base rates
# y evaluar un indicador economico.

# %%
def generar_datos_recesion(n_meses=960, base_rate=0.15,
                            dur_recesion_media=11, seed=42):
    """Genera serie de recesiones sintetica tipo NBER.

    Parametros
    ----------
    n_meses : int
        Numero de meses (~80 anos = 960).
    base_rate : float
        Fraccion del tiempo en recesion.
    dur_recesion_media : int
        Duracion media de recesion en meses.
    seed : int
        Semilla aleatoria.

    Retorna
    -------
    np.ndarray : array binario (1=recesion, 0=expansion).
    """
    np.random.seed(seed)
    recesion = np.zeros(n_meses, dtype=int)
    t = 0
    while t < n_meses:
        # Expansion
        dur_exp = max(12, int(np.random.exponential(
            (1 - base_rate) / base_rate * dur_recesion_media)))
        t += dur_exp
        if t >= n_meses:
            break
        # Recesion
        dur_rec = max(6, int(np.random.exponential(dur_recesion_media)))
        recesion[t:min(t + dur_rec, n_meses)] = 1
        t += dur_rec
    return recesion


recesion = generar_datos_recesion()
n_meses = len(recesion)
n_rec = recesion.sum()
base_rate = n_rec / n_meses

print(f"Simulacion: {n_meses} meses (~{n_meses//12} anos)")
print(f"Meses en recesion: {n_rec} ({base_rate:.1%})")
print(f"Meses en expansion: {n_meses - n_rec} ({1-base_rate:.1%})")

# Contar recesiones (periodos)
cambios = np.diff(recesion)
n_recesiones = (cambios == 1).sum()
print(f"Numero de recesiones: {n_recesiones}")
print(f"Duracion media: {n_rec / max(n_recesiones, 1):.1f} meses")

# %% [markdown]
# ---
# ## 4. Indicador Economico: Confusion Matrix y PPV

# %%
def evaluar_indicador(recesion, sensibilidad=0.85, fpr=0.20, seed=42):
    """Simula un indicador economico y calcula su confusion matrix.

    Parametros
    ----------
    recesion : array
        Serie binaria de recesiones.
    sensibilidad : float
        P(senal | recesion).
    fpr : float
        P(senal | no recesion) -- tasa de falsos positivos.
    seed : int
        Semilla aleatoria.

    Retorna
    -------
    dict con TP, FP, FN, TN, PPV, NPV, accuracy, F1.
    """
    np.random.seed(seed)
    n = len(recesion)
    senal = np.zeros(n, dtype=int)

    for i in range(n):
        if recesion[i] == 1:
            senal[i] = 1 if np.random.random() < sensibilidad else 0
        else:
            senal[i] = 1 if np.random.random() < fpr else 0

    tp = ((senal == 1) & (recesion == 1)).sum()
    fp = ((senal == 1) & (recesion == 0)).sum()
    fn = ((senal == 0) & (recesion == 1)).sum()
    tn = ((senal == 0) & (recesion == 0)).sum()

    ppv = tp / max(tp + fp, 1)
    npv = tn / max(tn + fn, 1)
    accuracy = (tp + tn) / n
    precision = ppv
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-10)

    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "ppv": ppv, "npv": npv, "accuracy": accuracy,
            "sensibilidad": recall, "especificidad": tn / max(tn + fp, 1),
            "f1": f1, "senal": senal}


# Indicador tipo "yield curve inversion"
result = evaluar_indicador(recesion, sensibilidad=0.85, fpr=0.20)

print("=== CONFUSION MATRIX: INDICADOR DE RECESION ===\n")
print(f"  Sensibilidad (recall): {result['sensibilidad']:.1%}")
print(f"  Especificidad:         {result['especificidad']:.1%}")
print(f"  Tasa falsos positivos: {1-result['especificidad']:.1%}")
print(f"  Base rate recesion:    {base_rate:.1%}")
print(f"\n  {'':15} {'Recesion':<12} {'Expansion':<12} {'Total'}")
print(f"  {'-'*45}")
print(f"  {'Senal':<15} {result['tp']:<12d} {result['fp']:<12d} {result['tp']+result['fp']}")
print(f"  {'Sin senal':<15} {result['fn']:<12d} {result['tn']:<12d} {result['fn']+result['tn']}")
print(f"\n  Valor Predictivo Positivo (PPV): {result['ppv']:.1%}")
print(f"  -> Cuando el indicador da senal, solo {result['ppv']:.0%} de las veces HAY recesion")
print(f"  -> El 'fiscal' diria: '85% de sensibilidad = 85% de acierto'")
print(f"  -> La REALIDAD: PPV = {result['ppv']:.0%} por el base rate bajo")

# %% [markdown]
# ### P(Senal|Recesion) vs P(Recesion|Senal)

# %%
# Comparacion directa: la falacia inversa en accion
p_senal_dado_rec = result['sensibilidad']
p_rec_dado_senal = result['ppv']

print("=== FALACIA INVERSA EN ACCION ===\n")
print(f"  P(Senal | Recesion) = {p_senal_dado_rec:.1%}  (lo que NHST evalua)")
print(f"  P(Recesion | Senal) = {p_rec_dado_senal:.1%}  (lo que tu NECESITAS)")
print(f"\n  Diferencia: {abs(p_senal_dado_rec - p_rec_dado_senal):.0%}")
print(f"  NHST confunde estas dos. Tu no deberias.")

# %% [markdown]
# ---
# ## 5. Sensibilidad del PPV al FPR y Base Rate

# %%
fprs = np.arange(0.01, 0.35, 0.02)
base_rates_test = [0.05, 0.10, 0.15, 0.25]

fig, ax = plt.subplots(figsize=(10, 6))
for br in base_rates_test:
    ppvs = []
    for fpr in fprs:
        ppv_bayes = (0.85 * br) / (0.85 * br + fpr * (1 - br))
        ppvs.append(ppv_bayes)
    ax.plot(fprs * 100, np.array(ppvs) * 100, lw=2,
            label=f'Base rate = {br:.0%}', marker='o', ms=4)

ax.axhline(50, color='gray', ls=':', label='50% (moneda al aire)')
ax.set_xlabel('Tasa de Falsos Positivos (FPR) %')
ax.set_ylabel('Valor Predictivo Positivo (PPV) %')
ax.set_title('PPV vs FPR para diferentes base rates\n'
             '(Sensibilidad fija = 85%)', fontsize=13)
ax.legend(fontsize=10)
ax.set_ylim(0, 100)
plt.tight_layout()
plt.show()

print("Con base rate bajo (5%), incluso FPR de 5% da PPV de solo 47%!")
print("Conclusion: el base rate DOMINA la utilidad del indicador.")

# %% [markdown]
# ---
# ## 6. Resumen
#
# | Concepto | NHST dice | Realidad (Bayes) |
# |----------|----------|------------------|
# | Sensibilidad 85% | "El indicador acierta 85%" | PPV depende del base rate |
# | p-value < 0.05 | "Efecto significativo" | Ignora base rate y multiples tests |
# | IC 95% de beta | "Beta esta en este rango" | Solo si residuales son normales |
# | Alpha significativo | "Hay retorno excedente" | Diagnosticos de OLS invalidan |
#
# ### Framework de evaluacion
# 1. Calcula el **base rate** del evento
# 2. Construye la **confusion matrix** con datos historicos
# 3. Aplica **Bayes** para obtener PPV (no usar sensibilidad cruda)
# 4. Verifica **diagnosticos OLS** antes de confiar en p-values
# 5. Corrige por **multiple testing** si probaste multiples indicadores
#
# ---
# *source_ref: turn0browsertab744690698*
