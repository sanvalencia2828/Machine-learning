"""
Visualizacion: PLE Aplicado -- 4 Aplicaciones Financieras.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_ple_applied.py
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

    np.random.seed(42)
    # Posteriors simulados
    alpha_mu, alpha_sig = 0.00005, 0.0005
    beta_mu, beta_sig = 1.20, 0.06

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Jensen's Alpha: P(alpha > 0)",
            "Cross-Hedging: distribucion de beta",
            "Cost of Equity: CAPM probabilistico",
            "Market Neutral: P(|beta| < umbral)",
        ),
        vertical_spacing=0.14, horizontal_spacing=0.08,
    )

    # Panel 1: Alpha posterior
    x_a = np.linspace(-0.002, 0.002, 200)
    pdf_a = stats.norm.pdf(x_a, alpha_mu, alpha_sig)
    p_pos = 1 - stats.norm.cdf(0, alpha_mu, alpha_sig)

    fig.add_trace(go.Scatter(
        x=x_a*100, y=pdf_a, name=f"Posterior alpha",
        line=dict(color="orangered", width=2),
        fill="tozeroy", fillcolor="rgba(255,69,0,0.15)",
    ), row=1, col=1)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", row=1, col=1)
    fig.add_annotation(x=0.1, y=max(pdf_a)*0.7,
                       text=f"P(alpha>0) = {p_pos:.0%}",
                       showarrow=False, font=dict(size=13, color="orangered"),
                       row=1, col=1)

    # Panel 2: Beta posterior for hedging
    x_b = np.linspace(0.9, 1.5, 200)
    pdf_b = stats.norm.pdf(x_b, beta_mu, beta_sig)

    fig.add_trace(go.Scatter(
        x=x_b, y=pdf_b, name="Posterior beta",
        line=dict(color="steelblue", width=2),
        fill="tozeroy", fillcolor="rgba(70,130,180,0.15)",
    ), row=1, col=2)
    hdi_b = (beta_mu - 1.96*beta_sig, beta_mu + 1.96*beta_sig)
    fig.add_annotation(x=beta_mu, y=max(pdf_b)*0.8,
                       text=f"Hedge ratio HDI:<br>({hdi_b[0]:.2f}, {hdi_b[1]:.2f})",
                       showarrow=False, font=dict(size=11),
                       row=1, col=2)

    # Panel 3: Cost of equity
    betas_s = np.random.normal(beta_mu, beta_sig, 50000)
    r_e = 0.045 + betas_s * 0.06
    hist_c, hist_e = np.histogram(r_e*100, bins=50, density=True)
    hist_centers = (hist_e[:-1] + hist_e[1:]) / 2

    fig.add_trace(go.Bar(
        x=hist_centers, y=hist_c, name="r_e distribucion",
        marker_color="rgba(46,204,113,0.6)",
        width=hist_centers[1]-hist_centers[0],
    ), row=2, col=1)
    re_ols = (0.045 + 1.20 * 0.06) * 100
    fig.add_vline(x=re_ols, line_dash="dash", line_color="steelblue",
                  annotation_text=f"OLS: {re_ols:.1f}%", row=2, col=1)

    # Panel 4: Market neutral test
    umbrales = np.linspace(0.01, 0.5, 50)
    p_neutral_beta12 = [stats.norm.cdf(u, beta_mu, beta_sig) -
                        stats.norm.cdf(-u, beta_mu, beta_sig) for u in umbrales]
    # Fondo "neutral" con beta~0.05
    p_neutral_low = [stats.norm.cdf(u, 0.05, 0.08) -
                     stats.norm.cdf(-u, 0.05, 0.08) for u in umbrales]

    fig.add_trace(go.Scatter(
        x=umbrales, y=[p*100 for p in p_neutral_beta12],
        name="Fondo beta=1.2", line=dict(color="#e74c3c", width=2),
    ), row=2, col=2)
    fig.add_trace(go.Scatter(
        x=umbrales, y=[p*100 for p in p_neutral_low],
        name="Fondo beta=0.05", line=dict(color="#2ecc71", width=2),
    ), row=2, col=2)
    fig.add_hline(y=90, line_dash="dot", line_color="gray",
                  annotation_text="90% confianza", row=2, col=2)

    fig.update_layout(
        height=800, width=1000,
        title="PLE Aplicado: 4 Preguntas Financieras que OLS No Responde",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_xaxes(title_text="alpha (%)", row=1, col=1)
    fig.update_xaxes(title_text="beta (hedge ratio)", row=1, col=2)
    fig.update_xaxes(title_text="Cost of equity (%)", row=2, col=1)
    fig.update_xaxes(title_text="Umbral |beta|", row=2, col=2)
    fig.update_yaxes(title_text="P(|beta| < umbral) %", row=2, col=2)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/ple_applied.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.linspace(-0.002, 0.002, 200)
    ax.plot(x*100, stats.norm.pdf(x, 0.00005, 0.0005), 'orangered', lw=2)
    ax.axvline(0, ls='--', color='gray')
    ax.set_title("Jensen's Alpha Posterior")
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz PLE Applied...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/ple_applied.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
