"""
Demo: Black-Scholes y la Trinidad de la Incertidumbre.

Demuestra las tres fallas de BSM mapeadas a los tres tipos de
incertidumbre (aleatoria, epistemica, ontologica). Incluye pricing,
volatility smile sintetico y comparacion cuantitativa.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/bsm_uncertainty_demo.py
"""
import numpy as np
from scipy import stats
from scipy.optimize import brentq


# ============================================================
# 1. Black-Scholes pricing
# ============================================================

def bsm_call(S, K, T, r, sigma):
    """Precio call europea Black-Scholes.

    Parametros
    ----------
    S : float
        Precio del subyacente.
    K : float
        Strike.
    T : float
        Tiempo al vencimiento (anos).
    r : float
        Tasa libre de riesgo.
    sigma : float
        Volatilidad anualizada.

    Retorna
    -------
    float : precio de la opcion call.
    """
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)


def bsm_put(S, K, T, r, sigma):
    """Precio put europea via paridad put-call."""
    return bsm_call(S, K, T, r, sigma) - S + K * np.exp(-r * T)


def demo_pricing_basico():
    """Demuestra pricing BSM con diferentes parametros."""
    print("=" * 60)
    print("1. BLACK-SCHOLES: PRICING BASICO")
    print("=" * 60)

    S, K, T, r = 150.0, 155.0, 0.25, 0.05
    sigmas = [0.15, 0.20, 0.25, 0.30, 0.40]

    print(f"\n  S={S}, K={K}, T={T}, r={r}")
    print(f"\n  {'sigma':<10} {'Call ($)':<12} {'Put ($)':<12} {'C-P':<12} {'S-Ke^-rT'}")
    print(f"  {'-'*56}")

    for sigma in sigmas:
        c = bsm_call(S, K, T, r, sigma)
        p = bsm_put(S, K, T, r, sigma)
        parity_lhs = c - p
        parity_rhs = S - K * np.exp(-r * T)
        print(f"  {sigma:<10.0%} ${c:<11.2f} ${p:<11.2f} "
              f"${parity_lhs:<11.2f} ${parity_rhs:.2f}")

    print(f"\n  -> Paridad put-call se cumple exactamente (C - P = S - Ke^-rT)")
    print(f"  -> Mayor sigma = mayor precio (mas incertidumbre = mas valor)")


# ============================================================
# 2. Incertidumbre aleatoria: Normal vs fat tails
# ============================================================

def demo_fat_tails():
    """Compara eventos extremos bajo Normal vs Student-t."""
    print("\n" + "=" * 60)
    print("2. INCERTIDUMBRE ALEATORIA: NORMAL vs FAT TAILS")
    print("=" * 60)

    sigma_d = 0.01  # 1% volatilidad diaria
    caida_1987 = -0.226  # Black Monday

    # Normal
    z_score = caida_1987 / sigma_d
    p_normal = stats.norm.cdf(caida_1987, 0, sigma_d)

    # Student-t(4) con misma varianza
    nu = 4
    sigma_t = sigma_d * np.sqrt((nu - 2) / nu)
    p_t = stats.t.cdf(caida_1987, nu, 0, sigma_t)

    print(f"\n  Black Monday (19 Oct 1987): caida de {caida_1987:.1%}")
    print(f"  Volatilidad diaria tipica: {sigma_d:.1%}")
    print(f"\n  {'Metrica':<35} {'Normal':<25} {'Student-t(4)'}")
    print(f"  {'-'*80}")
    print(f"  {'z-score (desv. estandar)':<35} {z_score:<25.1f} "
          f"{caida_1987/sigma_t:.1f}")
    print(f"  {'P(caida <= -22.6%)':<35} {p_normal:<25.2e} {p_t:.2e}")

    # Frecuencia esperada
    dias_por_ano = 252
    if p_normal > 0:
        anos_normal = 1 / (p_normal * dias_por_ano)
    else:
        anos_normal = float('inf')
    anos_t = 1 / (p_t * dias_por_ano)

    print(f"  {'Frecuencia (1 vez cada...)':<35} {'~10^110 anos':<25} "
          f"~{anos_t:,.0f} anos")

    print(f"\n  -> Bajo Normal, Black Monday es IMPOSIBLE (mas improbable que")
    print(f"     cualquier evento en la historia del universo)")
    print(f"  -> Bajo Student-t, es raro pero plausible (~cada {anos_t:,.0f} anos)")
    print(f"  -> BSM asume Normal -> subestima catastroficamente el riesgo de cola")


# ============================================================
# 3. Incertidumbre epistemica: sigma desconocida
# ============================================================

