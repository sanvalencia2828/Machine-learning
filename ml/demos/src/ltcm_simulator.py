"""
ltcm_simulator.py
=================
Simula un portafolio apalancado al estilo LTCM y lo compara con un
indice diversificado sin apalancamiento. Inspirado en la discusion
sobre el desastre de LTCM y los peligros del apalancamiento extremo.

Muestra como el apalancamiento amplifica tanto ganancias como perdidas,
y como un evento de crisis puede destruir portafolios altamente
apalancados mientras un portafolio conservador sobrevive.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict


def simulate_portfolio(
    initial_capital: float,
    returns: np.ndarray,
    leverage: float = 1.0,
) -> np.ndarray:
    """
    Simula la evolucion del valor de un portafolio apalancado dia a dia.

    El rendimiento efectivo cada dia es: leverage * rendimiento_mercado.
    Si el valor del portafolio cae a cero o menos, se considera liquidado
    (margin call) y permanece en cero.

    Parametros
    ----------
    initial_capital : float
        Capital inicial del portafolio.
    returns : np.ndarray
        Rendimientos diarios del mercado.
    leverage : float
        Factor de apalancamiento (1.0 = sin apalancamiento).

    Retorna
    -------
    np.ndarray
        Serie temporal del valor del portafolio (longitud = len(returns) + 1).
    """
    n_days = len(returns)
    portfolio = np.zeros(n_days + 1)
    portfolio[0] = initial_capital

    for t in range(n_days):
        # Rendimiento apalancado
        leveraged_return = leverage * returns[t]

        # Actualizar valor del portafolio
        new_value = portfolio[t] * (1 + leveraged_return)

        # Si el portafolio cae a cero, se liquida (margin call)
        if new_value <= 0:
            portfolio[t + 1:] = 0
            break
        portfolio[t + 1] = new_value

    return portfolio


def generate_market_scenarios(
    n_days: int = 1000,
    normal_vol: float = 0.01,
    crisis_vol: float = 0.04,
    crisis_start: int = 700,
    crisis_duration: int = 60,
    normal_drift: float = 0.0003,
    crisis_drift: float = -0.005,
    seed: int = 42,
) -> np.ndarray:
    """
    Genera rendimientos diarios del mercado con un periodo de crisis embebido.

    Durante la operacion normal, los rendimientos siguen una distribucion
    normal con drift positivo. Durante la crisis, la volatilidad aumenta
    significativamente y el drift se vuelve negativo.

    Parametros
    ----------
    n_days : int
        Numero total de dias de operacion.
    normal_vol : float
        Volatilidad diaria en periodo normal.
    crisis_vol : float
        Volatilidad diaria durante la crisis.
    crisis_start : int
        Dia en que comienza la crisis.
    crisis_duration : int
        Duracion de la crisis en dias.
    normal_drift : float
        Rendimiento medio diario en periodo normal.
    crisis_drift : float
        Rendimiento medio diario durante la crisis.
    seed : int
        Semilla para reproducibilidad.

    Retorna
    -------
    np.ndarray
        Rendimientos diarios simulados.
    """
    rng = np.random.default_rng(seed)

    returns = np.zeros(n_days)

    # Periodo normal previo a la crisis
    pre_crisis = min(crisis_start, n_days)
    returns[:pre_crisis] = rng.normal(loc=normal_drift, scale=normal_vol, size=pre_crisis)

    # Periodo de crisis
    crisis_end = min(crisis_start + crisis_duration, n_days)
    if crisis_start < n_days:
        n_crisis = crisis_end - crisis_start
        # La crisis incluye algunos shocks extremos (colas gruesas)
        base_crisis = rng.normal(loc=crisis_drift, scale=crisis_vol, size=n_crisis)

        # Inyectar dias de panico con caidas severas
        n_panic = max(1, n_crisis // 10)
        panic_days = rng.choice(n_crisis, size=n_panic, replace=False)
        base_crisis[panic_days] = rng.normal(loc=-0.08, scale=0.03, size=n_panic)

        returns[crisis_start:crisis_end] = base_crisis

    # Periodo de recuperacion post-crisis
    if crisis_end < n_days:
        n_recovery = n_days - crisis_end
        # Recuperacion gradual: volatilidad alta pero drift positivo
        recovery_vol = (normal_vol + crisis_vol) / 2
        returns[crisis_end:] = rng.normal(
            loc=normal_drift * 1.5, scale=recovery_vol, size=n_recovery
        )

    return returns


def compare_strategies(
    scenarios: np.ndarray,
    leverages: List[float],
    initial_capital: float = 1_000_000,
) -> Dict[float, dict]:
    """
    Compara distintos niveles de apalancamiento aplicados al mismo escenario.

    Parametros
    ----------
    scenarios : np.ndarray
        Rendimientos diarios del mercado.
    leverages : list
        Lista de niveles de apalancamiento a comparar.
    initial_capital : float
        Capital inicial (igual para todas las estrategias).

    Retorna
    -------
    dict
        Diccionario {apalancamiento: {metricas y serie temporal}}.
    """
    results = {}

    for lev in leverages:
        portfolio = simulate_portfolio(initial_capital, scenarios, leverage=lev)

        # Calcular metricas de desempenio
        final_value = portfolio[-1]
        peak = np.max(portfolio)
        # Maximo drawdown: peor caida desde un pico
        running_max = np.maximum.accumulate(portfolio)
        # Evitar division por cero en caso de portafolio liquidado
        with np.errstate(divide="ignore", invalid="ignore"):
            drawdowns = np.where(running_max > 0, (running_max - portfolio) / running_max, 0)
        max_drawdown = np.max(drawdowns)

        # Dia de liquidacion (si aplica)
        liquidated = portfolio[-1] <= 0
        liquidation_day = None
        if liquidated:
            zero_idx = np.where(portfolio <= 0)[0]
            if len(zero_idx) > 0:
                liquidation_day = zero_idx[0]

        # Rendimiento total
        total_return = (final_value / initial_capital - 1) * 100 if initial_capital > 0 else 0

        results[lev] = {
            "portfolio": portfolio,
            "valor_final": final_value,
            "rendimiento_total_%": total_return,
            "valor_pico": peak,
            "max_drawdown_%": max_drawdown * 100,
            "liquidado": liquidated,
            "dia_liquidacion": liquidation_day,
        }

    return results


def plot_ltcm_comparison(results: Dict[float, dict]) -> None:
    """
    Grafica la trayectoria de portafolios con distintos apalancamientos,
    mostrando como el apalancamiento amplifica ganancias y perdidas.

    Parametros
    ----------
    results : dict
        Salida de compare_strategies con las series temporales.
    """
    colores = {
        1: "#2196F3",    # azul para 1x
        5: "#4CAF50",    # verde para 5x
        10: "#FF9800",   # naranja para 10x
        25: "#F44336",   # rojo para 25x
    }

    _fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1]})

    # --- Panel superior: trayectorias de portafolio ---
    ax1 = axes[0]
    for lev, data in sorted(results.items()):
        portfolio = data["portfolio"]
        color = colores.get(int(lev), "gray")
        label = f"{int(lev)}x (Final: ${data['valor_final']:,.0f})"
        if data["liquidado"]:
            label = f"{int(lev)}x (LIQUIDADO dia {data['dia_liquidacion']})"
        ax1.plot(portfolio, color=color, linewidth=1.5, label=label, alpha=0.85)

    ax1.set_ylabel("Valor del Portafolio ($)")
    ax1.set_title(
        "Efecto del Apalancamiento: Portafolios con Crisis Embebida",
        fontsize=14,
        fontweight="bold",
    )
    ax1.legend(fontsize=10, loc="upper left")
    ax1.set_yscale("log")  # Escala logaritmica para ver todas las trayectorias
    ax1.set_ylim(bottom=100)
    ax1.axhline(y=1_000_000, color="gray", linestyle=":", alpha=0.5, label="Capital inicial")
    ax1.grid(True, alpha=0.3)

    # Sombrear periodo de crisis
    ax1.axvspan(700, 760, alpha=0.15, color="red", label="Crisis")

    # --- Panel inferior: rendimientos acumulados relativos ---
    ax2 = axes[1]
    for lev, data in sorted(results.items()):
        portfolio = data["portfolio"]
        # Rendimiento acumulado como porcentaje del capital inicial
        cum_return = (portfolio / portfolio[0] - 1) * 100
        color = colores.get(int(lev), "gray")
        ax2.plot(cum_return, color=color, linewidth=1.2, alpha=0.85)

    ax2.set_xlabel("Dia")
    ax2.set_ylabel("Rendimiento acumulado (%)")
    ax2.axhline(y=0, color="black", linewidth=0.8)
    ax2.axvspan(700, 760, alpha=0.15, color="red")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("data/ltcm_comparison.png", dpi=120, bbox_inches="tight")
    plt.show()
    print("Grafico guardado en data/ltcm_comparison.png")


if __name__ == "__main__":
    # --- Ejemplo de uso ---
    print("=" * 60)
    print("DEMO: Simulador de portafolio apalancado estilo LTCM")
    print("=" * 60)

    # 1. Generar escenario de mercado con crisis al dia 700
    print("\nGenerando escenario de mercado (1000 dias, crisis en dia 700)...")
    market_returns = generate_market_scenarios(
        n_days=1000,
        normal_vol=0.01,
        crisis_vol=0.04,
        crisis_start=700,
        crisis_duration=60,
    )

    # Estadisticos del mercado
    print(f"  Rendimiento medio diario: {np.mean(market_returns)*100:.4f}%")
    print(f"  Volatilidad diaria: {np.std(market_returns)*100:.4f}%")
    print(f"  Rendimiento minimo: {np.min(market_returns)*100:.2f}%")
    print(f"  Rendimiento maximo: {np.max(market_returns)*100:.2f}%")

    # 2. Comparar estrategias con distintos apalancamientos
    leverage_levels = [1, 5, 10, 25]
    print(f"\nComparando niveles de apalancamiento: {leverage_levels}")

    resultados = compare_strategies(
        scenarios=market_returns,
        leverages=leverage_levels,
        initial_capital=1_000_000,
    )

    # 3. Tabla resumen
    print("\n" + "-" * 75)
    print(f"{'Apalancamiento':>15} {'Valor Final':>15} {'Rendimiento':>12} "
          f"{'Max Drawdown':>13} {'Liquidado':>10}")
    print("-" * 75)

    for lev in leverage_levels:
        r = resultados[lev]
        estado = f"Dia {r['dia_liquidacion']}" if r["liquidado"] else "No"
        print(
            f"{int(lev):>14}x ${r['valor_final']:>14,.0f} "
            f"{r['rendimiento_total_%']:>11.1f}% "
            f"{r['max_drawdown_%']:>12.1f}% "
            f"{estado:>10}"
        )
    print("-" * 75)

    # 4. Leccion clave
    print("\nLeccion clave:")
    print("  El apalancamiento extremo puede generar rendimientos")
    print("  espectaculares en tiempos normales, pero un solo evento")
    print("  de crisis puede eliminar todo el capital (y mas).")
    print("  LTCM tenia apalancamiento de ~25x cuando colapso en 1998.")

    # 5. Graficar comparacion
    print("\nGenerando graficos...")
    plot_ltcm_comparison(resultados)
