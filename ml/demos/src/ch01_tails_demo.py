#!/usr/bin/env python3
"""
Capítulo 1: Tail Risk Demo - Forward Binomial & Trinomial Models
================
Source: turn0browsertab744690698
Purpose: Demonstrate Fed rate trajectory modeling for investment decisions

Scenario: US Federal Reserve holds a meeting. 
Current rate: 5.50%
Task: Predict rate after N meetings given probability p of hike

Demo ejecutado:
1. Forward binomial (only hike or hold)
2. Time-varying probabilities (Fed stance evolves)
3. Trinomial post-shock (Fed can now hike, hold, or cut)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import binom, multinomial


def generate_returns(
    n: int = 1000,
    mu: float = 0.0005,
    sigma: float = 0.01,
    regime_shift: bool = True,
    outliers: int = 15,
    seed: int = 42,
) -> np.ndarray:
    """
    Genera rendimientos sinteticos con regimenes de volatilidad y valores atipicos.

    Parametros
    ----------
    n : int
        Numero de observaciones a generar.
    mu : float
        Rendimiento medio diario.
    sigma : float
        Desviacion estandar base.
    regime_shift : bool
        Si True, introduce un periodo de alta volatilidad en el medio de la serie.
    outliers : int
        Cantidad de valores atipicos inyectados aleatoriamente.
    seed : int
        Semilla para reproducibilidad.

    Retorna
    -------
    np.ndarray
        Arreglo con los rendimientos sinteticos.
    """
    rng = np.random.default_rng(seed)

    # Rendimientos base con distribucion normal
    returns = rng.normal(loc=mu, scale=sigma, size=n)

    # Cambio de regimen: la volatilidad se triplica en el tercio central
    if regime_shift:
        start = n // 3
        end = 2 * n // 3
        returns[start:end] = rng.normal(loc=-0.001, scale=sigma * 3, size=end - start)

    # Inyectar valores atipicos (shocks extremos)
    if outliers > 0:
        idx_outliers = rng.choice(n, size=outliers, replace=False)
        # Shocks de entre 4 y 8 desviaciones estandar, con signo aleatorio
        signs = rng.choice([-1, 1], size=outliers)
        magnitudes = rng.uniform(4, 8, size=outliers)
        returns[idx_outliers] += signs * magnitudes * sigma

    return returns


def compare_distributions(
    real_returns: np.ndarray, simulated_normal: np.ndarray
) -> pd.DataFrame:
    """
    Compara rendimientos reales contra una muestra normal usando estadisticos
    descriptivos: media, desviacion estandar, asimetria y curtosis.

    Parametros
    ----------
    real_returns : np.ndarray
        Rendimientos con colas gruesas (o datos reales).
    simulated_normal : np.ndarray
        Rendimientos generados con distribucion normal pura.

    Retorna
    -------
    pd.DataFrame
        Tabla comparativa de estadisticos.
    """
    # Calcular estadisticos para ambas distribuciones
    stats_dict = {
        "Estadistico": [
            "Media",
            "Desv. Estandar",
            "Asimetria (Skewness)",
            "Curtosis (Excess)",
            "Minimo",
            "Maximo",
            "Jarque-Bera p-valor",
        ],
        "Fat-Tailed": [
            np.mean(real_returns),
            np.std(real_returns, ddof=1),
            stats.skew(real_returns),
            stats.kurtosis(real_returns),  # curtosis en exceso (Fisher)
            np.min(real_returns),
            np.max(real_returns),
            stats.jarque_bera(real_returns).pvalue,
        ],
        "Normal": [
            np.mean(simulated_normal),
            np.std(simulated_normal, ddof=1),
            stats.skew(simulated_normal),
            stats.kurtosis(simulated_normal),
            np.min(simulated_normal),
            np.max(simulated_normal),
            stats.jarque_bera(simulated_normal).pvalue,
        ],
    }

    df = pd.DataFrame(stats_dict)
    return df


def plot_fat_tails(returns: np.ndarray, title: str = "Distribucion de Rendimientos") -> None:
    """
    Grafica un histograma de rendimientos con una curva normal superpuesta
    para evidenciar las colas gruesas.

    Parametros
    ----------
    returns : np.ndarray
        Rendimientos a graficar.
    title : str
        Titulo del grafico.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Panel izquierdo: histograma con curva normal ---
    ax = axes[0]
    ax.hist(returns, bins=80, density=True, alpha=0.65, color="steelblue", label="Datos")

    # Superponer la curva normal ajustada
    mu_fit, sigma_fit = np.mean(returns), np.std(returns, ddof=1)
    x_grid = np.linspace(returns.min(), returns.max(), 400)
    pdf_normal = stats.norm.pdf(x_grid, loc=mu_fit, scale=sigma_fit)
    ax.plot(x_grid, pdf_normal, "r-", linewidth=2, label="Normal ajustada")

    ax.set_title(title)
    ax.set_xlabel("Rendimiento")
    ax.set_ylabel("Densidad")
    ax.legend()

    # --- Panel derecho: QQ-plot contra la normal ---
    ax2 = axes[1]
    stats.probplot(returns, dist="norm", plot=ax2)
    ax2.set_title("QQ-Plot vs Normal")
    ax2.get_lines()[0].set_markerfacecolor("steelblue")
    ax2.get_lines()[0].set_markersize(3)

    plt.tight_layout()
    plt.savefig("data/fat_tails_plot.png", dpi=120, bbox_inches="tight")
    plt.show()
    print("Grafico guardado en data/fat_tails_plot.png")


