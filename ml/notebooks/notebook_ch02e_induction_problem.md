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
# # Modulo 2E: El Problema de la Induccion en Finanzas
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Entender el problema de la induccion de Hume y su impacto en modelos financieros
# 2. Simular el "pavo de Russell" con datos financieros sinteticos
# 3. Comparar fragilidad inductiva de modelos frecuentistas vs bayesianos
# 4. Implementar deteccion de cambio de regimen con ventana deslizante
# 5. Aplicar stress testing para cuantificar riesgo inductivo

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
    'figure.figsize': (10, 6),
    'font.size': 12,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

print("Entorno listo.")

# %% [markdown]
# ---
# ## 2. El Pavo de Russell: Simulacion Financiera
#
# Un fondo opera una estrategia que genera retornos estables...
# hasta que el regimen cambia y la estrategia colapsa.
# Esto es exactamente el problema de la induccion.

# %%
def simular_pavo_russell(n_calma: int = 500, n_crisis: int = 50,
                          mu_calma: float = 0.001,
                          sigma_calma: float = 0.005,
                          mu_crisis: float = -0.03,
                          sigma_crisis: float = 0.04,
                          seed: int = 42):
    """Simula el 'pavo de Russell' financiero.

    Un periodo largo de calma seguido de un colapso subito.

    Parametros
    ----------
    n_calma : int
        Dias de operacion estable.
    n_crisis : int
        Dias de crisis.
    mu_calma, sigma_calma : float
        Media y vol de retornos en calma.
    mu_crisis, sigma_crisis : float
        Media y vol de retornos en crisis.
    seed : int
        Semilla aleatoria.

    Retorna
    -------
    dict con retornos, precios, y punto de quiebre.
    """
    np.random.seed(seed)
    ret_calma = np.random.normal(mu_calma, sigma_calma, n_calma)
    ret_crisis = np.random.normal(mu_crisis, sigma_crisis, n_crisis)
    retornos = np.concatenate([ret_calma, ret_crisis])

    precios = 100 * np.exp(np.cumsum(retornos))

    return {
        "retornos": retornos,
        "precios": precios,
        "punto_quiebre": n_calma,
        "n_total": n_calma + n_crisis,
    }


pavo = simular_pavo_russell()

fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

# Precios
axes[0].plot(pavo["precios"], 'steelblue', lw=1.5)
axes[0].axvline(pavo["punto_quiebre"], color='red', ls='--', lw=1.5,
                label=f'Quiebre (dia {pavo["punto_quiebre"]})')
axes[0].set_ylabel('Precio ($)')
axes[0].set_title('El Pavo de Russell: estrategia "estable" que colapsa',
                   fontsize=13, fontweight='bold')
axes[0].legend()

# Retornos
axes[1].bar(range(len(pavo["retornos"])), pavo["retornos"] * 100,
            color=['steelblue' if i < pavo["punto_quiebre"] else 'orangered'
                   for i in range(len(pavo["retornos"]))],
            width=1, alpha=0.7)
axes[1].axvline(pavo["punto_quiebre"], color='red', ls='--', lw=1.5)
axes[1].set_xlabel('Dia')
axes[1].set_ylabel('Retorno (%)')

plt.tight_layout()
plt.show()

retorno_total = (pavo["precios"][-1] / pavo["precios"][0] - 1) * 100
retorno_pre = (pavo["precios"][pavo["punto_quiebre"]] / pavo["precios"][0] - 1) * 100
retorno_post = (pavo["precios"][-1] / pavo["precios"][pavo["punto_quiebre"]] - 1) * 100

print(f"Retorno pre-crisis:  {retorno_pre:+.1f}%  ({pavo['punto_quiebre']} dias)")
print(f"Retorno en crisis:   {retorno_post:+.1f}%  (50 dias)")
print(f"Retorno total:       {retorno_total:+.1f}%")
print(f"\n500 dias de evidencia 'confirmando' la estrategia.")
print(f"50 dias destruyen todo. Eso es induccion.")

# %% [markdown]
# ---
# ## 3. Confianza Acumulada: Frecuentista vs Bayesiano
#
# El modelo frecuentista gana confianza sin limite con mas datos.
# El bayesiano tiene confianza acotada por sus priors.

# %%
def confianza_frecuentista(retornos):
    """IC 95% acumulado para la media de retornos.

    El frecuentista estrecha el intervalo con 1/sqrt(n).
    """
    medias, ic_lo, ic_hi = [], [], []
    for n in range(2, len(retornos) + 1):
        sub = retornos[:n]
        mu = sub.mean()
        se = sub.std() / np.sqrt(n)
        medias.append(mu)
        ic_lo.append(mu - 1.96 * se)
        ic_hi.append(mu + 1.96 * se)
    return np.array(medias), np.array(ic_lo), np.array(ic_hi)


