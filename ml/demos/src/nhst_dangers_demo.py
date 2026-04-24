"""
Demo: Peligros de NHST -- Falacias, P-hacking e Intervalos de Confianza.

Demuestra la falacia inversa, la falacia del fiscal en backtesting,
p-hacking con multiples pruebas, y los errores de interpretacion de IC.
Incluye modelo OLS con tests diagnosticos que fallan.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy, sklearn
Ejecutar: python src/nhst_dangers_demo.py
"""
import numpy as np
from scipy import stats


def demo_falacia_inversa():
    """Demuestra que P(datos|H0) != P(H0|datos)."""
    print("=" * 65)
    print("1. FALACIA INVERSA: P(datos|H0) != P(H0|datos)")
    print("=" * 65)

    print("""
  Test medico:
    Sensibilidad: P(positivo | enfermo) = 99%
    Especificidad: P(negativo | sano) = 95%
    Prevalencia: P(enfermo) = 1%

  Tu recibes resultado POSITIVO. P(enfermo | positivo) = ???
""")

    sens = 0.99
    spec = 0.95
    prev = 0.01

    p_positivo = sens * prev + (1 - spec) * (1 - prev)
    p_enfermo_dado_positivo = (sens * prev) / p_positivo

    print(f"  P(positivo) = {p_positivo:.4f}")
    print(f"  P(enfermo | positivo) = {p_enfermo_dado_positivo:.1%}")
    print(f"\n  -> A pesar de un test 99% sensible, solo hay {p_enfermo_dado_positivo:.0%}")
    print(f"     de probabilidad de estar enfermo")
    print(f"  -> NHST comete este mismo error con p-values")
    print(f"  -> P(datos | H0) = 0.03 NO implica P(H0 | datos) = 0.03")


def demo_falacia_fiscal():
    """Falacia del fiscal aplicada a backtesting."""
    print("\n" + "=" * 65)
    print("2. FALACIA DEL FISCAL EN BACKTESTING")
    print("=" * 65)

    np.random.seed(42)
    n_estrategias = 100
    n_dias = 252

    print(f"\n  Probando {n_estrategias} estrategias aleatorias (todas nulas)")
    print(f"  Cada una: {n_dias} retornos ~ Normal(0, 0.01)\n")

    p_values = []
    for i in range(n_estrategias):
        retornos = np.random.normal(0, 0.01, n_dias)
        t_stat, p_val = stats.ttest_1samp(retornos, 0)
        p_values.append(p_val)

    p_values = np.array(p_values)

    sig_005 = (p_values < 0.05).sum()
    sig_001 = (p_values < 0.01).sum()
    mejor_p = p_values.min()
    mejor_idx = p_values.argmin()

    print(f"  Resultados:")
    print(f"    Estrategias con p < 0.05: {sig_005}/{n_estrategias}")
    print(f"    Estrategias con p < 0.01: {sig_001}/{n_estrategias}")
    print(f"    Mejor p-value: {mejor_p:.6f} (estrategia #{mejor_idx+1})")
    print(f"\n  Fiscal dice: 'La estrategia #{mejor_idx+1} tiene p={mejor_p:.4f}!")
    print(f"                Solo hay {mejor_p:.2%} de probabilidad de que sea azar!'")
    print(f"\n  Realidad: TODAS son azar. El fiscal ignora las 99 que NO reporta.")
    print(f"  P(al menos 1 con p<0.05 | todas nulas) = "
          f"{1 - 0.95**n_estrategias:.1%}")


def demo_p_hacking():
    """Demuestra p-hacking con grados de libertad del investigador."""
    print("\n" + "=" * 65)
    print("3. P-HACKING: GRADOS DE LIBERTAD DEL INVESTIGADOR")
    print("=" * 65)

    np.random.seed(42)
    n = 200
    # Generar datos completamente aleatorios
    y = np.random.normal(0, 1, n)
    x1 = np.random.normal(0, 1, n)
    x2 = np.random.normal(0, 1, n)
    x3 = np.random.normal(0, 1, n)

    manipulaciones = [
        ("Muestra completa (n=200)", y, x1),
        ("Solo primeros 100", y[:100], x1[:100]),
        ("Solo ultimos 100", y[100:], x1[100:]),
        ("Usar x2 en vez de x1", y, x2),
        ("Usar x3 en vez de x1", y, x3),
        ("Eliminar outliers (|y|<2)", y[np.abs(y)<2], x1[np.abs(y)<2]),
        ("Log(|y|+1) transformado", np.log(np.abs(y)+1), x1),
    ]

    print(f"\n  Datos: y y x1-x3 son COMPLETAMENTE aleatorios (no hay efecto)")
    print(f"\n  {'Manipulacion':<35} {'Corr':<8} {'p-value':<12} {'Significativo?'}")
    print(f"  {'-'*65}")

    significativos = 0
    for nombre, yi, xi in manipulaciones:
        r, p = stats.pearsonr(yi[:len(xi)], xi[:len(yi)])
        sig = "SI *" if p < 0.05 else "no"
        if p < 0.05:
            significativos += 1
        print(f"  {nombre:<35} {r:>+.3f}   {p:<12.4f} {sig}")

    print(f"\n  -> {significativos} de {len(manipulaciones)} manipulaciones dan p < 0.05")
    print(f"  -> Con suficiente 'creatividad', siempre encuentras significancia")
    print(f"  -> Esto es p-hacking: NO es fraude, es sesgo de seleccion")


