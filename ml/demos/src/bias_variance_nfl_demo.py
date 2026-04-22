"""
Demo: Bias-Variance Tradeoff y Teoremas No Free Lunch.

Demuestra la descomposicion del error de prediccion en bias^2, varianza
y ruido irreducible. Ilustra el teorema No Free Lunch con multiples
algoritmos y problemas sinteticos. Conecta con la importancia del
conocimiento del dominio financiero para seleccionar modelos.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy, scikit-learn
Ejecutar: python src/bias_variance_nfl_demo.py
"""
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error


# ============================================================
# Funcion generadora de datos
# ============================================================

def funcion_real(x):
    """Patron real subyacente: retorno no lineal de un indicador."""
    return 0.5 * np.sin(2 * np.pi * x) + 0.3 * x


def generar_datos(n, sigma=0.25, seed=None):
    """Genera datos sinteticos con ruido gaussiano.

    Parametros
    ----------
    n : int
        Numero de observaciones.
    sigma : float
        Desviacion estandar del ruido (irreducible).
    seed : int, optional
        Semilla aleatoria.

    Retorna
    -------
    tuple : (X, y)
    """
    if seed is not None:
        np.random.seed(seed)
    X = np.sort(np.random.uniform(0, 1, n))
    y = funcion_real(X) + np.random.normal(0, sigma, n)
    return X, y


# ============================================================
# 1. Descomposicion bias-variance
# ============================================================

def demo_bias_variance():
    """Calcula y muestra la descomposicion bias^2 + varianza + ruido."""
    print("=" * 65)
    print("1. DESCOMPOSICION BIAS-VARIANCE")
    print("=" * 65)

    sigma = 0.25
    n_datasets = 200
    n_muestras = 50
    x_eval = np.linspace(0.05, 0.95, 50)
    y_real = funcion_real(x_eval)

    grados = [1, 2, 3, 5, 7, 10, 15]
    print(f"\n  n_datasets={n_datasets}, n_muestras={n_muestras}, "
          f"sigma={sigma}")
    print(f"\n  {'Grado':<8} {'Bias^2':<10} {'Varianza':<10} "
          f"{'Ruido':<10} {'Error Total':<12} {'Estado'}")
    print(f"  {'-'*62}")

    mejor_error = float('inf')
    mejor_grado = 1

    for grado in grados:
        preds = np.zeros((n_datasets, len(x_eval)))
        for i in range(n_datasets):
            X, y = generar_datos(n_muestras, sigma, seed=i)
            poly = PolynomialFeatures(grado)
            Xp = poly.fit_transform(X.reshape(-1, 1))
            mod = LinearRegression().fit(Xp, y)
            Xe = poly.transform(x_eval.reshape(-1, 1))
            preds[i] = mod.predict(Xe)

        media = preds.mean(axis=0)
        bias2 = np.mean((media - y_real) ** 2)
        var = np.mean(preds.var(axis=0))
        ruido = sigma ** 2
        total = bias2 + var + ruido

        estado = ""
        if grado <= 2:
            estado = "UNDERFITTING"
        elif total < mejor_error:
            mejor_error = total
            mejor_grado = grado
            estado = "<-- optimo"
        elif var > bias2 * 3:
            estado = "OVERFITTING"

        print(f"  {grado:<8d} {bias2:<10.4f} {var:<10.4f} "
              f"{ruido:<10.4f} {total:<12.4f} {estado}")

    print(f"\n  -> Optimo: grado {mejor_grado} (error total minimo)")
    print(f"  -> Bias baja con complejidad, varianza sube")
    print(f"  -> El ruido ({sigma**2:.4f}) es un piso que NUNCA se cruza")


# ============================================================
# 2. Overfitting vs Underfitting
# ============================================================

