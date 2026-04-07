"""
Visualizacion interactiva: Simulacion Monte Carlo del Problema de Monty Hall.
Genera HTML con Plotly + fallback PNG con Matplotlib.
source_ref: turn0browsertab744690698
"""
import numpy as np
import random
from pathlib import Path

def simular_monty_hall(n_simulaciones: int, seed: int = 42) -> dict:
    """Simula el problema de Monty Hall n veces.
    Retorna dict con resultados para estrategias 'quedarse' y 'cambiar'.
    """
    random.seed(seed)
    stay_wins = 0
    switch_wins = 0
    stay_cumulative = []
    switch_cumulative = []

    for i in range(1, n_simulaciones + 1):
        doors = [1, 2, 3]
        car = random.choice(doors)
        choice = random.choice(doors)
        remaining = [d for d in doors if d != choice and d != car]
        monty_opens = random.choice(remaining)
        switch_door = [d for d in doors if d != choice and d != monty_opens][0]

        if choice == car:
            stay_wins += 1
        if switch_door == car:
            switch_wins += 1

        stay_cumulative.append(stay_wins / i)
        switch_cumulative.append(switch_wins / i)

    return {
        "n": n_simulaciones,
        "stay_wins": stay_wins,
        "switch_wins": switch_wins,
        "stay_prob": stay_wins / n_simulaciones,
        "switch_prob": switch_wins / n_simulaciones,
        "stay_cumulative": stay_cumulative,
        "switch_cumulative": switch_cumulative,
    }


def crear_plotly_convergencia(resultados: dict) -> str:
    """Crea grafico Plotly de convergencia de probabilidades."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly no instalado. Usa: pip install plotly")
        return ""

    n = resultados["n"]
    x = list(range(1, n + 1))

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Convergencia de probabilidad (quedarse vs cambiar)",
            "Resultado final"
        ),
        row_heights=[0.7, 0.3],
        vertical_spacing=0.15,
    )

    # Panel 1: convergencia
    fig.add_trace(
        go.Scatter(
            x=x, y=resultados["stay_cumulative"],
            name="Quedarse", line=dict(color="steelblue", width=2),
            hovertemplate="Simulacion %{x}<br>P(ganar quedandose)=%{y:.3f}"
        ), row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=x, y=resultados["switch_cumulative"],
            name="Cambiar", line=dict(color="orangered", width=2),
            hovertemplate="Simulacion %{x}<br>P(ganar cambiando)=%{y:.3f}"
        ), row=1, col=1
    )
    fig.add_hline(y=1/3, line_dash="dot", line_color="steelblue",
                  annotation_text="1/3 teorico", row=1, col=1)
    fig.add_hline(y=2/3, line_dash="dot", line_color="orangered",
                  annotation_text="2/3 teorico", row=1, col=1)

    # Panel 2: barras finales
    fig.add_trace(
        go.Bar(
            x=["Quedarse", "Cambiar"],
            y=[resultados["stay_prob"], resultados["switch_prob"]],
            marker_color=["steelblue", "orangered"],
            text=[f"{resultados['stay_prob']:.2%}", f"{resultados['switch_prob']:.2%}"],
            textposition="outside",
            showlegend=False,
        ), row=2, col=1
    )

    fig.update_layout(
        title=f"Monty Hall MCS — {n:,} simulaciones",
        height=700, width=900,
        template="plotly_white",
        legend=dict(x=0.7, y=0.95),
    )
    fig.update_xaxes(title_text="Numero de simulacion", row=1, col=1)
    fig.update_yaxes(title_text="Probabilidad acumulada", range=[0, 1], row=1, col=1)
    fig.update_yaxes(title_text="Probabilidad", range=[0, 1], row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


def crear_matplotlib_convergencia(resultados: dict, output_path: str):
    """Crea version estatica con Matplotlib."""
    import matplotlib.pyplot as plt

    n = resultados["n"]
    x = range(1, n + 1)

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), gridspec_kw={"height_ratios": [3, 1]})

    # Convergencia
    axes[0].plot(x, resultados["stay_cumulative"], color="steelblue", lw=1.5, label="Quedarse")
    axes[0].plot(x, resultados["switch_cumulative"], color="orangered", lw=1.5, label="Cambiar")
    axes[0].axhline(1/3, ls=":", color="steelblue", alpha=0.6)
    axes[0].axhline(2/3, ls=":", color="orangered", alpha=0.6)
    axes[0].set_xlabel("Simulaciones")
    axes[0].set_ylabel("P(ganar)")
    axes[0].set_title(f"Monty Hall MCS — {n:,} simulaciones")
    axes[0].legend()
    axes[0].set_ylim(0, 1)

    # Barras
    bars = axes[1].bar(
        ["Quedarse", "Cambiar"],
        [resultados["stay_prob"], resultados["switch_prob"]],
        color=["steelblue", "orangered"],
    )
    for bar, val in zip(bars, [resultados["stay_prob"], resultados["switch_prob"]]):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                     f"{val:.2%}", ha="center", fontsize=11)
    axes[1].set_ylim(0, 1)
    axes[1].set_ylabel("P(ganar)")

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"PNG guardado: {output_path}")


if __name__ == "__main__":
    print("Simulando Monty Hall (10,000 iteraciones)...")
    res = simular_monty_hall(10_000)
    print(f"  Quedarse: {res['stay_prob']:.2%}")
    print(f"  Cambiar:  {res['switch_prob']:.2%}")

    # HTML interactivo
    html = crear_plotly_convergencia(res)
    if html:
        out_html = "hotmart/monty_hall_mcs.html"
        Path(out_html).parent.mkdir(parents=True, exist_ok=True)
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML guardado: {out_html}")

    # PNG estatico
    crear_matplotlib_convergencia(res, "data/monty_hall_mcs.png")
