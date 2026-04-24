"""
Demo: GVaR, GES y GTR -- Metricas Generativas de Riesgo.

Calcula las 3 metricas generativas de riesgo desde distribuciones
predictivas posteriores y las compara con VaR/ES clasicos.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/gvar_ges_gtr_demo.py
"""
import numpy as np
from scipy import stats


def generar_posterior_predictive(n_sim=50000, seed=42):
    """Genera retornos desde posterior predictive (tipo Apple).

    Simula incertidumbre parametrica (diferentes mu, sigma, nu)
    MAS incertidumbre aleatoria (retornos individuales).
    """
    np.random.seed(seed)

    # Posterior de parametros (simulando lo que PyMC produciria)
    mu_post = np.random.normal(0.0004, 0.0003, n_sim)
    sigma_post = np.abs(np.random.normal(0.013, 0.002, n_sim))
    nu_post = np.clip(np.random.exponential(4, n_sim) + 2, 2.5, 100)

    # Retornos: uno por cada muestra del posterior
    retornos = np.array([
        mu + sigma * np.random.standard_t(max(nu, 2.5))
        for mu, sigma, nu in zip(mu_post, sigma_post, nu_post)
    ])

    return retornos


def demo_3_metricas():
    """Calcula GVaR, GES y GTR."""
    print("=" * 65)
    print("1. GVaR, GES Y GTR: 3 METRICAS GENERATIVAS")
    print("=" * 65)

    retornos = generar_posterior_predictive()

    # Generativas
    gvar_95 = np.percentile(retornos, 5)
    ges_95 = retornos[retornos <= gvar_95].mean()
    gtr = retornos.min()

    # Clasicas (asumen Normal)
    mu = retornos.mean()
    sigma = retornos.std()
    var_95 = mu + stats.norm.ppf(0.05) * sigma
    es_95_normal = mu - sigma * stats.norm.pdf(stats.norm.ppf(0.05)) / 0.05

    print(f"\n  {50000:,} retornos desde posterior predictive")
    print(f"\n  {'Metrica':<25} {'Clasica (Normal)':<20} {'Generativa (PML)'}")
    print(f"  {'-'*60}")
    print(f"  {'VaR/GVaR 95%':<25} {var_95*100:>+10.2f}%     {gvar_95*100:>+10.2f}%")
    print(f"  {'ES/GES 95%':<25} {es_95_normal*100:>+10.2f}%     {ges_95*100:>+10.2f}%")
    print(f"  {'Tail Risk/GTR':<25} {'N/A':>10}       {gtr*100:>+10.2f}%")

    capital = 1_000_000
    print(f"\n  Con capital = ${capital:,}:")
    print(f"    GVaR: podrias perder hasta ${abs(gvar_95)*capital:,.0f} (1 en 20 dias)")
    print(f"    GES: si es un dia malo, pierdes ${abs(ges_95)*capital:,.0f} en promedio")
    print(f"    GTR: el peor escenario posible: ${abs(gtr)*capital:,.0f}")

    print(f"\n  Gap GES-GVaR: {abs(ges_95-gvar_95)*100:.2f}% "
          f"(severidad de la cola mas alla del GVaR)")
    print(f"  Ratio GES/GVaR: {ges_95/gvar_95:.2f}x")

    return retornos, gvar_95, ges_95, gtr


def demo_comparar_niveles(retornos):
    """GVaR/GES para diferentes niveles de confianza."""
    print("\n" + "=" * 65)
    print("2. GVaR Y GES PARA DIFERENTES NIVELES")
    print("=" * 65)

    niveles = [0.10, 0.05, 0.025, 0.01, 0.005]

    print(f"\n  {'Nivel':<10} {'GVaR':<12} {'GES':<12} {'N muestras cola':<18} {'Ratio GES/GVaR'}")
    print(f"  {'-'*60}")

    for alpha in niveles:
        gvar = np.percentile(retornos, alpha * 100)
        cola = retornos[retornos <= gvar]
        ges = cola.mean()
        ratio = ges / gvar if gvar != 0 else 0
        print(f"  {1-alpha:<10.1%} {gvar*100:>+8.2f}%   {ges*100:>+8.2f}%   "
              f"{len(cola):>12,}       {ratio:.2f}x")

    print(f"\n  -> A mayor confianza: GVaR y GES se alejan mas")
    print(f"  -> Ratio GES/GVaR CRECE con el nivel: colas mas pesadas")


def demo_stress_scenarios(retornos, gvar, ges, gtr):
    """Escenarios de stress usando las 3 metricas."""
    print("\n" + "=" * 65)
    print("3. STRESS SCENARIOS CON 3 METRICAS")
    print("=" * 65)

    capital = 1_000_000

    escenarios = [
        ("Dia normal (GVaR)", gvar, "1 en 20 dias"),
        ("Dia malo (GES)", ges, "promedio de peores 5%"),
        ("Peor caso (GTR)", gtr, "peor simulado de 50K"),
        ("2x GES", ges * 2, "escenario extremo"),
    ]

    print(f"\n  Capital: ${capital:,}")
    print(f"\n  {'Escenario':<25} {'Retorno':<12} {'Perdida ($)':<15} {'Frecuencia'}")
    print(f"  {'-'*65}")

    for nombre, ret, freq in escenarios:
        perdida = abs(ret) * capital
        print(f"  {nombre:<25} {ret*100:>+8.2f}%   ${perdida:>12,.0f}   {freq}")

    print(f"\n  -> Si tu portafolio NO sobrevive GTR, necesitas cobertura")
    print(f"  -> GES es la metrica mas util para sizing de posicion")
    print(f"  -> GTR es para stress testing de supervivencia")


def demo_resumen():
    """Resumen."""
    print("\n" + "=" * 65)
    print("4. RESUMEN: CUANDO USAR CADA METRICA")
    print("=" * 65)
    print("""
  Metrica   Pregunta que responde           Uso principal
  -------------------------------------------------------------------
  GVaR      Peor caso "normal" (95/99%)     Limites de riesgo diario
  GES       Severidad si GVaR se rompe      Sizing de posicion
  GTR       Peor caso absoluto simulado     Stress testing, supervivencia

  Ventajas de metricas generativas (vs clasicas):
  1. Propagan incertidumbre parametrica (no solo aleatoria)
  2. No asumen normalidad (capturan fat tails reales)
  3. Se calculan directamente desde posterior predictive
  4. Escalan a modelos complejos (via PyMC)
""")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: GVaR, GES Y GTR -- RIESGO GENERATIVO")
    print("  Modulo 8C")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    retornos, gvar, ges, gtr = demo_3_metricas()
    demo_comparar_niveles(retornos)
    demo_stress_scenarios(retornos, gvar, ges, gtr)
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
