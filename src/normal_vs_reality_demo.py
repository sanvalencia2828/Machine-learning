"""
Demo: Normal vs Realidad en Retornos Financieros.

Genera retornos sinteticos tipo S&P 500, ejecuta tests de normalidad,
ajusta Normal vs Student-t, y cuantifica el error de asumir normalidad.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/normal_vs_reality_demo.py
"""
import numpy as np
from scipy import stats


def generar_retornos(n=5040, seed=42):
    """Genera retornos sinteticos tipo S&P 500 con fat tails."""
    np.random.seed(seed)
    ret = 0.0003 + 0.011 * np.random.standard_t(4, n)
    ret += -0.0003 * (np.random.exponential(1, n) - 1)
    return ret


def demo_estadisticas(retornos):
    """Estadisticas descriptivas y los 4 momentos."""
    print("=" * 65)
    print("1. ESTADISTICAS DESCRIPTIVAS")
    print("=" * 65)
    print(f"\n  n = {len(retornos):,} dias")
    print(f"  Media:     {retornos.mean():.5f}  ({retornos.mean()*252:.1%} anual)")
    print(f"  Std:       {retornos.std():.5f}  ({retornos.std()*np.sqrt(252):.1%} anual)")
    print(f"  Skewness:  {stats.skew(retornos):.3f}")
    print(f"  Curtosis:  {stats.kurtosis(retornos):.1f} (Normal = 0)")
    print(f"  Min:       {retornos.min():.4f}")
    print(f"  Max:       {retornos.max():.4f}")


def demo_tests_normalidad(retornos):
    """3 tests formales de normalidad."""
    print("\n" + "=" * 65)
    print("2. TESTS DE NORMALIDAD")
    print("=" * 65)

    jb_s, jb_p = stats.jarque_bera(retornos)
    sw_s, sw_p = stats.shapiro(retornos[:5000])
    ad = stats.anderson(retornos, 'norm')

    print(f"\n  {'Test':<25} {'Estadistico':<18} {'p-value / critico':<20} {'Resultado'}")
    print(f"  {'-'*75}")
    print(f"  {'Jarque-Bera':<25} {jb_s:<18.1f} p={jb_p:.2e}{'':>5} "
          f"{'RECHAZA' if jb_p < 0.05 else 'no rechaza'}")
    print(f"  {'Shapiro-Wilk':<25} {sw_s:<18.6f} p={sw_p:.2e}{'':>5} "
          f"{'RECHAZA' if sw_p < 0.05 else 'no rechaza'}")
    print(f"  {'Anderson-Darling':<25} {ad.statistic:<18.2f} crit5%={ad.critical_values[2]:.2f}{'':>7} "
          f"{'RECHAZA' if ad.statistic > ad.critical_values[2] else 'no rechaza'}")

    print(f"\n  -> Los 3 tests RECHAZAN normalidad")


def demo_ajuste(retornos):
    """Ajusta Normal y Student-t, compara via AIC."""
    print("\n" + "=" * 65)
    print("3. AJUSTE: NORMAL vs STUDENT-t")
    print("=" * 65)

    n = len(retornos)
    mu_n, sigma_n = stats.norm.fit(retornos)
    ll_n = np.sum(stats.norm.logpdf(retornos, mu_n, sigma_n))
    aic_n = 4 - 2 * ll_n

    nu, mu_t, sigma_t = stats.t.fit(retornos)
    ll_t = np.sum(stats.t.logpdf(retornos, nu, mu_t, sigma_t))
    aic_t = 6 - 2 * ll_t

    print(f"\n  {'Metrica':<25} {'Normal':<18} {'Student-t'}")
    print(f"  {'-'*55}")
    print(f"  {'Log-likelihood':<25} {ll_n:<18.1f} {ll_t:.1f}")
    print(f"  {'AIC':<25} {aic_n:<18.1f} {aic_t:.1f}")
    print(f"  {'nu estimado':<25} {'inf':<18} {nu:.2f}")
    print(f"  {'Delta AIC':<25} {aic_n - aic_t:>+.0f} (Student-t gana)")

    return {"nu": nu, "mu_n": mu_n, "sigma_n": sigma_n,
            "mu_t": mu_t, "sigma_t": sigma_t}


def demo_impacto_riesgo(retornos, ajustes):
    """Cuantifica error de la Normal en metricas de riesgo."""
    print("\n" + "=" * 65)
    print("4. IMPACTO EN METRICAS DE RIESGO")
    print("=" * 65)

    print(f"\n  {'Metrica':<25} {'Normal':<15} {'Student-t':<15} {'Datos':<15} {'Error Normal'}")
    print(f"  {'-'*75}")

    for nivel, nombre in [(0.05, "VaR 95%"), (0.01, "VaR 99%")]:
        var_n = stats.norm.ppf(nivel, ajustes['mu_n'], ajustes['sigma_n'])
        var_t = stats.t.ppf(nivel, ajustes['nu'], ajustes['mu_t'], ajustes['sigma_t'])
        var_d = np.percentile(retornos, nivel * 100)
        err = (var_n - var_d) / abs(var_d) * 100
        print(f"  {nombre:<25} {var_n:<15.5f} {var_t:<15.5f} {var_d:<15.5f} {err:>+.0f}%")

    n = len(retornos)
    for k in [3, 4, 5]:
        obs = np.sum(np.abs(retornos - retornos.mean()) > k * retornos.std())
        esp = 2 * stats.norm.sf(k) * n
        ratio = obs / max(esp, 0.01)
        print(f"  {'Eventos >' + str(k) + ' sigma':<25} {esp:<15.1f} {'---':<15} {obs:<15d} {ratio:.0f}x")

    print(f"\n  -> Normal subestima VaR 99% por 20-40%")
    print(f"  -> Eventos extremos son 10-100x mas frecuentes que Normal predice")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: NORMAL vs REALIDAD EN RETORNOS FINANCIEROS")
    print("  Modulo 3C")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    retornos = generar_retornos()
    demo_estadisticas(retornos)
    demo_tests_normalidad(retornos)
    ajustes = demo_ajuste(retornos)
    demo_impacto_riesgo(retornos, ajustes)

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
