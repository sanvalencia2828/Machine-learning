"""
Visualizacion: MLE Falla con Pocos Datos -- Caso ZYX.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_zyx_mle_failure.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def crear_plotly_dashboard() -> str:
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    x = np.linspace(0.01, 0.99, 300)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "MLE (punto p=100%) vs PML (distribucion)",
            "Actualizacion secuencial: 8 trimestres",
            "Prediccion: beats en proximos 4 trimestres",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: MLE vs PML
    posterior_3 = stats.beta(4, 1)
    fig.add_trace(go.Scatter(
        x=x*100, y=stats.beta(1,1).pdf(x),
        name="Prior Uniforme", line=dict(color="gray", dash="dot", width=1.5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x*100, y=posterior_3.pdf(x),
        name="Posterior Beta(4,1): 80%", line=dict(color="orangered", width=2.5),
    ), row=1, col=1)
    fig.add_vline(x=100, line_dash="dash", line_color="steelblue",
                  annotation_text="MLE: p=100%", row=1, col=1)

    # Panel 2: Secuencial
    resultados = [1, 1, 1, 1, 1, 0, 1, 1]
    a, b = 1, 1
    medias_pml, hdi_lo, hdi_hi, medias_mle = [], [], [], []
    k_a, n_a = 0, 0
    for r in resultados:
        k_a += r; n_a += 1
        a += r; b += (1-r)
        post = stats.beta(a, b)
        medias_pml.append(post.mean())
        hdi = post.ppf([0.025, 0.975])
        hdi_lo.append(hdi[0])
        hdi_hi.append(hdi[1])
        medias_mle.append(k_a / n_a)

    pasos = list(range(1, 9))
    labels = [f"Q{i}" + (" MISS" if resultados[i-1]==0 else "") for i in pasos]

    fig.add_trace(go.Scatter(
        x=pasos, y=[m*100 for m in medias_pml],
        name="PML media", line=dict(color="orangered", width=2.5),
        mode="lines+markers", marker=dict(size=8),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=pasos+pasos[::-1],
        y=[h*100 for h in hdi_hi]+[h*100 for h in hdi_lo][::-1],
        fill="toself", fillcolor="rgba(255,69,0,0.15)",
        line=dict(color="rgba(0,0,0,0)"), name="HDI 95%",
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=pasos, y=[m*100 for m in medias_mle],
        name="MLE", line=dict(color="steelblue", dash="dash", width=2),
        mode="lines+markers", marker=dict(size=6, symbol="square"),
    ), row=1, col=2)
    fig.add_vline(x=6, line_dash="dot", line_color="red",
                  annotation_text="MISS!", row=1, col=2)

    # Panel 3: Predictiva
    np.random.seed(42)
    n_sim = 50000
    theta_post = np.random.beta(8, 2, n_sim)
    beats_pml = np.array([np.random.binomial(4, t) for t in theta_post])
    beats_mle = np.random.binomial(4, 7/8, n_sim)

    vals = [0, 1, 2, 3, 4]
    probs_pml = [(beats_pml==v).mean() for v in vals]
    probs_mle = [(beats_mle==v).mean() for v in vals]

    fig.add_trace(go.Bar(
        x=[str(v) for v in vals], y=[p*100 for p in probs_mle],
        name="MLE predictive", marker_color="steelblue", opacity=0.7,
        text=[f"{p:.0%}" for p in probs_mle], textposition="outside",
    ), row=2, col=1)
    fig.add_trace(go.Bar(
        x=[str(v) for v in vals], y=[p*100 for p in probs_pml],
        name="PML predictive", marker_color="orangered", opacity=0.7,
        text=[f"{p:.0%}" for p in probs_pml], textposition="outside",
    ), row=2, col=1)

    fig.update_layout(
        height=900, width=1000,
        title="MLE Falla con Pocos Datos: Caso ZYX (Earnings Beats)",
        template="plotly_white", font=dict(size=12),
        barmode="group",
    )
    fig.update_xaxes(title_text="P(beat) %", row=1, col=1)
    fig.update_xaxes(title_text="Trimestre", row=1, col=2)
    fig.update_yaxes(title_text="P(beat) %", row=1, col=2)
    fig.update_xaxes(title_text="Numero de beats (de 4)", row=2, col=1)
    fig.update_yaxes(title_text="Probabilidad (%)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/zyx_mle_failure.png"):
    import matplotlib.pyplot as plt
    x = np.linspace(0.01, 0.99, 300)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x*100, stats.beta(4,1).pdf(x), 'orangered', lw=2, label='PML Beta(4,1)')
    ax.axvline(100, color='steelblue', ls='--', lw=2, label='MLE: p=100%')
    ax.set_title('MLE vs PML: Caso ZYX')
    ax.set_xlabel('P(beat) %')
    ax.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion ZYX MLE Failure...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/zyx_mle_failure.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
