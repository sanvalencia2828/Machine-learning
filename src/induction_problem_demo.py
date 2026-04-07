"""
Demo: El Problema de la Induccion en Finanzas.

Simula el 'pavo de Russell' financiero, compara la fragilidad inductiva
de modelos frecuentistas vs bayesianos, implementa deteccion de cambio
de regimen y stress testing inductivo.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/induction_problem_demo.py
"""
import numpy as np
from scipy import stats


# ============================================================
# 1. El Pavo de Russell
# ============================================================

def demo_pavo_russell():
    """Simula estrategia estable que colapsa (pavo de Russell)."""
    print("=" * 65)
    print("1. EL PAVO DE RUSSELL: ESTRATEGIA ESTABLE QUE COLAPSA")
    print("=" * 65)

    np.random.seed(42)
    n_calma, n_crisis = 500, 50

    ret_calma = np.random.normal(0.001, 0.005, n_calma)
    ret_crisis = np.random.normal(-0.03, 0.04, n_crisis)
    retornos = np.concatenate([ret_calma, ret_crisis])

    precios = 100 * np.exp(np.cumsum(retornos))

    ret_pre = (precios[n_calma] / precios[0] - 1) * 100
    ret_post = (precios[-1] / precios[n_calma] - 1) * 100
    ret_total = (precios[-1] / precios[0] - 1) * 100

    print(f"\n  Simulacion: {n_calma} dias calma + {n_crisis} dias crisis")
    print(f"\n  {'Periodo':<25} {'Retorno':<12} {'Dias'}")
    print(f"  {'-'*45}")
    print(f"  {'Pre-crisis (calma)':<25} {ret_pre:>+8.1f}%    {n_calma}")
    print(f"  {'Crisis':<25} {ret_post:>+8.1f}%    {n_crisis}")
    print(f"  {'Total':<25} {ret_total:>+8.1f}%    {n_calma + n_crisis}")
    print(f"\n  -> 500 dias de evidencia 'confirmando' la estrategia")
    print(f"  -> 50 dias destruyen todo. ESO es induccion.")

    return retornos, n_calma


# ============================================================
# 2. Frecuentista vs Bayesiano ante el colapso
# ============================================================

def demo_confianza_comparada(retornos, punto_quiebre):
    """Compara como evoluciona la confianza de cada enfoque."""
    print("\n" + "=" * 65)
    print("2. CONFIANZA: FRECUENTISTA vs BAYESIANO")
    print("=" * 65)

    n = len(retornos)

    # Frecuentista: IC se estrecha con 1/sqrt(n)
    checkpoints = [50, 200, punto_quiebre - 1, punto_quiebre + 20, n - 1]

    print(f"\n  {'Dia':<8} {'Enfoque':<15} {'Media':<10} "
          f"{'IC/HDI 95%':<25} {'Ancho'}")
    print(f"  {'-'*68}")

    for cp in checkpoints:
        if cp >= n:
            continue
        sub = retornos[:cp + 1]

        # Frecuentista
        mu = sub.mean()
        se = sub.std() / np.sqrt(len(sub))
        lo_f = mu - 1.96 * se
        hi_f = mu + 1.96 * se
        ancho_f = hi_f - lo_f

        # Bayesiano
        tau_prior = 1 / 0.005**2
        tau_like = 1 / 0.01**2
        tau_post = tau_prior + len(sub) * tau_like
        mu_post = (tau_prior * 0.0 + len(sub) * tau_like * mu) / tau_post
        sigma_post = 1 / np.sqrt(tau_post)
        lo_b = mu_post - 1.96 * sigma_post
        hi_b = mu_post + 1.96 * sigma_post
        ancho_b = hi_b - lo_b

        etiqueta = ""
        if cp < punto_quiebre:
            etiqueta = "(calma)"
        else:
            etiqueta = "(crisis)"

        print(f"  {cp+1:<8d} {'Frecuentista':<15} {mu*100:>+7.4f}%  "
              f"({lo_f*100:>+7.4f}, {hi_f*100:>+7.4f})  {ancho_f*100:.4f}%  "
              f"{etiqueta}")
        print(f"  {'':<8} {'Bayesiano':<15} {mu_post*100:>+7.4f}%  "
              f"({lo_b*100:>+7.4f}, {hi_b*100:>+7.4f})  {ancho_b*100:.4f}%")

    print(f"\n  -> Frecuentista: IC se estrecha continuamente (pavo engorda)")
    print(f"  -> Bayesiano: HDI acotado por prior, reacciona a crisis")


# ============================================================
# 3. Deteccion de cambio de regimen
# ============================================================

