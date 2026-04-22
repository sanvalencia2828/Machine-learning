"""
Visualizacion interactiva: Bias-Variance Tradeoff y No Free Lunch.
Genera HTML con Plotly (3 paneles) + fallback PNG con Matplotlib.
source_ref: turn0browsertab744690698

Requisitos: numpy, scipy, sklearn, plotly (o matplotlib como fallback)
Ejecutar: python hotmart/viz_bias_variance_nfl.py
"""
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from pathlib import Path


# ================================================================
# Funciones auxiliares
# ================================================================

def funcion_real(x):
    """Patron real subyacente (desconocido para el modelo)."""
    return 0.5 * np.sin(2 * np.pi * x) + 0.3 * x


def generar_datos(n, sigma=0.25, seed=None):
    """Genera datos sinteticos con ruido."""
    if seed is not None:
        np.random.seed(seed)
    X = np.sort(np.random.uniform(0, 1, n))
    y = funcion_real(X) + np.random.normal(0, sigma, n)
    return X, y


# ================================================================
# Datos para los paneles
# ================================================================

def calcular_curva_bias_variance(grados=None, n_datasets=200,
                                  n_muestras=50, sigma=0.25):
    """Calcula bias^2, varianza y error total para cada grado."""
    if grados is None:
        grados = list(range(1, 16))

    x_eval = np.linspace(0.05, 0.95, 50)
    y_real = funcion_real(x_eval)
    resultados = []

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
        bias2 = float(np.mean((media - y_real) ** 2))
        var = float(np.mean(preds.var(axis=0)))
        ruido = sigma ** 2
        resultados.append({
            "grado": grado, "bias2": bias2,
            "varianza": var, "error_total": bias2 + var + ruido,
        })
    return resultados, sigma ** 2


def calcular_ajustes_polinomio(grados_mostrar=None):
    """Genera predicciones para visualizar underfitting/overfitting."""
    if grados_mostrar is None:
        grados_mostrar = [1, 3, 5, 10, 15]
    X, y = generar_datos(50, 0.25, seed=42)
    x_plot = np.linspace(0, 1, 200)
    ajustes = {}
    for g in grados_mostrar:
        poly = PolynomialFeatures(g)
        Xp = poly.fit_transform(X.reshape(-1, 1))
        mod = LinearRegression().fit(Xp, y)
        ajustes[g] = mod.predict(poly.transform(x_plot.reshape(-1, 1)))
    return x_plot, X, y, ajustes


def calcular_nfl():
    """Ejecuta demo NFL: 3 algoritmos x 3 problemas."""
    problemas = {
        "Lineal": lambda x: 2 * x + 0.5,
        "Escalonado": lambda x: np.where(x < 0.5, 0, 1).astype(float),
        "Sinusoidal": lambda x: np.sin(4 * np.pi * x),
    }
    algoritmos = {
        "Reg. lineal": lambda: LinearRegression(),
        "Arbol (d=3)": lambda: DecisionTreeRegressor(max_depth=3),
        "KNN (k=5)": lambda: KNeighborsRegressor(n_neighbors=5),
    }

    resultados = {}
    for p_nom, p_fn in problemas.items():
        resultados[p_nom] = {}
        for a_nom, a_fn in algoritmos.items():
            mses = []
            for s in range(30):
                np.random.seed(s)
                Xtr = np.sort(np.random.uniform(0, 1, 50))
                ytr = p_fn(Xtr) + np.random.normal(0, 0.2, 50)
                Xte = np.sort(np.random.uniform(0, 1, 200))
                yte = p_fn(Xte) + np.random.normal(0, 0.2, 200)
                m = a_fn().fit(Xtr.reshape(-1, 1), ytr)
                mses.append(mean_squared_error(yte, m.predict(Xte.reshape(-1, 1))))
            resultados[p_nom][a_nom] = np.mean(mses)
    return resultados


# ================================================================
# Plotly dashboard
# ================================================================

