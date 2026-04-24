"""
Demo: MPT, CAPM y su Critica -- Naive Diversification vs Optimizacion.

Construye frontera eficiente, compara con 1/N, y demuestra la
fragilidad de MPT ante errores de estimacion y fat tails.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/mpt_capm_critique_demo.py
"""
import numpy as np
from scipy import stats
from scipy.optimize import minimize


def generar_activos(n_activos=5, n_dias=504, seed=42):
    """Genera retornos sinteticos de 5 activos con fat tails."""
    np.random.seed(seed)
    mus = np.array([0.0004, 0.0003, 0.0005, 0.0002, 0.0006])[:n_activos]
    sigmas = np.array([0.015, 0.010, 0.020, 0.008, 0.025])[:n_activos]
    retornos = np.zeros((n_dias, n_activos))
    for i in range(n_activos):
        retornos[:, i] = mus[i] + sigmas[i] * np.random.standard_t(4, n_dias)
    # Agregar correlacion
    L = np.linalg.cholesky(np.eye(n_activos) * 0.5 + 0.5)
    retornos = retornos @ L.T
    return retornos, mus, sigmas


def frontera_eficiente(retornos, n_puntos=20):
    """Calcula frontera eficiente de Markowitz."""
    n = retornos.shape[1]
    mu_hat = retornos.mean(axis=0)
    cov = np.cov(retornos.T)

    mu_range = np.linspace(mu_hat.min(), mu_hat.max(), n_puntos)
    sigmas_ef = []
    pesos_ef = []

    for mu_target in mu_range:
        def objetivo(w):
            return w @ cov @ w

        constraints = [
            {'type': 'eq', 'fun': lambda w: w.sum() - 1},
            {'type': 'eq', 'fun': lambda w, mt=mu_target: w @ mu_hat - mt},
        ]
        bounds = [(0, 1)] * n
        w0 = np.ones(n) / n

        res = minimize(objetivo, w0, method='SLSQP',
                       constraints=constraints, bounds=bounds)
        if res.success:
            sigmas_ef.append(np.sqrt(res.fun) * np.sqrt(252) * 100)
            pesos_ef.append(res.x)
        else:
            sigmas_ef.append(np.nan)
            pesos_ef.append(np.ones(n) / n)

    return mu_range * 252 * 100, sigmas_ef, pesos_ef


def demo_mpt_vs_1n():
    """Compara MPT con 1/N fuera de muestra."""
    print("=" * 65)
    print("1. MPT vs 1/N: FUERA DE MUESTRA")
    print("=" * 65)

    np.random.seed(42)
    retornos_train, _, _ = generar_activos(n_dias=252)
    retornos_test, _, _ = generar_activos(n_dias=252, seed=99)

    n_activos = retornos_train.shape[1]

    # MPT: portafolio de minima varianza
    cov = np.cov(retornos_train.T)
    mu_hat = retornos_train.mean(axis=0)

    def min_var(w):
        return w @ cov @ w

    res = minimize(min_var, np.ones(n_activos)/n_activos,
                   constraints={'type': 'eq', 'fun': lambda w: w.sum() - 1},
                   bounds=[(0, 1)] * n_activos, method='SLSQP')
    w_mpt = res.x

    # 1/N
    w_1n = np.ones(n_activos) / n_activos

    # Evaluar en test
    for nombre, w in [("MPT (min var)", w_mpt), ("1/N (naive)", w_1n)]:
        r_port = retornos_test @ w
        sharpe = r_port.mean() / r_port.std() * np.sqrt(252)
        maxdd = np.min(np.cumsum(r_port) - np.maximum.accumulate(np.cumsum(r_port)))
        var_95 = np.percentile(r_port, 5)

        print(f"\n  {nombre}:")
        print(f"    Pesos: [{', '.join(f'{x:.1%}' for x in w)}]")
        print(f"    Sharpe (test): {sharpe:.3f}")
        print(f"    Max drawdown:  {maxdd*100:.2f}%")
        print(f"    VaR 95%:       {var_95*100:+.3f}%")
        print(f"    Retorno anual: {r_port.mean()*252*100:+.2f}%")

    print(f"\n  -> 1/N frecuentemente iguala o supera a MPT fuera de muestra")
    print(f"  -> MPT concentra pesos en activos de baja varianza estimada")
    print(f"  -> Si la estimacion tiene error, MPT amplifica el error")


