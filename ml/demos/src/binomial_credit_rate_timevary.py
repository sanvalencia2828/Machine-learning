"""
binomial_credit_rate_timevary.py
================================
Modela la incertidumbre en la tasa de interes de tarjetas de credito
usando un modelo binomial con probabilidad variable en el tiempo.
Inspirado en el ejemplo de decisiones de la Fed sobre tasas.

Simula multiples escenarios de reuniones de la Fed donde en cada una
se puede subir la tasa (con cierta probabilidad) o mantenerla. Luego
muestra como un cambio estructural a mitad de anio altera la distribucion
de resultados.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple


def simulate_credit_rate(
    fed_meetings: int = 8,
    prob_raises: float = 0.7,
    base_rate: float = 15.0,
    spread: float = 0.25,
    n_simulations: int = 50_000,
    seed: int = 42,
) -> np.ndarray:
    """
    Simula la tasa de interes de tarjeta de credito usando un modelo binomial.

    En cada reunion de la Fed, la tasa puede subir 'spread' puntos con
    probabilidad 'prob_raises', o mantenerse.

    Parametros
    ----------
    fed_meetings : int
        Numero de reuniones de la Fed en el anio.
    prob_raises : float
        Probabilidad de que la tasa suba en cada reunion.
    base_rate : float
        Tasa base inicial (en porcentaje).
    spread : float
        Incremento en puntos porcentuales por cada subida.
    n_simulations : int
        Numero de simulaciones Monte Carlo.
    seed : int
        Semilla para reproducibilidad.

    Retorna
    -------
    np.ndarray
        Arreglo con las tasas finales simuladas.
    """
    rng = np.random.default_rng(seed)

    # Numero de subidas en cada simulacion (variable binomial)
    n_raises = rng.binomial(n=fed_meetings, p=prob_raises, size=n_simulations)

    # Tasa final = base + incremento por cada subida
    final_rates = base_rate + n_raises * spread

    return final_rates


def plot_rate_distributions(
    results: Dict[float, np.ndarray],
    prob_raises_list: List[float],
) -> None:
    """
    Grafica las distribuciones de tasas finales para distintas probabilidades.

    Parametros
    ----------
    results : dict
        Diccionario {probabilidad: arreglo_de_tasas}.
    prob_raises_list : list
        Lista de probabilidades usadas (para el orden).
    """
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    axes = axes.flatten()

    colores = ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]

    for i, prob in enumerate(prob_raises_list):
        ax = axes[i]
        tasas = results[prob]

        # Valores unicos posibles de la distribucion binomial
        valores, conteos = np.unique(tasas, return_counts=True)
        frecuencias = conteos / len(tasas)

        ax.bar(valores, frecuencias, width=0.18, color=colores[i], alpha=0.8, edgecolor="black")
        ax.set_title(f"P(subida) = {prob:.1f}", fontsize=12)
        ax.set_xlabel("Tasa final (%)")
        ax.set_ylabel("Frecuencia relativa")

        # Anotar media y desviacion estandar
        media = np.mean(tasas)
        desv = np.std(tasas, ddof=1)
        ax.axvline(media, color="black", linestyle="--", linewidth=1.2, label=f"Media={media:.2f}%")
        ax.legend(fontsize=9)
        ax.text(
            0.02, 0.95,
            f"Desv.Est.={desv:.3f}%",
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
        )

    plt.suptitle(
        "Distribucion de Tasa de Credito Segun Probabilidad de Subida",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig("data/credit_rate_distributions.png", dpi=120, bbox_inches="tight")
    plt.show()
    print("Grafico guardado en data/credit_rate_distributions.png")


def time_varying_simulation(
    fed_meetings: int = 8,
    initial_prob: float = 0.6,
    shock_meeting: int = 4,
    new_prob: float = 0.9,
    base_rate: float = 15.0,
    spread_up: float = 0.25,
    spread_down: float = -0.10,
    prob_down_post_shock: float = 0.05,
    n_simulations: int = 50_000,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simula tasas con un cambio estructural a mitad de periodo.

    Antes del shock: modelo binomial (sube o se mantiene).
    Despues del shock: modelo trinomial (sube, se mantiene, o baja),
    con probabilidades ajustadas a la nueva realidad economica.

    Parametros
    ----------
    fed_meetings : int
        Numero total de reuniones.
    initial_prob : float
        Probabilidad de subida antes del shock.
    shock_meeting : int
        Reunion donde ocurre el cambio estructural.
    new_prob : float
        Nueva probabilidad de subida despues del shock.
    base_rate : float
        Tasa base inicial.
    spread_up : float
        Incremento por subida.
    spread_down : float
        Decremento por bajada (solo post-shock).
    prob_down_post_shock : float
        Probabilidad de bajada despues del shock.
    n_simulations : int
        Numero de simulaciones.
    seed : int
        Semilla.

    Retorna
    -------
    tuple(np.ndarray, np.ndarray)
        Tasas finales con cambio estructural y sin el (binomial puro).
    """
    rng = np.random.default_rng(seed)

    # --- Escenario 1: SIN cambio estructural (binomial puro) ---
    n_raises_puro = rng.binomial(n=fed_meetings, p=initial_prob, size=n_simulations)
    tasas_sin_cambio = base_rate + n_raises_puro * spread_up

    # --- Escenario 2: CON cambio estructural ---
    tasas_con_cambio = np.full(n_simulations, base_rate)

    # Fase 1: reuniones antes del shock (binomial clasico)
    reuniones_fase1 = shock_meeting
    subidas_fase1 = rng.binomial(n=reuniones_fase1, p=initial_prob, size=n_simulations)
    tasas_con_cambio += subidas_fase1 * spread_up

    # Fase 2: reuniones despues del shock (trinomial)
    reuniones_fase2 = fed_meetings - shock_meeting
    for _ in range(reuniones_fase2):
        # Para cada simulacion, sortear el resultado: subida, mantener o bajada
        u = rng.random(size=n_simulations)
        # Subida si u < new_prob
        subida_mask = u < new_prob
        # Bajada si u >= (1 - prob_down_post_shock)
        bajada_mask = u >= (1 - prob_down_post_shock)
        # El resto se mantiene

        tasas_con_cambio[subida_mask] += spread_up
        tasas_con_cambio[bajada_mask] += spread_down

    return tasas_con_cambio, tasas_sin_cambio


