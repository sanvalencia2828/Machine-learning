"""
Demo: Inferencia Bayesiana para Default de Bonos High-Yield.

Parametriza priors por rating, actualiza con eventos (downgrades/upgrades),
y genera distribucion predictiva de defaults para un portafolio.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/hy_default_demo.py
"""
import numpy as np
from scipy import stats


RATING_PRIORS = {
    "BBB": (2, 18), "BB": (3, 12), "B": (4, 8), "CCC": (5, 5),
}
EVENTS = {
    "downgrade": (1.0, 0.0), "upgrade": (0.0, 2.0), "neutral": (0.0, 1.0),
}


def actualizar(alpha, beta, eventos):
    """Actualiza posterior con lista de eventos."""
    tray = [{"a": alpha, "b": beta, "media": alpha/(alpha+beta)}]
    a, b = alpha, beta
    for ev in eventos:
        da, db = EVENTS[ev]
        a += da
        b += db
        tray.append({"a": a, "b": b, "media": a/(a+b), "evento": ev})
    return tray


def demo_megacorp():
    """Caso MegaCorp: BB con 8 trimestres de eventos."""
    print("=" * 65)
    print("1. MEGACORP: ACTUALIZACION SECUENCIAL")
    print("=" * 65)

    alpha, beta = RATING_PRIORS["BB"]
    eventos = ["neutral", "downgrade", "neutral", "downgrade",
               "neutral", "neutral", "upgrade", "neutral"]

    tray = actualizar(alpha, beta, eventos)

    print(f"\n  Rating inicial: BB, Prior Beta({alpha},{beta}), media={alpha/(alpha+beta):.0%}")
    print(f"\n  {'T':<4} {'Evento':<12} {'Alpha':<8} {'Beta':<8} {'P(def)':<10}")
    print(f"  {'-'*45}")
    print(f"  {0:<4} {'prior':<12} {alpha:<8.1f} {beta:<8.1f} {alpha/(alpha+beta):<10.1%}")
    for i, t in enumerate(tray[1:], 1):
        print(f"  {i:<4} {t['evento']:<12} {t['a']:<8.1f} {t['b']:<8.1f} {t['media']:<10.1%}")

    # P(default > 30%) antes y despues
    p_30_prior = 1 - stats.beta(alpha, beta).cdf(0.30)
    final = tray[-1]
    p_30_post = 1 - stats.beta(final['a'], final['b']).cdf(0.30)
    print(f"\n  P(default > 30%):")
    print(f"    Prior: {p_30_prior:.1%}")
    print(f"    Posterior (T8): {p_30_post:.1%}")


def demo_portafolio():
    """Portafolio de 15 bonos con posteriors diferentes."""
    print("\n" + "=" * 65)
    print("2. PORTAFOLIO: DISTRIBUCION PREDICTIVA DE DEFAULTS")
    print("=" * 65)

    np.random.seed(42)
    bonos = []
    for i in range(15):
        rating = np.random.choice(["BB", "B", "BBB"], p=[0.5, 0.3, 0.2])
        a, b = RATING_PRIORS.get(rating, (3, 12))
        n_ev = np.random.randint(2, 8)
        eventos = np.random.choice(["neutral", "downgrade", "upgrade"],
                                    n_ev, p=[0.5, 0.35, 0.15]).tolist()
        tray = actualizar(a, b, eventos)
        final = tray[-1]
        bonos.append({"rating": rating, "a": final["a"], "b": final["b"],
                       "p": final["media"]})

    print(f"\n  {'Bono':<8} {'Rating':<8} {'P(default)'}")
    print(f"  {'-'*30}")
    for i, bo in enumerate(bonos):
        print(f"  {i+1:<8} {bo['rating']:<8} {bo['p']:.1%}")

    # Predictive
    n_sim = 50000
    defaults = np.zeros(n_sim, dtype=int)
    for bo in bonos:
        theta = np.random.beta(bo["a"], bo["b"], n_sim)
        defaults += (np.random.random(n_sim) < theta).astype(int)

    print(f"\n  Distribucion predictiva ({n_sim:,} sims):")
    print(f"    Media: {defaults.mean():.1f} defaults")
    print(f"    P(0 defaults): {(defaults==0).mean():.1%}")
    print(f"    P(3+ defaults): {(defaults>=3).mean():.1%}")
    print(f"    P(5+ defaults): {(defaults>=5).mean():.1%}")

    # Comparar con frecuentista
    p_fija = np.mean([bo["p"] for bo in bonos])
    p_3_freq = 1 - stats.binom.cdf(2, 15, p_fija)
    print(f"\n  Comparacion:")
    print(f"    Bayesiano P(3+): {(defaults>=3).mean():.1%}")
    print(f"    Frecuentista P(3+): {p_3_freq:.1%} (p_fija={p_fija:.1%})")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: INFERENCIA BAYESIANA PARA DEFAULT HIGH-YIELD")
    print("  Modulo 5B")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_megacorp()
    demo_portafolio()

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
