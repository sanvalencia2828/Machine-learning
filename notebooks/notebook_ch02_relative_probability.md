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
# # Modulo 2B: Probabilidades Relativas y Critica a Riesgo vs Incertidumbre
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Entender que toda probabilidad es condicional: P(A) = P(A|I)
# 2. Criticar la distincion clasica de Knight entre riesgo e incertidumbre
# 3. Comparar la interpretacion frecuentista vs epistemica con ejemplos financieros
# 4. Implementar actualizacion bayesiana para demostrar probabilidades relativas
# 5. Cuantificar incertidumbre en decisiones de portafolio

# %% [markdown]
# ---
# ## 1. Setup e Importaciones

# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# Estilo para graficos
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'font.size': 12,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

print("Entorno listo. NumPy:", np.__version__)

# %% [markdown]
# ---
# ## 2. Probabilidad Relativa: Todo es Condicional
#
# La notacion P(A) es una abreviacion. La forma completa es **P(A|I)**,
# donde I representa toda la informacion de fondo que asumimos.
#
# No existe probabilidad "absoluta" — siempre depende del contexto informacional.

# %%
def probabilidad_dado(n_caras: int, cargado: bool = False, cara_favorecida: int = 6):
    """Demuestra como P(resultado) cambia segun la informacion disponible.

    Parametros
    ----------
    n_caras : int
        Numero de caras del dado.
    cargado : bool
        Si True, el dado esta cargado.
    cara_favorecida : int
        Cara que tiene mayor probabilidad si esta cargado.

    Retorna
    -------
    dict : probabilidades para cada cara
    """
    if cargado:
        # Dado cargado: la cara favorecida tiene el doble de probabilidad
        probs = np.ones(n_caras)
        probs[cara_favorecida - 1] = 2.0
        probs /= probs.sum()
    else:
        probs = np.ones(n_caras) / n_caras

    return {i + 1: round(p, 4) for i, p in enumerate(probs)}


# Informacion I1: "Es un dado justo de 6 caras"
p_i1 = probabilidad_dado(6, cargado=False)
print("I1 (dado justo):  ", p_i1)

# Informacion I2: "Es un dado cargado que favorece al 6"
p_i2 = probabilidad_dado(6, cargado=True, cara_favorecida=6)
print("I2 (dado cargado):", p_i2)

# Informacion I3: "Ya se lanzo y salio 6"
print("I3 (ya salio 6):   P(6|I3) = 1.0")

print("\nMisma pregunta, diferente informacion, diferente probabilidad.")

# %% [markdown]
# ### Visualizacion: Probabilidad condicional a informacion

# %%
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
caras = list(range(1, 7))

# I1: Dado justo
axes[0].bar(caras, [1/6]*6, color='steelblue', alpha=0.8, edgecolor='black')
axes[0].set_title("I₁: Dado justo\nP(k|I₁) = 1/6", fontsize=13)
axes[0].set_xlabel("Cara")
axes[0].set_ylabel("Probabilidad")
axes[0].set_ylim(0, 1.1)

# I2: Dado cargado
probs_cargado = [1/7]*5 + [2/7]
axes[1].bar(caras, probs_cargado, color='orangered', alpha=0.8, edgecolor='black')
axes[1].set_title("I₂: Dado cargado\nP(6|I₂) = 2/7", fontsize=13)
axes[1].set_xlabel("Cara")

# I3: Ya salio 6
probs_conocido = [0]*5 + [1]
axes[2].bar(caras, probs_conocido, color='forestgreen', alpha=0.8, edgecolor='black')
axes[2].set_title("I₃: Ya salio 6\nP(6|I₃) = 1.0", fontsize=13)
axes[2].set_xlabel("Cara")