if __name__ == "__main__":
    # --- Ejemplo de uso ---
    print("=" * 60)
    print("DEMO: Modelo binomial de tasa de credito con variacion temporal")
    print("=" * 60)

    # 1. Simular con 4 probabilidades distintas
    prob_list = [0.6, 0.7, 0.8, 0.9]
    resultados = {}

    print("\n--- Escenarios con probabilidad constante ---")
    for p in prob_list:
        tasas = simulate_credit_rate(fed_meetings=8, prob_raises=p, base_rate=15.0, spread=0.25)
        resultados[p] = tasas

        # Estadisticos resumidos
        media = np.mean(tasas)
        desv = np.std(tasas, ddof=1)
        percentil_5 = np.percentile(tasas, 5)
        percentil_95 = np.percentile(tasas, 95)

        print(f"  P(subida)={p:.1f} | Media={media:.2f}% | "
              f"Desv={desv:.3f}% | IC90%=[{percentil_5:.2f}%, {percentil_95:.2f}%]")

    # 2. Graficar distribuciones
    print("\nGenerando graficos de distribuciones...")
    plot_rate_distributions(resultados, prob_list)

    # 3. Escenario con cambio estructural
    print("\n--- Escenario con cambio estructural en reunion 4 ---")
    print("  Antes: P(subida)=0.6 (binomial)")
    print("  Despues: P(subida)=0.9, P(bajada)=0.05 (trinomial)")

    tasas_cambio, tasas_sin = time_varying_simulation(
        fed_meetings=8,
        initial_prob=0.6,
        shock_meeting=4,
        new_prob=0.9,
        base_rate=15.0,
    )

    # Comparar ambos escenarios
    print(f"\n  Sin cambio:  Media={np.mean(tasas_sin):.2f}% | Desv={np.std(tasas_sin, ddof=1):.3f}%")
    print(f"  Con cambio:  Media={np.mean(tasas_cambio):.2f}% | Desv={np.std(tasas_cambio, ddof=1):.3f}%")

    # Grafico comparativo
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(tasas_sin, bins=30, density=True, alpha=0.5, color="steelblue",
            label="Sin cambio estructural", edgecolor="black")
    ax.hist(tasas_cambio, bins=30, density=True, alpha=0.5, color="coral",
            label="Con cambio estructural", edgecolor="black")
    ax.axvline(np.mean(tasas_sin), color="steelblue", linestyle="--", linewidth=1.5)
    ax.axvline(np.mean(tasas_cambio), color="coral", linestyle="--", linewidth=1.5)
    ax.set_xlabel("Tasa final (%)")
    ax.set_ylabel("Densidad")
    ax.set_title("Efecto del cambio estructural en la distribucion de tasas")
    ax.legend()
    plt.tight_layout()
    plt.savefig("data/time_varying_comparison.png", dpi=120, bbox_inches="tight")
    plt.show()
    print("Grafico guardado en data/time_varying_comparison.png")
