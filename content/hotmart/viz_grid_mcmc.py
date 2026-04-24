"""
Visualizacion: Grid Approximation, Markov Chains y MCMC Metropolis.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_grid_mcmc.py
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

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Grid Approximation vs Analitico",
            "Markov Chain: convergencia a estacionaria",
            "MCMC Metropolis: trace plot + posterior de nu",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.45, 0.55],
        vertical_spacing=0.12,
    )

    # Panel 1: Grid
    theta = np.linspace(0.001, 0.999, 500)
    prior = stats.beta.pdf(theta, 2, 2)
    lik = stats.binom.pmf(7, 8, theta)
    post_raw = prior * lik
    post_grid = post_raw / (post_raw.sum() * (theta[1]-theta[0]))
    post_exact = stats.beta.pdf(theta, 9, 3)

    fig.add_trace(go.Scatter(
        x=theta*100, y=post_grid, name="Grid (500 pts)",
        line=dict(color="orangered", width=2),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=theta*100, y=post_exact, name="Exacto Beta(9,3)",
        line=dict(color="steelblue", dash="dash", width=2),
    ), row=1, col=1)

    # Panel 2: Markov chain convergencia
    T = np.array([[0.6,0.3,0.1],[0.2,0.5,0.3],[0.1,0.3,0.6]])
    cadena = [1]
    for _ in range(999):
        cadena.append(np.random.choice(3, p=T[cadena[-1]]))
    cadena = np.array(cadena)

    for i, (nombre, color) in enumerate(zip(
            ["Bear","Stagnant","Bull"], ["#e74c3c","#f39c12","#2ecc71"])):
        freq = np.cumsum(cadena == i) / np.arange(1, len(cadena)+1)
        fig.add_trace(go.Scatter(
            x=list(range(len(cadena))), y=freq.tolist(),
            name=nombre, line=dict(color=color, width=1.5),
        ), row=1, col=2)

    # Panel 3: MCMC trace + histograma
    nu_real = 4.0
    datos = 0.012 * np.random.standard_t(nu_real, 500)
    mu_d = np.median(datos)
    scale_d = np.median(np.abs(datos - mu_d)) * 1.4826

    def lp(nu):
        if nu <= 2: return -np.inf
        return stats.expon.logpdf(nu, scale=30) + np.sum(stats.t.logpdf(datos, nu, mu_d, scale_d))

    chain = [10.0]
    for _ in range(24999):
        prop = chain[-1] + np.random.normal(0, 0.8)
        if prop > 2 and np.log(np.random.random()) < lp(prop) - lp(chain[-1]):
            chain.append(prop)
        else:
            chain.append(chain[-1])

    post = np.array(chain[5000:])

    # Trace (subsample for performance)
    step = 5
    fig.add_trace(go.Scatter(
        x=list(range(0, len(chain), step)),
        y=[chain[i] for i in range(0, len(chain), step)],
        name="Trace nu", line=dict(color="steelblue", width=0.5),
        opacity=0.6,
    ), row=2, col=1)
    fig.add_hline(y=nu_real, line_dash="dash", line_color="red",
                  annotation_text=f"nu real={nu_real}", row=2, col=1)

    # Inset-like: histograma como barras al costado derecho
    hist_c, hist_e = np.histogram(post, bins=40, density=True)
    hist_centers = (hist_e[:-1] + hist_e[1:]) / 2

    fig.add_annotation(
        x=20000, y=post.mean(),
        text=f"Media={post.mean():.1f}<br>HDI=({np.percentile(post,2.5):.1f}, {np.percentile(post,97.5):.1f})",
        showarrow=True, arrowhead=2, font=dict(size=12, color="orangered"),
        bgcolor="white", bordercolor="orangered",
        row=2, col=1,
    )

    fig.update_layout(
        height=850, width=1000,
        title="Grid, Markov Chains y MCMC Metropolis",
        template="plotly_white", font=dict(size=12),
    )
    fig.update_xaxes(title_text="P(beat) %", row=1, col=1)
    fig.update_yaxes(title_text="Densidad", row=1, col=1)
    fig.update_xaxes(title_text="Paso", row=1, col=2)
    fig.update_yaxes(title_text="Frecuencia acumulada", row=1, col=2)
    fig.update_xaxes(title_text="Iteracion MCMC", row=2, col=1)
    fig.update_yaxes(title_text="nu", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/grid_mcmc.png"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    theta = np.linspace(0.001, 0.999, 500)
    ax.plot(theta*100, stats.beta.pdf(theta, 9, 3), 'orangered', lw=2)
    ax.set_title('Grid + MCMC')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG: {output_path}")


if __name__ == "__main__":
    print("Generando viz Grid + MCMC...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/grid_mcmc.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