def mean_ci(series: np.ndarray, alpha: float = 0.05) -> dict:
    """
    Calcula la media y su intervalo de confianza usando la distribucion t.

    Parametros
    ----------
    series : np.ndarray
        Serie de datos.
    alpha : float
        Nivel de significancia (por defecto 0.05 para 95% de confianza).

    Retorna
    -------
    dict
        Diccionario con la media, los limites inferior y superior
        del intervalo, y el error estandar.
    """
    n = len(series)
    mean_val = np.mean(series)
    se = stats.sem(series)  # error estandar de la media

    # Valor critico de la distribucion t
    t_crit = stats.t.ppf(1 - alpha / 2, df=n - 1)

    lower = mean_val - t_crit * se
    upper = mean_val + t_crit * se

    return {
        "media": mean_val,
        "error_estandar": se,
        "ci_inferior": lower,
        "ci_superior": upper,
        "nivel_confianza": 1 - alpha,
    }


if __name__ == "__main__":
    # --- Ejemplo de uso ---
    print("=" * 60)
    print("DEMO: Colas gruesas en rendimientos financieros")
    print("=" * 60)

    # 1. Generar rendimientos sinteticos con colas gruesas
    n_obs = 1000
    fat_returns = generate_returns(
        n=n_obs, mu=0.0003, sigma=0.012, regime_shift=True, outliers=20
    )

    # 2. Generar muestra normal pura para comparacion
    rng = np.random.default_rng(99)
    normal_returns = rng.normal(
        loc=np.mean(fat_returns), scale=np.std(fat_returns), size=n_obs
    )

    # 3. Comparar distribuciones
    tabla = compare_distributions(fat_returns, normal_returns)
    print("\nComparacion de distribuciones:")
    print(tabla.to_string(index=False))

    # 4. Intervalo de confianza de la media
    ci = mean_ci(fat_returns, alpha=0.05)
    print(f"\nMedia de rendimientos fat-tailed: {ci['media']:.6f}")
    print(
        f"IC 95%: [{ci['ci_inferior']:.6f}, {ci['ci_superior']:.6f}]"
    )
    print(f"Error estandar: {ci['error_estandar']:.6f}")

    # 5. Interpretar la curtosis
    kurt = stats.kurtosis(fat_returns)
    print(f"\nCurtosis en exceso: {kurt:.2f}")
    if kurt > 0:
        print("  -> Curtosis positiva: colas mas gruesas que la normal (leptocurtica).")
    else:
        print("  -> Curtosis cercana a cero o negativa: similar a la normal.")

    # 6. Graficar
    print("\nGenerando graficos...")
    plot_fat_tails(fat_returns, title="Rendimientos sinteticos con colas gruesas")
