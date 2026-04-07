"""
Visualizacion interactiva: Monte Carlo Simulation y Fat Tails.
Genera HTML con Plotly (3 paneles) + fallback PNG con Matplotlib.
source_ref: turn0browsertab744690698

Requisitos: numpy, scipy, plotly (o matplotlib)
Ejecutar: python hotmart/viz_sp500_fat_tails.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


# ================================================================
# Datos sinteticos
# ================================================================

def generar_retornos_sinteticos(n=2520, seed=42):
    """Genera retornos sinteticos que simulan S&P 500 (10 anos).

    Usa Student-t(nu=4) para capturar fat tails reales.
    """
    np.random.seed(seed)
    mu_diario = 0.0004
    sigma_diario = 0.012
    retornos = mu_diario + sigma_diario * np.random.standard_t(4, n)
    return retornos


def calcular_convergencia_pi(ns=None, seed=42):
    """Estima Pi con MCS para diferentes N."""
    if ns is None:
        ns = [10, 50, 100, 500, 1000, 5000, 10000, 50000]
    np.random.seed(seed)
    x = np.random.uniform(-1, 1, max(ns))
    y = np.random.uniform(-1, 1, max(ns))
    dentro = x**2 + y**2 <= 1
    estimaciones = [4 * dentro[:n].mean() for n in ns]
    return ns, estimaciones


def simular_proyecto_npv(n_sim=50000, seed=42):
    """MCS para NPV de proyecto de software."""
    np.random.seed(seed)
    # Factores de riesgo
    costo = np.random.triangular(50000, 80000, 120000, n_sim)
    meses = np.random.lognormal(np.log(12), 0.3, n_sim)
    adopcion = np.random.beta(2, 5, n_sim)
    ingreso_por_user = np.random.normal(50, 15, n_sim)
    ingreso_por_user = np.clip(ingreso_por_user, 10, None)

    mercado_potencial = 10000
    usuarios = mercado_potencial * adopcion
    ingresos_anuales = usuarios * ingreso_por_user
    # Discount rate 10%, horizonte 3 anos, delay penalty
    factor_delay = np.exp(-0.1 * meses / 12)
    npv = ingresos_anuales * 2.5 * factor_delay - costo

    return npv


# ================================================================
# Plotly dashboard
# ================================================================

def crear_plotly_dashboard() -> str:
    """Dashboard HTML con 3 paneles interactivos."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado. Usa: pip install plotly")
        return ""

    retornos = generar_retornos_sinteticos()
    ns, pi_est = calcular_convergencia_pi()
    npvs = simular_proyecto_npv()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Fat Tails: Normal vs Student-t (retornos diarios)",
            "Convergencia MCS: estimacion de Pi",
            "MCS Aplicado: distribucion de NPV de proyecto",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: Histograma Normal vs fat tails
    bins = np.linspace(-0.06, 0.06, 80)
    counts_real, _ = np.histogram(retornos, bins=bins, density=True)
    normal_pdf = stats.norm.pdf((bins[:-1]+bins[1:])/2, retornos.mean(), retornos.std())
    bin_centers = (bins[:-1] + bins[1:]) / 2

    fig.add_trace(go.Bar(
        x=bin_centers, y=counts_real, name="Retornos sinteticos (fat tails)",
        marker_color="rgba(255,69,0,0.5)", width=0.0015,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=bin_centers, y=normal_pdf, name="Normal ajustada",
        line=dict(color="steelblue", width=2, dash="dash"),
    ), row=1, col=1)

    # Panel 2: Convergencia Pi
    fig.add_trace(go.Scatter(
        x=ns, y=pi_est, name="Estimacion MCS",
        mode="lines+markers", line=dict(color="orangered", width=2),
        marker=dict(size=8),
        hovertemplate="N=%{x}: Pi~%{y:.4f}",
    ), row=1, col=2)
    fig.add_hline(y=np.pi, line_dash="dot", line_color="steelblue",
                  annotation_text=f"Pi real: {np.pi:.5f}", row=1, col=2)

    # Panel 3: NPV distribucion
    bins_npv = np.linspace(npvs.min(), np.percentile(npvs, 99), 80)
    counts_npv, edges_npv = np.histogram(npvs, bins=bins_npv)
    centers_npv = (edges_npv[:-1] + edges_npv[1:]) / 2
    colores_npv = ["rgba(231,76,60,0.6)" if c < 0 else "rgba(46,204,113,0.6)"
                   for c in centers_npv]

    fig.add_trace(go.Bar(
        x=centers_npv, y=counts_npv, name="NPV",
        marker_color=colores_npv, showlegend=False,
    ), row=2, col=1)

    p_exito = (npvs > 0).mean()
    var_95 = np.percentile(npvs, 5)
    media_npv = npvs.mean()

    fig.add_vline(x=0, line_dash="dash", line_color="black", row=2, col=1)
    fig.add_vline(x=media_npv, line_dash="dot", line_color="steelblue",
                  annotation_text=f"Media: ${media_npv:,.0f}", row=2, col=1)
    fig.add_vline(x=var_95, line_dash="dot", line_color="red",
                  annotation_text=f"VaR 5%: ${var_95:,.0f}", row=2, col=1)
    fig.add_annotation(
        x=np.percentile(npvs, 75), y=max(counts_npv) * 0.8,
        text=f"P(NPV>0) = {p_exito:.1%}",
        showarrow=False, font=dict(size=14, color="green"),
        row=2, col=1,
    )

    fig.update_layout(
        height=900, width=1000,
        title="Simulacion Monte Carlo: Fat Tails, Convergencia y Valoracion",
        template="plotly_white",
        font=dict(size=12),
        legend=dict(x=0.01, y=0.99),
    )
    fig.update_xaxes(title_text="Retorno diario", row=1, col=1)
    fig.update_yaxes(title_text="Densidad", row=1, col=1)
    fig.update_xaxes(title_text="N (simulaciones)", type="log", row=1, col=2)
    fig.update_yaxes(title_text="Estimacion de Pi", row=1, col=2)
    fig.update_xaxes(title_text="NPV ($)", row=2, col=1)
    fig.update_yaxes(title_text="Frecuencia", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


# ================================================================
# Matplotlib fallback
# ================================================================

def crear_matplotlib_fallback(output_path="data/mcs_fat_tails.png"):
    """Version estatica PNG."""
    import matplotlib.pyplot as plt

    retornos = generar_retornos_sinteticos()
    ns, pi_est = calcular_convergencia_pi()
    npvs = simular_proyecto_npv()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1
    bins = np.linspace(-0.06, 0.06, 60)
    axes[0, 0].hist(retornos, bins, density=True, alpha=0.5, color='orangered',
                    label='Fat tails')
    x_n = np.linspace(-0.06, 0.06, 200)
    axes[0, 0].plot(x_n, stats.norm.pdf(x_n, retornos.mean(), retornos.std()),
                    'steelblue', ls='--', lw=2, label='Normal')
    axes[0, 0].set_title('Fat Tails vs Normal')
    axes[0, 0].legend()

    # Panel 2
    axes[0, 1].semilogx(ns, pi_est, 'orangered', marker='o', lw=2)
    axes[0, 1].axhline(np.pi, ls=':', color='steelblue')
    axes[0, 1].set_title('Convergencia MCS (Pi)')
    axes[0, 1].set_ylabel('Pi estimado')

    # Panel 3
    axes[1, 0].remove()
    axes[1, 1].remove()
    ax3 = fig.add_subplot(2, 1, 2)
    ax3.hist(npvs[npvs < 0], bins=40, color='#e74c3c', alpha=0.7, label='NPV < 0')
    ax3.hist(npvs[npvs >= 0], bins=40, color='#2ecc71', alpha=0.7, label='NPV >= 0')
    ax3.axvline(0, color='black', ls='--')
    ax3.axvline(npvs.mean(), color='steelblue', ls=':',
                label=f'Media: ${npvs.mean():,.0f}')
    ax3.set_title(f'NPV Proyecto (P(NPV>0)={(npvs>0).mean():.1%})')
    ax3.set_xlabel('NPV ($)')
    ax3.legend()

    plt.suptitle('Monte Carlo Simulation', fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion MCS + Fat Tails...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/mcs_fat_tails.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
