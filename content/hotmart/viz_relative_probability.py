"""
Visualizacion interactiva: Probabilidades Relativas y Riesgo vs Incertidumbre.
Genera HTML con Plotly + fallback PNG con Matplotlib.
source_ref: turn0browsertab744690698
"""
import numpy as np
from scipy import stats
from pathlib import Path


def actualizacion_bayesiana(datos: np.ndarray, alpha_prior: float = 2,
                             beta_prior: float = 2) -> list:
    """Calcula la trayectoria posterior Beta-Binomial dato por dato.

    Parametros
    ----------
    datos : np.ndarray
        Array de 0s y 1s (Bernoulli).
    alpha_prior, beta_prior : float
        Parametros del prior Beta.

    Retorna
    -------
    list[tuple] : (alpha, beta) en cada paso.
    """
    trayectoria = [(alpha_prior, beta_prior)]
    a, b = alpha_prior, beta_prior
    for x in datos:
        a += x
        b += (1 - x)
        trayectoria.append((a, b))
    return trayectoria


def crear_plotly_probabilidad_relativa(n_datos: int = 80, p_real: float = 0.65,
                                        seed: int = 42) -> str:
    """Crea dashboard Plotly interactivo con 3 paneles.

    Panel 1: Actualizacion secuencial prior → posterior
    Panel 2: IC frecuentista vs intervalo credible bayesiano
    Panel 3: Espectro riesgo-incertidumbre con ejemplos financieros

    Retorna
    -------
    str : HTML completo con Plotly embebido.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado. Usa: pip install plotly")
        return ""

    np.random.seed(seed)
    datos = np.random.binomial(1, p_real, n_datos)
    trayectoria = actualizacion_bayesiana(datos, 2, 2)

    # --- Datos para Panel 1: Actualizacion secuencial ---
    pasos = list(range(len(trayectoria)))
    medias = [a / (a + b) for a, b in trayectoria]
    hdi_lo = [stats.beta(a, b).ppf(0.025) for a, b in trayectoria]
    hdi_hi = [stats.beta(a, b).ppf(0.975) for a, b in trayectoria]

    # --- Datos para Panel 2: Frecuentista vs Epistemico ---
    ns_comparar = [5, 15, 30, 60]
    categorias = [f"n={n}" for n in ns_comparar]

    ic_freq_lo, ic_freq_hi = [], []
    hdi_bayes_lo, hdi_bayes_hi = [], []
    medias_freq, medias_bayes = [], []

    for n in ns_comparar:
        sub = datos[:n]
        caras = sub.sum()
        p_hat = caras / n
        se = np.sqrt(p_hat * (1 - p_hat) / max(n, 1))

        medias_freq.append(p_hat)
        ic_freq_lo.append(max(0, p_hat - 1.96 * se))
        ic_freq_hi.append(min(1, p_hat + 1.96 * se))

        a_post = 2 + caras
        b_post = 2 + (n - caras)
        post = stats.beta(a_post, b_post)
        medias_bayes.append(post.mean())
        hdi_bayes_lo.append(post.ppf(0.025))
        hdi_bayes_hi.append(post.ppf(0.975))

    # --- Panel 3: Espectro riesgo-incertidumbre ---
    eventos = [
        "Cisne negro (guerra/pandemia)",
        "Nueva regulacion",
        "Recesion en 12 meses",
        "Default bonos AA",
        "Fed sube tasas",
        "Retorno S&P 500 manana",
        "Ruleta de casino",
    ]
    confianza = [0.05, 0.20, 0.35, 0.50, 0.60, 0.75, 0.95]
    colores_espectro = [
        f"rgb({int(255*(1-c))}, {int(200*c)}, {int(50*c)})" for c in confianza
    ]

    # --- Construir figura ---
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            "Actualizacion Bayesiana Secuencial",
            "IC Frecuentista vs HDI Bayesiano (por tamano de muestra)",
            "Espectro Continuo: Riesgo ↔ Incertidumbre",
        ),
        row_heights=[0.4, 0.3, 0.3],
        vertical_spacing=0.10,
    )

    # Panel 1: Convergencia
    fig.add_trace(go.Scatter(
        x=pasos, y=medias, name="Media posterior",
        line=dict(color="orangered", width=2),
        hovertemplate="Obs %{x}: media=%{y:.3f}",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=pasos + pasos[::-1],
        y=hdi_hi + hdi_lo[::-1],
        fill="toself", fillcolor="rgba(255,69,0,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="HDI 95%", showlegend=True,
        hoverinfo="skip",
    ), row=1, col=1)
    fig.add_hline(y=p_real, line_dash="dot", line_color="red",
                  annotation_text=f"Valor real: {p_real}", row=1, col=1)

    # Panel 2: Comparacion IC vs HDI
    offset = 0.15
    for i, cat in enumerate(categorias):
        # Frecuentista
        fig.add_trace(go.Scatter(
            x=[ic_freq_lo[i], medias_freq[i], ic_freq_hi[i]],
            y=[i - offset] * 3,
            mode="lines+markers",
            line=dict(color="steelblue", width=3),
            marker=dict(size=[8, 12, 8], symbol=["line-ns", "circle", "line-ns"]),
            name=f"Freq {cat}" if i == 0 else None,
            showlegend=(i == 0),
            legendgroup="freq",
            hovertemplate=f"Freq {cat}: ({ic_freq_lo[i]:.3f}, {ic_freq_hi[i]:.3f})",
        ), row=2, col=1)
        # Bayesiano
        fig.add_trace(go.Scatter(
            x=[hdi_bayes_lo[i], medias_bayes[i], hdi_bayes_hi[i]],
            y=[i + offset] * 3,
            mode="lines+markers",
            line=dict(color="orangered", width=3),
            marker=dict(size=[8, 12, 8], symbol=["line-ns", "diamond", "line-ns"]),
            name=f"Bayes {cat}" if i == 0 else None,
            showlegend=(i == 0),
            legendgroup="bayes",
            hovertemplate=f"Bayes {cat}: ({hdi_bayes_lo[i]:.3f}, {hdi_bayes_hi[i]:.3f})",
        ), row=2, col=1)

    fig.add_vline(x=p_real, line_dash="dot", line_color="red", row=2, col=1)
    fig.update_yaxes(
        tickvals=list(range(len(categorias))),
        ticktext=categorias, row=2, col=1,
    )

    # Panel 3: Espectro
    fig.add_trace(go.Bar(
        y=eventos, x=confianza, orientation="h",
        marker=dict(color=colores_espectro, line=dict(color="black", width=1)),
        text=[f"{c:.0%}" for c in confianza],
        textposition="outside",
        name="Confianza",
        showlegend=False,
        hovertemplate="%{y}: %{x:.0%}",
    ), row=3, col=1)

    # Layout general
    fig.update_layout(
        height=1000, width=950,
        title="Probabilidades Relativas: Todo es Condicional a la Informacion",
        template="plotly_white",
        legend=dict(x=0.75, y=0.98),
        font=dict(size=12),
    )
    fig.update_xaxes(title_text="Observaciones", row=1, col=1)
    fig.update_yaxes(title_text="P(cara)", range=[0, 1], row=1, col=1)
    fig.update_xaxes(title_text="Probabilidad estimada", range=[0, 1.05], row=2, col=1)
    fig.update_xaxes(title_text="Confianza en la estimacion", range=[0, 1.1], row=3, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_fallback(n_datos: int = 80, p_real: float = 0.65,
                               output_path: str = "data/relative_probability.png",
                               seed: int = 42):
    """Genera version estatica PNG como fallback."""
    import matplotlib.pyplot as plt

    np.random.seed(seed)
    datos = np.random.binomial(1, p_real, n_datos)
    trayectoria = actualizacion_bayesiana(datos, 2, 2)

    pasos = range(len(trayectoria))
    medias = [a / (a + b) for a, b in trayectoria]
    hdi_lo = [stats.beta(a, b).ppf(0.025) for a, b in trayectoria]
    hdi_hi = [stats.beta(a, b).ppf(0.975) for a, b in trayectoria]

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [2, 1]})

    # Panel 1: Convergencia
    axes[0].plot(pasos, medias, 'orangered', lw=2, label='Media posterior')
    axes[0].fill_between(pasos, hdi_lo, hdi_hi, alpha=0.2, color='orangered', label='HDI 95%')
    axes[0].axhline(p_real, ls='--', color='red', lw=1.5, label=f'Valor real: {p_real}')
    axes[0].set_xlabel('Observaciones')
    axes[0].set_ylabel('P(cara)')
    axes[0].set_title('Actualizacion Bayesiana Secuencial', fontsize=13)
    axes[0].legend(loc='upper right')
    axes[0].set_ylim(0, 1)
    axes[0].grid(True, alpha=0.3)

    # Panel 2: Espectro
    eventos = [
        "Cisne negro", "Nueva regulacion", "Recesion 12m",
        "Default AA", "Fed tasas", "S&P manana", "Ruleta",
    ]
    confianza = [0.05, 0.20, 0.35, 0.50, 0.60, 0.75, 0.95]
    colores = plt.cm.RdYlGn(confianza)

    bars = axes[1].barh(eventos, confianza, color=colores, edgecolor='black')
    axes[1].set_xlabel('Confianza en la estimacion')
    axes[1].set_title('Espectro Riesgo-Incertidumbre', fontsize=13)
    axes[1].set_xlim(0, 1.1)
    for bar, val in zip(bars, confianza):
        axes[1].text(val + 0.02, bar.get_y() + bar.get_height() / 2,
                     f"{val:.0%}", va='center', fontsize=10)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion de probabilidades relativas...")

    # HTML interactivo
    html = crear_plotly_probabilidad_relativa()
    if html:
        out_html = "hotmart/relative_probability.html"
        Path(out_html).parent.mkdir(parents=True, exist_ok=True)
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out_html}")

    # PNG fallback
    crear_matplotlib_fallback(output_path="data/relative_probability.png")
    print("Listo.")
