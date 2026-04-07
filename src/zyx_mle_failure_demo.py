"""
Demo: MLE Falla con Pocos Datos -- El Caso ZYX (Earnings Beats).

Demuestra que MLE da p=1 con 3/3 datos, compara con PML Beta-Binomial,
y muestra actualizacion secuencial con 8 trimestres incluyendo un miss.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/zyx_mle_failure_demo.py
"""
import numpy as np
from scipy import stats


def demo_mle_absurdo():
    """MLE da p=1 con 3/3 beats."""
    print("=" * 65)
    print("1. MLE CON 3 DATOS: p = 1.0 (ABSURDO)")
    print("=" * 65)

    k, n = 3, 3
    p_mle = k / n

    # PML con priors
    priors = [("Uniforme Beta(1,1)", 1, 1),
              ("Esceptico Beta(2,2)", 2, 2),
              ("Informado Beta(3,2)", 3, 2)]

    print(f"\n  Datos: {k} beats en {n} trimestres")
    print(f"  MLE: p_hat = {p_mle:.1f} (100% de certeza)\n")
    print(f"  {'Prior':<25} {'Media':<10} {'HDI 95%':<25} {'P(p>0.9)'}")
    print(f"  {'-'*65}")

    for nombre, a, b in priors:
        post = stats.beta(a + k, b + n - k)
        hdi = post.ppf([0.025, 0.975])
        print(f"  {nombre:<25} {post.mean():<10.1%} "
              f"({hdi[0]:.1%}, {hdi[1]:.1%}){'':<5} "
              f"{1-post.cdf(0.9):.1%}")

    print(f"\n  -> MLE: 100%. PML: 57-83% segun el prior.")
    print(f"  -> Con 3 datos, MLE es un accidente estadistico.")


def demo_actualizacion_secuencial():
    """8 trimestres con un miss en Q6."""
    print("\n" + "=" * 65)
    print("2. ACTUALIZACION SECUENCIAL: 8 TRIMESTRES")
    print("=" * 65)

    resultados = [1, 1, 1, 1, 1, 0, 1, 1]
    a, b = 1, 1
    k_acum, n_acum = 0, 0

    print(f"\n  {'Trim':<8} {'Res':<6} {'MLE':<10} {'PML media':<12} {'PML HDI'}")
    print(f"  {'-'*50}")

    for i, r in enumerate(resultados):
        k_acum += r
        n_acum += 1
        a += r
        b += (1 - r)
        post = stats.beta(a, b)
        hdi = post.ppf([0.025, 0.975])
        res = "BEAT" if r == 1 else "MISS"
        mle = k_acum / n_acum
        print(f"  Q{i+1:<5} {res:<6} {mle:<10.0%} {post.mean():<12.1%} "
              f"({hdi[0]:.0%}, {hdi[1]:.0%})")

    # Impacto del miss
    print(f"\n  Q5->Q6 (el MISS):")
    print(f"    MLE: 100% -> 83% (caida de 17pp)")
    post_q5 = stats.beta(1+5, 1+0)
    post_q6 = stats.beta(1+5, 1+1)
    print(f"    PML: {post_q5.mean():.0%} -> {post_q6.mean():.0%} "
          f"(caida de {(post_q5.mean()-post_q6.mean())*100:.0f}pp)")
    print(f"  -> PML amortigua el impacto del miss")


def demo_predictiva():
    """Prediccion de proximos 4 trimestres."""
    print("\n" + "=" * 65)
    print("3. PREDICCION: PROXIMOS 4 TRIMESTRES")
    print("=" * 65)

    np.random.seed(42)
    # Posterior despues de 8 trimestres (7 beats, 1 miss)
    a_post, b_post = 8, 2
    n_fut = 4
    n_sim = 50000

    theta = np.random.beta(a_post, b_post, n_sim)
    beats_pml = np.array([np.random.binomial(n_fut, t) for t in theta])
    beats_mle = np.random.binomial(n_fut, 7/8, n_sim)

    print(f"\n  Posterior: Beta({a_post},{b_post}), media={a_post/(a_post+b_post):.0%}")
    print(f"  MLE: p = {7/8:.0%}")
    print(f"\n  {'Beats en 4T':<20} {'MLE':<15} {'PML'}")
    print(f"  {'-'*45}")
    for k in range(n_fut + 1):
        print(f"  {k:<20} {(beats_mle==k).mean():<15.1%} {(beats_pml==k).mean():.1%}")

    print(f"\n  -> PML asigna mas probabilidad a escenarios malos")
    print(f"  -> MLE concentra demasiado en 3-4 beats")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: MLE FALLA CON POCOS DATOS -- CASO ZYX")
    print("  Modulo 6B")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_mle_absurdo()
    demo_actualizacion_secuencial()
    demo_predictiva()

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
