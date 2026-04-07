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
# # Modulo 2C: Black-Scholes y la Trinidad de la Incertidumbre
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Implementar la formula de Black-Scholes y comprender sus 5 supuestos criticos
# 2. Demostrar con datos sinteticos por que cada supuesto falla en mercados reales
# 3. Clasificar fallas de BSM segun la trinidad de incertidumbre (aleatoria, epistemica, ontologica)
# 4. Comparar pricing BSM (Normal) vs pricing con colas pesadas (Student-t)
# 5. Construir una volatility smile sintetica que emerge de distribuciones no-gaussianas

# %% [markdown]
# ---
# ## 1. Setup e Importaciones

# %%
import numpy as np
from scipy import stats
from scipy.optimize import brentq
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
# ## 2. Black-Scholes: La Formula y sus Supuestos
#
# La formula de Black-Scholes para una opcion europea call:
#
# $$C = S \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)$$
#
# donde:
# - $d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$
# - $d_2 = d_1 - \sigma\sqrt{T}$
#
# **Supuestos criticos:**
# 1. Retornos log-normales (movimiento Browniano geometrico)
# 2. Volatilidad constante
# 3. Trading continuo sin costos
# 4. No hay saltos ni discontinuidades
# 5. Tasa libre de riesgo constante

# %%
def black_scholes_call(S: float, K: float, T: float, r: float,
                        sigma: float) -> float:
    """Precio de una opcion call europea usando Black-Scholes.

    Parametros
    ----------
    S : float
        Precio actual del activo subyacente.
    K : float
        Precio de ejercicio (strike).
    T : float
        Tiempo al vencimiento en anos.
    r : float
        Tasa libre de riesgo anualizada.
    sigma : float
        Volatilidad anualizada (constante bajo BSM).

    Retorna
    -------
    float : precio de la opcion call.
    """
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call = S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)
    return call


def black_scholes_put(S: float, K: float, T: float, r: float,
                       sigma: float) -> float:
    """Precio de una opcion put europea usando Black-Scholes.

    Usa paridad put-call: P = C - S + K*exp(-rT).
    """
    call = black_scholes_call(S, K, T, r, sigma)
    put = call - S + K * np.exp(-r * T)
    return put


# Ejemplo: Apple-like
S = 150.0   # Precio actual
K = 155.0   # Strike (ligeramente OTM)
T = 0.25    # 3 meses
r = 0.05    # 5% tasa libre de riesgo
sigma = 0.25  # 25% volatilidad anualizada

call_price = black_scholes_call(S, K, T, r, sigma)
put_price = black_scholes_put(S, K, T, r, sigma)

print("=== Black-Scholes Pricing ===")
print(f"Subyacente: ${S:.2f}")
print(f"Strike:     ${K:.2f}")
print(f"Vencimiento: {T:.2f} anos ({T*252:.0f} dias)")
print(f"Tasa:       {r:.1%}")
print(f"Volatilidad: {sigma:.1%}")
print(f"\nCall: ${call_price:.2f}")
print(f"Put:  ${put_price:.2f}")

# %% [markdown]
# ---
# ## 3. Falla #1 (Aleatoria): Retornos NO son Normales
#
# BSM asume retornos log-normales. En la realidad, los retornos
# financieros tienen **colas pesadas** (fat tails), es decir,
# eventos extremos son mucho mas frecuentes de lo que la Normal predice.

# %%
def generar_retornos_comparacion(n: int = 10000, mu: float = 0.0,
                                  sigma: float = 0.01, nu: float = 4):
    """Genera retornos con Normal y Student-t para comparacion.

    Parametros
    ----------
    n : int
        Numero de retornos.
    mu : float
        Media de los retornos.
    sigma : float
        Escala.
    nu : float
        Grados de libertad para Student-t (menor = colas mas pesadas).

    Retorna
    -------
    tuple : (retornos_normal, retornos_t)
    """
    retornos_normal = np.random.normal(mu, sigma, n)
    retornos_t = mu + sigma * np.random.standard_t(nu, size=n)
    return retornos_normal, retornos_t