def crear_plotly_dashboard() -> str:
    """Crea dashboard HTML con 3 paneles."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado. Usa: pip install plotly")
        return ""

    # Datos
    bv_res, ruido = calcular_curva_bias_variance()
    x_plot, X_data, y_data, ajustes = calcular_ajustes_polinomio([1, 5, 15])
    nfl_res = calcular_nfl()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Curva Bias-Variance",
            "Underfitting vs Overfitting",
            "No Free Lunch: 3 algoritmos x 3 problemas",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.55, 0.45],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # Panel 1: Curva bias-variance
    grados = [r['grado'] for r in bv_res]
    fig.add_trace(go.Scatter(
        x=grados, y=[r['bias2'] for r in bv_res],
        name="Bias^2", line=dict(color="steelblue", width=2),
        mode="lines+markers", marker=dict(size=5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=grados, y=[r['varianza'] for r in bv_res],
        name="Varianza", line=dict(color="orangered", width=2),
        mode="lines+markers", marker=dict(size=5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=grados, y=[r['error_total'] for r in bv_res],
        name="Error Total", line=dict(color="black", width=2.5),
        mode="lines+markers", marker=dict(size=6),
    ), row=1, col=1)
    fig.add_hline(y=ruido, line_dash="dot", line_color="gray",
                  annotation_text=f"Ruido: {ruido:.3f}", row=1, col=1)

    # Panel 2: Ajustes polinomiales
    fig.add_trace(go.Scatter(
        x=X_data, y=y_data, mode="markers", name="Datos",
        marker=dict(color="gray", size=4, opacity=0.5),
        showlegend=False,
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x_plot, y=funcion_real(x_plot), name="f(x) real",
        line=dict(color="black", dash="dash", width=1.5),
    ), row=1, col=2)
    colores_poly = {"1": "steelblue", "5": "forestgreen", "15": "orangered"}
    for g, y_pred in ajustes.items():
        fig.add_trace(go.Scatter(
            x=x_plot, y=y_pred, name=f"Grado {g}",
            line=dict(color=colores_poly.get(str(g), "purple"), width=2),
        ), row=1, col=2)

    # Panel 3: NFL barras agrupadas
    problemas = list(nfl_res.keys())
    algos = list(nfl_res[problemas[0]].keys())
    colores_nfl = ["steelblue", "orangered", "forestgreen"]

    for i, algo in enumerate(algos):
        vals = [nfl_res[p][algo] for p in problemas]
        fig.add_trace(go.Bar(
            x=problemas, y=vals, name=algo,
            marker_color=colores_nfl[i],
            text=[f"{v:.3f}" for v in vals],
            textposition="outside",
        ), row=2, col=1)

    fig.update_layout(
        height=900, width=1000,
        title="Bias-Variance Tradeoff y No Free Lunch",
        template="plotly_white",
        barmode="group",
        font=dict(size=12),
        legend=dict(x=0.01, y=0.99),
    )
    fig.update_xaxes(title_text="Complejidad (grado)", row=1, col=1)
    fig.update_yaxes(title_text="Error (MSE)", row=1, col=1)
    fig.update_xaxes(title_text="x", row=1, col=2)
    fig.update_yaxes(title_text="y", row=1, col=2)
    fig.update_yaxes(title_text="MSE (promedio 30 runs)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


# ================================================================
# Matplotlib fallback
# ================================================================

def crear_matplotlib_fallback(output_path="data/bias_variance_nfl.png"):
    """Genera version estatica PNG."""
    import matplotlib.pyplot as plt

    bv_res, ruido = calcular_curva_bias_variance()
    nfl_res = calcular_nfl()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Panel 1: Curva bias-variance
    grados = [r['grado'] for r in bv_res]
    axes[0].plot(grados, [r['bias2'] for r in bv_res], 'steelblue',
                 lw=2, marker='o', ms=4, label='Bias^2')
    axes[0].plot(grados, [r['varianza'] for r in bv_res], 'orangered',
                 lw=2, marker='s', ms=4, label='Varianza')
    axes[0].plot(grados, [r['error_total'] for r in bv_res], 'k',
                 lw=2.5, marker='D', ms=4, label='Error Total')
    axes[0].axhline(ruido, ls=':', color='gray', label=f'Ruido: {ruido:.3f}')
    axes[0].set_xlabel('Complejidad (grado)')
    axes[0].set_ylabel('Error (MSE)')
    axes[0].set_title('Curva Bias-Variance')
    axes[0].legend(fontsize=9)

    # Panel 2: NFL
    problemas = list(nfl_res.keys())
    algos = list(nfl_res[problemas[0]].keys())
    x_pos = np.arange(len(problemas))
    width = 0.25
    colores = ['steelblue', 'orangered', 'forestgreen']

    for i, algo in enumerate(algos):
        vals = [nfl_res[p][algo] for p in problemas]
        axes[1].bar(x_pos + i * width, vals, width, label=algo,
                    color=colores[i], edgecolor='black')
    axes[1].set_xticks(x_pos + width)
    axes[1].set_xticklabels(problemas)
    axes[1].set_ylabel('MSE')
    axes[1].set_title('No Free Lunch')
    axes[1].legend(fontsize=9)

    plt.suptitle('Bias-Variance Tradeoff y No Free Lunch',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


# ================================================================
# Main
# ================================================================

if __name__ == "__main__":
    print("Generando visualizacion Bias-Variance + NFL...")

    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/bias_variance_nfl.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")

    crear_matplotlib_fallback()
    print("Listo.")
