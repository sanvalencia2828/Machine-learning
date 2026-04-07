"""
Visualizacion interactiva: Conceptos Estadisticos y Critica a la Volatilidad.
Genera HTML con Plotly (3 paneles) + fallback PNG.
source_ref: turn0browsertab744690698

Ejecutar: python hotmart/viz_stat_concepts.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


def generar_datos(n=50000, seed=42):
    """Genera 3 distribuciones con ~misma std."""
    np.random.seed(seed)
    ret_n = np.random.normal(0.0004, 0.012, n)
    ret_t = 0.0004 + 0.0085 * np.random.standard_t(4, n)
    mask = np.random.binomial(1, 0.95, n).astype(bool)
    ret_m = np.where(mask,
        np.random.normal(0.0006, 0.009, n),
        np.random.normal(-0.008, 0.04, n))
    return ret_n, ret_t, ret_m


def demo_ergodicidad_datos(seed=42):
    """Genera datos de no-ergodicidad."""
    np.random.seed(seed)
    n_tray, n_pasos = 5000, 100
    factores = np.where(
        np.random.binomial(1, 0.5, (n_tray, n_pasos)), 1.5, 0.6)
    riqueza = 100 * np.cumprod(factores, axis=1)
    return riqueza


def crear_plotly_dashboard() -> str:
    """Dashboard HTML con 3 paneles."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado. Usa: pip install plotly")
        return ""

    ret_n, ret_t, ret_m = generar_datos()
    riqueza = demo_ergodicidad_datos()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "3 Distribuciones: misma vol, diferente riesgo",
            "Eventos extremos por distribucion",
            "No-Ergodicidad: media del ensamble vs mediana",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.50, 0.50],
        vertical_spacing=0.12,
    )

    # Panel 1: Histogramas superpuestos
    bins = np.linspace(-0.06, 0.06, 80)
    for datos, nombre, color in [(ret_n, "Normal", "rgba(70,130,180,0.4)"),
                                  (ret_t, "Student-t(4)", "rgba(255,69,0,0.4)"),
                                  (ret_m, "Mezcla 95/5", "rgba(34,139,34,0.4)")]:
        counts, _ = np.histogram(datos, bins=bins, density=True)
        centers = (bins[:-1] + bins[1:]) / 2
        fig.add_trace(go.Bar(
            x=centers, y=counts, name=nombre,
            marker_color=color, width=0.0015,
        ), row=1, col=1)

    # Panel 2: Barras de eventos extremos
    categorias = ["Normal", "Student-t(4)", "Mezcla"]
    colores_bar = ["steelblue", "orangered", "forestgreen"]
    for k, nombre_k in [(3, ">3 sigma"), (4, ">4 sigma"), (5, ">5 sigma")]:
        vals = []
        for datos in [ret_n, ret_t, ret_m]:
            mu, sig = datos.mean(), datos.std()
            vals.append(np.sum(np.abs(datos - mu) > k * sig))
        fig.add_trace(go.Bar(
            x=categorias, y=vals, name=nombre_k,
            text=[str(v) for v in vals], textposition="outside",
        ), row=1, col=2)

    # Panel 3: Ergodicidad
    media_ens = riqueza.mean(axis=0)
    mediana = np.median(riqueza, axis=0)
    pasos = list(range(1, riqueza.shape[1] + 1))

    # Unas pocas trayectorias
    for i in range(20):
        fig.add_trace(go.Scatter(
            x=pasos, y=riqueza[i].tolist(),
            line=dict(color="rgba(150,150,150,0.15)", width=0.5),
            showlegend=False, hoverinfo="skip",
        ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=pasos, y=media_ens.tolist(),
        name=f"Media ensamble (${media_ens[-1]:,.0f})",
        line=dict(color="steelblue", width=2.5),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=pasos, y=mediana.tolist(),
        name=f"Mediana (${mediana[-1]:.2f})",
        line=dict(color="orangered", width=2.5),
    ), row=2, col=1)
    fig.add_hline(y=100, line_dash="dot", line_color="black", row=2, col=1)

    fig.update_layout(
        height=900, width=1000,
        title="Conceptos Estadisticos: 4 Momentos, Fat Tails y Ergodicidad",
        template="plotly_white",
        barmode="overlay" if True else "group",
        font=dict(size=12),
    )
    fig.update_xaxes(title_text="Retorno diario", row=1, col=1)
    fig.update_yaxes(title_text="Densidad", row=1, col=1)
    fig.update_yaxes(title_text="Eventos observados", row=1, col=2)
    fig.update_xaxes(title_text="Paso", row=2, col=1)
    fig.update_yaxes(title_text="Riqueza ($)", type="log", row=2, col=1)

    # Fix barmode for panel 2
    fig.update_layout(barmode="group")

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(output_path="data/stat_concepts.png"):
    """Version estatica PNG."""
    import matplotlib.pyplot as plt

    ret_n, ret_t, ret_m = generar_datos()
    riqueza = demo_ergodicidad_datos()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    bins = np.linspace(-0.06, 0.06, 60)
    axes[0].hist(ret_n, bins, density=True, alpha=0.4, color='steelblue', label='Normal')
    axes[0].hist(ret_t, bins, density=True, alpha=0.4, color='orangered', label='Student-t')
    axes[0].hist(ret_m, bins, density=True, alpha=0.4, color='forestgreen', label='Mezcla')
    axes[0].set_title('3 Distribuciones: misma vol')
    axes[0].legend()

    media_ens = riqueza.mean(axis=0)
    mediana = np.median(riqueza, axis=0)
    axes[1].semilogy(media_ens, 'steelblue', lw=2, label='Media ensamble')
    axes[1].semilogy(mediana, 'orangered', lw=2, label='Mediana')
    axes[1].axhline(100, ls=':', color='black')
    axes[1].set_title('No-Ergodicidad')
    axes[1].legend()

    plt.suptitle('Conceptos Estadisticos', fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion Conceptos Estadisticos...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/stat_concepts.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