def demo_ic_errores():
    """Demuestra los 3 errores de interpretacion de IC."""
    print("\n" + "=" * 65)
    print("4. INTERVALOS DE CONFIANZA: 3 ERRORES")
    print("=" * 65)

    np.random.seed(42)
    mu_real = 0.05  # 5% de retorno anual real
    sigma = 0.20
    n_anos = 10
    n_repeticiones = 1000

    contiene = 0
    anchos = []

    for _ in range(n_repeticiones):
        retornos = np.random.normal(mu_real, sigma, n_anos)
        mu_hat = retornos.mean()
        se = retornos.std() / np.sqrt(n_anos)
        lo = mu_hat - 1.96 * se
        hi = mu_hat + 1.96 * se
        anchos.append(hi - lo)
        if lo <= mu_real <= hi:
            contiene += 1

    cobertura = contiene / n_repeticiones

    print(f"\n  Parametro real: mu = {mu_real:.0%}")
    print(f"  {n_repeticiones} experimentos con IC 95%")
    print(f"\n  Cobertura real: {cobertura:.1%} (deberia ser ~95%)")
    print(f"  Ancho medio del IC: {np.mean(anchos):.3f}")

    print(f"""
  ERROR 1: "Hay 95% de prob de que mu este en MI intervalo"
    -> FALSO. mu es fijo. El IC es aleatorio.
    -> Correcto: "Si repito 1000 veces, ~950 ICs contienen mu"

  ERROR 2: "Si el IC no incluye 0, el efecto es significativo"
    -> Equivale a NHST con alpha=0.05. Mismos problemas.

  ERROR 3: "El ancho del IC mide mi incertidumbre personal"
    -> Solo mide precision muestral. No incorpora prior knowledge.
    -> Con 10 anos de datos: IC ancho de {np.mean(anchos):.1%}
       Util? Depende de lo que ya sabias antes.""")


def demo_ols_diagnosticos():
    """Modelo OLS sintetico con tests diagnosticos que fallan."""
    print("\n" + "=" * 65)
    print("5. MODELO OLS: TESTS DIAGNOSTICOS QUE FALLAN")
    print("=" * 65)

    np.random.seed(42)
    n = 504  # 2 anos

    # Retornos sinteticos tipo AAPL vs SP500 con fat tails
    r_mkt = 0.0003 + 0.01 * np.random.standard_t(4, n)
    # Beta ~1.2, alpha ~0.0002, con ruido fat-tailed
    r_asset = 0.0002 + 1.2 * r_mkt + 0.008 * np.random.standard_t(4, n)

    # OLS manual
    X = np.column_stack([np.ones(n), r_mkt])
    beta_hat = np.linalg.lstsq(X, r_asset, rcond=None)[0]
    residuals = r_asset - X @ beta_hat

    # Stats de regresion
    rss = np.sum(residuals**2)
    tss = np.sum((r_asset - r_asset.mean())**2)
    r_squared = 1 - rss / tss
    se_beta = np.sqrt(rss / (n - 2) * np.diag(np.linalg.inv(X.T @ X)))
    t_stats = beta_hat / se_beta
    p_values_ols = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - 2))

    print(f"\n  Modelo: r_asset = alpha + beta * r_market + epsilon")
    print(f"\n  {'Param':<10} {'Estimado':<12} {'SE':<12} {'t-stat':<10} {'p-value'}")
    print(f"  {'-'*50}")
    print(f"  {'alpha':<10} {beta_hat[0]:<12.6f} {se_beta[0]:<12.6f} "
          f"{t_stats[0]:<10.3f} {p_values_ols[0]:.4f}")
    print(f"  {'beta':<10} {beta_hat[1]:<12.4f} {se_beta[1]:<12.4f} "
          f"{t_stats[1]:<10.3f} {p_values_ols[1]:.2e}")
    print(f"  R-squared: {r_squared:.4f}")

    # Tests diagnosticos
    jb_stat, jb_p = stats.jarque_bera(residuals)
    # Durbin-Watson approximation
    dw = np.sum(np.diff(residuals)**2) / np.sum(residuals**2)

    print(f"\n  Tests diagnosticos:")
    print(f"    Jarque-Bera (normalidad):  stat={jb_stat:.1f}, p={jb_p:.2e} "
          f"-> {'RECHAZA' if jb_p < 0.05 else 'OK'}")
    print(f"    Durbin-Watson:             stat={dw:.3f} "
          f"({'autocorrelacion?' if dw < 1.5 or dw > 2.5 else 'OK'})")

    print(f"""
  CONCLUSION:
  - Alpha parece significativo (p={p_values_ols[0]:.4f})
  - PERO los residuales NO son normales (Jarque-Bera rechaza)
  - Los p-values de OLS ASUMEN residuales normales
  - Si el supuesto falla, los p-values NO son validos
  - Estas conclusiones son ENGANOSAS""")


def demo_resumen():
    """Resumen de peligros NHST."""
    print("\n" + "=" * 65)
    print("6. RESUMEN: PELIGROS DE NHST EN FINANZAS")
    print("=" * 65)
    print("""
  Falacia                Que confunde                    Consecuencia
  -------------------------------------------------------------------------
  Inversa                P(datos|H0) con P(H0|datos)     p-value enganoso
  Fiscal                 Ignora multiples comparaciones   Falsos positivos
  Abogado defensor       Ignora tasa base                 Falsos negativos
  IC mal interpretado    Frecuencia con probabilidad      Sobreconfianza

  En finanzas:
  1. Si probaste 100 estrategias, p<0.05 no significa nada
  2. Si los residuales no son normales, los p-values mienten
  3. Un IC de 95% NO dice que hay 95% de prob de que mu este ahi
  4. La alternativa: inferencia bayesiana (Modulos 5-7)
""")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: PELIGROS DE NHST EN FINANZAS")
    print("  Modulo 4")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_falacia_inversa()
    demo_falacia_fiscal()
    demo_p_hacking()
    demo_ic_errores()
    demo_ols_diagnosticos()
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
