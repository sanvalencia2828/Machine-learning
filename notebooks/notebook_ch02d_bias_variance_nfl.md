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
# # Modulo 2D: Bias-Variance Tradeoff y Teoremas No Free Lunch
# **source_ref: turn0browsertab744690698**
#
# ## Objetivos de Aprendizaje
# 1. Descomponer el error de prediccion en bias^2, varianza y ruido irreducible
# 2. Visualizar underfitting vs overfitting con polinomios de grado creciente
# 3. Demostrar el teorema No Free Lunch con multiples algoritmos y problemas
# 4. Aplicar bias-variance a modelos financieros (CAPM, arboles, redes neuronales)
# 5. Entender como los priors bayesianos regularizan el tradeoff

# %% [markdown]
# ---
# ## 1. Setup e Importaciones

# %%
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
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
# ## 2. Generacion de Datos Sinteticos
#
# Creamos datos con un patron no lineal conocido + ruido gaussiano.
# Esto nos permite calcular el bias y la varianza exactos.

# %%
def funcion_real(x):
    """Funcion real (desconocida para el modelo).

    Simula un patron financiero no lineal: retorno esperado que
    depende del nivel de un indicador macro.
    """
    return 0.5 * np.sin(2 * np.pi * x) + 0.3 * x


def generar_datos(n: int = 50, sigma_ruido: float = 0.25, seed: int = None):
    """Genera datos sinteticos con ruido.

    Parametros
    ----------
    n : int
        Numero de observaciones.
    sigma_ruido : float
        Desviacion estandar del ruido (irreducible).
    seed : int, optional
        Semilla para reproducibilidad.

    Retorna
    -------
    tuple : (X, y, y_real)
    """
    if seed is not None:
        np.random.seed(seed)
    X = np.sort(np.random.uniform(0, 1, n))
    y_real = funcion_real(X)
    y = y_real + np.random.normal(0, sigma_ruido, n)
    return X, y, y_real


X_train, y_train, y_real_train = generar_datos(n=50, seed=42)
X_test, y_test, y_real_test = generar_datos(n=200, seed=99)

fig, ax = plt.subplots(figsize=(10, 5))
x_plot = np.linspace(0, 1, 300)
ax.plot(x_plot, funcion_real(x_plot), 'k-', lw=2, label='Funcion real f(x)')
ax.scatter(X_train, y_train, c='steelblue', s=30, alpha=0.6, label='Datos training')
ax.set_xlabel('x (indicador)')
ax.set_ylabel('y (retorno)')
ax.set_title('Datos sinteticos: patron no lineal + ruido', fontsize=13)
ax.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. Underfitting vs Overfitting: Polinomios de Grado Creciente
#
# Ajustamos polinomios de grado 1 (lineal) hasta grado 20 para
# visualizar como cambia el ajuste.

# %%
grados = [1, 3, 5, 10, 20]

fig, axes = plt.subplots(1, len(grados), figsize=(4 * len(grados), 4), sharey=True)

x_plot = np.linspace(0, 1, 300)

for i, grado in enumerate(grados):
    poly = PolynomialFeatures(grado)
    X_poly = poly.fit_transform(X_train.reshape(-1, 1))
    X_plot_poly = poly.transform(x_plot.reshape(-1, 1))

    modelo = LinearRegression()
    modelo.fit(X_poly, y_train)
    y_pred = modelo.predict(X_plot_poly)

    # Error en test
    X_test_poly = poly.transform(X_test.reshape(-1, 1))
    mse_test = mean_squared_error(y_test, modelo.predict(X_test_poly))

    axes[i].scatter(X_train, y_train, c='steelblue', s=15, alpha=0.5)
    axes[i].plot(x_plot, funcion_real(x_plot), 'k--', lw=1, alpha=0.5)
    axes[i].plot(x_plot, y_pred, 'orangered', lw=2)
    axes[i].set_title(f'Grado {grado}\nMSE test: {mse_test:.3f}', fontsize=11)
    axes[i].set_xlabel('x')
    axes[i].set_ylim(-1.5, 1.5)
    if i == 0:
        axes[i].set_ylabel('y')

    # Etiquetar
    if grado == 1:
        axes[i].text(0.5, -1.2, 'UNDERFITTING', ha='center',
                     fontsize=10, color='blue', fontweight='bold')
    elif grado >= 15:
        axes[i].text(0.5, -1.2, 'OVERFITTING', ha='center',
                     fontsize=10, color='red', fontweight='bold')