def confianza_bayesiana(retornos, mu_prior=0.0, sigma_prior=0.01,
                         sigma_likelihood=0.01):
    """Posterior acumulado Normal-Normal para la media de retornos.

    El prior pone un techo a la confianza.

    Parametros
    ----------
    retornos : array
        Retornos observados.
    mu_prior : float
        Media del prior.
    sigma_prior : float
        Incertidumbre del prior sobre mu.
    sigma_likelihood : float
        Sigma conocida del likelihood.

    Retorna
    -------
    tuple : (medias_post, hdi_lo, hdi_hi)
    """
    medias, hdi_lo, hdi_hi = [], [], []
    tau_prior = 1 / sigma_prior**2
    tau_like = 1 / sigma_likelihood**2

    for n in range(1, len(retornos) + 1):
        data_mean = retornos[:n].mean()
        tau_post = tau_prior + n * tau_like
        mu_post = (tau_prior * mu_prior + n * tau_like * data_mean) / tau_post
        sigma_post = 1 / np.sqrt(tau_post)

        medias.append(mu_post)
        hdi_lo.append(mu_post - 1.96 * sigma_post)
        hdi_hi.append(mu_post + 1.96 * sigma_post)

    return np.array(medias), np.array(hdi_lo), np.array(hdi_hi)


ret = pavo["retornos"]
mu_f, lo_f, hi_f = confianza_frecuentista(ret)
mu_b, lo_b, hi_b = confianza_bayesiana(ret, mu_prior=0.0,
                                         sigma_prior=0.005,
                                         sigma_likelihood=0.01)

fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Frecuentista
x_f = range(2, len(ret) + 1)
axes[0].plot(x_f, mu_f * 100, 'steelblue', lw=1.5, label='Media estimada')
axes[0].fill_between(x_f, lo_f * 100, hi_f * 100, alpha=0.2, color='steelblue',
                     label='IC 95%')
axes[0].axvline(pavo["punto_quiebre"], color='red', ls='--', lw=1.5)
axes[0].axhline(0, color='gray', ls=':', alpha=0.5)
axes[0].set_ylabel('Retorno medio (%)')
axes[0].set_title('Frecuentista: confianza crece sin limite (pavo mas gordo)',
                   fontsize=12)
axes[0].legend(fontsize=10)

# Bayesiano
x_b = range(1, len(ret) + 1)
axes[1].plot(x_b, mu_b * 100, 'orangered', lw=1.5, label='Media posterior')
axes[1].fill_between(x_b, lo_b * 100, hi_b * 100, alpha=0.2, color='orangered',
                     label='HDI 95%')
axes[1].axvline(pavo["punto_quiebre"], color='red', ls='--', lw=1.5)
axes[1].axhline(0, color='gray', ls=':', alpha=0.5)
axes[1].set_xlabel('Dia')
axes[1].set_ylabel('Retorno medio (%)')
axes[1].set_title('Bayesiano: prior acota la confianza, actualiza ante crisis',
                   fontsize=12)
axes[1].legend(fontsize=10)