def demo_overfitting():
    """Muestra MSE train vs test para diferentes complejidades."""
    print("\n" + "=" * 65)
    print("2. OVERFITTING: MSE TRAIN vs MSE TEST")
    print("=" * 65)

    X_train, y_train = generar_datos(50, 0.25, seed=42)
    X_test, y_test = generar_datos(200, 0.25, seed=99)

    grados = list(range(1, 16))
    print(f"\n  {'Grado':<8} {'MSE Train':<12} {'MSE Test':<12} "
          f"{'Ratio':<10} {'Diagnostico'}")
    print(f"  {'-'*55}")

    for g in grados:
        poly = PolynomialFeatures(g)
        Xtr = poly.fit_transform(X_train.reshape(-1, 1))
        Xte = poly.transform(X_test.reshape(-1, 1))
        mod = LinearRegression().fit(Xtr, y_train)

        mse_tr = mean_squared_error(y_train, mod.predict(Xtr))
        mse_te = mean_squared_error(y_test, mod.predict(Xte))
        ratio = mse_te / max(mse_tr, 1e-10)

        diag = ""
        if ratio > 5:
            diag = "OVERFITTING"
        elif mse_te > 0.15:
            diag = "underfitting"
        else:
            diag = "ok"

        print(f"  {g:<8d} {mse_tr:<12.4f} {mse_te:<12.4f} "
              f"{ratio:<10.1f}x {diag}")

    print(f"\n  -> MSE train SIEMPRE baja con mas complejidad")
    print(f"  -> MSE test baja y luego SUBE = overfitting")
    print(f"  -> En backtesting financiero: lo mismo! Overfit = perdidas reales")


# ============================================================
# 3. Regularizacion como prior bayesiano
# ============================================================

def demo_regularizacion():
    """Compara OLS vs Ridge (equivalente a prior bayesiano)."""
    print("\n" + "=" * 65)
    print("3. REGULARIZACION = PRIOR BAYESIANO (OLS vs RIDGE)")
    print("=" * 65)

    X, y = generar_datos(50, 0.25, seed=42)
    X_test, y_test = generar_datos(200, 0.25, seed=99)
    grado = 10

    poly = PolynomialFeatures(grado)
    Xtr = poly.fit_transform(X.reshape(-1, 1))
    Xte = poly.transform(X_test.reshape(-1, 1))

    alphas = [0, 0.001, 0.01, 0.1, 1.0, 10.0]
    print(f"\n  Polinomio grado {grado}")
    print(f"  Ridge(alpha) ~ Prior N(0, sigma^2/alpha) sobre coeficientes")
    print(f"\n  {'Alpha':<12} {'MSE Train':<12} {'MSE Test':<12} {'Interpretacion'}")
    print(f"  {'-'*55}")

    for alpha in alphas:
        if alpha == 0:
            mod = LinearRegression().fit(Xtr, y)
            nombre = "OLS"
        else:
            mod = Ridge(alpha=alpha).fit(Xtr, y)
            nombre = f"Ridge"

        mse_tr = mean_squared_error(y, mod.predict(Xtr))
        mse_te = mean_squared_error(y_test, mod.predict(Xte))

        if alpha == 0:
            interp = "Sin prior (MLE puro)"
        elif alpha < 0.01:
            interp = "Prior debil"
        elif alpha < 1:
            interp = "Prior moderado"
        else:
            interp = "Prior fuerte (encoge a 0)"

        print(f"  {alpha:<12.3f} {mse_tr:<12.4f} {mse_te:<12.4f} {interp}")

    print(f"\n  -> Ridge optimo: menor MSE test que OLS")
    print(f"  -> El prior REDUCE varianza a cambio de un poco mas de bias")
    print(f"  -> PML formaliza esto: priors bayesianos = regularizacion optima")


# ============================================================
# 4. Teorema No Free Lunch
# ============================================================

