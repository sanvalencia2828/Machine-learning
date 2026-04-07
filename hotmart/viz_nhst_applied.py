"""
Visualizacion interactiva: NHST Aplicado -- OLS, Base Rates, Confusion Matrix.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_nhst_applied.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def datos_ols():
    """Genera datos OLS sinteticos y ajusta."""
    np.random.seed(42)
    n = 504
    r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_apple = 0.0002 + 1.25 * r_mkt + 0.01 * np.random.standard_t(4, n)
    X = np.column_stack([np.ones(n), r_mkt])
    b = np.linalg.lstsq(X, r_apple, rcond=None)[0]
    return r_mkt, r_apple, b


def datos_ppv_curves(sens=0.85):
    """PPV vs FPR para diferentes base rates."""
    fprs = np.linspace(0.01, 0.35, 40)
    brs = [0.05, 0.10, 0.15, 0.25]
    curves = {}
    for br in brs:
        curves[br] = (sens * br) / (sens * br + fprs * (1 - br))
    return fprs, curves


def datos_confusion(sens=0.85, fpr=0.20, base_rate=0.15, n=960):
    """Confusion matrix simulada."""
    tp = int(sens * base_rate * n)
    fp = int(fpr * (1 - base_rate) * n)
    fn = int((1 - sens) * base_rate * n)
    tn = n - tp - fp - fn
    return np.array([[tp, fp], [fn, tn]])


def crear_plotly_dashboard() -> str:
    """Dashboard HTML con 3 paneles."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    r_mkt, r_apple, b = datos_ols()
    fprs, ppv_curves = datos_ppv_curves()
    cm = datos_confusion()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "OLS: Apple vs S&P 500 (sintetico)",
            "PPV vs FPR para diferentes base rates",
            "Confusion Matrix: Indicador de Recesion",
        ),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "heatmap", "colspan": 2}, None]],
        row_heights=[0.55, 0.45],
        vertical_spacing=0.14,
    )

    # Panel 1: OLS scatter
    fig.add_trace(go.Scatter(
        x=r_mkt * 100, y=r_apple * 100, mode="markers",
        marker=dict(color="steelblue", size=3, opacity=0.3),
        name="Datos",
    ), row=1, col=1)
    x_line = np.linspace(r_mkt.min(), r_mkt.max(), 100)
    y_line = b[0] + b[1] * x_line
    fig.add_trace(go.Scatter(
        x=x_line * 100, y=y_line * 100,
        name=f"OLS: a={b[0]:.5f}, b={b[1]:.3f}",
        line=dict(color="orangered", width=2),
    ), row=1, col=1)

    # Panel 2: PPV curves
    colores = ["#e74c3c", "#f39c12", "#2ecc71", "#3498db"]
    for (br, ppvs), color in zip(ppv_curves.items(), colores):
        fig.add_trace(go.Scatter(
            x=fprs * 100, y=ppvs * 100,
            name=f"Base rate {br:.0%}",
            line=dict(color=color, width=2),
            hovertemplate="FPR=%{x:.0f}%<br>PPV=%{y:.1f}%",
        ), row=1, col=2)
    fig.add_hline(y=50, line_dash="dot", line_color="gray",
                  annotation_text="50% (moneda)", row=1, col=2)

    # Panel 3: Heatmap confusion matrix
    labels = [["TP", "FP"], ["FN", "TN"]]
    text = [[f"{labels[i][j]}<br>{cm[i][j]}" for j in range(2)] for i in range(2)]
    fig.add_trace(go.Heatmap(
        z=cm, x=["Recesion", "Expansion"], y=["Senal", "Sin senal"],
        colorscale=[[0, "#fee0d2"], [0.5, "#fc9272"], [1, "#de2d26"]],
        text=text, texttemplate="%{text}",
        textfont=dict(size=16),
        showscale=False,
    ), row=2, col=1)

    ppv = cm[0, 0] / max(cm[0, 0] + cm[0, 1], 1)
    fig.add_annotation(
        x=1.5, y=-0.3,
        text=f"PPV = {ppv:.1%} | Sensibilidad = 85%<br>"
             f"El 'fiscal' diria 85%. Bayes dice {ppv:.0%}.",
        showarrow=False, font=dict(size=13),
        xref="x3", yref="y3",
    )

    fig.update_layout(
        height=900, width=1000,
        title="NHST Aplicado: OLS, Base Rates y Confusion Matrix",
        template="plotly_white",
        font=dict(size=12),
    )
    fig.update_xaxes(title_text="Retorno S&P (%)", row=1, col=1)
    fig.update_yaxes(title_text="Retorno Apple (%)", row=1, col=1)
    fig.update_xaxes(title_text="FPR (%)", row=1, col=2)
    fig.update_yaxes(title_text="PPV (%)", row=1, col=2)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/nhst_applied.png"):
    """Fallback PNG."""
    import matplotlib.pyplot as plt

    r_mkt, r_apple, b = datos_ols()
    fprs, ppv_curves = datos_ppv_curves()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].scatter(r_mkt * 100, r_apple * 100, s=5, alpha=0.3, color='steelblue')
    x_l = np.linspace(r_mkt.min(), r_mkt.max(), 100)
    axes[0].plot(x_l * 100, (b[0] + b[1] * x_l) * 100, 'orangered', lw=2)
    axes[0].set_title('OLS: Apple vs S&P 500')
    axes[0].set_xlabel('r_market (%)')

    for br, ppvs in ppv_curves.items():
        axes[1].plot(fprs * 100, ppvs * 100, lw=2, label=f'BR={br:.0%}')
    axes[1].axhline(50, ls=':', color='gray')
    axes[1].set_title('PPV vs FPR')
    axes[1].set_xlabel('FPR (%)')
    axes[1].legend()

    plt.suptitle('NHST Aplicado', fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion NHST Applied...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/nhst_applied.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