plt.suptitle('Confianza Acumulada: Frecuentista vs Bayesiano',
             fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.show()

# Ancho del intervalo antes y despues de crisis
dia_pre = pavo["punto_quiebre"] - 2
dia_post = min(len(mu_f) - 1, pavo["punto_quiebre"] + 30)

print(f"\nAncho del intervalo en dia {dia_pre+2} (pre-crisis):")
print(f"  Frecuentista: {(hi_f[dia_pre] - lo_f[dia_pre])*100:.4f}%")
print(f"  Bayesiano:    {(hi_b[dia_pre] - lo_b[dia_pre])*100:.4f}%")
print(f"\nAncho del intervalo en dia {dia_post+2} (post-crisis):")
print(f"  Frecuentista: {(hi_f[dia_post] - lo_f[dia_post])*100:.4f}%")
print(f"  Bayesiano:    {(hi_b[dia_post] - lo_b[dia_post])*100:.4f}%")

# %% [markdown]
# ---
# ## 4. Deteccion de Cambio de Regimen (Ventana Deslizante)
#
# Una forma practica de detectar cuando la induccion esta fallando:
# monitorear estadisticas en una ventana deslizante y detectar
# cuando se desvian significativamente.

# %%
def detectar_cambio_regimen(retornos, ventana: int = 30,
                             umbral_zscore: float = 3.0):
    """Detecta cambio de regimen con ventana deslizante.

    Compara la media de la ventana reciente con la media historica.

    Parametros
    ----------
    retornos : array
        Serie de retornos.
    ventana : int
        Tamano de la ventana deslizante.
    umbral_zscore : float
        Umbral para declarar cambio de regimen.

    Retorna
    -------
    dict con z-scores y punto de deteccion.
    """
    z_scores = np.full(len(retornos), np.nan)
    deteccion = None

    for i in range(ventana * 2, len(retornos)):
        # Historico: todo antes de la ventana actual
        historico = retornos[:i - ventana]
        reciente = retornos[i - ventana:i]

        mu_hist = historico.mean()
        sigma_hist = historico.std()

        if sigma_hist > 0:
            z = (reciente.mean() - mu_hist) / (sigma_hist / np.sqrt(ventana))
            z_scores[i] = z

            if deteccion is None and abs(z) > umbral_zscore:
                deteccion = i

    return {"z_scores": z_scores, "deteccion": deteccion}


det = detectar_cambio_regimen(pavo["retornos"], ventana=20, umbral_zscore=3.0)

fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

axes[0].plot(pavo["precios"], 'steelblue', lw=1.5)
axes[0].axvline(pavo["punto_quiebre"], color='red', ls='--', label='Quiebre real')
if det["deteccion"]:
    axes[0].axvline(det["deteccion"], color='orange', ls='--',
                    label=f'Deteccion (dia {det["deteccion"]})')
axes[0].set_ylabel('Precio ($)')
axes[0].set_title('Precio y deteccion de cambio de regimen', fontsize=12)
axes[0].legend()

axes[1].plot(det["z_scores"], 'steelblue', lw=1)
axes[1].axhline(3, color='red', ls=':', label='Umbral +3')
axes[1].axhline(-3, color='red', ls=':')
axes[1].axvline(pavo["punto_quiebre"], color='red', ls='--')
if det["deteccion"]:
    axes[1].axvline(det["deteccion"], color='orange', ls='--')
axes[1].set_xlabel('Dia')
axes[1].set_ylabel('Z-score')
axes[1].set_title('Z-score de la ventana deslizante', fontsize=12)
axes[1].legend()

plt.tight_layout()
plt.show()

if det["deteccion"]:
    retraso = det["deteccion"] - pavo["punto_quiebre"]
    print(f"Quiebre real: dia {pavo['punto_quiebre']}")
    print(f"Deteccion:    dia {det['deteccion']} (retraso: {retraso} dias)")
    print(f"\nEl detector NO previene la crisis -- la DETECTA despues.")
    print(f"Pero {retraso} dias de retraso es mejor que nunca detectar.")
else:
    print("No se detecto cambio de regimen (umbral muy alto?)")

# %% [markdown]
# ---
# ## 5. Stress Testing: Cuantificar el Riesgo Inductivo
#
# Si la induccion puede fallar, debemos cuantificar CUANTO perderiamos
# si falla. Esto es stress testing inductivo.

# %%
def stress_test_inductivo(retornos_calma, capital: float = 1_000_000,
                           escenarios_crisis=None, n_sim: int = 10000):
    """Cuantifica perdidas bajo diferentes escenarios de falla inductiva.

    Parametros
    ----------
    retornos_calma : array
        Retornos observados en periodo de calma.
    capital : float
        Capital invertido.
    escenarios_crisis : list[dict]
        Lista de escenarios con mu_crisis y sigma_crisis.
    n_sim : int
        Simulaciones por escenario.

    Retorna
    -------
    list[dict] con resultados por escenario.
    """
    if escenarios_crisis is None:
        escenarios_crisis = [
            {"nombre": "Crisis leve", "mu": -0.01, "sigma": 0.02, "dias": 30},
            {"nombre": "Crisis moderada", "mu": -0.03, "sigma": 0.04, "dias": 30},
            {"nombre": "Crisis severa", "mu": -0.05, "sigma": 0.06, "dias": 30},
            {"nombre": "Cisne negro", "mu": -0.08, "sigma": 0.10, "dias": 10},
        ]

    resultados = []
    for esc in escenarios_crisis:
        perdidas = []
        for _ in range(n_sim):
            ret_crisis = np.random.normal(esc["mu"], esc["sigma"], esc["dias"])
            valor_final = capital * np.exp(np.sum(ret_crisis))
            perdida = capital - valor_final
            perdidas.append(perdida)

        perdidas = np.array(perdidas)
        resultados.append({
            "nombre": esc["nombre"],
            "perdida_media": perdidas.mean(),
            "perdida_p95": np.percentile(perdidas, 95),
            "perdida_max": perdidas.max(),
            "prob_ruina_50pct": (perdidas > capital * 0.5).mean(),
        })

    return resultados


np.random.seed(42)
ret_calma = pavo["retornos"][:pavo["punto_quiebre"]]
stress = stress_test_inductivo(ret_calma)

print("=== STRESS TEST INDUCTIVO ===")
print(f"Capital: $1,000,000\n")
print(f"{'Escenario':<20} {'Perdida Media':<16} {'Perdida P95':<16} "
      f"{'Perdida Max':<16} {'P(ruina>50%)'}")
print("-" * 80)
for s in stress:
    print(f"{s['nombre']:<20} ${s['perdida_media']:>12,.0f} "
          f"${s['perdida_p95']:>12,.0f} ${s['perdida_max']:>12,.0f} "
          f"{s['prob_ruina_50pct']:>10.1%}")

print(f"\n--> El stress test cuantifica lo que la induccion ignora")
print(f"--> 'Cisne negro' tiene {stress[-1]['prob_ruina_50pct']:.0%} prob de perder >50% del capital")
print(f"--> Ningun modelo inductivo te protege -- solo la preparacion")

# %% [markdown]
# ---
# ## 6. Falsacionismo Aplicado: Test de Hipotesis Invertido
#
# Popper dice: busca refutar, no confirmar. Aplicamos esto a
# una estrategia de trading.

# %%
def test_falsacionista(retornos, hipotesis_mu: float = 0.0,
                        ventana: int = 50, alpha: float = 0.05):
    """Test falsacionista: busca evidencia CONTRA la hipotesis.

    En vez de preguntar 'funciona mi estrategia?', pregunta
    'hay evidencia de que mi estrategia NO funciona?'

    Parametros
    ----------
    retornos : array
        Retornos de la estrategia.
    hipotesis_mu : float
        Retorno medio bajo hipotesis nula (0 = no hay alpha).
    ventana : int
        Tamano de ventana para test.
    alpha : float
        Nivel de significancia.

    Retorna
    -------
    dict con resultados del test.
    """
    n_ventanas = len(retornos) // ventana
    refutaciones = 0
    p_values = []

    for i in range(n_ventanas):
        sub = retornos[i * ventana:(i + 1) * ventana]
        # Test t: la media es significativamente diferente de hipotesis_mu?
        t_stat, p_val = stats.ttest_1samp(sub, hipotesis_mu)
        p_values.append(p_val)
        if p_val < alpha and sub.mean() < hipotesis_mu:
            refutaciones += 1

    return {
        "n_ventanas": n_ventanas,
        "refutaciones": refutaciones,
        "p_values": p_values,
        "tasa_refutacion": refutaciones / max(n_ventanas, 1),
    }


# Testar la estrategia del pavo
ret_total = pavo["retornos"]
resultado = test_falsacionista(ret_total, hipotesis_mu=0.0, ventana=50)

print("=== TEST FALSACIONISTA ===")
print(f"Hipotesis: 'La estrategia genera retorno >= 0'")
print(f"Ventanas de {50} dias: {resultado['n_ventanas']}")
print(f"Refutaciones: {resultado['refutaciones']}")
print(f"Tasa de refutacion: {resultado['tasa_refutacion']:.0%}")
print(f"\np-values por ventana:")
for i, pv in enumerate(resultado['p_values']):
    estado = "REFUTA" if pv < 0.05 and ret_total[i*50:(i+1)*50].mean() < 0 else "no refuta"
    print(f"  Ventana {i+1} (dias {i*50+1}-{(i+1)*50}): p={pv:.4f} -> {estado}")

# %% [markdown]
# ---
# ## 7. Resumen y Conclusiones
#
# | Concepto | Implicacion en finanzas |
# |----------|----------------------|
# | **Hume (induccion)** | El pasado no garantiza el futuro |
# | **Popper (falsacion)** | Busca refutar tu estrategia, no confirmarla |
# | **Pavo de Russell** | Exito pasado aumenta la fragilidad, no la seguridad |
# | **Cisnes negros** | Modelos frecuentistas asignan P~0 a lo inevitable |
# | **PML** | Cuantifica incertidumbre sobre los propios supuestos |
#
# ### Takeaways
# 1. La induccion es necesaria pero NO suficiente para invertir
# 2. Mas datos historicos = mas confianza PERO tambien mas fragilidad
# 3. PML: priors escepticos + actualizacion continua + stress testing
# 4. Popper: busca REFUTAR tu estrategia, no acumular confirmaciones
# 5. El riesgo inductivo se CUANTIFICA con stress testing, no se ignora
#
# ---
# *source_ref: turn0browsertab744690698*
#
# **Siguiente**: Modulo 3 -- Simulacion Monte Carlo
