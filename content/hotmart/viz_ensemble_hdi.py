"""
Visualizacion: Ensambles Generativos y HDI.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_ensemble_hdi.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def generar_datos(n=252, seed=42):
    np.random.seed(seed)
    r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_asset = 0.0002 + 1.25 * r_mkt + 0.010 * np.random.standard_t(4, n)
    X = np.column_stack([np.ones(n), r_mkt])
    b = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    res = r_asset - X @ b
    se = np.sqrt(np.sum(res**2)/(n-2) * np.diag(np.linalg.inv(X.T @ X)))
    return r_mkt, r_asset, b, se


def crear_plotly_dashboard() -> str:
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    r_mkt, r_asset, b, se = generar_datos()
    np.random.seed(42)

    # Posteriors aproximados
    alpha_mu = b[0] * 0.3  # shrunk by prior
    alpha_sig = se[0] * 0.8
    beta_mu = (b[1] * se[1]**-2 + 1.0 * 0.5**-2) / (se[1]**-2 + 0.5**-2)
    beta_sig = 1 / np.sqrt(se[1]**-2 + 0.5**-2)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Ensamble Generativo: 100 lineas de regresion",
            "Posterior de beta: OLS vs Bayesiano",
            "Prediccion: distribucion predictiva para 3 escenarios",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: Spaghetti plot
    fig.add_trace(go.Scatter(
        x=r_mkt*100, y=r_asset*100, mode="markers",
        marker=dict(color="gray", size=3, opacity=0.3),
        name="Datos", showlegend=True,
    ), row=1, col=1)

    x_line = np.linspace(r_mkt.min(), r_mkt.max(), 100)
    for i in range(100):
        a_i = np.random.normal(alpha_mu, alpha_sig)
        b_i = np.random.normal(beta_mu, beta_sig)
        y_i = a_i + b_i * x_line
        fig.add_trace(go.Scatter(
            x=x_line*100, y=y_i*100,
            line=dict(color="rgba(255,69,0,0.08)", width=0.5),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)

    # OLS line
    fig.add_trace(go.Scatter(
        x=x_line*100, y=(b[0]+b[1]*x_line)*100,
        name="OLS", line=dict(color="steelblue", width=2.5, dash="dash"),
    ), row=1, col=1)

    # Panel 2: Posterior de beta
    x_beta = np.linspace(0.5, 2.0, 200)
    freq_pdf = stats.norm.pdf(x_beta, b[1], se[1])
    bayes_pdf = stats.norm.pdf(x_beta, beta_mu, beta_sig)

    fig.add_trace(go.Scatter(
        x=x_beta, y=freq_pdf / freq_pdf.max(),
        name="OLS (likelihood)", line=dict(color="steelblue", dash="dash", width=2),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x_beta, y=bayes_pdf / bayes_pdf.max(),
        name="Posterior bayesiano", line=dict(color="orangered", width=2),
    ), row=1, col=2)
    fig.add_vline(x=1.0, line_dash="dot", line_color="gray",
                  annotation_text="beta=1", row=1, col=2)
    p_gt1 = 1 - stats.norm.cdf(1.0, beta_mu, beta_sig)
    fig.add_annotation(
        x=1.5, y=0.5, text=f"P(beta>1) = {p_gt1:.0%}",
        showarrow=False, font=dict(size=13, color="orangered"),
        row=1, col=2,
    )

    # Panel 3: Prediccion 3 escenarios
    sigma_res = np.std(r_asset - (b[0] + b[1] * r_mkt))
    escenarios = {"Crash (-3%)": -0.03, "Neutral (0%)": 0.0, "Rally (+2%)": 0.02}
    colores_esc = ["#e74c3c", "#95a5a6", "#2ecc71"]

    for (nombre, r), color in zip(escenarios.items(), colores_esc):
        np.random.seed(42)
        alphas_s = np.random.normal(alpha_mu, alpha_sig, 10000)
        betas_s = np.random.normal(beta_mu, beta_sig, 10000)
        preds = alphas_s + betas_s * r + sigma_res * np.random.standard_t(4, 10000)

        hist_c, hist_e = np.histogram(preds * 100, bins=50, density=True)
        hist_centers = (hist_e[:-1] + hist_e[1:]) / 2

        fig.add_trace(go.Scatter(
            x=hist_centers, y=hist_c,
            name=nombre, line=dict(color=color, width=2),
            fill="tozeroy", fillcolor=color.replace(")", ",0.15)").replace("rgb", "rgba") if "rgb" in color else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)",
        ), row=2, col=1)

    fig.update_layout(
        height=900, width=1000,
        title="Ensambles Generativos: regresion probabilistica",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_xaxes(title_text="r_SP500 (%)", row=1, col=1)
    fig.update_yaxes(title_text="r_AAPL (%)", row=1, col=1)
    fig.update_xaxes(title_text="beta", row=1, col=2)
    fig.update_xaxes(title_text="r_AAPL predicho (%)", row=2, col=1)
    fig.update_yaxes(title_text="Densidad", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/ensemble_hdi.png"):
    import matplotlib.pyplot as plt
    r_mkt, r_asset, b, se = generar_datos()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(r_mkt*100, r_asset*100, s=5, alpha=0.3, color='gray')
    x_l = np.linspace(r_mkt.min(), r_mkt.max(), 100)
    np.random.seed(42)
    for _ in range(50):
        a_i = np.random.normal(b[0]*0.3, se[0]*0.8)
        b_i = np.random.normal(b[1], se[1]*0.9)
        ax.plot(x_l*100, (a_i+b_i*x_l)*100, 'orangered', alpha=0.05, lw=0.5)
    ax.plot(x_l*100, (b[0]+b[1]*x_l)*100, 'steelblue', lw=2, ls='--')
    ax.set_title('Ensamble Generativo')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz Ensambles Generativos...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/ensemble_hdi.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
