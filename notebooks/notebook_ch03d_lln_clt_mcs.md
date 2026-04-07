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
# # Modulo 3D: LGN, TLC y los Fundamentos de Monte Carlo
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Demostrar la LGN con convergencia del promedio muestral a E[X]
# 2. Verificar el TLC: medias muestrales son Normales para cualquier distribucion (con varianza finita)
# 3. Calcular intervalos de confianza para estimaciones MCS usando TLC
# 4. Medir la tasa de convergencia de MCS: error ~ 1/sqrt(N)
# 5. Identificar cuando TLC falla (Cauchy, dependencia, N pequeno)

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
# ## 2. Ley de Grandes Numeros: Convergencia del Promedio

# %%
def demo_lgn(distribucion, nombre, mu_real, n_max=10000, seed=42):
    """Demuestra convergencia del promedio muestral a E[X].

    Parametros
    ----------
    distribucion : callable
        Funcion que genera n muestras.
    nombre : str
        Nombre de la distribucion.
    mu_real : float
        Valor esperado teorico.
    n_max : int
        Numero maximo de muestras.
    seed : int
        Semilla aleatoria.
    """
    np.random.seed(seed)
    datos = distribucion(n_max)
    medias_acumuladas = np.cumsum(datos) / np.arange(1, n_max + 1)
    return medias_acumuladas, mu_real


