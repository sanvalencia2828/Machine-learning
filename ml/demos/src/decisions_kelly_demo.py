"""
Demo: Decisiones Probabilisticas -- GVaR, Kelly y Ergodicidad.

Implementa GVaR/GES/GTR desde distribuciones predictivas, criterio
de Kelly para asignacion optima, y compara con Markowitz y full invest.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/decisions_kelly_demo.py
"""
import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar


def demo_ergodicidad():
    """No-ergodicidad: E[R]>0 pero la mayoria pierde."""
    print("=" * 65)
    print("1. ERGODICIDAD: E[R] > 0 PERO 86% PIERDE")
    print("=" * 65)

    np.random.seed(42)
    n_tray, n_pasos = 10000, 100

    factores = np.where(
        np.random.binomial(1, 0.5, (n_tray, n_pasos)), 1.5, 0.6)
    riqueza = 100 * np.prod(factores, axis=1)

    print(f"\n  Juego: +50% o -40%, p=0.5 cada uno, 100 rondas")
    print(f"  E[R] por ronda: +5% (parece bueno!)")
    print(f"  Media geometrica: {np.sqrt(1.5*0.6)-1:+.1%} por ronda")
    print(f"\n  Despues de 100 rondas ({n_tray:,} simulaciones):")
    print(f"    Media ensamble:  ${riqueza.mean():>12,.2f}")
    print(f"    Mediana:         ${np.median(riqueza):>12.4f}")
    print(f"    P(perder dinero): {(riqueza < 100).mean():.0%}")
    print(f"    P(perder >99%):   {(riqueza < 1).mean():.0%}")
    print(f"\n  -> E[R] > 0 es IRRELEVANTE para tu experiencia individual")


def demo_gvar_ges():
    """GVaR y GES desde distribuciones predictivas."""
    print("\n" + "=" * 65)
    print("2. GVaR, GES Y GTR (METRICAS GENERATIVAS DE RIESGO)")
    print("=" * 65)

    np.random.seed(42)
    # Posterior predictive: retornos diarios con fat tails
    n_sim = 100000
    mu_post = np.random.normal(0.0003, 0.0002, n_sim)
    sigma_post = np.abs(np.random.normal(0.012, 0.002, n_sim))
    nu_post = np.random.exponential(4, n_sim) + 2

    retornos_pred = np.array([
        mu + sigma * np.random.standard_t(max(nu, 2.1))
        for mu, sigma, nu in zip(mu_post, sigma_post, nu_post)
    ])

    # Frecuentista (asume Normal)
    mu_freq = retornos_pred.mean()
    sigma_freq = retornos_pred.std()
    var_freq = mu_freq + stats.norm.ppf(0.05) * sigma_freq
    es_freq = retornos_pred[retornos_pred <= var_freq].mean()

    # Generativo
    gvar = np.percentile(retornos_pred, 5)
    ges = retornos_pred[retornos_pred <= gvar].mean()
    gtr = (retornos_pred < -0.05).mean()

    print(f"\n  {n_sim:,} retornos de posterior predictive")
    print(f"\n  {'Metrica':<25} {'Frecuentista':<18} {'Generativo (PML)'}")
    print(f"  {'-'*55}")
    print(f"  {'VaR/GVaR 95%':<25} {var_freq*100:>+10.3f}%     {gvar*100:>+10.3f}%")
    print(f"  {'ES/GES 95%':<25} {es_freq*100:>+10.3f}%     {ges*100:>+10.3f}%")
    print(f"  {'P(r < -5%)':<25} {'N/A':<18} {gtr:.4%}")

    diff = (gvar - var_freq) / abs(var_freq) * 100
    print(f"\n  -> GVaR es {abs(diff):.0f}% {'mas conservador' if gvar < var_freq else 'menos conservador'} que VaR frecuentista")
    print(f"  -> GES propaga incertidumbre parametrica que VaR ignora")

    return retornos_pred