def demo_sigma_incierta():
    """Muestra impacto de incertidumbre en sigma sobre pricing."""
    print("\n" + "=" * 60)
    print("3. INCERTIDUMBRE EPISTEMICA: SIGMA DESCONOCIDA")
    print("=" * 60)

    S, K, T, r = 150, 165, 0.25, 0.05
    sigma_central = 0.25

    # BSM puntual
    precio_puntual = bsm_call(S, K, T, r, sigma_central)

    # Sigma incierta: Normal(0.25, 0.05)
    np.random.seed(42)
    n_muestras = 10000
    sigmas = np.random.normal(sigma_central, 0.05, n_muestras)
    sigmas = np.clip(sigmas, 0.05, None)
    precios = np.array([bsm_call(S, K, T, r, s) for s in sigmas])

    precio_medio = precios.mean()
    precio_std = precios.std()
    precio_p5 = np.percentile(precios, 5)
    precio_p95 = np.percentile(precios, 95)

    print(f"\n  Opcion: Call S={S}, K={K} (OTM), T={T}")
    print(f"  Sigma central: {sigma_central:.0%}")
    print(f"  Incertidumbre en sigma: +/- 5pp")
    print(f"\n  {'Metrica':<30} {'Valor'}")
    print(f"  {'-'*50}")
    print(f"  {'BSM puntual (sigma=25%)':<30} ${precio_puntual:.2f}")
    print(f"  {'Media (sigma incierta)':<30} ${precio_medio:.2f}")
    print(f"  {'Std del precio':<30} ${precio_std:.2f}")
    print(f"  {'Rango 90% del precio':<30} (${precio_p5:.2f}, ${precio_p95:.2f})")
    print(f"  {'Sesgo vs puntual':<30} "
          f"{(precio_medio - precio_puntual)/precio_puntual:+.1%}")

    print(f"\n  -> La incertidumbre en sigma AMPLIFICA la incertidumbre en precio")
    print(f"  -> El precio medio con sigma incierta es MAYOR que el puntual")
    print(f"     (convexidad de BSM en sigma -- Jensen's inequality)")


# ============================================================
# 4. Incertidumbre ontologica: saltos y cambios de regimen
# ============================================================

def demo_jump_diffusion():
    """Compara GBM (BSM) vs jump-diffusion."""
    print("\n" + "=" * 60)
    print("4. INCERTIDUMBRE ONTOLOGICA: SALTOS Y CAMBIOS DE REGIMEN")
    print("=" * 60)

    S, K, T, r, sigma = 150, 155, 0.25, 0.05, 0.25
    sigma_d = sigma / np.sqrt(252)
    n_dias = int(T * 252)
    n_sim = 200000

    # BSM puntual
    bsm_precio = bsm_call(S, K, T, r, sigma)

    # MCS Normal (sin saltos)
    np.random.seed(42)
    log_ret_n = np.zeros(n_sim)
    for _ in range(n_dias):
        log_ret_n += (r / 252 - 0.5 * sigma_d**2) + sigma_d * np.random.normal(0, 1, n_sim)
    S_T_n = S * np.exp(log_ret_n)
    mcs_normal = np.exp(-r * T) * np.maximum(S_T_n - K, 0).mean()

    # MCS con saltos
    np.random.seed(42)
    log_ret_j = np.zeros(n_sim)
    for d in range(n_dias):
        z = np.random.normal(0, 1, n_sim)
        log_ret_j += (r / 252 - 0.5 * sigma_d**2) + sigma_d * z
        jumps = np.random.binomial(1, 0.03 / 252, n_sim)
        log_ret_j += jumps * np.random.normal(-0.10, 0.05, n_sim)
    S_T_j = S * np.exp(log_ret_j)
    mcs_jump = np.exp(-r * T) * np.maximum(S_T_j - K, 0).mean()

    print(f"\n  Opcion: Call S={S}, K={K}, T={T}")
    print(f"\n  {'Modelo':<30} {'Precio ($)':<12} {'vs BSM'}")
    print(f"  {'-'*55}")
    print(f"  {'BSM analitico':<30} ${bsm_precio:<11.2f} ---")
    print(f"  {'MCS Normal (verificacion)':<30} ${mcs_normal:<11.2f} "
          f"{(mcs_normal-bsm_precio)/bsm_precio:+.1%}")
    print(f"  {'MCS Jump-Diffusion':<30} ${mcs_jump:<11.2f} "
          f"{(mcs_jump-bsm_precio)/bsm_precio:+.1%}")

    print(f"\n  -> MCS Normal converge a BSM (como debe ser)")
    print(f"  -> Jump-diffusion captura riesgo de saltos que BSM ignora")
    print(f"  -> Los saltos son incertidumbre ontologica: el proceso cambia")


