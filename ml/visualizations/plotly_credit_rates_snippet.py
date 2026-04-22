"""
Modulo: plotly_credit_rates_snippet.py
Proposito: Visualizaciones interactivas de distribuciones de probabilidad
           de tasas de tarjetas de credito bajo diferentes escenarios de
           alzas de la tasa de la Reserva Federal (Fed).

Este script genera:
  1. Una grafica interactiva con Plotly (slider para variar p).
  2. Una grafica estatica de respaldo con matplotlib.
  3. Una comparacion lado a lado para distintos valores de p.
  4. Un analisis de sensibilidad (valor esperado y varianza vs. p).

Modelo subyacente:
  - Se modela el numero de alzas de tasa como una variable aleatoria
    binomial: X ~ Binomial(n=fed_meetings, p=prob_alza).
  - La tasa de tarjeta de credito resultante es:
    tasa_cc = tasa_base + X * (puntos_base_por_alza / 100)

Fuente: Probabilistic ML for Finance and Investing (Kanungo, 2023)
Referencia: turn0browsertab744690698
Capitulo: 1 - The Need for Probabilistic Machine Learning
Fecha: 2026-03-27

Requisitos:
  numpy, scipy, matplotlib, plotly
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import binom
from typing import List, Optional


# =============================================================================
# CONSTANTES POR DEFECTO
# =============================================================================

REUNIONES_FED: int = 8
"""Numero de reuniones de la Reserva Federal en un anio."""

TASA_BASE: float = 12.0
"""Tasa base de tarjeta de credito (%) antes de cualquier alza."""

PUNTOS_BASE_POR_ALZA: float = 25.0
"""Puntos base anadidos a la tasa por cada alza de la Fed."""


# =============================================================================
# VERSION INTERACTIVA CON PLOTLY
# =============================================================================

def crear_figura_interactiva(
    reuniones_fed: int = REUNIONES_FED,
    tasa_base: float = TASA_BASE,
    puntos_base: float = PUNTOS_BASE_POR_ALZA,
) -> go.Figure:
    """
    Crea una figura interactiva de Plotly con un control deslizante (slider)
    que permite variar la probabilidad de alza de tasa de la Fed (p).

    La distribucion mostrada es la funcion de masa de probabilidad (PMF)
    de la tasa de tarjeta de credito resultante, calculada a partir de
    un modelo binomial.

    Parametros
    ----------
    reuniones_fed : int
        Numero de reuniones de la Fed (n en el modelo binomial).
    tasa_base : float
        Tasa base de la tarjeta de credito en porcentaje.
    puntos_base : float
        Puntos base anadidos por cada alza.

    Retorna
    -------
    go.Figure
        Figura de Plotly lista para mostrar o exportar a HTML.
    """
    valores_p = np.arange(0.0, 1.05, 0.05)
    k = np.arange(0, reuniones_fed + 1)

    # Crear frames para la animacion / slider
    frames = []
    for p in valores_p:
        pmf = binom.pmf(k, reuniones_fed, p)
        tasas_cc = tasa_base + (k * puntos_base) / 100.0

        frame_data = [
            go.Bar(
                x=tasas_cc,
                y=pmf,
                name=f"p = {p:.2f}",
                marker=dict(
                    color="steelblue",
                    line=dict(color="navy", width=1.2),
                ),
                hovertemplate=(
                    "<b>Tasa: %{x:.2f}%</b><br>"
                    "Probabilidad: %{y:.4f}<extra></extra>"
                ),
            )
        ]
        frames.append(go.Frame(data=frame_data, name=f"{p:.2f}"))

    # Estado inicial (p = 0.70)
    p_inicial = 0.70
    pmf_ini = binom.pmf(k, reuniones_fed, p_inicial)
    tasas_ini = tasa_base + (k * puntos_base) / 100.0

    fig = go.Figure(
        data=[
            go.Bar(
                x=tasas_ini,
                y=pmf_ini,
                name=f"p = {p_inicial:.2f}",
                marker=dict(
                    color="steelblue",
                    line=dict(color="navy", width=1.2),
                ),
                hovertemplate=(
                    "<b>Tasa: %{x:.2f}%</b><br>"
                    "Probabilidad: %{y:.4f}<extra></extra>"
                ),
            )
        ],
        frames=frames,
    )

    # Control deslizante (slider)
    pasos = [
        dict(
            args=[
                [f"{p:.2f}"],
                {
                    "frame": {"duration": 200, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 200},
                },
            ],
            label=f"{p:.2f}",
            method="animate",
        )
        for p in valores_p
    ]

    slider = dict(
        active=int(p_inicial / 0.05),
        steps=pasos,
        currentvalue=dict(
            prefix="Probabilidad de alza de tasa Fed (p) = ",
            visible=True,
            xanchor="center",
            font=dict(size=12),
        ),
        len=0.9,
        x=0.05,
        y=0,
        xanchor="left",
        yanchor="top",
    )

    # Botones de reproduccion
    botones = [
        dict(
            label="Reproducir",
            method="animate",
            args=[
                None,
                {
                    "frame": {"duration": 300, "redraw": True},
                    "fromcurrent": True,
                    "mode": "immediate",
                    "transition": {"duration": 300},
                },
            ],
        ),
        dict(
            label="Pausar",
            method="animate",
            args=[
                [None],
                {
                    "frame": {"duration": 0, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 0},
                },
            ],
        ),
    ]

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=1.05,
                x=0.0,
                xanchor="left",
                yanchor="top",
                buttons=botones,
            )
        ],
        sliders=[slider],
        title=dict(
            text=(
                "<b>Distribucion de tasas de tarjeta de credito</b><br>"
                "<sub>Varie p para ver como la probabilidad de alza "
                "de la Fed afecta la distribucion</sub>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=16),
        ),
        xaxis=dict(
            title="Tasa de tarjeta de credito (%)",
            gridcolor="lightgray",
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title="Masa de probabilidad",
            gridcolor="lightgray",
            showgrid=True,
            zeroline=False,
        ),
        hovermode="closest",
        height=600,
        template="plotly_white",
        font=dict(family="Arial", size=11),
        margin=dict(l=80, r=40, b=150, t=120),
    )

    return fig


# =============================================================================
# VERSION ESTATICA CON MATPLOTLIB (respaldo / fallback)
# =============================================================================

def crear_figura_estatica_matplotlib(
    valores_p: Optional[List[float]] = None,
    reuniones_fed: int = REUNIONES_FED,
    tasa_base: float = TASA_BASE,
    puntos_base: float = PUNTOS_BASE_POR_ALZA,
    guardar_como: Optional[str] = None,
) -> plt.Figure:
    """
    Genera una version estatica de la distribucion de tasas de tarjeta
    de credito usando matplotlib. Sirve como respaldo cuando Plotly
    no esta disponible o cuando se necesita una imagen rasterizada
    (por ejemplo, para documentos PDF o presentaciones).

    Parametros
    ----------
    valores_p : list de float, opcional
        Lista de probabilidades a graficar. Por defecto [0.3, 0.5, 0.7, 0.9].
    reuniones_fed : int
        Numero de reuniones de la Fed.
    tasa_base : float
        Tasa base de la tarjeta de credito (%).
    puntos_base : float
        Puntos base por alza.
    guardar_como : str, opcional
        Ruta del archivo para guardar la figura (ej. 'tasas_credito.png').
        Si es None, no se guarda automaticamente.

    Retorna
    -------
    matplotlib.figure.Figure
        Objeto Figure de matplotlib con los subplots generados.
    """
    if valores_p is None:
        valores_p = [0.3, 0.5, 0.7, 0.9]

    k = np.arange(0, reuniones_fed + 1)
    n_plots = len(valores_p)

    fig, axes = plt.subplots(1, n_plots, figsize=(4 * n_plots, 5), sharey=True)

    if n_plots == 1:
        axes = [axes]

    colores = plt.cm.Blues(np.linspace(0.4, 0.9, n_plots))

    for ax, p, color in zip(axes, valores_p, colores):
        pmf = binom.pmf(k, reuniones_fed, p)
        tasas_cc = tasa_base + (k * puntos_base) / 100.0
        tasa_esperada = tasa_base + (reuniones_fed * p * puntos_base) / 100.0

        ax.bar(
            tasas_cc,
            pmf,
            width=0.18,
            color=color,
            edgecolor="navy",
            linewidth=0.8,
            alpha=0.85,
            label=f"PMF (p={p})",
        )

        # Linea vertical en el valor esperado
        ax.axvline(
            tasa_esperada,
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=f"E[tasa] = {tasa_esperada:.2f}%",
        )

        ax.set_title(f"p = {p:.2f}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Tasa de tarjeta (%)", fontsize=10)
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(axis="y", alpha=0.3)
        ax.set_xlim(tasa_base - 0.3, tasa_base + (reuniones_fed * puntos_base) / 100.0 + 0.3)

    axes[0].set_ylabel("Masa de probabilidad", fontsize=10)

    fig.suptitle(
        "Distribucion de tasas de tarjeta de credito\n"
        f"(modelo binomial: n={reuniones_fed} reuniones, "
        f"tasa base={tasa_base}%, {puntos_base} pb/alza)",
        fontsize=13,
        fontweight="bold",
        y=1.02,
    )

    fig.tight_layout()

    if guardar_como:
        fig.savefig(guardar_como, dpi=150, bbox_inches="tight")
        print(f"    Figura guardada en: {guardar_como}")

    return fig


# =============================================================================
# COMPARACION LADO A LADO (PLOTLY)
# =============================================================================

def crear_comparacion_plotly(
    valores_p: Optional[List[float]] = None,
    reuniones_fed: int = REUNIONES_FED,
    tasa_base: float = TASA_BASE,
    puntos_base: float = PUNTOS_BASE_POR_ALZA,
) -> go.Figure:
    """
    Crea una figura de Plotly con subplots lado a lado, comparando la
    distribucion de tasas para diferentes valores de p.

    Parametros
    ----------
    valores_p : list de float, opcional
        Probabilidades a comparar. Por defecto [0.3, 0.6, 0.9].
    reuniones_fed : int
        Numero de reuniones de la Fed.
    tasa_base : float
        Tasa base de la tarjeta de credito (%).
    puntos_base : float
        Puntos base por alza.

    Retorna
    -------
    go.Figure
        Figura de Plotly con la comparacion.
    """
    if valores_p is None:
        valores_p = [0.3, 0.6, 0.9]

    n_subplots = len(valores_p)
    k = np.arange(0, reuniones_fed + 1)
    paleta = ["skyblue", "steelblue", "darkblue", "midnightblue"]

    fig = make_subplots(
        rows=1,
        cols=n_subplots,
        subplot_titles=[f"p = {p}" for p in valores_p],
        specs=[[{"type": "bar"} for _ in range(n_subplots)]],
    )

    for col, p in enumerate(valores_p, start=1):
        pmf = binom.pmf(k, reuniones_fed, p)
        tasas_cc = tasa_base + (k * puntos_base) / 100.0
        tasa_esperada = tasa_base + (reuniones_fed * p * puntos_base) / 100.0
        color = paleta[min(col - 1, len(paleta) - 1)]

        fig.add_trace(
            go.Bar(
                x=tasas_cc,
                y=pmf,
                marker=dict(color=color, line=dict(color="navy", width=1)),
                name=f"p={p}",
                hovertemplate=(
                    "<b>Tasa: %{x:.2f}%</b><br>"
                    "Probabilidad: %{y:.4f}<extra></extra>"
                ),
                showlegend=False,
            ),
            row=1,
            col=col,
        )

        # Anotacion del valor esperado
        fig.add_vline(
            x=tasa_esperada,
            line=dict(color="red", dash="dash", width=2),
            row=1,
            col=col,
            annotation_text=f"E[tasa]={tasa_esperada:.2f}%",
            annotation_position="top right",
            annotation_font_size=10,
        )

    fig.update_xaxes(title_text="Tasa de tarjeta (%)", row=1, col=1)
    fig.update_yaxes(title_text="Masa de probabilidad", row=1, col=1)
    for col in range(2, n_subplots + 1):
        fig.update_xaxes(title_text="Tasa de tarjeta (%)", row=1, col=col)

    fig.update_layout(
        title=dict(
            text=(
                "<b>Comparacion: efecto de la probabilidad de alza "
                "de la Fed sobre las tasas</b>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=16),
        ),
        height=500,
        template="plotly_white",
        font=dict(family="Arial", size=11),
        showlegend=False,
        hovermode="closest",
    )

    return fig


# =============================================================================
# ANALISIS DE SENSIBILIDAD (PLOTLY)
# =============================================================================

def crear_sensibilidad(
    reuniones_fed: int = REUNIONES_FED,
    tasa_base: float = TASA_BASE,
    puntos_base: float = PUNTOS_BASE_POR_ALZA,
) -> go.Figure:
    """
    Crea un analisis de sensibilidad mostrando como varian el valor
    esperado E[tasa] y la varianza Var[tasa] en funcion de p.

    Parametros
    ----------
    reuniones_fed : int
        Numero de reuniones de la Fed.
    tasa_base : float
        Tasa base de la tarjeta de credito (%).
    puntos_base : float
        Puntos base por alza.

    Retorna
    -------
    go.Figure
        Figura de Plotly con dos subplots (valor esperado y varianza).
    """
    rango_p = np.linspace(0, 1, 101)

    # Valor esperado: E[tasa] = tasa_base + n * p * (pb / 100)
    e_tasa = tasa_base + (reuniones_fed * rango_p * puntos_base) / 100.0

    # Varianza: Var[tasa] = n * p * (1-p) * (pb/100)^2
    var_tasa = (
        reuniones_fed * rango_p * (1 - rango_p) * ((puntos_base / 100.0) ** 2)
    )

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Valor esperado de la tasa",
            "Varianza de la distribucion de tasas",
        ),
    )

    # Subplot 1: valor esperado
    fig.add_trace(
        go.Scatter(
            x=rango_p,
            y=e_tasa,
            mode="lines",
            name="E[tasa]",
            line=dict(color="steelblue", width=3),
            hovertemplate=(
                "<b>p = %{x:.2f}</b><br>"
                "E[tasa] = %{y:.2f}%<extra></extra>"
            ),
            fill="tozeroy",
            fillcolor="rgba(70, 130, 180, 0.2)",
        ),
        row=1,
        col=1,
    )

    # Subplot 2: varianza
    fig.add_trace(
        go.Scatter(
            x=rango_p,
            y=var_tasa,
            mode="lines",
            name="Var[tasa]",
            line=dict(color="coral", width=3),
            hovertemplate=(
                "<b>p = %{x:.2f}</b><br>"
                "Var[tasa] = %{y:.6f}<extra></extra>"
            ),
            fill="tozeroy",
            fillcolor="rgba(255, 127, 80, 0.2)",
        ),
        row=1,
        col=2,
    )

    fig.update_xaxes(
        title_text="Probabilidad de alza de tasa (p)", row=1, col=1
    )
    fig.update_yaxes(title_text="Tasa esperada (%)", row=1, col=1)

    fig.update_xaxes(
        title_text="Probabilidad de alza de tasa (p)", row=1, col=2
    )
    fig.update_yaxes(title_text="Varianza", row=1, col=2)

    fig.update_layout(
        title=dict(
            text=(
                "<b>Analisis de sensibilidad: estadisticos de la tasa "
                "vs. probabilidad de alza de la Fed</b>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=16),
        ),
        height=500,
        template="plotly_white",
        font=dict(family="Arial", size=11),
        hovermode="closest",
        showlegend=False,
    )

    return fig


# =============================================================================
# EJECUCION PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("VISUALIZACIONES DE TASAS DE CREDITO")
    print("Modelo binomial: probabilidad de alzas de la Reserva Federal")
    print("=" * 80)

    # --- Plotly interactivo ---
    print("\n[1/4] Creando figura interactiva con slider (Plotly)...")
    fig_interactiva = crear_figura_interactiva()
    fig_interactiva.write_html("credit_rates_interactive_slider.html")
    print("      Guardado: credit_rates_interactive_slider.html")

    # --- Matplotlib estatico (fallback) ---
    print("\n[2/4] Creando figura estatica de respaldo (matplotlib)...")
    fig_estatica = crear_figura_estatica_matplotlib(
        valores_p=[0.3, 0.5, 0.7, 0.9],
        guardar_como="credit_rates_static_fallback.png",
    )
    print("      Guardado: credit_rates_static_fallback.png")

    # --- Comparacion Plotly ---
    print("\n[3/4] Creando comparacion lado a lado (Plotly)...")
    fig_comparacion = crear_comparacion_plotly(valores_p=[0.3, 0.6, 0.9])
    fig_comparacion.write_html("credit_rates_comparison.html")
    print("      Guardado: credit_rates_comparison.html")

    # --- Sensibilidad Plotly ---
    print("\n[4/4] Creando analisis de sensibilidad (Plotly)...")
    fig_sensibilidad = crear_sensibilidad()
    fig_sensibilidad.write_html("credit_rates_sensitivity.html")
    print("      Guardado: credit_rates_sensitivity.html")

    print("\n" + "=" * 80)
    print("Todas las figuras generadas exitosamente.")
    print("\nArchivos HTML listos para incrustar:")
    print("  <iframe src='credit_rates_interactive_slider.html' "
          "width='100%' height='700'></iframe>")
    print("=" * 80)
