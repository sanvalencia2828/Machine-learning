"""
Visualizacion: Framework PML -- Prior, Posterior y Prediccion de Default.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_debt_default_updating.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def crear_plotly_dashboard() -> str:
    """Dashboard con 3 paneles: prior vs posterior, actualizacion secuencial, predictivas."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    x = np.linspace(0.001, 0.5, 300)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Prior vs Posterior: P(default) de bonos high-yield",
            "Actualizacion secuencial (trimestral)",
            "Distribucion Predictiva: defaults en proximos 20 bonos",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: Prior vs Posterior
    prior = stats.beta(2, 8)
    posterior = stats.beta(5, 25)

    fig.add_trace(go.Scatter(
        x=x * 100, y=prior.pdf(x),
        name="Prior Beta(2,8)", line=dict(color="gray", dash="dash", width=2),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x * 100, y=posterior.pdf(x),
        name="Posterior Beta(5,25)", line=dict(color="orangered", width=2),
    ), row=1, col=1)
    # HDI posterior
    hdi_lo, hdi_hi = posterior.ppf(0.025), posterior.ppf(0.975)
    mask = (x >= hdi_lo) & (x <= hdi_hi)
    fig.add_trace(go.Scatter(
        x=x[mask] * 100, y=posterior.pdf(x[mask]),
        fill="tozeroy", fillcolor="rgba(255,69,0,0.2)",
        line=dict(color="rgba(0,0,0,0)"),
        name=f"HDI 95%: ({hdi_lo*100:.1f}%, {hdi_hi*100:.1f}%)",
    ), row=1, col=1)

    # Panel 2: Actualizacion secuencial
    actualizaciones = [
        ("Prior", 2, 8),
        ("Q1: 3/20 defaults", 5, 25),
        ("Q2: +1/20", 6, 44),
        ("Q3: +0/20", 6, 64),
        ("Q4: +2/20", 8, 82),
    ]
    colores_seq = ["gray", "#e74c3c", "#f39c12", "#2ecc71", "#3498db"]
    for (nombre, a, b_param), color in zip(actualizaciones, colores_seq):
        dist = stats.beta(a, b_param)
        fig.add_trace(go.Scatter(
            x=x * 100, y=dist.pdf(x),
            name=f"{nombre} ({a/(a+b_param)*100:.1f}%)",
            line=dict(color=color, width=2, dash="dash" if nombre == "Prior" else "solid"),
        ), row=1, col=2)

    # Panel 3: Prior predictive vs Posterior predictive
    np.random.seed(42)
    n_sim = 50000
    n_bonos = 20

    # Prior predictive
    theta_prior = np.random.beta(2, 8, n_sim)
    defaults_prior = np.array([np.random.binomial(n_bonos, t) for t in theta_prior])

    # Posterior predictive
    theta_post = np.random.beta(5, 25, n_sim)
    defaults_post = np.array([np.random.binomial(n_bonos, t) for t in theta_post])

    vals = np.arange(0, n_bonos + 1)
    counts_prior = np.array([(defaults_prior == v).mean() for v in vals])
    counts_post = np.array([(defaults_post == v).mean() for v in vals])

    fig.add_trace(go.Bar(
        x=vals, y=counts_prior * 100, name="Prior predictive",
        marker_color="rgba(150,150,150,0.5)", width=0.4,
        offset=-0.2,
    ), row=2, col=1)
    fig.add_trace(go.Bar(
        x=vals, y=counts_post * 100, name="Posterior predictive",
        marker_color="rgba(255,69,0,0.6)", width=0.4,
        offset=0.2,
    ), row=2, col=1)

    fig.update_layout(
        height=900, width=1000,
        title="Framework PML: Prior, Posterior y Prediccion de Default",
        template="plotly_white",
        font=dict(size=12),
        barmode="overlay",
    )
    fig.update_xaxes(title_text="P(default) %", row=1, col=1)
    fig.update_yaxes(title_text="Densidad", row=1, col=1)
    fig.update_xaxes(title_text="P(default) %", row=1, col=2)
    fig.update_xaxes(title_text="Numero de defaults (de 20 bonos)", row=2, col=1)
    fig.update_yaxes(title_text="Probabilidad (%)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/pml_framework.png"):
    """Fallback PNG."""
    import matplotlib.pyplot as plt

    x = np.linspace(0.001, 0.5, 300)
    prior = stats.beta(2, 8)
    posterior = stats.beta(5, 25)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(x * 100, prior.pdf(x), 'gray', ls='--', lw=2, label='Prior')
    axes[0].plot(x * 100, posterior.pdf(x), 'orangered', lw=2, label='Posterior')
    axes[0].set_title('Prior vs Posterior')
    axes[0].set_xlabel('P(default) %')
    axes[0].legend()

    # Secuencial
    for nombre, a, b in [("Prior", 2, 8), ("Q1", 5, 25), ("Q2", 6, 44), ("Q4", 8, 82)]:
        axes[1].plot(x * 100, stats.beta(a, b).pdf(x), lw=2, label=f'{nombre} ({a/(a+b)*100:.0f}%)')
    axes[1].set_title('Actualizacion Secuencial')
    axes[1].legend()

    plt.suptitle('Framework PML', fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion PML Framework...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/pml_framework.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
