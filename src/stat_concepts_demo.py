"""
Demo: Conceptos Estadisticos y Critica a la Volatilidad.

Calcula los 4 momentos (media, varianza, skewness, curtosis), demuestra
por que la volatilidad es insuficiente, y compara Normal vs fat tails
vs mezclas. Incluye demo de no-ergodicidad.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/stat_concepts_demo.py
"""
import numpy as np
from scipy import stats


def demo_4_momentos():
    """Calcula los 4 momentos para 3 distribuciones con ~misma std."""
    print("=" * 65)
    print("1. LOS 4 MOMENTOS: 3 DISTRIBUCIONES CON ~MISMA VOLATILIDAD")
    print("=" * 65)

    np.random.seed(42)
    n = 50000

    ret_n = np.random.normal(0.0004, 0.012, n)
    ret_t = 0.0004 + 0.0085 * np.random.standard_t(4, n)
    mask = np.random.binomial(1, 0.95, n).astype(bool)
    ret_m = np.where(mask,
        np.random.normal(0.0006, 0.009, n),
        np.random.normal(-0.008, 0.04, n))

    distribuciones = [
        ("Normal", ret_n),
        ("Student-t(4)", ret_t),
        ("Mezcla 95/5", ret_m),
    ]

    print(f"\n  {'Metrica':<25}", end="")
    for nombre, _ in distribuciones:
        print(f"{nombre:<18}", end="")
    print()
    print(f"  {'-'*60}")

    for metrica, func in [
        ("Media", lambda d: d.mean()),
        ("Std (volatilidad)", lambda d: d.std()),
        ("Skewness", lambda d: float(stats.skew(d))),
        ("Curtosis exceso", lambda d: float(stats.kurtosis(d))),
        ("VaR 95%", lambda d: np.percentile(d, 5)),
        ("Expected Shortfall 95%", lambda d: d[d <= np.percentile(d, 5)].mean()),
        ("P(retorno < -3%)", lambda d: (d < -0.03).mean()),
        ("Peor retorno", lambda d: d.min()),
    ]:
        print(f"  {metrica:<25}", end="")
        for _, datos in distribuciones:
            val = func(datos)
            print(f"{val:<18.6f}", end="")
        print()

    print(f"\n  -> MISMA volatilidad, DIFERENTE riesgo real")
    print(f"  -> Skewness y curtosis revelan lo que sigma esconde")

    return distribuciones


def demo_eventos_extremos(distribuciones):
    """Compara eventos extremos observados vs Normal."""
    print("\n" + "=" * 65)
    print("2. EVENTOS EXTREMOS: NORMAL PREDICE vs REALIDAD")
    print("=" * 65)

    for nombre, datos in distribuciones:
        mu, sigma = datos.mean(), datos.std()
        n = len(datos)
        print(f"\n  {nombre}:")
        print(f"  {'Umbral':<12} {'Normal predice':<16} {'Observados':<14} {'Ratio'}")
        print(f"  {'-'*50}")
        for k in [2, 3, 4, 5]:
            p_norm = 2 * stats.norm.sf(k)
            esperados = p_norm * n
            observados = np.sum(np.abs(datos - mu) > k * sigma)
            ratio = observados / max(esperados, 0.01)
            print(f"  {k} sigma     {esperados:>12.1f}    {observados:>10d}   {ratio:>6.1f}x")


def demo_ergodicidad():
    """Demuestra no-ergodicidad: E[R]>0 pero la mayoria pierde."""
    print("\n" + "=" * 65)
    print("3. NO-ERGODICIDAD: VALOR ESPERADO vs EXPERIENCIA REAL")
    print("=" * 65)

    np.random.seed(42)
    n_pasos, n_tray = 100, 10000

    factores = np.where(
        np.random.binomial(1, 0.5, (n_tray, n_pasos)),
        1.5, 0.6)

    riqueza_final = 100 * np.prod(factores, axis=1)

    print(f"\n  Juego: +50% o -40% con p=0.5")
    print(f"  E[R] por paso: {0.5*1.5 + 0.5*0.6 - 1:+.0%} (parece buen negocio)")
    print(f"  Media geometrica: {np.sqrt(1.5*0.6) - 1:+.1%} (realidad)")
    print(f"\n  Despues de {n_pasos} pasos ({n_tray:,} simulaciones):")
    print(f"    Media del ensamble:  ${riqueza_final.mean():>12,.2f}")
    print(f"    Mediana:             ${np.median(riqueza_final):>12.4f}")
    print(f"    P(perder dinero):    {(riqueza_final < 100).mean():>10.0%}")
    print(f"    P(perder >90%):      {(riqueza_final < 10).mean():>10.0%}")
    print(f"\n  -> La media del ensamble sube (unos pocos ganan mucho)")
    print(f"  -> La mediana colapsa (la MAYORIA pierde casi todo)")
    print(f"  -> E[R] > 0 NO implica que es buena inversion")


def demo_resumen():
    """Resumen de implicaciones."""
    print("\n" + "=" * 65)
    print("4. RESUMEN: DE SIGMA A DISTRIBUCIONES COMPLETAS")
    print("=" * 65)
    print("""
  Momento   Nombre       Que mide              Normal asume
  -----------------------------------------------------------
  1         Media        Centro                Cualquier valor
  2         Varianza     Dispersion            UNICO param riesgo
  3         Skewness     Asimetria             = 0 (simetrica)
  4         Curtosis     Peso de colas         = 3 (delgadas)

  La volatilidad:
  - Solo captura el momento 2
  - Ignora asimetria y colas pesadas
  - Trata subidas y bajadas como iguales
  - Subestima riesgo extremo por ordenes de magnitud

  Alternativas: VaR, ES, downside deviation, distribuciones completas
""")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: CONCEPTOS ESTADISTICOS Y CRITICA A LA VOLATILIDAD")
    print("  Modulo 3B")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    distribuciones = demo_4_momentos()
    demo_eventos_extremos(distribuciones)
    demo_ergodicidad()
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