# ============================================================
# 5. Volatility smile sintetico
# ============================================================

def demo_volatility_smile():
    """Genera volatility smile sintetico con MCS fat-tailed."""
    print("\n" + "=" * 60)
    print("5. VOLATILITY SMILE: EL MERCADO SABE QUE BSM ESTA MAL")
    print("=" * 60)

    S, T, r, sigma = 150, 0.25, 0.05, 0.25
    sigma_d = sigma / np.sqrt(252)
    n_dias = int(T * 252)
    n_sim = 200000
    nu = 4

    np.random.seed(42)
    log_ret = np.zeros(n_sim)
    for _ in range(n_dias):
        log_ret += sigma_d * np.random.standard_t(nu, n_sim)
    S_T = S * np.exp((r - 0.5 * sigma**2) * T + log_ret)

    strikes = np.linspace(S * 0.85, S * 1.15, 15)
    print(f"\n  {'Strike':<10} {'K/S':<8} {'BSM IV':<10} {'Market IV':<10} {'Diff'}")
    print(f"  {'-'*48}")

    for K in strikes:
        precio_mcs = np.exp(-r * T) * np.maximum(S_T - K, 0).mean()
        try:
            iv = brentq(lambda s: bsm_call(S, K, T, r, s) - precio_mcs,
                        0.001, 5.0, xtol=1e-6)
        except (ValueError, RuntimeError):
            iv = np.nan

        bsm_iv = sigma
        if not np.isnan(iv):
            diff = iv - bsm_iv
            print(f"  ${K:<9.0f} {K/S:<8.3f} {bsm_iv:<10.1%} {iv:<10.1%} "
                  f"{diff:+.1%}")
        else:
            print(f"  ${K:<9.0f} {K/S:<8.3f} {bsm_iv:<10.1%} {'N/A':<10} ---")

    print(f"\n  -> El 'smile' emerge porque Student-t tiene mas masa en las colas")
    print(f"  -> Opciones OTM son mas caras de lo que BSM predice")
    print(f"  -> El mercado de opciones ya incorpora fat tails en los precios")


# ============================================================
# 6. Resumen: Trinidad de incertidumbre
# ============================================================

def demo_resumen_trinidad():
    """Resumen cuantitativo del impacto de cada tipo."""
    print("\n" + "=" * 60)
    print("6. RESUMEN: TRINIDAD DE INCERTIDUMBRE EN BSM")
    print("=" * 60)

    S, K, T, r, sigma = 150, 165, 0.25, 0.05, 0.25
    bsm_base = bsm_call(S, K, T, r, sigma)

    print(f"\n  Opcion: Call S={S}, K={K} (deep OTM), T={T}")
    print(f"  BSM baseline: ${bsm_base:.2f}\n")

    print(f"  {'Tipo':<15} {'Que ignora BSM':<35} {'Solucion PML'}")
    print(f"  {'-'*75}")
    print(f"  {'Aleatoria':<15} "
          f"{'Colas pesadas en retornos':<35} "
          f"Student-t, distribuciones mixtas")
    print(f"  {'Epistemica':<15} "
          f"{'Sigma es incierta, no fija':<35} "
          f"Prior sobre sigma, posterior via MCMC")
    print(f"  {'Ontologica':<15} "
          f"{'Saltos, cambios de regimen':<35} "
          f"Jump-diffusion, stress testing")

    print(f"\n  Implicaciones practicas:")
    print(f"  1. NO uses BSM literalmente para pricing real")
    print(f"  2. USA distribuciones completas (no solo Normal)")
    print(f"  3. CUANTIFICA tu incertidumbre sobre los parametros")
    print(f"  4. PREPARA escenarios para cambios de regimen")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  DEMO: BLACK-SCHOLES Y TRINIDAD DE LA INCERTIDUMBRE")
    print("  Modulo 2C")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 60)

    demo_pricing_basico()
    demo_fat_tails()
    demo_sigma_incierta()
    demo_jump_diffusion()
    demo_volatility_smile()
    demo_resumen_trinidad()

    print("\n" + "=" * 60)
    print("  DEMO COMPLETADA")
    print("  Archivos relacionados:")
    print("    - notebooks/notebook_ch02c_bsm_uncertainty_trinity.md")
    print("    - hotmart/viz_bsm_uncertainty_trinity.py")
    print("    - hotmart/ejercicios/ejercicios_mod02c_bsm_uncertainty.md")
    print("=" * 60)
