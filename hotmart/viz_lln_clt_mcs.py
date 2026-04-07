"""
Visualizacion interactiva: LGN, TLC y Monte Carlo.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_lln_clt_mcs.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def crear_plotly_dashboard() -> str:
    """Dashboard con 3 paneles: convergencia LGN, TLC histogramas, IC vs N."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    np.random.seed(42)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "LGN: convergencia del promedio (Exponencial)",
            "TLC: medias muestrales (n=30, Exponencial)",
            "MCS: IC de P(loss>5%) vs numero de simulaciones",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: LGN convergencia
    datos = np.random.exponential(2, 10000)
    medias_acum = np.cumsum(datos) / np.arange(1, 10001)
    ns = list(range(1, 10001))

    fig.add_trace(go.Scatter(
        x=ns, y=medias_acum.tolist(), name="Media acumulada",
        line=dict(color="steelblue", width=1),
    ), row=1, col=1)
    fig.add_hline(y=2.0, line_dash="dash", line_color="red",
                  annotation_text="E[X]=2.0", row=1, col=1)

    # Panel 2: TLC histograma
    medias_30 = np.array([np.random.exponential(2, 30).mean() for _ in range(10000)])
    hist_counts, hist_edges = np.histogram(medias_30, bins=50, density=True)
    hist_centers = (hist_edges[:-1] + hist_edges[1:]) / 2

    fig.add_trace(go.Bar(
        x=hist_centers, y=hist_counts, name="Medias (n=30)",
        marker_color="rgba(70,130,180,0.5)", width=0.04,
    ), row=1, col=2)
    x_norm = np.linspace(medias_30.min(), medias_30.max(), 200)
    fig.add_trace(go.Scatter(
        x=x_norm, y=stats.norm.pdf(x_norm, medias_30.mean(), medias_30.std()),
        name="Normal ref", line=dict(color="orangered", width=2),
    ), row=1, col=2)

    # Panel 3: IC vs N
    ns_ic = [100, 500, 1000, 5000, 10000, 50000, 100000]
    ret_real = 0.0003 + 0.012 * np.random.standard_t(4, 1_000_000)
    p_real = (ret_real < -0.05).mean()

    estimaciones, lo_list, hi_list = [], [], []
    for N in ns_ic:
        np.random.seed(42 + N)
        ret = 0.0003 + 0.012 * np.random.standard_t(4, N)
        p = (ret < -0.05).mean()
        se = np.sqrt(p * (1 - p) / N)
        estimaciones.append(p * 100)
        lo_list.append((p - 1.96 * se) * 100)
        hi_list.append((p + 1.96 * se) * 100)

    fig.add_trace(go.Scatter(
        x=ns_ic, y=estimaciones, name="Estimacion",
        mode="lines+markers", line=dict(color="steelblue", width=2),
        marker=dict(size=8),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=ns_ic + ns_ic[::-1],
        y=hi_list + lo_list[::-1],
        fill="toself", fillcolor="rgba(70,130,180,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="IC 95%", showlegend=True,
    ), row=2, col=1)
    fig.add_hline(y=p_real * 100, line_dash="dot", line_color="red",
                  annotation_text=f"Real: {p_real:.2%}", row=2, col=1)

    fig.update_layout(
        height=900, width=1000,
        title="LGN + TLC: los fundamentos de Monte Carlo",
        template="plotly_white",
        font=dict(size=12),
    )
    fig.update_xaxes(title_text="N", row=1, col=1)
    fig.update_yaxes(title_text="Media acumulada", row=1, col=1)
    fig.update_xaxes(title_text="Media muestral", row=1, col=2)
    fig.update_xaxes(title_text="N simulaciones", type="log", row=2, col=1)
    fig.update_yaxes(title_text="P(loss>5%) (%)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/lln_clt_mcs.png"):
    """Fallback PNG."""
    import matplotlib.pyplot as plt

    np.random.seed(42)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # LGN
    datos = np.random.exponential(2, 10000)
    axes[0].plot(np.cumsum(datos) / np.arange(1, 10001), 'steelblue', lw=1)
    axes[0].axhline(2.0, color='red', ls='--')
    axes[0].set_title('LGN: convergencia')
    axes[0].set_xlabel('N')

    # TLC
    medias = np.array([np.random.exponential(2, 30).mean() for _ in range(10000)])
    axes[1].hist(medias, bins=50, density=True, alpha=0.6, color='steelblue')
    x = np.linspace(medias.min(), medias.max(), 200)
    axes[1].plot(x, stats.norm.pdf(x, medias.mean(), medias.std()), 'orangered', lw=2)
    axes[1].set_title('TLC: medias(n=30) son Normales')

    plt.suptitle('LGN + TLC', fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion LGN + TLC...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/lln_clt_mcs.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
