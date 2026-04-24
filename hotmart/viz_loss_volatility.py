"""
Visualizacion: Loss Functions, VaR/ES y Volatility Drag.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_loss_volatility.py
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

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Expected Loss: R1 vs R2 vs R3 segun P(default)",
            "VaR vs ES: Normal vs Fat Tails",
            "Volatility Drag: riqueza mediana vs sigma",
            "Path Dependence: trayectorias con media=0",
        ),
        vertical_spacing=0.14, horizontal_spacing=0.08,
    )

    # Panel 1: Expected loss
    p_range = np.linspace(0.01, 0.50, 50)
    el_r1 = p_range * (-100) + (1 - p_range) * 15
    el_r2 = p_range * 0 + (1 - p_range) * 0
    el_r3 = p_range * (-5) + (1 - p_range) * 10

    fig.add_trace(go.Scatter(x=p_range*100, y=el_r1, name="R1 (invertir)",
                              line=dict(color="#e74c3c", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=p_range*100, y=el_r2, name="R2 (no invertir)",
                              line=dict(color="#95a5a6", width=2, dash="dash")), row=1, col=1)
    fig.add_trace(go.Scatter(x=p_range*100, y=el_r3, name="R3 (cubrir)",
                              line=dict(color="#2ecc71", width=2)), row=1, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=1)

    # Panel 2: VaR vs ES
    ret_n = np.random.normal(0.0005, 0.015, 50000)
    ret_t = 0.0005 + 0.010 * np.random.standard_t(3, 50000)

    bins_r = np.linspace(-0.08, 0.08, 80)
    for ret, nombre, color in [(ret_n, "Normal", "steelblue"),
                                (ret_t, "Fat tails", "orangered")]:
        counts, _ = np.histogram(ret, bins=bins_r, density=True)
        centers = (bins_r[:-1] + bins_r[1:]) / 2
        fig.add_trace(go.Bar(x=centers*100, y=counts, name=nombre,
                              marker_color=color, opacity=0.4,
                              width=0.2, showlegend=True), row=1, col=2)
        var = np.percentile(ret, 5)
        fig.add_vline(x=var*100, line_dash="dash", line_color=color, row=1, col=2)

    # Panel 3: Volatility drag
    sigmas = np.linspace(0.002, 0.035, 20)
    medianas = []
    for s in sigmas:
        ret = np.random.normal(0, s, (2000, 252))
        w = 100 * np.exp(np.sum(np.log(1 + ret), axis=1))
        medianas.append(np.median(w))

    fig.add_trace(go.Scatter(
        x=sigmas*100, y=medianas, name="Riqueza mediana",
        line=dict(color="orangered", width=2.5),
        mode="lines+markers", marker=dict(size=5),
    ), row=2, col=1)
    fig.add_hline(y=100, line_dash="dot", line_color="gray",
                  annotation_text="Capital inicial", row=2, col=1)

    # Panel 4: Trayectorias con media=0
    for i in range(50):
        ret = np.random.normal(0, 0.02, 252)
        w = 100 * np.cumprod(1 + ret)
        color_t = "rgba(231,76,60,0.15)" if w[-1] < 100 else "rgba(46,204,113,0.15)"
        fig.add_trace(go.Scatter(
            x=list(range(252)), y=w.tolist(),
            line=dict(color=color_t, width=0.5),
            showlegend=False, hoverinfo="skip",
        ), row=2, col=2)
    fig.add_hline(y=100, line_dash="dot", line_color="black", row=2, col=2)

    fig.update_layout(
        height=850, width=1000,
        title="Loss Functions, VaR/ES y Volatility Drag",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_xaxes(title_text="P(default) %", row=1, col=1)
    fig.update_yaxes(title_text="Expected Loss ($K)", row=1, col=1)
    fig.update_xaxes(title_text="Retorno (%)", row=1, col=2)
    fig.update_xaxes(title_text="Sigma diaria (%)", row=2, col=1)
    fig.update_yaxes(title_text="Riqueza mediana ($)", row=2, col=1)
    fig.update_xaxes(title_text="Dia", row=2, col=2)
    fig.update_yaxes(title_text="Riqueza ($)", row=2, col=2)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/loss_volatility.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    p = np.linspace(0.01, 0.5, 50)
    ax.plot(p*100, p*(-100)+(1-p)*15, 'r', label='R1')
    ax.plot(p*100, np.zeros_like(p), 'gray', ls='--', label='R2')
    ax.plot(p*100, p*(-5)+(1-p)*10, 'g', label='R3')
    ax.axhline(0, ls=':', color='black')
    ax.set_title('Expected Loss')
    ax.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz Loss + Volatility...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/loss_volatility.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
