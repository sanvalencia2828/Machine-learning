"""
Visualizacion: MLE vs PML -- Peligros de la IA Convencional.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_mle_vs_probabilistic.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def crear_plotly_dashboard() -> str:
    """Dashboard con 3 paneles: MLE vs PML, correlaciones espurias, MCMC posterior."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado.")
        return ""

    np.random.seed(42)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "MLE (punto) vs PML (distribucion): prediccion de earnings",
            "Correlaciones espurias: 50 series aleatorias",
            "MCMC Metropolis: posterior de nu (Student-t)",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: MLE vs PML
    earnings = np.array([2.1, 2.3, 2.0, 2.5, 2.2])
    mu_mle = earnings.mean()
    sigma_mle = earnings.std()

    prior_mu, prior_sigma = 2.0, 0.5
    tau_pr = 1 / prior_sigma**2
    tau_d = len(earnings) / sigma_mle**2
    tau_po = tau_pr + tau_d
    mu_po = (tau_pr * prior_mu + tau_d * mu_mle) / tau_po
    sig_po = 1 / np.sqrt(tau_po)

    x_earn = np.linspace(1.0, 3.5, 200)
    fig.add_trace(go.Scatter(
        x=x_earn, y=stats.norm.pdf(x_earn, prior_mu, prior_sigma),
        name="Prior N(2.0, 0.5)", line=dict(color="gray", dash="dot", width=1.5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x_earn, y=stats.norm.pdf(x_earn, mu_po, sig_po),
        name=f"Posterior (PML) mu={mu_po:.2f}", line=dict(color="orangered", width=2),
    ), row=1, col=1)
    fig.add_vline(x=mu_mle, line_dash="dash", line_color="steelblue",
                  annotation_text=f"MLE: {mu_mle:.2f}", row=1, col=1)
    for e in earnings:
        fig.add_trace(go.Scatter(
            x=[e], y=[0], mode="markers", marker=dict(size=10, color="black"),
            showlegend=False,
        ), row=1, col=1)

    # Panel 2: Heatmap de correlaciones espurias
    datos = np.random.normal(0, 1, (252, 20))
    corr = np.corrcoef(datos.T)
    np.fill_diagonal(corr, np.nan)

    fig.add_trace(go.Heatmap(
        z=corr, colorscale="RdBu_r", zmin=-0.3, zmax=0.3,
        showscale=True, name="Correlaciones",
        hovertemplate="Serie %{x} vs %{y}: r=%{z:.3f}",
    ), row=1, col=2)

    # Panel 3: MCMC posterior de nu
    nu_real = 4.0
    datos_t = 0.01 * np.random.standard_t(nu_real, 500)

    def log_post(nu, d):
        if nu <= 1: return -np.inf
        return stats.expon.logpdf(nu, scale=30) + np.sum(stats.t.logpdf(d, nu, 0, d.std()))

    n_iter = 15000
    chain = np.zeros(n_iter)
    chain[0] = 10
    for i in range(1, n_iter):
        prop = chain[i-1] + np.random.normal(0, 1)
        if prop > 1 and np.log(np.random.random()) < log_post(prop, datos_t) - log_post(chain[i-1], datos_t):
            chain[i] = prop
        else:
            chain[i] = chain[i-1]

    post = chain[3000:]
    hist_counts, hist_edges = np.histogram(post, bins=50, density=True)
    hist_centers = (hist_edges[:-1] + hist_edges[1:]) / 2

    fig.add_trace(go.Bar(
        x=hist_centers, y=hist_counts, name="Posterior nu",
        marker_color="rgba(255,69,0,0.6)", width=hist_centers[1]-hist_centers[0],
    ), row=2, col=1)
    fig.add_vline(x=nu_real, line_dash="dash", line_color="steelblue",
                  annotation_text=f"nu real = {nu_real}", row=2, col=1)
    fig.add_annotation(
        x=post.mean(), y=max(hist_counts)*0.8,
        text=f"Media posterior: {post.mean():.1f}<br>HDI: ({np.percentile(post,2.5):.1f}, {np.percentile(post,97.5):.1f})",
        showarrow=False, font=dict(size=12), bgcolor="white",
        row=2, col=1,
    )

    fig.update_layout(
        height=900, width=1000,
        title="MLE vs PML: Peligros de la IA Convencional",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_xaxes(title_text="Earnings ($)", row=1, col=1)
    fig.update_yaxes(title_text="Densidad", row=1, col=1)
    fig.update_xaxes(title_text="nu (grados libertad)", row=2, col=1)
    fig.update_yaxes(title_text="Densidad posterior", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/mle_vs_pml.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.linspace(1, 3.5, 200)
    ax.plot(x, stats.norm.pdf(x, 2.0, 0.5), 'gray', ls='--', label='Prior')
    ax.plot(x, stats.norm.pdf(x, 2.18, 0.08), 'orangered', lw=2, label='Posterior')
    ax.axvline(2.22, color='steelblue', ls='--', label='MLE')
    ax.set_title('MLE vs PML')
    ax.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion MLE vs PML...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/mle_vs_pml.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
