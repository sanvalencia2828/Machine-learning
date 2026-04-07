"""
Visualizacion: IC, CAPM y la Trampa de Alpha.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_ci_capm.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def generar_datos(seed=42):
    """Genera AAPL vs SPY sinteticos."""
    np.random.seed(seed)
    n = 504
    r_spy = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_aapl = 0.0002 + 1.25 * r_spy + 0.010 * np.random.standard_t(4, n)
    X = np.column_stack([np.ones(n), r_spy])
    b = np.linalg.lstsq(X, r_aapl, rcond=None)[0]
    res = r_aapl - X @ b
    mse = np.sum(res**2) / (n - 2)
    return r_spy, r_aapl, b, mse, n


def crear_plotly_dashboard() -> str:
    """Dashboard con 3 paneles: scatter+IC, IC param vs pred, freq vs bayes."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    r_spy, r_aapl, b, mse, n = generar_datos()
    x_plot = np.linspace(r_spy.min(), r_spy.max(), 100)
    y_plot = b[0] + b[1] * x_plot

    # IC parametro y prediccion
    spy_mean = r_spy.mean()
    spy_var = np.sum((r_spy - spy_mean)**2)
    se_param = np.sqrt(mse * (1/n + (x_plot - spy_mean)**2 / spy_var))
    se_pred = np.sqrt(mse + mse * (1/n + (x_plot - spy_mean)**2 / spy_var))

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "OLS: AAPL vs SPY con IC parametro y prediccion",
            "Ancho de IC: parametro vs prediccion",
            "IC Frecuentista vs Intervalo Credible Bayesiano (alpha)",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.55, 0.45],
        vertical_spacing=0.12,
    )

    # Panel 1: Scatter + ambos IC
    fig.add_trace(go.Scatter(
        x=r_spy * 100, y=r_aapl * 100, mode="markers",
        marker=dict(color="gray", size=3, opacity=0.3),
        name="Datos", showlegend=True,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x_plot * 100, y=y_plot * 100,
        name="OLS fit", line=dict(color="orangered", width=2),
    ), row=1, col=1)
    # IC parametro
    fig.add_trace(go.Scatter(
        x=np.concatenate([x_plot, x_plot[::-1]]) * 100,
        y=np.concatenate([(y_plot + 1.96*se_param), (y_plot - 1.96*se_param)[::-1]]) * 100,
        fill="toself", fillcolor="rgba(255,69,0,0.2)",
        line=dict(color="rgba(0,0,0,0)"),
        name="IC parametro 95%",
    ), row=1, col=1)
    # IC prediccion
    fig.add_trace(go.Scatter(
        x=np.concatenate([x_plot, x_plot[::-1]]) * 100,
        y=np.concatenate([(y_plot + 1.96*se_pred), (y_plot - 1.96*se_pred)[::-1]]) * 100,
        fill="toself", fillcolor="rgba(70,130,180,0.1)",
        line=dict(color="rgba(0,0,0,0)"),
        name="IC prediccion 95%",
    ), row=1, col=1)

    # Panel 2: Ancho IC vs posicion
    fig.add_trace(go.Scatter(
        x=x_plot * 100, y=2 * 1.96 * se_param * 100,
        name="Ancho IC parametro",
        line=dict(color="orangered", width=2),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x_plot * 100, y=2 * 1.96 * se_pred * 100,
        name="Ancho IC prediccion",
        line=dict(color="steelblue", width=2),
    ), row=1, col=2)

    # Panel 3: Freq vs Bayes para alpha
    se_alpha = np.sqrt(mse * np.linalg.inv(
        np.column_stack([np.ones(n), r_spy]).T @
        np.column_stack([np.ones(n), r_spy]))[0, 0])

    # Frecuentista
    x_alpha = np.linspace(-0.003, 0.003, 200)
    freq_pdf = stats.norm.pdf(x_alpha, b[0], se_alpha) / stats.norm.pdf(x_alpha, b[0], se_alpha).max()

    # Bayesiano
    prior_sigma = 0.0005
    tau_pr = 1 / prior_sigma**2
    tau_d = 1 / se_alpha**2
    tau_po = tau_pr + tau_d
    mu_po = (tau_pr * 0 + tau_d * b[0]) / tau_po
    sig_po = 1 / np.sqrt(tau_po)
    bayes_pdf = stats.norm.pdf(x_alpha, mu_po, sig_po) / stats.norm.pdf(x_alpha, mu_po, sig_po).max()
    prior_pdf = stats.norm.pdf(x_alpha, 0, prior_sigma) / stats.norm.pdf(x_alpha, 0, prior_sigma).max()

    fig.add_trace(go.Scatter(
        x=x_alpha * 100, y=prior_pdf,
        name="Prior N(0, 0.05%)", line=dict(color="gray", dash="dot", width=1.5),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=x_alpha * 100, y=freq_pdf,
        name="Likelihood (datos)", line=dict(color="steelblue", width=2, dash="dash"),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=x_alpha * 100, y=bayes_pdf,
        name="Posterior bayesiano", line=dict(color="orangered", width=2),
    ), row=2, col=1)
    fig.add_vline(x=0, line_dash="dot", line_color="black", row=2, col=1)

    p_pos = 1 - stats.norm.cdf(0, mu_po, sig_po)
    fig.add_annotation(
        x=0.15, y=0.5,
        text=f"P(alpha>0) = {p_pos:.0%}",
        showarrow=False, font=dict(size=14, color="orangered"),
        row=2, col=1,
    )

    fig.update_layout(
        height=900, width=1000,
        title="IC, CAPM y la Trampa de Alpha",
        template="plotly_white",
        font=dict(size=12),
    )
    fig.update_xaxes(title_text="Retorno SPY (%)", row=1, col=1)
    fig.update_yaxes(title_text="Retorno AAPL (%)", row=1, col=1)
    fig.update_xaxes(title_text="Retorno SPY (%)", row=1, col=2)
    fig.update_yaxes(title_text="Ancho IC (%)", row=1, col=2)
    fig.update_xaxes(title_text="Alpha (%)", row=2, col=1)
    fig.update_yaxes(title_text="Densidad (normalizada)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/ci_capm_alpha.png"):
    """Fallback PNG."""
    import matplotlib.pyplot as plt
    r_spy, r_aapl, b, mse, n = generar_datos()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(r_spy * 100, r_aapl * 100, s=5, alpha=0.3, color='gray')
    x_p = np.linspace(r_spy.min(), r_spy.max(), 100)
    ax.plot(x_p * 100, (b[0] + b[1] * x_p) * 100, 'orangered', lw=2)
    ax.set_title('OLS: AAPL vs SPY')
    ax.set_xlabel('SPY (%)')
    ax.set_ylabel('AAPL (%)')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion CI + CAPM...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/ci_capm_alpha.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
