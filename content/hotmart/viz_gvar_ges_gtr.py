"""
Visualizacion: GVaR, GES y GTR sobre distribucion de retornos.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_gvar_ges_gtr.py
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
    n = 50000
    mu_p = np.random.normal(0.0004, 0.0003, n)
    sig_p = np.abs(np.random.normal(0.013, 0.002, n))
    nu_p = np.clip(np.random.exponential(4, n) + 2, 2.5, 100)
    ret = np.array([m + s * np.random.standard_t(max(v, 2.5))
                    for m, s, v in zip(mu_p, sig_p, nu_p)])

    gvar = np.percentile(ret, 5)
    ges = ret[ret <= gvar].mean()
    gtr = ret.min()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Distribucion + GVaR/GES/GTR",
            "Zoom en cola izquierda",
            "GVaR y GES por nivel de confianza",
            "Impacto en dolares ($1M capital)",
        ),
        vertical_spacing=0.14, horizontal_spacing=0.08,
    )

    # Panel 1: Histograma completo
    bins = np.linspace(-0.12, 0.12, 100)
    counts, edges = np.histogram(ret, bins=bins, density=True)
    centers = (edges[:-1] + edges[1:]) / 2

    fig.add_trace(go.Bar(x=centers*100, y=counts, name="Posterior pred",
                          marker_color="rgba(70,130,180,0.5)", width=0.25), row=1, col=1)
    fig.add_vline(x=gvar*100, line_dash="dash", line_color="#e74c3c",
                  annotation_text=f"GVaR: {gvar*100:.2f}%", row=1, col=1)
    fig.add_vline(x=ges*100, line_dash="dash", line_color="#f39c12",
                  annotation_text=f"GES: {ges*100:.2f}%", row=1, col=1)
    fig.add_vline(x=gtr*100, line_dash="dash", line_color="#8e44ad",
                  annotation_text=f"GTR: {gtr*100:.1f}%", row=1, col=1)

    # Panel 2: Zoom cola
    mask = ret < gvar
    bins_z = np.linspace(ret.min(), gvar, 40)
    counts_z, _ = np.histogram(ret[mask], bins=bins_z, density=True)
    centers_z = (bins_z[:-1] + bins_z[1:]) / 2

    fig.add_trace(go.Bar(x=centers_z*100, y=counts_z, name="Cola (<GVaR)",
                          marker_color="rgba(231,76,60,0.6)", width=0.15,
                          showlegend=False), row=1, col=2)
    fig.add_vline(x=ges*100, line_dash="dash", line_color="#f39c12", row=1, col=2)
    fig.add_annotation(x=ges*100, y=max(counts_z)*0.8,
                       text=f"GES = media de esta area<br>{ges*100:.2f}%",
                       showarrow=True, arrowhead=2, font=dict(size=11),
                       row=1, col=2)

    # Panel 3: GVaR/GES por nivel
    niveles = np.array([0.10, 0.05, 0.025, 0.01, 0.005])
    gvars = [np.percentile(ret, a*100) for a in niveles]
    gess = [ret[ret <= g].mean() for g in gvars]

    fig.add_trace(go.Scatter(
        x=(1-niveles)*100, y=[g*100 for g in gvars],
        name="GVaR", line=dict(color="#e74c3c", width=2.5),
        mode="lines+markers", marker=dict(size=8),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=(1-niveles)*100, y=[g*100 for g in gess],
        name="GES", line=dict(color="#f39c12", width=2.5),
        mode="lines+markers", marker=dict(size=8),
    ), row=2, col=1)

    # Panel 4: Dolares
    capital = 1_000_000
    metricas = ["GVaR 95%", "GES 95%", "GTR"]
    valores = [abs(gvar)*capital, abs(ges)*capital, abs(gtr)*capital]
    colores_bar = ["#e74c3c", "#f39c12", "#8e44ad"]

    fig.add_trace(go.Bar(
        x=metricas, y=valores, name="Perdida ($)",
        marker_color=colores_bar,
        text=[f"${v:,.0f}" for v in valores],
        textposition="outside", showlegend=False,
    ), row=2, col=2)

    fig.update_layout(
        height=850, width=1000,
        title="GVaR, GES y GTR: Metricas Generativas de Riesgo",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_xaxes(title_text="Retorno (%)", row=1, col=1)
    fig.update_xaxes(title_text="Retorno (%) -- cola", row=1, col=2)
    fig.update_xaxes(title_text="Nivel de confianza (%)", row=2, col=1)
    fig.update_yaxes(title_text="Retorno (%)", row=2, col=1)
    fig.update_yaxes(title_text="Perdida ($)", row=2, col=2)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/gvar_ges_gtr.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    np.random.seed(42)
    ret = 0.0004 + 0.013 * np.random.standard_t(4, 50000)
    ax.hist(ret*100, bins=80, density=True, alpha=0.5, color='steelblue')
    gvar = np.percentile(ret, 5)
    ax.axvline(gvar*100, color='red', ls='--', label=f'GVaR: {gvar*100:.2f}%')
    ax.set_title('GVaR, GES, GTR')
    ax.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz GVaR/GES/GTR...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/gvar_ges_gtr.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