retornos_n, retornos_t = generar_retornos_comparacion(n=50000)

# Estadisticas comparativas
print("=== Comparacion: Normal vs Student-t(nu=4) ===\n")
print(f"{'Metrica':<25} {'Normal':<15} {'Student-t(4)':<15} {'Diferencia'}")
print("-" * 65)

for nombre, func in [("Media", np.mean), ("Std", np.std)]:
    vn, vt = func(retornos_n), func(retornos_t)
    print(f"{nombre:<25} {vn:<15.6f} {vt:<15.6f} {(vt-vn)/max(abs(vn),1e-10):.1%}")

from scipy.stats import kurtosis, skew
kurt_n, kurt_t = kurtosis(retornos_n), kurtosis(retornos_t)
skew_n, skew_t = skew(retornos_n), skew(retornos_t)
print(f"{'Curtosis (exceso)':<25} {kurt_n:<15.2f} {kurt_t:<15.2f}")
print(f"{'Asimetria':<25} {skew_n:<15.3f} {skew_t:<15.3f}")

# Eventos extremos
umbral_3sigma = 3 * 0.01  # 3 desviaciones estandar
extremos_n = np.sum(np.abs(retornos_n) > umbral_3sigma)
extremos_t = np.sum(np.abs(retornos_t) > umbral_3sigma)
print(f"\n{'Eventos > 3 sigma':<25} {extremos_n:<15d} {extremos_t:<15d}")
print(f"{'Ratio extremos':<25} {'1.0x':<15} {extremos_t/max(extremos_n,1):<15.1f}x")

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel 1: Histogramas superpuestos
bins = np.linspace(-0.06, 0.06, 100)
axes[0].hist(retornos_n, bins=bins, density=True, alpha=0.5,
             color='steelblue', label='Normal (BSM asume)')
axes[0].hist(retornos_t, bins=bins, density=True, alpha=0.5,
             color='orangered', label='Student-t(4) (realidad)')
axes[0].set_title('Distribucion de Retornos: Normal vs Fat Tails', fontsize=13)
axes[0].set_xlabel('Retorno diario')
axes[0].set_ylabel('Densidad')
axes[0].legend()

# Panel 2: Zoom en las colas
axes[1].hist(retornos_n, bins=bins, density=True, alpha=0.5,
             color='steelblue', label='Normal')
axes[1].hist(retornos_t, bins=bins, density=True, alpha=0.5,
             color='orangered', label='Student-t(4)')
axes[1].set_xlim(-0.06, -0.02)
axes[1].set_title('Zoom en Cola Izquierda (riesgo extremo)', fontsize=13)
axes[1].set_xlabel('Retorno diario')
axes[1].set_ylabel('Densidad')
axes[1].legend()

