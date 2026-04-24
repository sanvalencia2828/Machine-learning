"""
Visualizacion: Decisiones Probabilisticas -- Kelly, GVaR, Ergodicidad.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_kelly_vs_markowitz.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def crear_plotly_dashboard() -> str:
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        return ""

    np.random.seed(42)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Ergodicidad: media sube, mediana colapsa",
            "GVaR vs VaR frecuentista",
            "Kelly: tasa geometrica vs fraccion",
            "Trayectorias: Kelly vs Full Invest (252 dias)",
        ),
        vertical_spacing=0.14, horizontal_spacing=0.08,
    )

    # Panel 1: Ergodicidad
    n_tray, n_pasos = 5000, 100
    factores = np.where(np.random.binomial(1, 0.5, (n_tray, n_pasos)), 1.5, 0.6)
    riqueza = 100 * np.cumprod(factores, axis=1)
    media = riqueza.mean(axis=0)
    mediana = np.median(riqueza, axis=0)
    pasos = list(range(1, n_pasos + 1))

    for i in range(min(30, n_tray)):
        fig.add_trace(go.Scatter(
            x=pasos, y=riqueza[i].tolist(),
            line=dict(color="rgba(150,150,150,0.08)", width=0.3),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)
    fig.add_trace(go.Scatter(x=pasos, y=media.tolist(), name="Media ensamble",
                              line=dict(color="steelblue", width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=pasos, y=mediana.tolist(), name="Mediana",
                              line=dict(color="orangered", width=2.5)), row=1, col=1)
    fig.add_hline(y=100, line_dash="dot", line_color="gray", row=1, col=1)
    fig.update_yaxes(type="log", row=1, col=1)

    # Panel 2: GVaR vs VaR
    ret_pred = np.random.normal(0.0003, 0.012, 100000) + 0.003 * np.random.standard_t(4, 100000)
    var_freq = np.mean(ret_pred) + stats.norm.ppf(0.05) * np.std(ret_pred)
    gvar = np.percentile(ret_pred, 5)

    bins_r = np.linspace(-0.08, 0.08, 80)
    counts, _ = np.histogram(ret_pred, bins=bins_r, density=True)
    centers = (bins_r[:-1] + bins_r[1:]) / 2

    fig.add_trace(go.Bar(x=centers*100, y=counts, name="Posterior predictive",
                          marker_color="rgba(70,130,180,0.5)", width=0.2,
                          showlegend=False), row=1, col=2)
    fig.add_vline(x=var_freq*100, line_dash="dash", line_color="steelblue",
                  annotation_text=f"VaR: {var_freq*100:.2f}%", row=1, col=2)
    fig.add_vline(x=gvar*100, line_dash="dash", line_color="orangered",
                  annotation_text=f"GVaR: {gvar*100:.2f}%", row=1, col=2)

    # Panel 3: Kelly curve
    fracs = np.linspace(0.01, 2.0, 100)
    tasas = [np.log(np.maximum(1 + f * ret_pred, 1e-10)).mean() for f in fracs]
    kelly_f = fracs[np.argmax(tasas)]

    fig.add_trace(go.Scatter(x=fracs.tolist(), y=tasas, name="E[log(1+fR)]",
                              line=dict(color="orangered", width=2.5)), row=2, col=1)
    fig.add_vline(x=kelly_f, line_dash="dash", line_color="green",
                  annotation_text=f"f*={kelly_f:.2f}", row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)

    # Panel 4: Trayectorias Kelly vs Full
    n_t, n_d = 200, 252
    for nombre, f, color in [("Kelly", kelly_f, "green"), ("Full", 1.0, "red")]:
        for _ in range(50):
            r = np.random.choice(ret_pred, n_d)
            w = 100000 * np.cumprod(1 + f * r)
            fig.add_trace(go.Scatter(
                x=list(range(n_d)), y=w.tolist(),
                line=dict(color=color.replace("green", "rgba(46,204,113,0.1)").replace("red", "rgba(231,76,60,0.1)"), width=0.3),
                showlegend=False, hoverinfo="skip",
            ), row=2, col=2)
    fig.add_hline(y=100000, line_dash="dot", line_color="gray", row=2, col=2)

    fig.update_layout(
        height=850, width=1000,
        title="Decisiones Probabilisticas: Kelly, GVaR y Ergodicidad",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_yaxes(title_text="Riqueza ($)", row=1, col=1)
    fig.update_xaxes(title_text="Retorno (%)", row=1, col=2)
    fig.update_xaxes(title_text="Fraccion f", row=2, col=1)
    fig.update_yaxes(title_text="Tasa geometrica", row=2, col=1)
    fig.update_xaxes(title_text="Dia", row=2, col=2)
    fig.update_yaxes(title_text="Riqueza ($)", row=2, col=2)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/kelly_decisions.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.text(0.5, 0.5, "Instala Plotly para la version interactiva",
            ha='center', va='center', fontsize=14)
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz Kelly + Decisiones...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/kelly_decisions.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