plt.suptitle('Bias-Variance: de underfitting a overfitting',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 4. Descomposicion Bias-Variance
#
# Para calcular bias y varianza exactos, generamos muchos datasets
# del mismo proceso y medimos:
# - **Bias^2**: (media de predicciones - valor real)^2
# - **Varianza**: variabilidad de predicciones entre datasets
# - **Error total**: bias^2 + varianza + ruido^2

# %%
def calcular_bias_varianza(grado: int, n_datasets: int = 200,
                            n_muestras: int = 50,
                            sigma_ruido: float = 0.25):
    """Calcula bias^2, varianza y error total para un polinomio de grado dado.

    Parametros
    ----------
    grado : int
        Grado del polinomio.
    n_datasets : int
        Numero de datasets a generar.
    n_muestras : int
        Tamano de cada dataset.
    sigma_ruido : float
        Ruido irreducible.

    Retorna
    -------
    dict con bias2, varianza, ruido, error_total.
    """
    x_eval = np.linspace(0.05, 0.95, 50)
    y_real = funcion_real(x_eval)
    predicciones = np.zeros((n_datasets, len(x_eval)))

    for i in range(n_datasets):
        X, y, _ = generar_datos(n_muestras, sigma_ruido, seed=i)
        poly = PolynomialFeatures(grado)
        X_poly = poly.fit_transform(X.reshape(-1, 1))
        modelo = LinearRegression()
        modelo.fit(X_poly, y)
        X_eval_poly = poly.transform(x_eval.reshape(-1, 1))
        predicciones[i] = modelo.predict(X_eval_poly)

    media_pred = predicciones.mean(axis=0)
    bias2 = np.mean((media_pred - y_real) ** 2)
    varianza = np.mean(predicciones.var(axis=0))
    ruido = sigma_ruido ** 2
    error_total = bias2 + varianza + ruido

    return {"grado": grado, "bias2": bias2, "varianza": varianza,
            "ruido": ruido, "error_total": error_total}


# Calcular para varios grados
grados_eval = list(range(1, 16))
resultados = [calcular_bias_varianza(g) for g in grados_eval]

print(f"{'Grado':<8} {'Bias^2':<10} {'Varianza':<10} {'Ruido':<10} {'Error Total'}")
print("-" * 48)
for r in resultados:
    print(f"{r['grado']:<8d} {r['bias2']:<10.4f} {r['varianza']:<10.4f} "
          f"{r['ruido']:<10.4f} {r['error_total']:.4f}")

# %%
bias2_arr = [r['bias2'] for r in resultados]
var_arr = [r['varianza'] for r in resultados]
ruido_arr = [r['ruido'] for r in resultados]
total_arr = [r['error_total'] for r in resultados]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(grados_eval, bias2_arr, 'steelblue', lw=2, marker='o', ms=5, label='Bias^2')
ax.plot(grados_eval, var_arr, 'orangered', lw=2, marker='s', ms=5, label='Varianza')
ax.plot(grados_eval, total_arr, 'k', lw=2.5, marker='D', ms=5, label='Error Total')
ax.axhline(ruido_arr[0], ls=':', color='gray', lw=1.5, label=f'Ruido irreducible ({ruido_arr[0]:.3f})')

# Marcar optimo
idx_opt = np.argmin(total_arr)
ax.axvline(grados_eval[idx_opt], ls='--', color='green', alpha=0.5)
ax.annotate(f'Optimo: grado {grados_eval[idx_opt]}',
            xy=(grados_eval[idx_opt], total_arr[idx_opt]),
            xytext=(grados_eval[idx_opt]+2, total_arr[idx_opt]+0.03),
            fontsize=11, color='green',
            arrowprops=dict(arrowstyle='->', color='green'))

# Zonas
ax.axvspan(0.5, 2.5, alpha=0.05, color='blue')
ax.axvspan(10.5, 15.5, alpha=0.05, color='red')
ax.text(1.5, max(total_arr)*0.9, 'Underfitting\n(bias alto)', ha='center',
        fontsize=10, color='blue', style='italic')
ax.text(13, max(total_arr)*0.9, 'Overfitting\n(varianza alta)', ha='center',
        fontsize=10, color='red', style='italic')

ax.set_xlabel('Complejidad del modelo (grado del polinomio)', fontsize=12)
ax.set_ylabel('Error (MSE)', fontsize=12)
ax.set_title('Descomposicion Bias-Variance', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 5. Aplicacion Financiera: Modelos con Diferente Complejidad
#
# Simulamos retornos dependientes de un factor macro y comparamos
# tres niveles de complejidad de modelo.

# %%
def simular_retornos_factor(n: int = 200, seed: int = 42):
    """Genera retornos que dependen no-linealmente de un factor macro.

    Relacion real: r = 0.02*factor - 0.001*factor^3 + ruido
    """
    np.random.seed(seed)
    factor = np.random.normal(0, 1, n)
    retorno_real = 0.02 * factor - 0.001 * factor**3
    ruido = np.random.normal(0, 0.01, n)
    retorno = retorno_real + ruido
    return factor, retorno, retorno_real


factor, retorno, retorno_real = simular_retornos_factor()
f_train, f_test, r_train, r_test = train_test_split(
    factor, retorno, test_size=0.3, random_state=42
)

modelos = {
    "Media historica (bias alto)": 0,
    "Lineal / CAPM (equilibrado)": 1,
    "Polinomio grado 10 (varianza alta)": 10,
}

fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
f_plot = np.linspace(factor.min(), factor.max(), 200)

for idx, (nombre, grado) in enumerate(modelos.items()):
    if grado == 0:
        y_pred_plot = np.full_like(f_plot, r_train.mean())
        mse = mean_squared_error(r_test, np.full_like(r_test, r_train.mean()))
    else:
        poly = PolynomialFeatures(grado)
        X_tr = poly.fit_transform(f_train.reshape(-1, 1))
        X_te = poly.transform(f_test.reshape(-1, 1))
        X_pl = poly.transform(f_plot.reshape(-1, 1))
        mod = LinearRegression().fit(X_tr, r_train)
        y_pred_plot = mod.predict(X_pl)
        mse = mean_squared_error(r_test, mod.predict(X_te))

    axes[idx].scatter(f_train, r_train, c='steelblue', s=10, alpha=0.4)
    axes[idx].plot(f_plot, 0.02*f_plot - 0.001*f_plot**3, 'k--', lw=1, alpha=0.5)
    axes[idx].plot(f_plot, y_pred_plot, 'orangered', lw=2)
    axes[idx].set_title(f'{nombre}\nMSE test: {mse:.6f}', fontsize=10)
    axes[idx].set_xlabel('Factor macro')
    if idx == 0:
        axes[idx].set_ylabel('Retorno')

plt.suptitle('Bias-Variance en Modelos Financieros', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 6. Regularizacion como Priors: Ridge vs OLS
#
# Ridge regression es equivalente a un prior Normal sobre los coeficientes.
# Esto REDUCE la varianza a costa de un poco mas de bias -- exactamente
# lo que hacen los priors bayesianos.

# %%
def comparar_ols_vs_ridge(grado: int = 10, alphas: list = None):
    """Compara OLS (sin prior) vs Ridge (con prior) para un polinomio.

    Ridge con alpha > 0 es equivalente a un prior N(0, 1/alpha) sobre
    los coeficientes -- regularizacion bayesiana.
    """
    if alphas is None:
        alphas = [0, 0.001, 0.01, 0.1, 1.0, 10.0]

    X, y, _ = generar_datos(50, 0.25, seed=42)
    X_test_bv, y_test_bv, _ = generar_datos(200, 0.25, seed=99)

    poly = PolynomialFeatures(grado)
    X_poly = poly.fit_transform(X.reshape(-1, 1))
    X_test_poly = poly.transform(X_test_bv.reshape(-1, 1))

    resultados = []
    for alpha in alphas:
        if alpha == 0:
            mod = LinearRegression().fit(X_poly, y)
            nombre = "OLS (sin prior)"
        else:
            mod = Ridge(alpha=alpha).fit(X_poly, y)
            nombre = f"Ridge (alpha={alpha})"

        mse_train = mean_squared_error(y, mod.predict(X_poly))
        mse_test = mean_squared_error(y_test_bv, mod.predict(X_test_poly))
        resultados.append({
            "nombre": nombre, "alpha": alpha,
            "mse_train": mse_train, "mse_test": mse_test,
        })

    return resultados


res_ridge = comparar_ols_vs_ridge()

print(f"Polinomio grado 10 -- OLS vs Ridge:\n")
print(f"{'Modelo':<25} {'MSE Train':<12} {'MSE Test':<12} {'Overfit?'}")
print("-" * 55)
for r in res_ridge:
    ratio = r['mse_test'] / max(r['mse_train'], 1e-10)
    overfit = "SI" if ratio > 2 else "no"
    print(f"{r['nombre']:<25} {r['mse_train']:<12.4f} {r['mse_test']:<12.4f} {overfit}")

print("\n--> Ridge con alpha optimo: menor MSE test que OLS")
print("--> El 'prior' (regularizacion) reduce varianza sin destruir la senal")
print("--> Esto es EXACTAMENTE lo que hacen los priors bayesianos en PML")

# %% [markdown]
# ---
# ## 7. Teorema No Free Lunch: Demostracion Practica
#
# Creamos 3 problemas con estructuras diferentes y mostramos que
# ningun algoritmo gana en todos.

# %%
def demo_nfl():
    """Demuestra No Free Lunch con 3 problemas y 3 algoritmos."""
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.neighbors import KNeighborsRegressor

    problemas = {
        "Lineal": lambda x: 2 * x + 0.5,
        "Escalonado": lambda x: np.where(x < 0.5, 0, 1).astype(float),
        "Sinusoidal": lambda x: np.sin(4 * np.pi * x),
    }

    algoritmos = {
        "Regresion lineal": lambda: LinearRegression(),
        "Arbol decision (d=3)": lambda: DecisionTreeRegressor(max_depth=3),
        "KNN (k=5)": lambda: KNeighborsRegressor(n_neighbors=5),
    }

    n_train, n_test = 50, 200
    sigma = 0.2

    resultados = {}
    for p_nombre, p_func in problemas.items():
        resultados[p_nombre] = {}
        for a_nombre, a_factory in algoritmos.items():
            mses = []
            for seed in range(30):  # 30 repeticiones
                np.random.seed(seed)
                X_tr = np.sort(np.random.uniform(0, 1, n_train))
                y_tr = p_func(X_tr) + np.random.normal(0, sigma, n_train)
                X_te = np.sort(np.random.uniform(0, 1, n_test))
                y_te = p_func(X_te) + np.random.normal(0, sigma, n_test)

                mod = a_factory()
                mod.fit(X_tr.reshape(-1, 1), y_tr)
                y_pred = mod.predict(X_te.reshape(-1, 1))
                mses.append(mean_squared_error(y_te, y_pred))

            resultados[p_nombre][a_nombre] = np.mean(mses)

    return resultados


res_nfl = demo_nfl()

print("=== TEOREMA NO FREE LUNCH: 3 algoritmos x 3 problemas ===\n")
algos = list(list(res_nfl.values())[0].keys())
print(f"{'Problema':<18}", end="")
for a in algos:
    print(f"{a:<22}", end="")
print("Ganador")
print("-" * 85)

for prob, scores in res_nfl.items():
    print(f"{prob:<18}", end="")
    vals = []
    for a in algos:
        print(f"{scores[a]:<22.4f}", end="")
        vals.append(scores[a])
    ganador = algos[np.argmin(vals)]
    print(ganador)

print("\n--> Ningun algoritmo gana en TODOS los problemas")
print("--> El ganador depende de la ESTRUCTURA del problema")
print("--> Sin conocimiento del dominio: rendimiento = azar en promedio")

# %%
# Visualizacion de NFL
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
problemas_func = {
    "Lineal": lambda x: 2 * x + 0.5,
    "Escalonado": lambda x: np.where(x < 0.5, 0, 1).astype(float),
    "Sinusoidal": lambda x: np.sin(4 * np.pi * x),
}
colores_algo = ['steelblue', 'orangered', 'forestgreen']
algos_list = list(res_nfl[list(res_nfl.keys())[0]].keys())

for idx, (prob, mses) in enumerate(res_nfl.items()):
    vals = [mses[a] for a in algos_list]
    bars = axes[idx].bar(range(len(vals)), vals, color=colores_algo, edgecolor='black')
    axes[idx].set_xticks(range(len(vals)))
    axes[idx].set_xticklabels(['Lineal', 'Arbol', 'KNN'], fontsize=9)
    axes[idx].set_title(f'Problema: {prob}', fontsize=11)
    axes[idx].set_ylabel('MSE' if idx == 0 else '')

    # Marcar ganador
    ganador_idx = np.argmin(vals)
    bars[ganador_idx].set_edgecolor('gold')
    bars[ganador_idx].set_linewidth(3)

plt.suptitle('No Free Lunch: ningun algoritmo domina en todos los problemas',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 8. Resumen y Conclusiones Clave
#
# | Concepto | Implicacion practica |
# |----------|---------------------|
# | **Bias alto** | Modelo demasiado simple; anade complejidad o features |
# | **Varianza alta** | Modelo memoriza ruido; regulariza o usa priors |
# | **Ruido irreducible** | No puedes eliminarlo; en finanzas es ENORME |
# | **NFL** | No hay "mejor algoritmo" sin conocimiento del dominio |
# | **Priors (PML)** | Formalizan el conocimiento financiero como regularizacion |
#
# ### Takeaways
# 1. Error = Bias^2 + Varianza + Ruido
# 2. En finanzas, el ruido domina --> modelos simples con priors ganan
# 3. NFL: debes integrar conocimiento financiero -- ML ciego fracasa
# 4. PML resuelve el tradeoff formalmente via priors bayesianos
# 5. Overfitting en backtesting = varianza alta = perdidas reales
#
# ---
# *source_ref: turn0browsertab744690698*
#
# **Siguiente**: Modulo 3 -- Simulacion Monte Carlo