plt.suptitle('Incertidumbre ALEATORIA: BSM subestima eventos extremos',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 4. Falla #2 (Epistemica): Volatilidad NO es Constante
#
# BSM asume una volatilidad sigma fija. En realidad, la volatilidad
# cambia con el tiempo y con la informacion disponible. Esta es
# **incertidumbre epistemica**: no sabemos el valor real de sigma.

# %%
def simular_volatilidad_cambiante(n_dias: int = 504, sigma_base: float = 0.15,
                                    regimenes: bool = True):
    """Simula retornos con volatilidad que cambia segun regimenes.

    Parametros
    ----------
    n_dias : int
        Numero de dias de trading.
    sigma_base : float
        Volatilidad anualizada base.
    regimenes : bool
        Si True, introduce cambios de regimen en volatilidad.

    Retorna
    -------
    tuple : (retornos, volatilidades_diarias)
    """
    sigma_diaria_base = sigma_base / np.sqrt(252)

    if regimenes:
        # 3 regimenes: calma, transicion, crisis
        sigmas = np.zeros(n_dias)
        sigmas[:250] = sigma_diaria_base * 0.8        # Calma
        sigmas[250:400] = sigma_diaria_base * 1.2      # Transicion
        sigmas[400:] = sigma_diaria_base * 2.5          # Crisis
        # Suavizar transiciones
        from scipy.ndimage import uniform_filter1d
        sigmas = uniform_filter1d(sigmas, size=20)
    else:
        sigmas = np.full(n_dias, sigma_diaria_base)

    retornos = np.random.normal(0, sigmas)
    return retornos, sigmas


ret_const, vol_const = simular_volatilidad_cambiante(regimenes=False)
ret_regim, vol_regim = simular_volatilidad_cambiante(regimenes=True)

fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# Volatilidad constante (BSM)
axes[0, 0].plot(vol_const * np.sqrt(252) * 100, color='steelblue', lw=1)
axes[0, 0].set_title('BSM: Volatilidad Constante', fontsize=12)
axes[0, 0].set_ylabel('Vol anualizada (%)')
axes[0, 0].set_ylim(0, 50)

axes[1, 0].plot(ret_const * 100, color='steelblue', alpha=0.7, lw=0.5)
axes[1, 0].set_title('Retornos bajo Vol Constante', fontsize=12)
axes[1, 0].set_ylabel('Retorno (%)')
axes[1, 0].set_xlabel('Dia')

# Volatilidad con regimenes (realidad)
axes[0, 1].plot(vol_regim * np.sqrt(252) * 100, color='orangered', lw=1)
axes[0, 1].set_title('Realidad: Volatilidad con Regimenes', fontsize=12)
axes[0, 1].set_ylim(0, 50)
axes[0, 1].axvspan(0, 250, alpha=0.1, color='green', label='Calma')
axes[0, 1].axvspan(250, 400, alpha=0.1, color='yellow', label='Transicion')
axes[0, 1].axvspan(400, 504, alpha=0.1, color='red', label='Crisis')
axes[0, 1].legend(fontsize=9)

axes[1, 1].plot(ret_regim * 100, color='orangered', alpha=0.7, lw=0.5)
axes[1, 1].set_title('Retornos bajo Regimenes', fontsize=12)
axes[1, 1].set_xlabel('Dia')

plt.suptitle('Incertidumbre EPISTEMICA: sigma NO es conocida ni constante',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 5. Falla #3 (Ontologica): Cambios Estructurales y Saltos
#
# BSM asume paths continuos (movimiento Browniano geometrico).
# En la realidad, los precios **saltan** (gaps, flash crashes) y
# las reglas del juego **cambian** (regulacion, crisis, pandemias).
# Esta es **incertidumbre ontologica**: el proceso generador de datos
# cambia sin previo aviso.

# %%
def simular_paths_con_saltos(S0: float = 100, T: float = 1.0,
                               n_pasos: int = 252, n_paths: int = 5,
                               mu: float = 0.08, sigma: float = 0.20,
                               saltos: bool = False,
                               lambda_salto: float = 0.02,
                               mu_salto: float = -0.05,
                               sigma_salto: float = 0.08):
    """Simula paths de precios con y sin saltos (jump-diffusion).

    Parametros
    ----------
    S0 : float
        Precio inicial.
    T : float
        Horizonte en anos.
    n_pasos : int
        Numero de pasos de tiempo.
    n_paths : int
        Numero de trayectorias.
    mu, sigma : float
        Drift y volatilidad del componente difusivo.
    saltos : bool
        Si True, agrega componente de saltos (Merton jump-diffusion).
    lambda_salto : float
        Frecuencia de saltos (Poisson).
    mu_salto, sigma_salto : float
        Media y std del tamano del salto (log-normal).

    Retorna
    -------
    np.ndarray : matriz (n_pasos+1, n_paths) con precios.
    """
    dt = T / n_pasos
    precios = np.zeros((n_pasos + 1, n_paths))
    precios[0] = S0

    for i in range(n_pasos):
        z = np.random.normal(0, 1, n_paths)
        # Componente difusivo (GBM)
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt) * z
        log_return = drift + diffusion

        if saltos:
            # Componente de saltos (Poisson + Normal)
            n_jumps = np.random.poisson(lambda_salto * dt, n_paths)
            jump_sizes = np.where(
                n_jumps > 0,
                np.random.normal(mu_salto, sigma_salto, n_paths) * n_jumps,
                0
            )
            log_return += jump_sizes

        precios[i + 1] = precios[i] * np.exp(log_return)

    return precios


np.random.seed(42)
paths_gbm = simular_paths_con_saltos(n_paths=8, saltos=False)
np.random.seed(42)
paths_jump = simular_paths_con_saltos(n_paths=8, saltos=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
dias = np.arange(paths_gbm.shape[0])

for i in range(paths_gbm.shape[1]):
    axes[0].plot(dias, paths_gbm[:, i], alpha=0.7, lw=1)
axes[0].set_title('BSM: Geometric Brownian Motion\n(paths continuos, sin saltos)', fontsize=12)
axes[0].set_xlabel('Dia')
axes[0].set_ylabel('Precio ($)')

for i in range(paths_jump.shape[1]):
    axes[1].plot(dias, paths_jump[:, i], alpha=0.7, lw=1)
axes[1].set_title('Realidad: Jump-Diffusion\n(saltos + cambios de regimen)', fontsize=12)
axes[1].set_xlabel('Dia')

plt.suptitle('Incertidumbre ONTOLOGICA: las reglas del juego cambian',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 6. Volatility Smile: La Prueba de que el Mercado Sabe que BSM esta Mal
#
# Si BSM fuera correcto, la volatilidad implicita seria la misma para
# todos los strikes. En la realidad, opciones deep OTM tienen volatilidad
# implicita mayor, formando una "sonrisa" o "smirk".

# %%
def implied_vol_bsm(precio_mercado: float, S: float, K: float, T: float,
                     r: float, tipo: str = 'call') -> float:
    """Calcula la volatilidad implicita de BSM por biseccion.

    Parametros
    ----------
    precio_mercado : float
        Precio observado de la opcion.
    S, K, T, r : float
        Parametros de la opcion.
    tipo : str
        'call' o 'put'.

    Retorna
    -------
    float : volatilidad implicita.
    """
    func_precio = black_scholes_call if tipo == 'call' else black_scholes_put

    def objetivo(sigma):
        return func_precio(S, K, T, r, sigma) - precio_mercado

    try:
        return brentq(objetivo, 0.001, 5.0, xtol=1e-6)
    except ValueError:
        return np.nan


def generar_smile_sintetico(S: float = 150, T: float = 0.25, r: float = 0.05,
                             sigma_base: float = 0.25, nu: float = 4,
                             n_sim: int = 100000):
    """Genera volatility smile sintetico usando MCS con Student-t.

    Precio las opciones con MCS fat-tailed, luego extraigo la vol implicita
    de BSM para cada strike. La diferencia revela el smile.

    Parametros
    ----------
    S : float
        Precio actual.
    T : float
        Tiempo al vencimiento.
    r : float
        Tasa libre de riesgo.
    sigma_base : float
        Volatilidad base anualizada.
    nu : float
        Grados de libertad de Student-t.
    n_sim : int
        Numero de simulaciones Monte Carlo.

    Retorna
    -------
    tuple : (strikes, iv_bsm, iv_mercado)
    """
    sigma_diaria = sigma_base / np.sqrt(252)
    n_dias = int(T * 252)

    # Simular precios finales con Student-t (fat tails)
    log_returns = np.zeros(n_sim)
    for _ in range(n_dias):
        log_returns += sigma_diaria * np.random.standard_t(nu, n_sim)
    S_T = S * np.exp((r - 0.5 * sigma_base**2) * T + log_returns)

    # Strikes: 80% a 120% del spot
    strikes = np.linspace(S * 0.80, S * 1.20, 25)
    iv_list = []

    for K in strikes:
        # Precio MCS (risk-neutral con fat tails)
        payoffs = np.maximum(S_T - K, 0)
        precio_mcs = np.exp(-r * T) * payoffs.mean()

        # Vol implicita de BSM para ese precio
        iv = implied_vol_bsm(precio_mcs, S, K, T, r, 'call')
        iv_list.append(iv)

    return strikes, np.full_like(strikes, sigma_base), np.array(iv_list)


strikes, iv_bsm, iv_mercado = generar_smile_sintetico()

fig, ax = plt.subplots(figsize=(10, 6))
moneyness = strikes / 150  # K/S

ax.plot(moneyness, iv_bsm * 100, 'steelblue', ls='--', lw=2,
        label='BSM (vol constante)')
valid = ~np.isnan(iv_mercado)
ax.plot(moneyness[valid], iv_mercado[valid] * 100, 'orangered', lw=2,
        marker='o', markersize=4, label='Mercado (fat tails)')

ax.axvline(1.0, color='gray', ls=':', alpha=0.5, label='ATM (K=S)')
ax.set_xlabel('Moneyness (K/S)', fontsize=12)
ax.set_ylabel('Volatilidad Implicita (%)', fontsize=12)
ax.set_title('Volatility Smile: BSM vs Mercado con Colas Pesadas', fontsize=14)
ax.legend(fontsize=11)

plt.tight_layout()
plt.show()

print("\nLa 'sonrisa' emerge porque el mercado asigna mayor probabilidad")
print("a eventos extremos de lo que BSM predice con su Normal.")
print("Deep OTM puts son mas caras -> proteccion contra crashes.")

# %% [markdown]
# ---
# ## 7. Impacto en Pricing: Cuanto se Equivoca BSM?

# %%
def comparar_pricing(S: float = 150, T: float = 0.25, r: float = 0.05,
                      sigma: float = 0.25, nu: float = 4, n_sim: int = 200000):
    """Compara pricing BSM vs MCS con colas pesadas para varios strikes.

    Retorna tabla con precios y diferencia porcentual.
    """
    sigma_diaria = sigma / np.sqrt(252)
    n_dias = int(T * 252)

    # Simular con Student-t
    log_ret = np.zeros(n_sim)
    for _ in range(n_dias):
        log_ret += sigma_diaria * np.random.standard_t(nu, n_sim)
    S_T = S * np.exp((r - 0.5 * sigma**2) * T + log_ret)

    # Strikes OTM a ITM
    strikes = [120, 130, 140, 145, 150, 155, 160, 170, 180]
    resultados = []

    for K in strikes:
        bsm_price = black_scholes_call(S, K, T, r, sigma)
        payoffs = np.maximum(S_T - K, 0)
        mcs_price = np.exp(-r * T) * payoffs.mean()
        diff_pct = (mcs_price - bsm_price) / max(bsm_price, 0.01) * 100

        moneyness = "ITM" if K < S else ("ATM" if K == S else "OTM")
        resultados.append({
            "K": K, "moneyness": moneyness,
            "bsm": bsm_price, "mcs_t": mcs_price, "diff": diff_pct,
        })

    return resultados


np.random.seed(42)
tabla = comparar_pricing()

print("=== Comparacion de Pricing: BSM vs MCS Student-t(4) ===\n")
print(f"{'Strike':<10} {'Tipo':<6} {'BSM ($)':<12} {'MCS-t ($)':<12} {'Diff (%)':<10}")
print("-" * 50)
for r in tabla:
    print(f"${r['K']:<9.0f} {r['moneyness']:<6} ${r['bsm']:<11.2f} "
          f"${r['mcs_t']:<11.2f} {r['diff']:>+8.1f}%")

print("\n--> BSM subprecia opciones deep OTM (colas pesadas)")
print("--> BSM sobreprecia ligeramente opciones deep ITM")

# %% [markdown]
# ---
# ## 8. Trinidad de la Incertidumbre: Resumen Aplicado
#
# | Tipo | Que ignora BSM | Solucion PML |
# |------|---------------|--------------|
# | **Aleatoria** | Colas pesadas en retornos | Distribuciones Student-t, mixtas |
# | **Epistemica** | Sigma es incierta, no fija | Tratar sigma como variable con distribucion |
# | **Ontologica** | Cambios de regimen, saltos | Stress testing, jump-diffusion, escenarios |
#
# ### Como el ML Probabilistico aborda cada tipo:
# - **Aleatoria**: usa distribuciones con colas pesadas como likelihood
# - **Epistemica**: pone priors sobre parametros y aprende posteriors
# - **Ontologica**: genera escenarios contrafactuales con MCS

# %%
# Resumen cuantitativo del impacto de cada tipo de incertidumbre
print("=== Impacto de Cada Tipo de Incertidumbre en Pricing ===\n")

# BSM baseline
S, K_otm, T, r, sigma = 150, 165, 0.25, 0.05, 0.25
bsm_base = black_scholes_call(S, K_otm, T, r, sigma)

# 1. Aleatoria: usar Student-t
sigma_d = sigma / np.sqrt(252)
n_dias = int(T * 252)
np.random.seed(42)
log_ret_t = np.zeros(100000)
for _ in range(n_dias):
    log_ret_t += sigma_d * np.random.standard_t(4, 100000)
S_T_t = S * np.exp((r - 0.5 * sigma**2) * T + log_ret_t)
precio_aleatoria = np.exp(-r * T) * np.maximum(S_T_t - K_otm, 0).mean()

# 2. Epistemica: sigma incierta (muestrear sigma de una distribucion)
np.random.seed(42)
precios_epistemica = []
for _ in range(1000):
    sigma_sample = np.random.normal(sigma, 0.05)  # incertidumbre en sigma
    sigma_sample = max(sigma_sample, 0.05)
    p = black_scholes_call(S, K_otm, T, r, sigma_sample)
    precios_epistemica.append(p)
precio_epistemica = np.mean(precios_epistemica)

# 3. Ontologica: salto de -15% con prob 3%
np.random.seed(42)
n_sim = 100000
log_ret_jump = np.zeros(n_sim)
for d in range(n_dias):
    z = np.random.normal(0, 1, n_sim)
    log_ret_jump += (r/252 - 0.5*sigma_d**2) + sigma_d * z
    # Salto
    jumps = np.random.binomial(1, 0.03/252, n_sim)
    log_ret_jump += jumps * np.random.normal(-0.15, 0.05, n_sim)
S_T_jump = S * np.exp(log_ret_jump)
precio_ontologica = np.exp(-r * T) * np.maximum(S_T_jump - K_otm, 0).mean()

print(f"Opcion: Call S={S}, K={K_otm} (OTM), T={T}\n")
print(f"{'Modelo':<30} {'Precio ($)':<12} {'vs BSM'}")
print("-" * 55)
print(f"{'BSM baseline':<30} ${bsm_base:<11.2f} {'---'}")
print(f"{'+ Aleatoria (Student-t)':<30} ${precio_aleatoria:<11.2f} "
      f"{(precio_aleatoria-bsm_base)/bsm_base:>+.1%}")
print(f"{'+ Epistemica (sigma incierta)':<30} ${precio_epistemica:<11.2f} "
      f"{(precio_epistemica-bsm_base)/bsm_base:>+.1%}")
print(f"{'+ Ontologica (jump-diffusion)':<30} ${precio_ontologica:<11.2f} "
      f"{(precio_ontologica-bsm_base)/bsm_base:>+.1%}")

print("\n--> Cada tipo de incertidumbre anade un 'colchon' al precio")
print("--> Ignorarlas = subpreciar sistematicamente el riesgo")

# %% [markdown]
# ---
# ## 9. Conclusiones Clave
#
# 1. **BSM no esta "mal"** -- es un benchmark util, pero sus supuestos son falsos
# 2. **Incertidumbre aleatoria**: retornos con colas pesadas generan el volatility smile
# 3. **Incertidumbre epistemica**: sigma incierta amplifica el error de pricing
# 4. **Incertidumbre ontologica**: saltos y cambios de regimen rompen el modelo
# 5. **El ML probabilistico** aborda las tres: distribuciones fat-tailed,
#    posteriors sobre parametros, y escenarios contrafactuales
#
# ### Siguiente: Modulo 3 -- Simulacion Monte Carlo para propagar incertidumbre
#
# ---
# *source_ref: turn0browsertab744690698*
