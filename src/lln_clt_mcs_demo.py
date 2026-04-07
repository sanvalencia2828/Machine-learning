"""
Demo: LGN, TLC y los Fundamentos de Monte Carlo Simulation.

Demuestra convergencia (LGN), normalidad de medias (TLC), tasa 1/sqrt(N),
contra-ejemplo Cauchy, e intervalos de confianza para estimaciones MCS.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/lln_clt_mcs_demo.py
"""
import numpy as np
from scipy import stats


def demo_lgn():
    """Demuestra convergencia del promedio a E[X]."""
    print("=" * 65)
    print("1. LEY DE GRANDES NUMEROS: CONVERGENCIA")
    print("=" * 65)

    np.random.seed(42)
    ns = [10, 100, 1000, 10000, 100000]

    print(f"\n  Distribucion: Exponencial(lambda=2), E[X] = 2.0\n")
    print(f"  {'N':<12} {'Media muestral':<18} {'Error abs':<12} {'Error %'}")
    print(f"  {'-'*50}")

    for n in ns:
        datos = np.random.exponential(2, n)
        media = datos.mean()
        error = abs(media - 2.0)
        print(f"  {n:<12,d} {media:<18.6f} {error:<12.6f} {error/2*100:.3f}%")

    print(f"\n  -> El error baja con ~1/sqrt(N)")
    print(f"  -> De N=100 a N=10000 (100x): error baja ~10x")


def demo_tlc():
    """Demuestra que medias muestrales son Normales."""
    print("\n" + "=" * 65)
    print("2. TEOREMA DEL LIMITE CENTRAL: MEDIAS SON NORMALES")
    print("=" * 65)

    np.random.seed(42)
    n_rep = 10000
    tamanos = [5, 20, 100]

    # Exponencial (asimetrica)
    print(f"\n  Distribucion base: Exponencial(2) -- skew = 2.0\n")
    print(f"  {'n muestra':<12} {'Skew medias':<15} {'Kurt exc medias':<18} {'JB p-value':<15} {'Normal?'}")
    print(f"  {'-'*65}")

    for n in tamanos:
        medias = np.array([np.random.exponential(2, n).mean() for _ in range(n_rep)])
        sk = stats.skew(medias)
        ku = stats.kurtosis(medias)
        _, jb_p = stats.jarque_bera(medias)
        es_normal = "SI" if jb_p > 0.05 else "no"
        print(f"  {n:<12d} {sk:<15.3f} {ku:<18.3f} {jb_p:<15.4f} {es_normal}")

    print(f"\n  -> Con n=5: medias aun asimetricas")
    print(f"  -> Con n>=20: medias ya son ~Normales (TLC funciona)")


def demo_cauchy():
    """Contra-ejemplo: TLC falla con Cauchy."""
    print("\n" + "=" * 65)
    print("3. CONTRA-EJEMPLO: CAUCHY (VARIANZA INFINITA)")
    print("=" * 65)

    np.random.seed(42)
    n_rep = 5000

    print(f"\n  Cauchy tiene varianza INFINITA -> TLC NO se cumple\n")
    print(f"  {'n muestra':<12} {'Std medias':<15} {'Converge?'}")
    print(f"  {'-'*40}")

    for n in [5, 20, 100, 1000]:
        medias = np.array([np.random.standard_cauchy(n).mean() for _ in range(n_rep)])
        # Usar MAD en vez de std (mas robusta)
        mad = np.median(np.abs(medias - np.median(medias)))
        print(f"  {n:<12d} MAD={mad:<12.3f} {'NO' if mad > 0.5 else '?'}")

    print(f"\n  -> La dispersion de las medias NO se reduce con n")
    print(f"  -> Cauchy viola el TLC: varianza infinita")
    print(f"  -> Leccion: verifica que Var(X) sea finita antes de usar MCS")


def demo_mcs_ic():
    """MCS con intervalos de confianza para P(loss > 5%)."""
    print("\n" + "=" * 65)
    print("4. MCS CON INTERVALOS DE CONFIANZA")
    print("=" * 65)

    np.random.seed(42)
    # Valor "real"
    ret_real = 0.0003 + 0.012 * np.random.standard_t(4, 1_000_000)
    p_real = (ret_real < -0.05).mean()

    print(f"\n  Estimando P(retorno diario < -5%)")
    print(f"  Valor 'real' (1M sims): {p_real:.4%}\n")
    print(f"  {'N sims':<12} {'Estimacion':<14} {'IC 95%':<28} {'Ancho':<10} {'OK?'}")
    print(f"  {'-'*68}")

    for N in [100, 500, 1000, 5000, 10000, 100000]:
        np.random.seed(42 + N)
        ret = 0.0003 + 0.012 * np.random.standard_t(4, N)
        p = (ret < -0.05).mean()
        se = np.sqrt(p * (1 - p) / N)
        lo, hi = p - 1.96*se, p + 1.96*se
        ok = "SI" if lo <= p_real <= hi else "NO"
        print(f"  {N:<12,d} {p:<14.4%} ({lo:.4%}, {hi:.4%}){'':>5} "
              f"{hi-lo:<10.4%} {ok}")

    print(f"\n  -> IC se estrecha con sqrt(N)")
    print(f"  -> TLC garantiza la validez del IC")


def demo_pricing():
    """Pricing de opcion call por MCS."""
    print("\n" + "=" * 65)
    print("5. PRICING DE OPCION CALL POR MCS")
    print("=" * 65)

    S, K, T, r, sigma = 100, 105, 0.25, 0.05, 0.25

    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    bsm = S*stats.norm.cdf(d1) - K*np.exp(-r*T)*stats.norm.cdf(d2)

    print(f"\n  BSM analitico: ${bsm:.4f}\n")
    print(f"  {'N':<12} {'MCS':<12} {'Error':<12} {'IC 95%':<25}")
    print(f"  {'-'*60}")

    for N in [100, 1000, 10000, 100000]:
        np.random.seed(42)
        z = np.random.normal(0, 1, N)
        ST = S * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*z)
        disc = np.exp(-r*T) * np.maximum(ST - K, 0)
        precio = disc.mean()
        se = disc.std() / np.sqrt(N)
        print(f"  {N:<12,d} ${precio:<11.4f} ${abs(precio-bsm):<11.4f} "
              f"(${precio-1.96*se:.4f}, ${precio+1.96*se:.4f})")

    print(f"\n  -> MCS converge a BSM con mas simulaciones")
    print(f"  -> IC cuantifica la precision de la estimacion")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: LGN, TLC Y FUNDAMENTOS DE MONTE CARLO")
    print("  Modulo 3D")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_lgn()
    demo_tlc()
    demo_cauchy()
    demo_mcs_ic()
    demo_pricing()

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