# 4 distribuciones
distribuciones = [
    (lambda n: np.random.choice([1,2,3,4,5,6], n), "Dado justo", 3.5),
    (lambda n: np.random.binomial(1, 0.7, n).astype(float), "Moneda p=0.7", 0.7),
    (lambda n: np.random.exponential(2, n), "Exponencial(2)", 2.0),
    (lambda n: 0.01 * np.random.standard_t(4, n), "Student-t(4)", 0.0),
]

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
for idx, (dist, nombre, mu) in enumerate(distribuciones):
    ax = axes[idx // 2, idx % 2]
    medias, mu_real = demo_lgn(dist, nombre, mu)
    ns = np.arange(1, len(medias) + 1)

    ax.plot(ns, medias, 'steelblue', lw=1, alpha=0.8)
    ax.axhline(mu_real, color='red', ls='--', lw=1.5, label=f'E[X] = {mu_real}')
    # Bandas teoricas +/- 2/sqrt(n)
    if mu_real != 0:
        scale = abs(mu_real) * 0.5
    else:
        scale = 0.005
    ax.fill_between(ns, mu_real - 2*scale/np.sqrt(ns),
                    mu_real + 2*scale/np.sqrt(ns),
                    alpha=0.1, color='red')
    ax.set_title(f'{nombre}', fontsize=11)
    ax.set_xlabel('n')
    ax.set_ylabel('Media acumulada')
    ax.legend(fontsize=9)

plt.suptitle('LGN: el promedio muestral converge a E[X]',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. Tasa de Convergencia: Error ~ 1/sqrt(N)

# %%
def medir_convergencia(distribucion, mu_real, ns_list, n_rep=1000, seed=42):
    """Mide el error medio absoluto para diferentes tamanos de muestra.

    Retorna
    -------
    list[float] : error medio absoluto para cada n.
    """
    np.random.seed(seed)
    errores = []
    for n in ns_list:
        errs = []
        for _ in range(n_rep):
            muestra = distribucion(n)
            errs.append(abs(muestra.mean() - mu_real))
        errores.append(np.mean(errs))
    return errores


ns_list = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
errores = medir_convergencia(
    lambda n: np.random.exponential(2, n), 2.0, ns_list)

fig, ax = plt.subplots(figsize=(10, 5))
ax.loglog(ns_list, errores, 'orangered', marker='o', lw=2, label='Error medio observado')
# Linea teorica 1/sqrt(n)
c = errores[0] * np.sqrt(ns_list[0])
ax.loglog(ns_list, [c / np.sqrt(n) for n in ns_list], 'steelblue', ls='--',
          lw=1.5, label='Teorico: C/sqrt(N)')
ax.set_xlabel('N (tamano de muestra)')
ax.set_ylabel('Error medio absoluto')
ax.set_title('Tasa de convergencia: error ~ 1/sqrt(N)', fontsize=13)
ax.legend()
plt.tight_layout()
plt.show()

print("Para reducir el error a la mitad, necesitas 4x mas simulaciones.")
print("De 1% a 0.1% de error: 100x mas simulaciones.")

# %% [markdown]
# ---
# ## 4. Teorema del Limite Central: Medias Muestrales son Normales

# %%
def demo_tlc(distribucion, nombre, tamanos_muestra=None, n_rep=10000, seed=42):
    """Demuestra TLC: medias muestrales se vuelven Normales.

    Parametros
    ----------
    distribucion : callable
        Funcion que genera n muestras.
    nombre : str
        Nombre para el grafico.
    tamanos_muestra : list
        Tamanos n para calcular medias.
    n_rep : int
        Repeticiones por tamano.
    """
    if tamanos_muestra is None:
        tamanos_muestra = [1, 5, 20, 100]

    np.random.seed(seed)
    fig, axes = plt.subplots(1, len(tamanos_muestra), figsize=(4 * len(tamanos_muestra), 4))

    for i, n in enumerate(tamanos_muestra):
        medias = np.array([distribucion(n).mean() for _ in range(n_rep)])
        axes[i].hist(medias, bins=50, density=True, alpha=0.6, color='steelblue')
        # Normal de referencia
        x = np.linspace(medias.min(), medias.max(), 200)
        axes[i].plot(x, stats.norm.pdf(x, medias.mean(), medias.std()),
                     'orangered', lw=2, label='Normal ref')
        axes[i].set_title(f'n = {n}', fontsize=11)
        axes[i].legend(fontsize=8)

    axes[0].set_ylabel('Densidad')
    plt.suptitle(f'TLC con {nombre}: medias muestrales se vuelven Normales',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()


# Exponencial (muy asimetrica)
demo_tlc(lambda n: np.random.exponential(2, n), "Exponencial(2)")

# %%
# Student-t(3) (colas MUY pesadas, pero varianza finita)
demo_tlc(lambda n: np.random.standard_t(3, n), "Student-t(3)")

# %% [markdown]
# ### Contra-ejemplo: Cauchy (varianza infinita) -- TLC FALLA

# %%
demo_tlc(lambda n: np.random.standard_cauchy(n), "Cauchy (nu=1) -- TLC FALLA")
print("Con Cauchy (nu=1), la varianza es INFINITA.")
print("El TLC NO se cumple: las medias muestrales NO convergen a Normal.")
print("Esto demuestra que el TLC tiene CONDICIONES que deben verificarse.")

# %% [markdown]
# ---
# ## 5. Aplicacion: MCS con Intervalos de Confianza

# %%
def mcs_con_ic(n_sims_list=None, seed=42):
    """Estima P(perdida > 5%) con MCS y calcula IC para cada N.

    Retornos sinteticos tipo S&P con Student-t(4).
    """
    if n_sims_list is None:
        n_sims_list = [100, 500, 1000, 5000, 10000, 50000, 100000]

    np.random.seed(seed)
    # "Verdadero" con muchas simulaciones
    ret_grande = 0.0003 + 0.012 * np.random.standard_t(4, 1_000_000)
    p_real = (ret_grande < -0.05).mean()

    print(f"P(loss > 5%) 'real' (1M sims): {p_real:.4%}\n")
    print(f"{'N sims':<12} {'Estimacion':<15} {'IC 95%':<30} {'Ancho IC':<12} {'Contiene real?'}")
    print("-" * 80)

    for N in n_sims_list:
        np.random.seed(seed + N)
        ret = 0.0003 + 0.012 * np.random.standard_t(4, N)
        p_hat = (ret < -0.05).mean()
        se = np.sqrt(p_hat * (1 - p_hat) / N)
        lo = p_hat - 1.96 * se
        hi = p_hat + 1.96 * se
        ancho = hi - lo
        contiene = "SI" if lo <= p_real <= hi else "NO"
        print(f"{N:<12,d} {p_hat:<15.4%} ({lo:.4%}, {hi:.4%}){'':<5} "
              f"{ancho:<12.4%} {contiene}")

    return p_real


p_real = mcs_con_ic()
print(f"\n--> Con mas simulaciones: IC se estrecha")
print(f"--> TLC garantiza que el IC es valido")
print(f"--> Para precision de 0.1%: necesitas ~100,000 sims")

# %% [markdown]
# ---
# ## 6. Aplicacion Financiera: Pricing de Opcion por MCS

# %%
def pricing_call_mcs(S=100, K=105, T=0.25, r=0.05, sigma=0.25,
                      ns_list=None, seed=42):
    """Estima precio de call europea via MCS con diferentes N."""
    if ns_list is None:
        ns_list = [100, 1000, 10000, 100000]

    # BSM analitico (referencia)
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    bsm_price = S*stats.norm.cdf(d1) - K*np.exp(-r*T)*stats.norm.cdf(d2)

    print(f"Pricing Call: S={S}, K={K}, T={T}, r={r}, sigma={sigma}")
    print(f"BSM analitico: ${bsm_price:.4f}\n")
    print(f"{'N sims':<12} {'MCS Precio':<15} {'Error':<12} {'IC 95%':<25} {'Ancho IC'}")
    print("-" * 70)

    for N in ns_list:
        np.random.seed(seed)
        z = np.random.normal(0, 1, N)
        ST = S * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*z)
        payoffs = np.maximum(ST - K, 0)
        discounted = np.exp(-r*T) * payoffs
        precio = discounted.mean()
        se = discounted.std() / np.sqrt(N)
        lo = precio - 1.96 * se
        hi = precio + 1.96 * se
        error = abs(precio - bsm_price)
        print(f"{N:<12,d} ${precio:<14.4f} ${error:<11.4f} "
              f"(${lo:.4f}, ${hi:.4f})  ${hi-lo:.4f}")


pricing_call_mcs()

# %% [markdown]
# ---
# ## 7. Resumen
#
# | Teorema | Que garantiza | Condicion clave | Falla si... |
# |---------|--------------|-----------------|-------------|
# | **LGN** | Promedio converge a E[X] | E[X] existe | Cauchy (E[X] no existe) |
# | **TLC** | Error del promedio es Normal | Var(X) finita | Cauchy (varianza infinita) |
# | **MCS** | Estimacion correcta con IC | LGN + TLC | Violacion de supuestos |
#
# ### Takeaways
# 1. LGN: el promedio muestral converge al valor real
# 2. TLC: el error es Normal -> IC validos para MCS
# 3. Tasa: error ~ 1/sqrt(N) (para mitad de error: 4x sims)
# 4. Cauchy destruye TLC (varianza infinita)
# 5. MCS con IC = estimacion + medida de confianza
#
# ---
# *source_ref: turn0browsertab744690698*
