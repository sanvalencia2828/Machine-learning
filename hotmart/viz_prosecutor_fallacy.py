"""
Visualizacion interactiva: Peligros de NHST.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_prosecutor_fallacy.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def datos_falacia_fiscal(n_estrategias=200, n_dias=252, seed=42):
    """Simula backtesting de estrategias nulas (p-hacking)."""
    np.random.seed(seed)
    p_values = []
    for _ in range(n_estrategias):
        ret = np.random.normal(0, 0.01, n_dias)
        _, p = stats.ttest_1samp(ret, 0)
        p_values.append(p)
    return np.array(p_values)


def datos_bayes_vs_pvalue(prevalencias=None):
    """Compara P(H1|data) vs p-value para diferentes tasas base."""
    if prevalencias is None:
        prevalencias = np.linspace(0.001, 0.5, 50)
    sens = 0.95  # "power" analogia
    alpha = 0.05  # false positive rate
    p_h1_dado_pos = (sens * prevalencias) / (sens * prevalencias + alpha * (1 - prevalencias))
    return prevalencias, p_h1_dado_pos


def crear_plotly_dashboard() -> str:
    """Dashboard HTML con 3 paneles."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    p_values = datos_falacia_fiscal()
    prevs, p_h1 = datos_bayes_vs_pvalue()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "P-hacking: distribucion de p-values (200 estrategias nulas)",
            "Falacia inversa: P(H1|datos) vs tasa base",
            "Falacia del fiscal: estrategias 'significativas' por azar",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: Histograma de p-values (deberia ser uniforme)
    fig.add_trace(go.Histogram(
        x=p_values, nbinsx=20, name="p-values",
        marker_color="steelblue", opacity=0.7,
    ), row=1, col=1)
    fig.add_vline(x=0.05, line_dash="dash", line_color="red",
                  annotation_text="p=0.05", row=1, col=1)

    # Panel 2: P(H1|data) vs prevalencia
    fig.add_trace(go.Scatter(
        x=prevs * 100, y=p_h1 * 100, name="P(H1 verdadera | test positivo)",
        line=dict(color="orangered", width=2),
        hovertemplate="Tasa base: %{x:.1f}%<br>P(real): %{y:.1f}%",
    ), row=1, col=2)
    fig.add_hline(y=50, line_dash="dot", line_color="gray",
                  annotation_text="50-50", row=1, col=2)
    fig.add_vline(x=5, line_dash="dot", line_color="gray",
                  annotation_text="5% tasa base", row=1, col=2)

    # Panel 3: Acumulado de "descubrimientos" falsos por N estrategias
    ns = list(range(1, 201))
    p_al_menos_1 = [1 - 0.95**n for n in ns]
    sig_esperadas = [n * 0.05 for n in ns]

    fig.add_trace(go.Scatter(
        x=ns, y=[p * 100 for p in p_al_menos_1],
        name="P(al menos 1 falso positivo)",
        line=dict(color="orangered", width=2),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=ns, y=sig_esperadas,
        name="Falsos positivos esperados (N*0.05)",
        line=dict(color="steelblue", width=2, dash="dash"),
    ), row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)

    n_sig = (p_values < 0.05).sum()
    fig.add_annotation(
        x=100, y=70,
        text=f"Con 200 estrategias nulas:<br>{n_sig} tienen p < 0.05<br>"
             f"P(>= 1 falso positivo) = {1-0.95**200:.0%}",
        showarrow=False, font=dict(size=12),
        bgcolor="rgba(255,255,255,0.8)", bordercolor="red",
        row=2, col=1,
    )

    fig.update_layout(
        height=900, width=1000,
        title="Peligros de NHST: Falacias, P-hacking y Falsos Positivos",
        template="plotly_white",
        font=dict(size=12),
    )
    fig.update_xaxes(title_text="p-value", row=1, col=1)
    fig.update_yaxes(title_text="Frecuencia", row=1, col=1)
    fig.update_xaxes(title_text="Tasa base (%)", row=1, col=2)
    fig.update_yaxes(title_text="P(H1 real | test positivo) %", row=1, col=2)
    fig.update_xaxes(title_text="N estrategias probadas", row=2, col=1)
    fig.update_yaxes(title_text="Probabilidad / Conteo", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/nhst_dangers.png"):
    """Fallback PNG."""
    import matplotlib.pyplot as plt

    p_values = datos_falacia_fiscal()
    prevs, p_h1 = datos_bayes_vs_pvalue()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(p_values, bins=20, color='steelblue', alpha=0.7)
    axes[0].axvline(0.05, color='red', ls='--', label='p=0.05')
    axes[0].set_title(f'P-values de {len(p_values)} estrategias nulas')
    axes[0].set_xlabel('p-value')
    axes[0].legend()

    axes[1].plot(prevs * 100, p_h1 * 100, 'orangered', lw=2)
    axes[1].axhline(50, ls=':', color='gray')
    axes[1].set_title('P(H1 real | test+) vs tasa base')
    axes[1].set_xlabel('Tasa base (%)')
    axes[1].set_ylabel('P(H1 real) %')

    plt.suptitle('Peligros de NHST', fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion NHST dangers...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/nhst_dangers.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
