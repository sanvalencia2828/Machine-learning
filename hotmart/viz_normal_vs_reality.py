"""
Visualizacion interactiva: Normal vs Realidad en Retornos Financieros.
Genera HTML con Plotly (3 paneles) + fallback PNG.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_normal_vs_reality.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def generar_retornos(n=5040, seed=42):
    """Genera retornos sinteticos tipo S&P 500."""
    np.random.seed(seed)
    ret = 0.0003 + 0.011 * np.random.standard_t(4, n)
    ret += -0.0003 * (np.random.exponential(1, n) - 1)
    return ret


def crear_plotly_dashboard() -> str:
    """Dashboard HTML con 3 paneles."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    ret = generar_retornos()
    mu_n, sig_n = stats.norm.fit(ret)
    nu_t, mu_t, sig_t = stats.t.fit(ret)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Histograma: datos vs Normal vs Student-t",
            "Log-scale: la diferencia en las colas",
            "Eventos extremos: observados vs Normal esperados",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: Histograma
    bins = np.linspace(-0.06, 0.06, 80)
    counts, _ = np.histogram(ret, bins=bins, density=True)
    centers = (bins[:-1] + bins[1:]) / 2
    x = np.linspace(-0.08, 0.08, 300)

    fig.add_trace(go.Bar(
        x=centers, y=counts, name="Datos (tipo S&P)",
        marker_color="rgba(150,150,150,0.5)", width=0.0015,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x, y=stats.norm.pdf(x, mu_n, sig_n),
        name="Normal MLE", line=dict(color="steelblue", width=2, dash="dash"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x, y=stats.t.pdf(x, nu_t, mu_t, sig_t),
        name=f"Student-t(nu={nu_t:.1f}) MLE",
        line=dict(color="orangered", width=2),
    ), row=1, col=1)

    # Panel 2: Log-scale
    fig.add_trace(go.Bar(
        x=centers, y=np.maximum(counts, 0.01), name="Datos",
        marker_color="rgba(150,150,150,0.5)", width=0.0015,
        showlegend=False,
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x, y=stats.norm.pdf(x, mu_n, sig_n),
        name="Normal", line=dict(color="steelblue", width=2, dash="dash"),
        showlegend=False,
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x, y=stats.t.pdf(x, nu_t, mu_t, sig_t),
        name="Student-t", line=dict(color="orangered", width=2),
        showlegend=False,
    ), row=1, col=2)
    fig.update_yaxes(type="log", range=[-2, 2], row=1, col=2)

    # Panel 3: Eventos extremos barras
    n = len(ret)
    sigmas = [2, 3, 4, 5]
    obs = [np.sum(np.abs(ret - ret.mean()) > k * ret.std()) for k in sigmas]
    esp = [2 * stats.norm.sf(k) * n for k in sigmas]
    labels = [f">{k} sigma" for k in sigmas]

    fig.add_trace(go.Bar(
        x=labels, y=esp, name="Normal predice",
        marker_color="steelblue",
        text=[f"{v:.0f}" for v in esp], textposition="outside",
    ), row=2, col=1)
    fig.add_trace(go.Bar(
        x=labels, y=obs, name="Observados",
        marker_color="orangered",
        text=[f"{v}" for v in obs], textposition="outside",
    ), row=2, col=1)

    # Ratios como anotaciones
    for i, (o, e) in enumerate(zip(obs, esp)):
        if e > 0.01:
            fig.add_annotation(
                x=labels[i], y=max(o, e) * 1.3,
                text=f"{o/e:.0f}x", showarrow=False,
                font=dict(size=12, color="red", weight="bold"),
                row=2, col=1,
            )

    fig.update_layout(
        height=900, width=1000,
        title="Normal vs Realidad: retornos financieros NO son gaussianos",
        template="plotly_white",
        barmode="group",
        font=dict(size=12),
    )
    fig.update_xaxes(title_text="Retorno diario", row=1, col=1)
    fig.update_xaxes(title_text="Retorno diario (log-y)", row=1, col=2)
    fig.update_yaxes(title_text="Frecuencia", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/normal_vs_reality.png"):
    """Fallback PNG."""
    import matplotlib.pyplot as plt

    ret = generar_retornos()
    mu_n, sig_n = stats.norm.fit(ret)
    nu_t, mu_t, sig_t = stats.t.fit(ret)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    bins = np.linspace(-0.06, 0.06, 60)
    x = np.linspace(-0.08, 0.08, 300)

    axes[0].hist(ret, bins, density=True, alpha=0.4, color='gray', label='Datos')
    axes[0].plot(x, stats.norm.pdf(x, mu_n, sig_n), 'steelblue', ls='--', lw=2, label='Normal')
    axes[0].plot(x, stats.t.pdf(x, nu_t, mu_t, sig_t), 'orangered', lw=2, label='Student-t')
    axes[0].set_title('Normal vs Student-t')
    axes[0].legend()

    axes[1].hist(ret, bins, density=True, alpha=0.4, color='gray')
    axes[1].plot(x, stats.norm.pdf(x, mu_n, sig_n), 'steelblue', ls='--', lw=2)
    axes[1].plot(x, stats.t.pdf(x, nu_t, mu_t, sig_t), 'orangered', lw=2)
    axes[1].set_yscale('log')
    axes[1].set_title('Log-scale: colas')
    axes[1].set_ylim(0.01, 100)

    plt.suptitle('Normal vs Realidad', fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion Normal vs Realidad...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/normal_vs_reality.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
