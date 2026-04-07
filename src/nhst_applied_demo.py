"""
Demo: NHST Aplicado -- OLS, Base Rates e Indicadores Economicos.

Construye un modelo OLS con diagnosticos, simula indicadores de
recesion con confusion matrix, y demuestra como el base rate
determina el valor predictivo real de un indicador.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/nhst_applied_demo.py
"""
import numpy as np
from scipy import stats


def demo_ols_diagnosticos():
    """Modelo OLS sintetico con tests diagnosticos."""
    print("=" * 65)
    print("1. REGRESION OLS: APPLE vs S&P 500 (SINTETICO)")
    print("=" * 65)

    np.random.seed(42)
    n = 504
    r_mkt = 0.0003 + 0.012 * np.random.standard_t(4, n)
    epsilon = 0.01 * np.random.standard_t(4, n)
    r_apple = 0.0002 + 1.25 * r_mkt + epsilon

    # OLS manual
    X = np.column_stack([np.ones(n), r_mkt])
    beta_hat = np.linalg.lstsq(X, r_apple, rcond=None)[0]
    residuals = r_apple - X @ beta_hat
    rss = np.sum(residuals**2)
    tss = np.sum((r_apple - r_apple.mean())**2)
    r_sq = 1 - rss / tss
    mse = rss / (n - 2)
    se_beta = np.sqrt(mse * np.diag(np.linalg.inv(X.T @ X)))
    t_stats = beta_hat / se_beta
    p_vals = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - 2))

    print(f"\n  r_apple = alpha + beta * r_market + epsilon")
    print(f"\n  {'Param':<10} {'Valor':<12} {'SE':<12} {'t':<10} {'p-value'}")
    print(f"  {'-'*50}")
    print(f"  {'alpha':<10} {beta_hat[0]:<12.6f} {se_beta[0]:<12.6f} "
          f"{t_stats[0]:<10.3f} {p_vals[0]:.4f}")
    print(f"  {'beta':<10} {beta_hat[1]:<12.4f} {se_beta[1]:<12.4f} "
          f"{t_stats[1]:<10.3f} {p_vals[1]:.2e}")
    print(f"  R-squared: {r_sq:.4f}")

    # Diagnosticos
    jb_s, jb_p = stats.jarque_bera(residuals)
    dw = np.sum(np.diff(residuals)**2) / np.sum(residuals**2)

    print(f"\n  Diagnosticos:")
    print(f"    Jarque-Bera: stat={jb_s:.1f}, p={jb_p:.2e} "
          f"-> {'RECHAZA normalidad' if jb_p < 0.05 else 'OK'}")
    print(f"    Durbin-Watson: {dw:.3f} "
          f"-> {'OK' if 1.5 <= dw <= 2.5 else 'SOSPECHOSO'}")

    if jb_p < 0.05:
        print(f"\n  ADVERTENCIA: residuales no son normales.")
        print(f"  Los p-values de OLS ({p_vals[0]:.4f}, {p_vals[1]:.2e}) son SOSPECHOSOS.")


def demo_base_rates():
    """Simula recesiones y calcula base rates."""
    print("\n" + "=" * 65)
    print("2. BASE RATES DE RECESIONES (SIMULACION TIPO NBER)")
    print("=" * 65)

    np.random.seed(42)
    n_meses = 960
    recesion = np.zeros(n_meses, dtype=int)

    t = 0
    while t < n_meses:
        dur_exp = max(12, int(np.random.exponential(50)))
        t += dur_exp
        if t >= n_meses:
            break
        dur_rec = max(6, int(np.random.exponential(11)))
        recesion[t:min(t + dur_rec, n_meses)] = 1
        t += dur_rec

    base_rate = recesion.mean()
    n_rec = (np.diff(recesion) == 1).sum()

    print(f"\n  Simulacion: {n_meses} meses (~{n_meses//12} anos)")
    print(f"  Recesiones: {n_rec}")
    print(f"  Base rate: {base_rate:.1%} del tiempo en recesion")
    print(f"  Expansion media: ~{(n_meses - recesion.sum()) / max(n_rec, 1):.0f} meses")
    print(f"  Recesion media: ~{recesion.sum() / max(n_rec, 1):.0f} meses")

    return recesion, base_rate


def demo_confusion_matrix(recesion, base_rate):
    """Confusion matrix de un indicador de recesion."""
    print("\n" + "=" * 65)
    print("3. CONFUSION MATRIX: INDICADOR DE RECESION")
    print("=" * 65)

    np.random.seed(42)
    sens = 0.85
    fpr = 0.20

    senal = np.zeros(len(recesion), dtype=int)
    for i in range(len(recesion)):
        if recesion[i]:
            senal[i] = int(np.random.random() < sens)
        else:
            senal[i] = int(np.random.random() < fpr)

    tp = ((senal == 1) & (recesion == 1)).sum()
    fp = ((senal == 1) & (recesion == 0)).sum()
    fn = ((senal == 0) & (recesion == 1)).sum()
    tn = ((senal == 0) & (recesion == 0)).sum()
    ppv = tp / max(tp + fp, 1)
    npv = tn / max(tn + fn, 1)

    print(f"\n  Sensibilidad: {sens:.0%}, FPR: {fpr:.0%}, Base rate: {base_rate:.1%}")
    print(f"\n  {'':15} {'Recesion':<12} {'Expansion':<12}")
    print(f"  {'-'*35}")
    print(f"  {'Senal':<15} {tp:<12d} {fp:<12d}")
    print(f"  {'Sin senal':<15} {fn:<12d} {tn:<12d}")
    print(f"\n  PPV (P(recesion|senal)):  {ppv:.1%}")
    print(f"  NPV (P(expansion|nada)):  {npv:.1%}")

    print(f"\n  FALACIA INVERSA:")
    print(f"    P(senal | recesion) = {sens:.0%} (sensibilidad)")
    print(f"    P(recesion | senal) = {ppv:.1%} (PPV -- lo que NECESITAS)")
    print(f"    Diferencia: {abs(sens - ppv):.0%}")


def demo_ppv_vs_fpr():
    """PPV para diferentes FPR y base rates."""
    print("\n" + "=" * 65)
    print("4. PPV vs FPR PARA DIFERENTES BASE RATES")
    print("=" * 65)

    sens = 0.85
    print(f"\n  Sensibilidad fija: {sens:.0%}")
    print(f"\n  {'FPR':<8}", end="")
    for br in [0.05, 0.10, 0.15, 0.25]:
        print(f"BR={br:.0%}{'':>5}", end="")
    print()
    print(f"  {'-'*48}")

    for fpr in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        print(f"  {fpr:<8.0%}", end="")
        for br in [0.05, 0.10, 0.15, 0.25]:
            ppv = (sens * br) / (sens * br + fpr * (1 - br))
            marker = " *" if ppv < 0.50 else ""
            print(f"{ppv:<12.1%}{marker}", end="")
        print()

    print(f"\n  * = PPV < 50% (peor que moneda al aire)")
    print(f"  -> Con base rate 5%, incluso FPR 5% da PPV solo 47%")
    print(f"  -> El base rate DOMINA la utilidad del indicador")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: NHST APLICADO -- OLS, BASE RATES E INDICADORES")
    print("  Modulo 4B")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_ols_diagnosticos()
    recesion, base_rate = demo_base_rates()
    demo_confusion_matrix(recesion, base_rate)
    demo_ppv_vs_fpr()

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