plt.suptitle("Probabilidad Relativa: misma pregunta, diferente informacion",
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. Critica a la Distincion Riesgo vs Incertidumbre de Knight
#
# Frank Knight (1921) propuso:
# - **Riesgo**: probabilidades conocidas y medibles
# - **Incertidumbre**: probabilidades desconocidas o no medibles
#
# El libro argumenta que esta distincion es **inutil en la practica financiera**
# porque toda probabilidad depende de la informacion disponible.

# %%
def clasificacion_knight():
    """Muestra ejemplos clasicos y por que la frontera es difusa."""
    ejemplos = {
        "Lanzar un dado":        {"knight": "Riesgo",        "por_que_falla": "¿Como sabes que es justo? Lo MEDISTE → epistemico"},
        "Ruleta de casino":      {"knight": "Riesgo",        "por_que_falla": "El casino verifica la rueda. Sin verificacion → incertidumbre"},
        "Retorno S&P 500":      {"knight": "Riesgo",        "por_que_falla": "Asumes estacionariedad. Si cambia el regimen → incertidumbre"},
        "Proxima recesion":      {"knight": "Incertidumbre", "por_que_falla": "Los bonos del tesoro la estiman diariamente con precios"},
        "Fed sube tasas":        {"knight": "Incertidumbre", "por_que_falla": "CME FedWatch da probabilidades en tiempo real"},
        "Pandemia global":       {"knight": "Incertidumbre", "por_que_falla": "Actuarios de seguros asignan probabilidades a pandemias"},
    }

    print(f"{'Evento':<25} {'Knight dice':<15} {'Por que falla la clasificacion'}")
    print("-" * 90)
    for evento, info in ejemplos.items():
        print(f"{evento:<25} {info['knight']:<15} {info['por_que_falla']}")


clasificacion_knight()

# %% [markdown]
# ### Conclusion clave
#
# La frontera entre "riesgo" y "incertidumbre" depende de cuanta informacion
# tengas. Con mas datos o mejor modelado, la "incertidumbre" se convierte en
# "riesgo". La distincion no es una propiedad del mundo — es una propiedad
# de tu **conocimiento**.

# %% [markdown]
# ---
# ## 4. Frecuentista vs Epistemico: Dos Paradigmas

# %%
def demo_frecuentista_vs_epistemico(n_lanzamientos: int = 50, p_real: float = 0.7):
    """Compara inferencia frecuentista y epistemica para estimar sesgo de moneda.

    Parametros
    ----------
    n_lanzamientos : int
        Numero de lanzamientos simulados.
    p_real : float
        Probabilidad real de cara (desconocida para el observador).

    Retorna
    -------
    dict con resultados de ambos enfoques.
    """
    # Generar datos
    datos = np.random.binomial(1, p_real, n_lanzamientos)
    caras = datos.sum()
    n = len(datos)

    # --- Enfoque frecuentista ---
    p_hat = caras / n  # MLE
    se = np.sqrt(p_hat * (1 - p_hat) / n)  # Error estandar
    ic_95 = (p_hat - 1.96 * se, p_hat + 1.96 * se)

    # --- Enfoque epistemico (Beta-Binomial) ---
    # Prior: Beta(2, 2) — leve preferencia por 0.5, pero flexible
    alpha_prior, beta_prior = 2, 2
    alpha_post = alpha_prior + caras
    beta_post = beta_prior + (n - caras)

    posterior = stats.beta(alpha_post, beta_post)
    hdi_95 = posterior.ppf([0.025, 0.975])
    media_post = posterior.mean()

    return {
        "datos": datos,
        "n": n,
        "caras": caras,
        "p_real": p_real,
        # Frecuentista
        "p_hat": p_hat,
        "ic_95": ic_95,
        # Epistemico
        "alpha_post": alpha_post,
        "beta_post": beta_post,
        "media_post": media_post,
        "hdi_95": hdi_95,
        "posterior": posterior,
    }


# Ejecutar con pocos datos para ver la diferencia
resultado = demo_frecuentista_vs_epistemico(n_lanzamientos=15, p_real=0.7)

print(f"Datos: {resultado['caras']} caras en {resultado['n']} lanzamientos")
print(f"\n--- Frecuentista (MLE) ---")
print(f"  p_hat = {resultado['p_hat']:.3f}")
print(f"  IC 95%: ({resultado['ic_95'][0]:.3f}, {resultado['ic_95'][1]:.3f})")
print(f"  Interpretacion: 'Si repito el experimento infinitas veces,")
print(f"   el 95% de los intervalos contendran el valor real.'")

print(f"\n--- Epistemico (Beta-Binomial) ---")
print(f"  Media posterior = {resultado['media_post']:.3f}")
print(f"  HDI 95%: ({resultado['hdi_95'][0]:.3f}, {resultado['hdi_95'][1]:.3f})")
print(f"  Interpretacion: 'Hay 95% de probabilidad de que p este en este intervalo.'")

print(f"\nValor real: {resultado['p_real']}")

# %% [markdown]
# ### Visualizacion: Frecuentista vs Epistemico

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
r = resultado

# Panel 1: IC Frecuentista
x_freq = np.linspace(0, 1, 200)
# El frecuentista no tiene distribucion del parametro — solo el punto y el intervalo
axes[0].axvline(r['p_hat'], color='steelblue', lw=2, label=f"MLE: {r['p_hat']:.3f}")
axes[0].axvspan(r['ic_95'][0], r['ic_95'][1], alpha=0.2, color='steelblue',
                label=f"IC 95%: ({r['ic_95'][0]:.3f}, {r['ic_95'][1]:.3f})")
axes[0].axvline(r['p_real'], color='red', ls='--', lw=1.5, label=f"Valor real: {r['p_real']}")
axes[0].set_title("Frecuentista: Estimacion puntual + IC", fontsize=13)
axes[0].set_xlabel("p (probabilidad de cara)")
axes[0].legend(loc='upper left', fontsize=10)
axes[0].set_xlim(0, 1)

# Panel 2: Distribucion posterior epistemica
x_bayes = np.linspace(0, 1, 200)
y_bayes = r['posterior'].pdf(x_bayes)

# Prior
prior = stats.beta(2, 2)
y_prior = prior.pdf(x_bayes)

axes[1].plot(x_bayes, y_prior, 'gray', ls='--', lw=1.5, label="Prior Beta(2,2)")
axes[1].plot(x_bayes, y_bayes, 'orangered', lw=2,
             label=f"Posterior Beta({r['alpha_post']},{r['beta_post']})")
axes[1].fill_between(x_bayes, y_bayes,
                     where=(x_bayes >= r['hdi_95'][0]) & (x_bayes <= r['hdi_95'][1]),
                     alpha=0.3, color='orangered',
                     label=f"HDI 95%: ({r['hdi_95'][0]:.3f}, {r['hdi_95'][1]:.3f})")
axes[1].axvline(r['p_real'], color='red', ls='--', lw=1.5, label=f"Valor real: {r['p_real']}")
axes[1].set_title("Epistemico: Distribucion posterior completa", fontsize=13)
axes[1].set_xlabel("p (probabilidad de cara)")
axes[1].set_ylabel("Densidad")
axes[1].legend(loc='upper left', fontsize=9)
axes[1].set_xlim(0, 1)

plt.suptitle(f"Comparacion con n={r['n']} observaciones ({r['caras']} caras)",
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 5. Actualizacion Secuencial: La Probabilidad Aprende

# %%
def actualizacion_secuencial(datos: np.ndarray, alpha_prior: float = 2,
                              beta_prior: float = 2):
    """Actualiza la distribucion posterior dato por dato.

    Retorna lista de (alpha, beta) en cada paso.
    """
    trayectoria = [(alpha_prior, beta_prior)]
    a, b = alpha_prior, beta_prior

    for x in datos:
        a += x        # cara: incrementa alpha
        b += (1 - x)  # cruz: incrementa beta
        trayectoria.append((a, b))

    return trayectoria


# Generar 100 lanzamientos de moneda sesgada
np.random.seed(123)
p_real = 0.65
datos_secuencial = np.random.binomial(1, p_real, 100)

trayectoria = actualizacion_secuencial(datos_secuencial, alpha_prior=2, beta_prior=2)

# Graficar la evolucion de la media y HDI
medias = [a / (a + b) for a, b in trayectoria]
hdi_low = [stats.beta(a, b).ppf(0.025) for a, b in trayectoria]
hdi_high = [stats.beta(a, b).ppf(0.975) for a, b in trayectoria]
pasos = range(len(trayectoria))

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(pasos, medias, 'orangered', lw=2, label='Media posterior')
ax.fill_between(pasos, hdi_low, hdi_high, alpha=0.2, color='orangered', label='HDI 95%')
ax.axhline(p_real, color='red', ls='--', lw=1.5, label=f'Valor real: {p_real}')
ax.set_xlabel('Numero de observaciones')
ax.set_ylabel('P(cara)')
ax.set_title('Actualizacion Secuencial: el modelo aprende con cada dato', fontsize=13)
ax.legend(loc='upper right')
ax.set_ylim(0, 1)
plt.tight_layout()
plt.show()

print(f"\nCon 0 datos:   HDI = ({hdi_low[0]:.3f}, {hdi_high[0]:.3f}) — ancho: {hdi_high[0]-hdi_low[0]:.3f}")
print(f"Con 10 datos:  HDI = ({hdi_low[10]:.3f}, {hdi_high[10]:.3f}) — ancho: {hdi_high[10]-hdi_low[10]:.3f}")
print(f"Con 50 datos:  HDI = ({hdi_low[50]:.3f}, {hdi_high[50]:.3f}) — ancho: {hdi_high[50]-hdi_low[50]:.3f}")
print(f"Con 100 datos: HDI = ({hdi_low[100]:.3f}, {hdi_high[100]:.3f}) — ancho: {hdi_high[100]-hdi_low[100]:.3f}")
print("\n→ Mas informacion = intervalos mas estrechos = menor incertidumbre")

# %% [markdown]
# ---
# ## 6. Aplicacion Financiera: Portafolio bajo los Dos Paradigmas
#
# Simulamos retornos de un activo con colas pesadas (Student-t)
# y comparamos las decisiones de portafolio que tomaria un
# frecuentista vs un epistemico.

# %%
def simular_retornos_fat_tail(n: int = 252, mu: float = 0.0005,
                               sigma: float = 0.015, nu: float = 4):
    """Genera retornos diarios con colas pesadas (Student-t).

    Parametros
    ----------
    n : int
        Numero de dias.
    mu : float
        Retorno medio diario.
    sigma : float
        Escala de los retornos.
    nu : float
        Grados de libertad (menor = colas mas pesadas).

    Retorna
    -------
    np.ndarray : retornos diarios simulados.
    """
    retornos = mu + sigma * np.random.standard_t(nu, size=n)
    return retornos


# Generar 1 año de retornos
retornos = simular_retornos_fat_tail(n=252, mu=0.0005, sigma=0.015, nu=4)

# --- Enfoque frecuentista: asume normalidad ---
mu_freq = retornos.mean()
sigma_freq = retornos.std()
var_95_freq = mu_freq - 1.645 * sigma_freq  # VaR parametrico normal

# --- Enfoque epistemico: usa distribucion completa ---
# Ajustar Student-t a los datos (estima nu, mu, sigma)
nu_fit, mu_fit, sigma_fit = stats.t.fit(retornos)
var_95_epist = stats.t.ppf(0.05, nu_fit, mu_fit, sigma_fit)

# Expected Shortfall
n_sim = 50_000
sim_freq = np.random.normal(mu_freq, sigma_freq, n_sim)
sim_epist = stats.t.rvs(nu_fit, mu_fit, sigma_fit, size=n_sim)

es_freq = sim_freq[sim_freq <= np.percentile(sim_freq, 5)].mean()
es_epist = sim_epist[sim_epist <= np.percentile(sim_epist, 5)].mean()

print("=== Comparacion de Riesgo: Frecuentista vs Epistemico ===\n")
print(f"{'Metrica':<30} {'Frecuentista (Normal)':<25} {'Epistemico (Student-t)'}")
print("-" * 80)
print(f"{'Media diaria':<30} {mu_freq:>20.5f}     {mu_fit:>20.5f}")
print(f"{'Volatilidad diaria':<30} {sigma_freq:>20.5f}     {sigma_fit:>20.5f}")
print(f"{'VaR 95% diario':<30} {var_95_freq:>20.5f}     {var_95_epist:>20.5f}")
print(f"{'Expected Shortfall 95%':<30} {es_freq:>20.5f}     {es_epist:>20.5f}")
print(f"{'nu (grados libertad)':<30} {'∞ (asumido)':>20}     {nu_fit:>20.2f}")

diferencia_var = (var_95_epist - var_95_freq) / abs(var_95_freq) * 100
print(f"\n→ El VaR epistemico es {abs(diferencia_var):.1f}% {'peor' if diferencia_var < 0 else 'mejor'} que el frecuentista")
print("→ El frecuentista SUBESTIMA el riesgo de cola")

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

x_range = np.linspace(retornos.min() * 1.5, retornos.max() * 1.5, 300)

# Panel 1: Densidades
pdf_norm = stats.norm.pdf(x_range, mu_freq, sigma_freq)
pdf_t = stats.t.pdf(x_range, nu_fit, mu_fit, sigma_fit)

axes[0].hist(retornos, bins=40, density=True, alpha=0.3, color='gray', label='Datos reales')
axes[0].plot(x_range, pdf_norm, 'steelblue', lw=2, label=f'Normal (freq)')
axes[0].plot(x_range, pdf_t, 'orangered', lw=2, label=f'Student-t (epist, ν={nu_fit:.1f})')
axes[0].axvline(var_95_freq, color='steelblue', ls='--', lw=1.5, label=f'VaR freq: {var_95_freq:.4f}')
axes[0].axvline(var_95_epist, color='orangered', ls='--', lw=1.5, label=f'VaR epist: {var_95_epist:.4f}')
axes[0].set_title('Distribucion de Retornos: Normal vs Student-t', fontsize=13)
axes[0].set_xlabel('Retorno diario')
axes[0].set_ylabel('Densidad')
axes[0].legend(fontsize=9)

# Panel 2: QQ-plot
from scipy.stats import probplot
probplot(retornos, dist='norm', plot=axes[1])
axes[1].set_title('QQ-Plot: Retornos vs Normal', fontsize=13)
axes[1].get_lines()[0].set_markerfacecolor('orangered')
axes[1].get_lines()[0].set_markersize(4)

plt.suptitle('Frecuentista (Normal) vs Epistemico (Student-t)',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 7. El Espectro Riesgo-Incertidumbre: Una Vision Unificada
#
# En lugar de la dicotomia riesgo/incertidumbre de Knight, usamos un
# **espectro continuo** donde la posicion depende de la calidad de tu
# modelo y la cantidad de informacion disponible.

# %%
eventos_espectro = [
    ("Ruleta de casino\n(probabilidades calibradas)",                  0.95),
    ("Retorno S&P 500 mañana\n(1+ siglo de datos)",                   0.75),
    ("Fed sube tasas\n(CME FedWatch + comunicados)",                   0.60),
    ("Default de bonos AA\n(agencias de rating)",                      0.50),
    ("Recesion en 12 meses\n(indicadores macro)",                     0.35),
    ("Impacto de nueva regulacion\n(precedentes parciales)",           0.20),
    ("Cisne negro: pandemia/guerra\n(sin precedente directo)",         0.05),
]

fig, ax = plt.subplots(figsize=(12, 6))
nombres = [e[0] for e in eventos_espectro]
valores = [e[1] for e in eventos_espectro]
colores = plt.cm.RdYlGn(valores)

bars = ax.barh(range(len(nombres)), valores, color=colores, edgecolor='black', alpha=0.85)
ax.set_yticks(range(len(nombres)))
ax.set_yticklabels(nombres, fontsize=10)
ax.set_xlabel("Confianza en la estimacion de probabilidad", fontsize=12)
ax.set_title("Espectro Continuo: No hay frontera fija entre riesgo e incertidumbre",
             fontsize=13, fontweight='bold')
ax.set_xlim(0, 1)

# Anotaciones
ax.axvline(0.5, color='gray', ls=':', alpha=0.5)
ax.text(0.02, -0.8, '← Mayor incertidumbre', fontsize=10, color='red', style='italic')
ax.text(0.75, -0.8, 'Mayor confianza →', fontsize=10, color='green', style='italic')

for bar, val in zip(bars, valores):
    ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
            f"{val:.0%}", va='center', fontsize=10)

plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 8. Resumen y Conclusiones Clave
#
# | Concepto | Frecuentista | Epistemico |
# |----------|-------------|------------|
# | Probabilidad | Frecuencia de largo plazo | Grado de plausibilidad dado I |
# | Parametros | Constantes fijas desconocidas | Variables con distribucion |
# | Eventos unicos | No aplica | Si aplica |
# | Actualizacion | No (fija) | Si (regla inversa) |
# | Incertidumbre | No cuantificada | Cuantificada como ancho del intervalo |
#
# ### Takeaways
# 1. **P(A) = P(A|I)**: toda probabilidad es relativa a la informacion
# 2. **Knight falla**: la frontera riesgo/incertidumbre no es fija
# 3. **Frecuentista ⊂ Epistemico**: lo frecuentista es un caso especial
# 4. **El modelo honesto**: cuando sabe poco, sus intervalos se ensanchan
# 5. **Implicacion practica**: usa distribuciones completas, no puntos

# %% [markdown]
# ---
# *source_ref: turn0browsertab744690698*
#
# **Siguiente**: Modulo 3 — Simulacion Monte Carlo para Incertidumbre