def demo_deteccion_regimen(retornos, punto_quiebre):
    """Detecta cambio de regimen con ventana deslizante."""
    print("\n" + "=" * 65)
    print("3. DETECCION DE CAMBIO DE REGIMEN")
    print("=" * 65)

    ventana = 20
    umbral = 3.0
    deteccion = None

    for i in range(ventana * 2, len(retornos)):
        hist = retornos[:i - ventana]
        reciente = retornos[i - ventana:i]
        mu_h = hist.mean()
        sigma_h = hist.std()
        if sigma_h > 0:
            z = (reciente.mean() - mu_h) / (sigma_h / np.sqrt(ventana))
            if deteccion is None and abs(z) > umbral:
                deteccion = i
                break

    if deteccion:
        retraso = deteccion - punto_quiebre
        print(f"\n  Ventana: {ventana} dias, umbral z-score: {umbral}")
        print(f"  Quiebre real:  dia {punto_quiebre}")
        print(f"  Deteccion:     dia {deteccion}")
        print(f"  Retraso:       {retraso} dias")
        print(f"\n  -> El detector NO previene la crisis, la DETECTA despues")
        print(f"  -> {retraso} dias de retraso es mejor que nunca detectar")
    else:
        print(f"\n  No se detecto cambio de regimen")


# ============================================================
# 4. Stress testing inductivo
# ============================================================

def demo_stress_test():
    """Cuantifica perdidas bajo falla inductiva."""
    print("\n" + "=" * 65)
    print("4. STRESS TEST INDUCTIVO")
    print("=" * 65)

    np.random.seed(42)
    capital = 1_000_000

    escenarios = [
        {"nombre": "Crisis leve",     "mu": -0.01, "sigma": 0.02, "dias": 30},
        {"nombre": "Crisis moderada", "mu": -0.03, "sigma": 0.04, "dias": 30},
        {"nombre": "Crisis severa",   "mu": -0.05, "sigma": 0.06, "dias": 30},
        {"nombre": "Cisne negro",     "mu": -0.08, "sigma": 0.10, "dias": 10},
    ]

    print(f"\n  Capital: ${capital:,}")
    print(f"\n  {'Escenario':<20} {'Perdida Media':<16} {'Perdida P95':<16} "
          f"{'P(>50% perdida)'}")
    print(f"  {'-'*68}")

    for esc in escenarios:
        perdidas = []
        for _ in range(10000):
            ret = np.random.normal(esc["mu"], esc["sigma"], esc["dias"])
            valor_final = capital * np.exp(np.sum(ret))
            perdidas.append(capital - valor_final)
        perdidas = np.array(perdidas)

        print(f"  {esc['nombre']:<20} ${perdidas.mean():>12,.0f} "
              f"${np.percentile(perdidas, 95):>12,.0f} "
              f"{(perdidas > capital * 0.5).mean():>12.1%}")

    print(f"\n  -> El stress test cuantifica lo que la induccion ignora")
    print(f"  -> Preparacion > prediccion")


# ============================================================
# 5. Resumen
# ============================================================

def demo_resumen():
    """Resumen de implicaciones practicas."""
    print("\n" + "=" * 65)
    print("5. RESUMEN: LA INDUCCION EN FINANZAS")
    print("=" * 65)

    print("""
  Filosofo        Leccion                        Aplicacion financiera
  -----------------------------------------------------------------------
  Hume (1739)     Pasado no garantiza futuro     Backtest no garantiza P&L
  Popper (1934)   Busca refutar, no confirmar    Stress test tu estrategia
  Taleb (2007)    Cisnes negros son inevitables   Prepara, no predice
  Russell         El pavo mas gordo = mas fragil  Mas backtest = mas peligro

  Estrategias PML contra la trampa inductiva:
  1. Priors escepticos: no confiar ciegamente en datos pasados
  2. Actualizacion continua: nuevos datos actualizan creencias
  3. Distribucion predictiva: propaga incertidumbre al futuro
  4. Stress testing: cuantifica perdida si la induccion falla
  5. Falsacionismo: busca REFUTAR tu modelo, no confirmarlo
""")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: EL PROBLEMA DE LA INDUCCION EN FINANZAS")
    print("  Modulo 2E")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    retornos, punto_quiebre = demo_pavo_russell()
    demo_confianza_comparada(retornos, punto_quiebre)
    demo_deteccion_regimen(retornos, punto_quiebre)
    demo_stress_test()
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("  Archivos relacionados:")
    print("    - notebooks/notebook_ch02e_induction_problem.md")
    print("    - hotmart/viz_induction_problem.py")
    print("    - hotmart/ejercicios/ejercicios_mod02e_induction.md")
    print("=" * 65)
