"""
Visualizacion interactiva: El Problema de la Induccion en Finanzas.
Genera HTML con Plotly (3 paneles) + fallback PNG con Matplotlib.
source_ref: turn0browsertab744690698

Requisitos: numpy, scipy, plotly (o matplotlib)
Ejecutar: python hotmart/viz_induction_problem.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


# ================================================================
# Datos
# ================================================================

def simular_pavo(seed=42):
    """Genera datos del pavo de Russell."""
    np.random.seed(seed)
    n_calma, n_crisis = 500, 50
    ret_calma = np.random.normal(0.001, 0.005, n_calma)
    ret_crisis = np.random.normal(-0.03, 0.04, n_crisis)
    retornos = np.concatenate([ret_calma, ret_crisis])
    precios = 100 * np.exp(np.cumsum(retornos))
    return retornos, precios, n_calma


def calcular_confianzas(retornos):
    """Calcula intervalos frecuentista y bayesiano acumulados."""
    n = len(retornos)
    mu_f, lo_f, hi_f = [], [], []
    mu_b, lo_b, hi_b = [], [], []

    tau_prior = 1 / 0.005**2
    tau_like = 1 / 0.01**2

    for i in range(2, n + 1):
        sub = retornos[:i]
        # Frecuentista
        m = sub.mean()
        se = sub.std() / np.sqrt(i)
        mu_f.append(m)
        lo_f.append(m - 1.96 * se)
        hi_f.append(m + 1.96 * se)
        # Bayesiano
        tau_post = tau_prior + i * tau_like
        m_post = (tau_prior * 0.0 + i * tau_like * m) / tau_post
        s_post = 1 / np.sqrt(tau_post)
        mu_b.append(m_post)
        lo_b.append(m_post - 1.96 * s_post)
        hi_b.append(m_post + 1.96 * s_post)

    return (np.array(mu_f), np.array(lo_f), np.array(hi_f),
            np.array(mu_b), np.array(lo_b), np.array(hi_b))


def calcular_stress(seed=42):
    """Stress test inductivo."""
    np.random.seed(seed)
    capital = 1_000_000
    escenarios = [
        ("Leve", -0.01, 0.02, 30),
        ("Moderada", -0.03, 0.04, 30),
        ("Severa", -0.05, 0.06, 30),
        ("Cisne negro", -0.08, 0.10, 10),
    ]
    nombres, medias, p95s = [], [], []
    for nom, mu, sig, dias in escenarios:
        perdidas = []
        for _ in range(10000):
            ret = np.random.normal(mu, sig, dias)
            perdidas.append(capital - capital * np.exp(np.sum(ret)))
        arr = np.array(perdidas)
        nombres.append(nom)
        medias.append(arr.mean())
        p95s.append(np.percentile(arr, 95))
    return nombres, medias, p95s


# ================================================================
# Plotly
# ================================================================

def crear_plotly_dashboard() -> str:
    """Dashboard HTML interactivo con 3 paneles."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado. Usa: pip install plotly")
        return ""

    retornos, precios, quiebre = simular_pavo()
    mu_f, lo_f, hi_f, mu_b, lo_b, hi_b = calcular_confianzas(retornos)
    nombres_st, medias_st, p95s_st = calcular_stress()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "El Pavo de Russell: precio acumulado",
            "Confianza Frecuentista vs Bayesiana (media)",
            "Stress Test Inductivo: perdidas por escenario",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.55, 0.45],
        vertical_spacing=0.12,
    )

    # Panel 1: Precio del pavo
    dias = list(range(len(precios)))
    fig.add_trace(go.Scatter(
        x=dias, y=precios, name="Precio",
        line=dict(color="steelblue", width=1.5),
        hovertemplate="Dia %{x}: $%{y:.2f}",
    ), row=1, col=1)
    fig.add_vline(x=quiebre, line_dash="dash", line_color="red",
                  annotation_text="Quiebre", row=1, col=1)

    # Panel 2: Confianza
    x_conf = list(range(2, len(retornos) + 1))

    # Frecuentista
    fig.add_trace(go.Scatter(
        x=x_conf, y=(mu_f * 100).tolist(),
        name="Freq media", line=dict(color="steelblue", width=1.5),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x_conf + x_conf[::-1],
        y=(hi_f * 100).tolist() + (lo_f * 100).tolist()[::-1],
        fill="toself", fillcolor="rgba(70,130,180,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="IC 95% freq", showlegend=True, hoverinfo="skip",
    ), row=1, col=2)

    # Bayesiano
    fig.add_trace(go.Scatter(
        x=x_conf, y=(mu_b * 100).tolist(),
        name="Bayes media", line=dict(color="orangered", width=1.5),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x_conf + x_conf[::-1],
        y=(hi_b * 100).tolist() + (lo_b * 100).tolist()[::-1],
        fill="toself", fillcolor="rgba(255,69,0,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="HDI 95% bayes", showlegend=True, hoverinfo="skip",
    ), row=1, col=2)
    fig.add_vline(x=quiebre, line_dash="dash", line_color="red", row=1, col=2)

    # Panel 3: Stress test
    x_st = list(range(len(nombres_st)))
    fig.add_trace(go.Bar(
        x=nombres_st, y=[m / 1000 for m in medias_st],
        name="Perdida media ($K)",
        marker_color="steelblue",
        text=[f"${m/1000:.0f}K" for m in medias_st],
        textposition="outside",
    ), row=2, col=1)
    fig.add_trace(go.Bar(
        x=nombres_st, y=[p / 1000 for p in p95s_st],
        name="Perdida P95 ($K)",
        marker_color="orangered",
        text=[f"${p/1000:.0f}K" for p in p95s_st],
        textposition="outside",
    ), row=2, col=1)

    fig.update_layout(
        height=900, width=1000,
        title="El Problema de la Induccion en Finanzas",
        template="plotly_white",
        barmode="group",
        font=dict(size=12),
        legend=dict(x=0.01, y=0.99),
    )
    fig.update_xaxes(title_text="Dia", row=1, col=1)
    fig.update_yaxes(title_text="Precio ($)", row=1, col=1)
    fig.update_xaxes(title_text="Dia", row=1, col=2)
    fig.update_yaxes(title_text="Retorno medio (%)", row=1, col=2)
    fig.update_yaxes(title_text="Perdida ($K)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


# ================================================================
# Matplotlib fallback
# ================================================================

def crear_matplotlib_fallback(output_path="data/induction_problem.png"):
    """Version estatica PNG."""
    import matplotlib.pyplot as plt

    retornos, precios, quiebre = simular_pavo()
    mu_f, lo_f, hi_f, mu_b, lo_b, hi_b = calcular_confianzas(retornos)
    nombres_st, medias_st, p95s_st = calcular_stress()

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    # Panel 1
    axes[0, 0].plot(precios, 'steelblue', lw=1.5)
    axes[0, 0].axvline(quiebre, color='red', ls='--')
    axes[0, 0].set_title('Pavo de Russell')
    axes[0, 0].set_ylabel('Precio ($)')

    # Panel 2
    x = range(2, len(retornos) + 1)
    axes[0, 1].plot(x, mu_f * 100, 'steelblue', lw=1, label='Freq')
    axes[0, 1].fill_between(x, lo_f * 100, hi_f * 100, alpha=0.15, color='steelblue')
    axes[0, 1].plot(x, mu_b * 100, 'orangered', lw=1, label='Bayes')
    axes[0, 1].fill_between(x, lo_b * 100, hi_b * 100, alpha=0.15, color='orangered')
    axes[0, 1].axvline(quiebre, color='red', ls='--')
    axes[0, 1].set_title('Confianza Freq vs Bayes')
    axes[0, 1].legend(fontsize=9)

    # Panel 3
    axes[1, 0].remove()
    axes[1, 1].remove()
    ax3 = fig.add_subplot(2, 1, 2)
    xp = np.arange(len(nombres_st))
    w = 0.35
    ax3.bar(xp - w/2, [m/1000 for m in medias_st], w, label='Media', color='steelblue')
    ax3.bar(xp + w/2, [p/1000 for p in p95s_st], w, label='P95', color='orangered')
    ax3.set_xticks(xp)
    ax3.set_xticklabels(nombres_st)
    ax3.set_ylabel('Perdida ($K)')
    ax3.set_title('Stress Test Inductivo')
    ax3.legend()

    plt.suptitle('El Problema de la Induccion en Finanzas',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Generando visualizacion del Problema de la Induccion...")
    html = crear_plotly_dashboard()
    if html:
        out = "hotmart/induction_problem.html"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out}")
    crear_matplotlib_fallback()
    print("Listo.")
