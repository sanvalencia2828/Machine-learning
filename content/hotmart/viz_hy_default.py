"""
Visualizacion: Default de Bonos High-Yield con Actualizacion Bayesiana.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_hy_default.py
"""
import numpy as np
from scipy import stats
from pathlib import Path

RATING_PRIORS = {"BBB": (2, 18), "BB": (3, 12), "B": (4, 8), "CCC": (5, 5)}
EVENTS = {"downgrade": (1, 0), "upgrade": (0, 2), "neutral": (0, 1)}


def actualizar(a, b, eventos):
    tray = [{"a": a, "b": b}]
    for ev in eventos:
        da, db = EVENTS[ev]
        a += da; b += db
        tray.append({"a": a, "b": b, "evento": ev})
    return tray


def crear_plotly_dashboard() -> str:
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    x = np.linspace(0.001, 0.6, 200)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Priors por Rating Crediticio",
            "MegaCorp: P(default) por trimestre",
            "Portafolio: Distribucion Predictiva de Defaults",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: Priors
    colores_r = {"BBB": "#2ecc71", "BB": "#f39c12", "B": "#e74c3c", "CCC": "#8e44ad"}
    for rating, (a, b) in RATING_PRIORS.items():
        fig.add_trace(go.Scatter(
            x=x*100, y=stats.beta(a, b).pdf(x),
            name=f"{rating} ({a/(a+b)*100:.0f}%)",
            line=dict(color=colores_r[rating], width=2),
        ), row=1, col=1)

    # Panel 2: MegaCorp secuencial
    a0, b0 = RATING_PRIORS["BB"]
    eventos = ["neutral", "downgrade", "neutral", "downgrade",
               "neutral", "neutral", "upgrade", "neutral"]
    tray = actualizar(a0, b0, eventos)

    pasos = list(range(len(tray)))
    medias = [t["a"]/(t["a"]+t["b"]) for t in tray]
    hdi_lo = [stats.beta(t["a"], t["b"]).ppf(0.025) for t in tray]
    hdi_hi = [stats.beta(t["a"], t["b"]).ppf(0.975) for t in tray]

    fig.add_trace(go.Scatter(
        x=pasos, y=[m*100 for m in medias],
        name="P(default)", line=dict(color="orangered", width=2),
        mode="lines+markers", marker=dict(size=10),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=pasos+pasos[::-1],
        y=[h*100 for h in hdi_hi]+[h*100 for h in hdi_lo][::-1],
        fill="toself", fillcolor="rgba(255,69,0,0.15)",
        line=dict(color="rgba(0,0,0,0)"), name="HDI 95%",
    ), row=1, col=2)

    # Panel 3: Portafolio predictive
    np.random.seed(42)
    bonos = []
    for _ in range(15):
        rat = np.random.choice(["BB", "B", "BBB"], p=[0.5, 0.3, 0.2])
        a, b = RATING_PRIORS.get(rat, (3, 12))
        evts = np.random.choice(["neutral", "downgrade", "upgrade"],
                                 np.random.randint(2, 8), p=[0.5, 0.35, 0.15])
        for e in evts:
            da, db = EVENTS[e]
            a += da; b += db
        bonos.append({"a": a, "b": b})

    n_sim = 50000
    defaults = np.zeros(n_sim, dtype=int)
    for bo in bonos:
        theta = np.random.beta(bo["a"], bo["b"], n_sim)
        defaults += (np.random.random(n_sim) < theta).astype(int)

    vals = np.arange(0, defaults.max()+1)
    probs = [(defaults == v).mean() for v in vals]
    colors = ["#2ecc71" if v <= 2 else "#f39c12" if v <= 4 else "#e74c3c" for v in vals]

    fig.add_trace(go.Bar(
        x=vals, y=[p*100 for p in probs], name="Defaults",
        marker_color=colors, showlegend=False,
        text=[f"{p:.1%}" if p > 0.01 else "" for p in probs],
        textposition="outside",
    ), row=2, col=1)

    p3 = (defaults >= 3).mean()
    fig.add_annotation(
        x=5, y=max(probs)*100*0.8,
        text=f"P(3+ defaults) = {p3:.1%}<br>Media = {defaults.mean():.1f}",
        showarrow=False, font=dict(size=13), bgcolor="white",
        row=2, col=1,
    )

    fig.update_layout(
        height=900, width=1000,
        title="Inferencia Bayesiana: Default de Bonos High-Yield",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_xaxes(title_text="P(default) %", row=1, col=1)
    fig.update_xaxes(title_text="Trimestre", row=1, col=2)
    fig.update_yaxes(title_text="P(default) %", row=1, col=2)
    fig.update_xaxes(title_text="Numero de defaults", row=2, col=1)
    fig.update_yaxes(title_text="Probabilidad (%)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/hy_default.png"):
    import matplotlib.pyplot as plt
    x = np.linspace(0.001, 0.6, 200)
    fig, ax = plt.subplots(figsize=(10, 5))
    for r, (a, b) in RATING_PRIORS.items():
        ax.plot(x*100, stats.beta(a, b).pdf(x), lw=2, label=f'{r}')
    ax.set_title('Priors por Rating')
    ax.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion HY Default...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/hy_default.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