def demo_sensibilidad_mpt():
    """Demuestra que pequenos cambios en mu cambian pesos drasticamente."""
    print("\n" + "=" * 65)
    print("2. SENSIBILIDAD DE MPT A INPUTS")
    print("=" * 65)

    retornos, _, _ = generar_activos()
    mu_hat = retornos.mean(axis=0)
    cov = np.cov(retornos.T)
    n = len(mu_hat)

    # Optimizar con mu original y mu perturbado
    def opt_pesos(mu):
        def obj(w): return w @ cov @ w
        target = mu.mean()
        cons = [{'type': 'eq', 'fun': lambda w: w.sum() - 1},
                {'type': 'eq', 'fun': lambda w: w @ mu - target}]
        res = minimize(obj, np.ones(n)/n, method='SLSQP',
                       constraints=cons, bounds=[(0,1)]*n)
        return res.x if res.success else np.ones(n)/n

    w_orig = opt_pesos(mu_hat)
    perturbacion = 0.0001  # Solo 0.01% de cambio en un activo
    mu_pert = mu_hat.copy()
    mu_pert[0] += perturbacion
    w_pert = opt_pesos(mu_pert)

    print(f"\n  Perturbacion: mu[0] cambia {perturbacion*100:.2f}% (0.01%)")
    print(f"\n  {'Activo':<10} {'Peso original':<15} {'Peso perturbado':<18} {'Cambio'}")
    print(f"  {'-'*50}")
    for i in range(n):
        cambio = abs(w_pert[i] - w_orig[i])
        print(f"  {i+1:<10} {w_orig[i]:<15.1%} {w_pert[i]:<18.1%} {cambio:.1%}")

    max_cambio = np.max(np.abs(w_pert - w_orig))
    print(f"\n  Cambio maximo en pesos: {max_cambio:.1%}")
    print(f"  Con solo 0.01% de perturbacion en UN activo!")
    print(f"  -> MPT es un 'estimation error maximizer'")


def demo_correlaciones_crisis():
    """Correlaciones cambian en crisis."""
    print("\n" + "=" * 65)
    print("3. CORRELACIONES EN CRISIS: DIVERSIFICACION DESAPARECE")
    print("=" * 65)

    np.random.seed(42)
    n = 504
    # Calma: correlacion baja
    ret_calma = np.random.multivariate_normal(
        [0.001, 0.0005], [[0.0002, 0.00002], [0.00002, 0.0001]], 400)
    # Crisis: correlacion alta
    ret_crisis = np.random.multivariate_normal(
        [-0.005, -0.003], [[0.001, 0.0008], [0.0008, 0.0006]], 104)

    corr_calma = np.corrcoef(ret_calma.T)[0, 1]
    corr_crisis = np.corrcoef(ret_crisis.T)[0, 1]
    corr_total = np.corrcoef(np.vstack([ret_calma, ret_crisis]).T)[0, 1]

    print(f"\n  Correlacion Activo A vs B:")
    print(f"    Periodo calma (400 dias):  {corr_calma:+.3f}")
    print(f"    Periodo crisis (104 dias): {corr_crisis:+.3f}")
    print(f"    Total:                     {corr_total:+.3f}")
    print(f"\n  -> En crisis, la correlacion SUBE de {corr_calma:.2f} a {corr_crisis:.2f}")
    print(f"  -> La diversificacion desaparece cuando mas la necesitas")
    print(f"  -> MPT usa la correlacion PROMEDIO que esconde esto")


def demo_resumen():
    """Tabla resumen."""
    print("\n" + "=" * 65)
    print("4. RESUMEN: MPT vs ALTERNATIVAS")
    print("=" * 65)
    print("""
  Criterio          MPT          Kelly        1/N       PML Ensemble
  -------------------------------------------------------------------
  Asume Normal      SI           No           No        No
  Estima mu         SI (fragil)  SI (robusto) NO        SI (robusto)
  En crisis         Falla        Reduce       Estable   Se adapta
  Complejidad       Media        Media        Nula      Alta
  Rendimiento OOS   Variable     Bueno        Bueno     Mejor

  Conclusion:
  - MPT es un buen CONCEPTO pero mal IMPLEMENTACION
  - 1/N es sorprendentemente competitivo
  - Kelly/PML son superiores si tienes distribuciones posteriores
  - La diversificacion es buena; la OPTIMIZACION ruidosa no
""")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: MPT, CAPM Y SU CRITICA PROBABILISTICA")
    print("  Modulo 8D")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_mpt_vs_1n()
    demo_sensibilidad_mpt()
    demo_correlaciones_crisis()
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
