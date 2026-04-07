"""
Visualizacion interactiva: Black-Scholes y la Trinidad de la Incertidumbre.
Genera HTML con Plotly (3 paneles) + fallback PNG con Matplotlib.
source_ref: turn0browsertab744690698

Requisitos: numpy, scipy, plotly (o matplotlib como fallback)
Ejecutar: python hotmart/viz_bsm_uncertainty_trinity.py
"""
import numpy as np
from scipy import stats
from scipy.optimize import brentq
from pathlib import Path


# ================================================================
# Funciones auxiliares
# ================================================================

def black_scholes_call(S, K, T, r, sigma):
    """Precio call europea Black-Scholes."""
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)


def implied_vol(precio, S, K, T, r):
    """Calcula volatilidad implicita por biseccion."""
    try:
        return brentq(lambda s: black_scholes_call(S, K, T, r, s) - precio,
                      0.001, 5.0, xtol=1e-6)
    except (ValueError, RuntimeError):
        return np.nan


# ================================================================
# Generacion de datos para los 3 paneles
# ================================================================

def generar_datos_panel1(n_sim=50000, sigma=0.01, nu=4, seed=42):
    """Panel 1: Normal vs Student-t (incertidumbre aleatoria)."""
    np.random.seed(seed)
    ret_n = np.random.normal(0, sigma, n_sim)
    ret_t = sigma * np.random.standard_t(nu, n_sim)
    return ret_n, ret_t


def generar_datos_panel2(S=150, T=0.25, r=0.05, sigma=0.25, nu=4,
                          n_sim=100000, seed=42):
    """Panel 2: Volatility smile (BSM vs fat tails)."""
    np.random.seed(seed)
    sigma_d = sigma / np.sqrt(252)
    n_dias = int(T * 252)

    log_ret = np.zeros(n_sim)
    for _ in range(n_dias):
        log_ret += sigma_d * np.random.standard_t(nu, n_sim)
    S_T = S * np.exp((r - 0.5 * sigma**2) * T + log_ret)

    strikes = np.linspace(S * 0.82, S * 1.18, 20)
    iv_bsm = np.full_like(strikes, sigma)
    iv_mkt = np.array([
        implied_vol(
            np.exp(-r * T) * np.maximum(S_T - K, 0).mean(),
            S, K, T, r
        ) for K in strikes
    ])
    moneyness = strikes / S
    return moneyness, iv_bsm, iv_mkt


def generar_datos_panel3(S=150, K=165, T=0.25, r=0.05, sigma=0.25,
                          seed=42):
    """Panel 3: Impacto de cada tipo de incertidumbre en pricing."""
    np.random.seed(seed)
    sigma_d = sigma / np.sqrt(252)
    n_dias = int(T * 252)
    n_sim = 100000

    bsm_base = black_scholes_call(S, K, T, r, sigma)

    # Aleatoria: Student-t
    log_r = np.zeros(n_sim)
    for _ in range(n_dias):
        log_r += sigma_d * np.random.standard_t(4, n_sim)
    S_T = S * np.exp((r - 0.5 * sigma**2) * T + log_r)
    p_alea = np.exp(-r * T) * np.maximum(S_T - K, 0).mean()

    # Epistemica: sigma incierta
    precios = []
    for _ in range(2000):
        s = max(np.random.normal(sigma, 0.05), 0.05)
        precios.append(black_scholes_call(S, K, T, r, s))
    p_epis = np.mean(precios)

    # Ontologica: jump-diffusion
    log_r2 = np.zeros(n_sim)
    for d in range(n_dias):
        z = np.random.normal(0, 1, n_sim)
        log_r2 += (r / 252 - 0.5 * sigma_d**2) + sigma_d * z
        jumps = np.random.binomial(1, 0.03 / 252, n_sim)
        log_r2 += jumps * np.random.normal(-0.15, 0.05, n_sim)
    S_T2 = S * np.exp(log_r2)
    p_onto = np.exp(-r * T) * np.maximum(S_T2 - K, 0).mean()

    labels = ["BSM baseline", "+ Aleatoria\n(Student-t)",
              "+ Epistemica\n(sigma incierta)", "+ Ontologica\n(jumps)"]
    precios_arr = [bsm_base, p_alea, p_epis, p_onto]
    return labels, precios_arr


# ================================================================
# Plotly: dashboard interactivo
# ================================================================

