"""
Visualizacion: MPT, CAPM y su Critica Probabilistica.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_mpt_critique.py
"""
import numpy as np
from scipy.optimize import minimize
from pathlib import Path


def crear_plotly_dashboard() -> str:
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        return ""

    np.random.seed(42)
    n_a, n_d = 5, 504

    # Generar activos
    mus = np.array([0.0004, 0.0003, 0.0005, 0.0002, 0.0006])
    sigs = np.array([0.015, 0.010, 0.020, 0.008, 0.025])
    ret = np.zeros((n_d, n_a))
    for i in range(n_a):
        ret[:, i] = mus[i] + sigs[i] * np.random.standard_t(4, n_d)

    mu_hat = ret.mean(axis=0)
    cov = np.cov(ret.T)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Frontera Eficiente + Portafolio 1/N",
            "Sensibilidad: pesos MPT ante perturbacion de mu",
            "Correlaciones: calma vs crisis",
            "MPT vs 1/N: Sharpe fuera de muestra (100 runs)",
        ),
        vertical_spacing=0.14, horizontal_spacing=0.10,
    )

    # Panel 1: Frontera eficiente
    mu_range = np.linspace(mu_hat.min(), mu_hat.max(), 15)
    ef_sigma, ef_ret = [], []
    for mt in mu_range:
        def obj(w): return w @ cov @ w
        cons = [{'type':'eq','fun':lambda w:w.sum()-1},
                {'type':'eq','fun':lambda w,m=mt:w@mu_hat-m}]
        r = minimize(obj, np.ones(n_a)/n_a, method='SLSQP',
                     constraints=cons, bounds=[(0,1)]*n_a)
        if r.success:
            ef_sigma.append(np.sqrt(r.fun)*np.sqrt(252)*100)
            ef_ret.append(mt*252*100)

    fig.add_trace(go.Scatter(x=ef_sigma, y=ef_ret, name="Frontera eficiente",
                              line=dict(color="steelblue", width=2.5),
                              mode="lines+markers", marker=dict(size=5)), row=1, col=1)

    # 1/N
    w_1n = np.ones(n_a) / n_a
    r_1n = ret @ w_1n
    fig.add_trace(go.Scatter(
        x=[r_1n.std()*np.sqrt(252)*100], y=[r_1n.mean()*252*100],
        name="1/N", mode="markers",
        marker=dict(color="orangered", size=15, symbol="star"),
    ), row=1, col=1)

    # Activos individuales
    for i in range(n_a):
        fig.add_trace(go.Scatter(
            x=[ret[:, i].std()*np.sqrt(252)*100],
            y=[ret[:, i].mean()*252*100],
            name=f"Activo {i+1}", mode="markers",
            marker=dict(size=8, color="gray"), showlegend=(i==0),
        ), row=1, col=1)

    # Panel 2: Sensibilidad
    perts = np.linspace(-0.0002, 0.0002, 20)
    pesos_activo1 = []
    for p in perts:
        mu_p = mu_hat.copy()
        mu_p[0] += p
        target = mu_p.mean()
        def obj(w): return w @ cov @ w
        cons = [{'type':'eq','fun':lambda w:w.sum()-1},
                {'type':'eq','fun':lambda w,m=target:w@mu_p-m}]
        r = minimize(obj, np.ones(n_a)/n_a, method='SLSQP',
                     constraints=cons, bounds=[(0,1)]*n_a)
        pesos_activo1.append(r.x[0] if r.success else 0.2)

    fig.add_trace(go.Scatter(
        x=(perts*10000).tolist(), y=[p*100 for p in pesos_activo1],
        name="Peso Activo 1", line=dict(color="orangered", width=2.5),
    ), row=1, col=2)
    fig.add_hline(y=20, line_dash="dot", line_color="gray",
                  annotation_text="1/N = 20%", row=1, col=2)

    # Panel 3: Correlaciones
    import plotly.graph_objects as go
    corr_calma = np.array([[1.0, 0.2, 0.15], [0.2, 1.0, 0.1], [0.15, 0.1, 1.0]])
    corr_crisis = np.array([[1.0, 0.85, 0.80], [0.85, 1.0, 0.75], [0.80, 0.75, 1.0]])

    fig.add_trace(go.Heatmap(
        z=corr_calma, x=["A","B","C"], y=["A","B","C"],
        colorscale="Blues", zmin=0, zmax=1, showscale=False,
        text=[[f"{v:.2f}" for v in row] for row in corr_calma],
        texttemplate="%{text}", name="Calma",
    ), row=2, col=1)

    # Panel 4: Sharpe OOS
    sharpes_mpt, sharpes_1n = [], []
    for s in range(100):
        np.random.seed(s)
        r_tr = np.zeros((252, n_a))
        r_te = np.zeros((252, n_a))
        for i in range(n_a):
            r_tr[:, i] = mus[i] + sigs[i] * np.random.standard_t(4, 252)
            r_te[:, i] = mus[i] + sigs[i] * np.random.standard_t(4, 252)

        cov_tr = np.cov(r_tr.T)
        def obj(w): return w @ cov_tr @ w
        res = minimize(obj, np.ones(n_a)/n_a, method='SLSQP',
                       constraints={'type':'eq','fun':lambda w:w.sum()-1},
                       bounds=[(0,1)]*n_a)
        w_m = res.x if res.success else np.ones(n_a)/n_a

        r_mpt = r_te @ w_m
        r_naive = r_te @ (np.ones(n_a)/n_a)
        sharpes_mpt.append(r_mpt.mean()/r_mpt.std()*np.sqrt(252))
        sharpes_1n.append(r_naive.mean()/r_naive.std()*np.sqrt(252))

    fig.add_trace(go.Histogram(x=sharpes_mpt, name="MPT", opacity=0.6,
                                marker_color="steelblue", nbinsx=20), row=2, col=2)
    fig.add_trace(go.Histogram(x=sharpes_1n, name="1/N", opacity=0.6,
                                marker_color="orangered", nbinsx=20), row=2, col=2)

    pct_1n_gana = sum(s1 > sm for s1, sm in zip(sharpes_1n, sharpes_mpt)) / len(sharpes_mpt)
    fig.add_annotation(x=np.mean(sharpes_1n), y=15,
                       text=f"1/N gana {pct_1n_gana:.0%} de las veces",
                       showarrow=False, font=dict(size=12, color="orangered"),
                       row=2, col=2)

    fig.update_layout(
        height=850, width=1000,
        title="MPT, CAPM y su Critica Probabilistica",
        template="plotly_white", font=dict(size=12),
        barmode="overlay",
    )
    fig.update_xaxes(title_text="Volatilidad anual (%)", row=1, col=1)
    fig.update_yaxes(title_text="Retorno anual (%)", row=1, col=1)
    fig.update_xaxes(title_text="Perturbacion mu[0] (bps)", row=1, col=2)
    fig.update_yaxes(title_text="Peso Activo 1 (%)", row=1, col=2)
    fig.update_xaxes(title_text="Sharpe ratio (test)", row=2, col=2)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/mpt_critique.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, "Instala Plotly para version interactiva",
            ha='center', va='center')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz MPT Critique...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/mpt_critique.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