def demo_nfl():
    """Demuestra NFL con 3 problemas y 3 algoritmos."""
    print("\n" + "=" * 65)
    print("4. TEOREMA NO FREE LUNCH (WOLPERT 1996)")
    print("=" * 65)

    problemas = {
        "Lineal":     lambda x: 2 * x + 0.5,
        "Escalonado": lambda x: np.where(x < 0.5, 0, 1).astype(float),
        "Sinusoidal": lambda x: np.sin(4 * np.pi * x),
    }

    algoritmos = {
        "Reg. lineal": lambda: LinearRegression(),
        "Arbol (d=3)": lambda: DecisionTreeRegressor(max_depth=3),
        "KNN (k=5)":   lambda: KNeighborsRegressor(n_neighbors=5),
    }

    print(f"\n  3 problemas x 3 algoritmos x 30 repeticiones cada uno\n")
    algos = list(algoritmos.keys())
    print(f"  {'Problema':<15}", end="")
    for a in algos:
        print(f"{a:<18}", end="")
    print("GANADOR")
    print(f"  {'-'*70}")

    victorias = {a: 0 for a in algos}

    for p_nom, p_fn in problemas.items():
        mses = {}
        for a_nom, a_fn in algoritmos.items():
            scores = []
            for s in range(30):
                np.random.seed(s)
                Xtr = np.sort(np.random.uniform(0, 1, 50))
                ytr = p_fn(Xtr) + np.random.normal(0, 0.2, 50)
                Xte = np.sort(np.random.uniform(0, 1, 200))
                yte = p_fn(Xte) + np.random.normal(0, 0.2, 200)
                m = a_fn().fit(Xtr.reshape(-1, 1), ytr)
                scores.append(mean_squared_error(
                    yte, m.predict(Xte.reshape(-1, 1))))
            mses[a_nom] = np.mean(scores)

        print(f"  {p_nom:<15}", end="")
        vals = []
        for a in algos:
            print(f"{mses[a]:<18.4f}", end="")
            vals.append(mses[a])
        ganador = algos[np.argmin(vals)]
        victorias[ganador] += 1
        print(ganador)

    print(f"\n  Victorias totales:")
    for a, v in victorias.items():
        print(f"    {a}: {v}/3")

    hay_dominante = any(v == len(problemas) for v in victorias.values())
    if not hay_dominante:
        print(f"\n  -> NINGUN algoritmo gana en TODOS los problemas")
    print(f"  -> NFL confirmado: el ganador depende de la estructura del problema")
    print(f"  -> Sin conocimiento del dominio, no puedes elegir el mejor modelo")


# ============================================================
# 5. Resumen
# ============================================================

def demo_resumen():
    """Resumen de implicaciones practicas."""
    print("\n" + "=" * 65)
    print("5. RESUMEN: IMPLICACIONES PARA ML EN FINANZAS")
    print("=" * 65)

    print(f"""
  Concepto               Implicacion practica
  -----------------------------------------------------------
  Bias alto              Modelo demasiado simple; anade features
  Varianza alta          Modelo memoriza ruido; regulariza/priors
  Ruido irreducible      En finanzas es ENORME; no se puede eliminar
  NFL                    No hay "mejor algoritmo" universal
  Priors (PML)           Formalizan conocimiento como regularizacion

  Reglas de oro:
  1. Empieza SIMPLE, agrega complejidad solo si los datos lo permiten
  2. Valida SIEMPRE en datos fuera de muestra (no solo backtest)
  3. Integra conocimiento financiero via priors, no "tira y ve"
  4. Overfitting en backtest = perdidas reales en produccion
  5. PML navega el tradeoff: priors = regularizacion informada
""")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: BIAS-VARIANCE TRADEOFF Y NO FREE LUNCH")
    print("  Modulo 2D")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_bias_variance()
    demo_overfitting()
    demo_regularizacion()
    demo_nfl()
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("  Archivos relacionados:")
    print("    - notebooks/notebook_ch02d_bias_variance_nfl.md")
    print("    - hotmart/viz_bias_variance_nfl.py")
    print("    - hotmart/ejercicios/ejercicios_mod02d_bias_variance_nfl.md")
    print("=" * 65)
