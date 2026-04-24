"""
Visualizacion: Retrodiccion y Evaluacion de PLEs.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_retrodiction_eval.py
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
    n = 252
    r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
    r_asset = 0.0002 + 1.25 * r_mkt + 0.010 * np.random.standard_t(4, n)

    X = np.column_stack([np.ones(n), r_mkt])
    b = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    se = np.sqrt(np.sum((r_asset - X@b)**2)/(n-2) * np.diag(np.linalg.inv(X.T@X)))
    sig_r = np.std(r_asset - X@b)

    # Posteriors
    tau_b = 1/0.5**2 + 1/se[1]**2
    mu_b = (1/0.5**2 + b[1]/se[1]**2) / tau_b
    sig_b = 1/np.sqrt(tau_b)
    mu_a = b[0] * 0.3
    sig_a = se[0] * 0.8

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Prior Predictive: lineas desde los priors",
            "Posterior Predictive: lineas desde el posterior",
            "Extrapolacion: HDI se ensancha fuera de muestra",
            "R2 probabilistico: distribucion, no punto",
        ),
        vertical_spacing=0.14, horizontal_spacing=0.08,
    )

    x_l = np.linspace(r_mkt.min()*1.5, r_mkt.max()*1.5, 100)

    # Panel 1: Prior predictive
    for _ in range(50):
        a_i = np.random.normal(0, 0.001)
        b_i = np.random.normal(1, 0.5)
        fig.add_trace(go.Scatter(
            x=x_l*100, y=(a_i + b_i*x_l)*100,
            line=dict(color="rgba(150,150,150,0.15)", width=0.5),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=r_mkt*100, y=r_asset*100, mode="markers",
        marker=dict(color="orangered", size=3, opacity=0.5),
        name="Datos reales",
    ), row=1, col=1)

    # Panel 2: Posterior predictive
    for _ in range(50):
        a_i = np.random.normal(mu_a, sig_a)
        b_i = np.random.normal(mu_b, sig_b)
        fig.add_trace(go.Scatter(
            x=x_l*100, y=(a_i + b_i*x_l)*100,
            line=dict(color="rgba(255,69,0,0.12)", width=0.5),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=r_mkt*100, y=r_asset*100, mode="markers",
        marker=dict(color="steelblue", size=3, opacity=0.5),
        name="Datos", showlegend=False,
    ), row=1, col=2)

    # Panel 3: Extrapolacion
    r_test = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10])
    anchos = []
    for r in r_test:
        preds = np.random.normal(mu_a, sig_a, 20000) + np.random.normal(mu_b, sig_b, 20000) * r
        preds += sig_r * np.random.standard_t(4, 20000)
        anchos.append((np.percentile(preds, 97.5) - np.percentile(preds, 2.5)) * 100)

    fig.add_trace(go.Scatter(
        x=r_test*100, y=anchos, name="Ancho HDI 95%",
        line=dict(color="orangered", width=2.5),
        mode="lines+markers", marker=dict(size=8),
    ), row=2, col=1)
    fig.add_annotation(x=5, y=anchos[4], text="Fuera de muestra",
                       showarrow=True, arrowhead=2, row=2, col=1)

    # Panel 4: R2 distribucion
    r2s = []
    var_y = np.var(r_asset)
    for _ in range(3000):
        a_s = np.random.normal(mu_a, sig_a)
        b_s = np.random.normal(mu_b, sig_b)
        r2s.append(1 - np.var(r_asset - a_s - b_s*r_mkt) / var_y)

    hist_c, hist_e = np.histogram(r2s, bins=40, density=True)
    hist_cen = (hist_e[:-1] + hist_e[1:]) / 2
    fig.add_trace(go.Bar(
        x=hist_cen, y=hist_c, name="R2 posterior",
        marker_color="rgba(70,130,180,0.6)",
        width=hist_cen[1]-hist_cen[0],
    ), row=2, col=2)
    r2_ols = 1 - np.var(r_asset - X@b) / var_y
    fig.add_vline(x=r2_ols, line_dash="dash", line_color="orangered",
                  annotation_text=f"OLS: {r2_ols:.3f}", row=2, col=2)

    fig.update_layout(
        height=850, width=1000,
        title="Retrodiccion y Evaluacion de PLEs",
        template="plotly_white", font=dict(size=12),
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/retrodiction_eval.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, "Instala Plotly para la version interactiva",
            ha='center', va='center', fontsize=14)
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz Retrodiccion + Eval...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/retrodiction_eval.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