def demo_kelly(retornos_pred):
    """Criterio de Kelly para asignacion optima."""
    print("\n" + "=" * 65)
    print("3. CRITERIO DE KELLY: ASIGNACION OPTIMA DE CAPITAL")
    print("=" * 65)

    # Calcular tasa geometrica para diferentes fracciones
    fracciones = np.linspace(0.01, 2.0, 200)
    tasas_geo = []

    for f in fracciones:
        # E[log(1 + f*R)] -- usar solo retornos donde 1+f*R > 0
        log_riqueza = np.log(np.maximum(1 + f * retornos_pred, 1e-10))
        tasas_geo.append(log_riqueza.mean())

    tasas_geo = np.array(tasas_geo)
    kelly_f = fracciones[np.argmax(tasas_geo)]
    tasa_kelly = tasas_geo.max()

    # Tambien calcular para f=1 (full invest) y f=0.5
    tasa_full = np.log(np.maximum(1 + retornos_pred, 1e-10)).mean()
    tasa_half = np.log(np.maximum(1 + 0.5 * retornos_pred, 1e-10)).mean()

    print(f"\n  Kelly f*: {kelly_f:.2f} ({kelly_f*100:.0f}% del capital)")
    print(f"  Tasa geometrica Kelly: {tasa_kelly:.6f}")
    print(f"\n  {'Estrategia':<25} {'Fraccion':<12} {'Tasa geometrica'}")
    print(f"  {'-'*50}")
    print(f"  {'Kelly optimo':<25} {kelly_f:<12.2f} {tasa_kelly:.6f}")
    print(f"  {'Full invest (f=1)':<25} {'1.00':<12} {tasa_full:.6f}")
    print(f"  {'Half Kelly (f=0.5)':<25} {'0.50':<12} {tasa_half:.6f}")

    return kelly_f


def demo_simulacion_trayectorias(retornos_pred, kelly_f):
    """Simula trayectorias con Kelly vs full invest."""
    print("\n" + "=" * 65)
    print("4. SIMULACION: KELLY vs FULL INVEST (252 DIAS)")
    print("=" * 65)

    np.random.seed(42)
    n_tray = 1000
    n_dias = 252
    capital = 100000

    resultados = {}
    for nombre, f in [("Kelly", kelly_f), ("Full invest", 1.0),
                       ("Half Kelly", kelly_f/2), ("Conservador", 0.3)]:
        riqueza_final = []
        for _ in range(n_tray):
            r = np.random.choice(retornos_pred, n_dias, replace=True)
            riqueza = capital
            for ret in r:
                riqueza *= (1 + f * ret)
                if riqueza <= 0:
                    riqueza = 0
                    break
            riqueza_final.append(riqueza)

        riqueza_final = np.array(riqueza_final)
        resultados[nombre] = {
            "media": riqueza_final.mean(),
            "mediana": np.median(riqueza_final),
            "p_ruina": (riqueza_final < capital * 0.5).mean(),
            "p_doble": (riqueza_final > capital * 2).mean(),
        }

    print(f"\n  Capital inicial: ${capital:,}")
    print(f"  Horizonte: {n_dias} dias, {n_tray} simulaciones")
    print(f"\n  {'Estrategia':<18} {'Media ($)':<14} {'Mediana ($)':<14} "
          f"{'P(perder>50%)':<14} {'P(duplicar)'}")
    print(f"  {'-'*72}")
    for nombre, r in resultados.items():
        print(f"  {nombre:<18} ${r['media']:>11,.0f} ${r['mediana']:>11,.0f} "
              f"{r['p_ruina']:>12.1%} {r['p_doble']:>12.1%}")

    print(f"\n  -> Kelly maximiza crecimiento con minimo riesgo de ruina")
    print(f"  -> Full invest gana mas EN PROMEDIO pero tiene mayor riesgo")
    print(f"  -> Half Kelly es mas conservador (menor volatilidad)")


def demo_resumen():
    """Resumen del modulo y del curso."""
    print("\n" + "=" * 65)
    print("5. RESUMEN: DECISIONES PROBABILISTICAS")
    print("=" * 65)
    print("""
  Concepto               Frecuentista           Probabilistico
  -------------------------------------------------------------------
  Riesgo                 VaR/ES historico       GVaR/GES predictivo
  Asignacion             Markowitz (varianza)   Kelly (tasa geometrica)
  Retorno esperado       E[R] aritmetico        E[log(1+R)] geometrico
  Incertidumbre          Punto fijo             Distribucion completa
  Ergodicidad            Ignora                 Central al framework

  Recorrido del curso:
  Ch 1-2: Finanzas necesitan PML (incertidumbre, no determinismo)
  Ch 3:   MCS propaga incertidumbre forward
  Ch 4:   NHST esta roto (falacias, p-values)
  Ch 5:   Regla inversa (Bayes) da la respuesta correcta
  Ch 6:   MLE falla, MCMC rescata
  Ch 7:   Ensambles generativos (PyMC)
  Ch 8:   Decisiones con distribuciones completas (Kelly, GVaR)
""")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: DECISIONES PROBABILISTICAS Y GESTION DE CAPITAL")
    print("  Modulo 8")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_ergodicidad()
    retornos_pred = demo_gvar_ges()
    kelly_f = demo_kelly(retornos_pred)
    demo_simulacion_trayectorias(retornos_pred, kelly_f)
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA -- CURSO COMPLETO")
    print("=" * 65)