def crear_plotly_dashboard() -> str:
    """Crea dashboard HTML con 3 paneles interactivos."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado. Usa: pip install plotly")
        return ""

    # Generar datos
    ret_n, ret_t = generar_datos_panel1()
    moneyness, iv_bsm, iv_mkt = generar_datos_panel2()
    labels, precios = generar_datos_panel3()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Aleatoria: Normal vs Student-t (retornos)",
            "Aleatoria: Volatility Smile (BSM vs mercado)",
            "Trinidad: Impacto en Pricing de Opciones OTM",
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.55, 0.45],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # Panel 1: Histogramas Normal vs Student-t
    bins_edges = np.linspace(-0.06, 0.06, 80)
    counts_n, _ = np.histogram(ret_n, bins=bins_edges, density=True)
    counts_t, _ = np.histogram(ret_t, bins=bins_edges, density=True)
    bin_centers = (bins_edges[:-1] + bins_edges[1:]) / 2

    fig.add_trace(go.Bar(
        x=bin_centers, y=counts_n, name="Normal (BSM)",
        marker_color="rgba(70,130,180,0.5)", width=0.0015,
        hovertemplate="Retorno: %{x:.4f}<br>Densidad: %{y:.1f}",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=bin_centers, y=counts_t, name="Student-t(4)",
        marker_color="rgba(255,69,0,0.5)", width=0.0015,
        hovertemplate="Retorno: %{x:.4f}<br>Densidad: %{y:.1f}",
    ), row=1, col=1)

    # Panel 2: Volatility smile
    fig.add_trace(go.Scatter(
        x=moneyness, y=iv_bsm * 100, name="BSM (flat)",
        line=dict(color="steelblue", dash="dash", width=2),
        hovertemplate="K/S=%{x:.2f}<br>IV=%{y:.1f}%",
    ), row=1, col=2)
    valid = ~np.isnan(iv_mkt)
    fig.add_trace(go.Scatter(
        x=moneyness[valid], y=iv_mkt[valid] * 100, name="Mercado (fat tails)",
        line=dict(color="orangered", width=2),
        mode="lines+markers", marker=dict(size=5),
        hovertemplate="K/S=%{x:.2f}<br>IV=%{y:.1f}%",
    ), row=1, col=2)
    fig.add_vline(x=1.0, line_dash="dot", line_color="gray", row=1, col=2)

    # Panel 3: Barras de pricing por tipo de incertidumbre
    colores_barras = ["steelblue", "#e74c3c", "#f39c12", "#8e44ad"]
    fig.add_trace(go.Bar(
        x=labels, y=precios, name="Precio opcion",
        marker_color=colores_barras,
        text=[f"${p:.2f}" for p in precios],
        textposition="outside",
        hovertemplate="%{x}: $%{y:.2f}",
        showlegend=False,
    ), row=2, col=1)

    # Anotacion con diferencia porcentual
    base = precios[0]
    for i in range(1, len(precios)):
        diff = (precios[i] - base) / base * 100
        fig.add_annotation(
            x=labels[i], y=precios[i] + 0.15,
            text=f"{diff:+.1f}% vs BSM",
            showarrow=False, font=dict(size=10, color=colores_barras[i]),
            row=2, col=1,
        )

    fig.update_layout(
        height=900, width=1000,
        title="Black-Scholes y la Trinidad de la Incertidumbre",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99),
        font=dict(size=12),
        barmode="overlay",
    )
    fig.update_xaxes(title_text="Retorno diario", row=1, col=1)
    fig.update_yaxes(title_text="Densidad", row=1, col=1)
    fig.update_xaxes(title_text="Moneyness (K/S)", row=1, col=2)
    fig.update_yaxes(title_text="Vol Implicita (%)", row=1, col=2)
    fig.update_yaxes(title_text="Precio opcion ($)", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


# ================================================================
# Matplotlib fallback
# ================================================================

def crear_matplotlib_fallback(output_path="data/bsm_uncertainty_trinity.png"):
    """Genera version estatica PNG."""
    import matplotlib.pyplot as plt

    ret_n, ret_t = generar_datos_panel1()
    moneyness, iv_bsm, iv_mkt = generar_datos_panel2()
    labels, precios = generar_datos_panel3()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1
    bins = np.linspace(-0.06, 0.06, 80)
    axes[0, 0].hist(ret_n, bins, density=True, alpha=0.5,
                    color='steelblue', label='Normal (BSM)')
    axes[0, 0].hist(ret_t, bins, density=True, alpha=0.5,
                    color='orangered', label='Student-t(4)')
    axes[0, 0].set_title('Aleatoria: Normal vs Fat Tails')
    axes[0, 0].set_xlabel('Retorno diario')
    axes[0, 0].legend()

    # Panel 2
    valid = ~np.isnan(iv_mkt)
    axes[0, 1].plot(moneyness, iv_bsm * 100, 'steelblue', ls='--', lw=2,
                    label='BSM (flat)')
    axes[0, 1].plot(moneyness[valid], iv_mkt[valid] * 100, 'orangered',
                    lw=2, marker='o', ms=4, label='Mercado')
    axes[0, 1].axvline(1.0, color='gray', ls=':', alpha=0.5)
    axes[0, 1].set_title('Volatility Smile')
    axes[0, 1].set_xlabel('Moneyness (K/S)')
    axes[0, 1].set_ylabel('Vol Implicita (%)')
    axes[0, 1].legend()

    # Panel 3 (spanning bottom)
    axes[1, 0].remove()
    axes[1, 1].remove()
    ax3 = fig.add_subplot(2, 1, 2)
    colores = ['steelblue', '#e74c3c', '#f39c12', '#8e44ad']
    bars = ax3.bar(labels, precios, color=colores, edgecolor='black')
    for bar, val in zip(bars, precios):
        ax3.text(bar.get_x() + bar.get_width() / 2, val + 0.08,
                 f"${val:.2f}", ha='center', fontsize=11)
    ax3.set_ylabel('Precio opcion ($)')
    ax3.set_title('Trinidad: Impacto en Pricing OTM')

    plt.suptitle('Black-Scholes y la Trinidad de la Incertidumbre',
                 fontsize=15, fontweight='bold')
    plt.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


# ================================================================
# Main
# ================================================================

if __name__ == "__main__":
    print("Generando visualizacion BSM + Trinidad de Incertidumbre...")

    html = crear_plotly_dashboard()
    if html:
        out_html = "hotmart/bsm_uncertainty_trinity.html"
        Path(out_html).parent.mkdir(parents=True, exist_ok=True)
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out_html}")

    crear_matplotlib_fallback(output_path="data/bsm_uncertainty_trinity.png")
    print("Listo.")
