"""
Demo: Loss Functions, Volatility Drag y Expected Loss.

Implementa loss functions para decisiones de inversion, calcula
expected loss con distribuciones predictivas, y demuestra volatility drag.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/loss_volatility_demo.py
"""
import numpy as np
from scipy import stats


def demo_loss_functions():
    """Expected loss para 3 decisiones de bonos corporativos."""
    print("=" * 65)
    print("1. LOSS FUNCTIONS Y EXPECTED LOSS")
    print("=" * 65)

    # Loss matrix: L[decision][estado]
    # Estados: default, no_default
    # Decisiones: R1 (invertir), R2 (no invertir), R3 (cubrir)
    loss_matrix = {
        "R1 (invertir)":     {"default": -100000, "no_default": +15000},
        "R2 (no invertir)":  {"default": 0,       "no_default": 0},
        "R3 (cubrir)":       {"default": -5000,   "no_default": +10000},
    }

    print(f"\n  Loss Matrix (ganancia/perdida por decision-estado):")
    print(f"  {'Decision':<20} {'Default':<15} {'No Default'}")
    print(f"  {'-'*45}")
    for dec, costos in loss_matrix.items():
        print(f"  {dec:<20} ${costos['default']:>+10,}   ${costos['no_default']:>+10,}")

    # Expected loss para diferentes P(default)
    p_defaults = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]

    print(f"\n  Expected Loss para diferentes P(default):")
    print(f"  {'P(default)':<12}", end="")
    for dec in loss_matrix:
        print(f"{dec:<22}", end="")
    print("Optima")
    print(f"  {'-'*80}")

    for p in p_defaults:
        el = {}
        for dec, costos in loss_matrix.items():
            el[dec] = p * costos["default"] + (1-p) * costos["no_default"]
        mejor = max(el, key=el.get)
        print(f"  {p:<12.0%}", end="")
        for dec in loss_matrix:
            marker = " <-" if dec == mejor else ""
            print(f"${el[dec]:>+10,.0f}{marker:<10}", end="")
        print(mejor.split(" ")[0])

    print(f"\n  -> Con P(default) < ~13%: R1 (invertir) es optimo")
    print(f"  -> Con P(default) > ~13%: R3 (cubrir) es optimo")
    print(f"  -> R2 (no invertir) nunca es optimo (costo oportunidad)")


def demo_var_es():
    """VaR y ES desde distribuciones predictivas."""
    print("\n" + "=" * 65)
    print("2. VaR Y EXPECTED SHORTFALL")
    print("=" * 65)

    np.random.seed(42)
    n_sim = 100000

    # Dos portafolios: mismo VaR, diferente ES
    ret_a = np.random.normal(0.0005, 0.015, n_sim)  # Normal
    ret_b = 0.0005 + 0.010 * np.random.standard_t(3, n_sim)  # Fat tails

    for nombre, ret in [("Portafolio A (Normal)", ret_a),
                         ("Portafolio B (Fat tails)", ret_b)]:
        var_95 = np.percentile(ret, 5)
        es_95 = ret[ret <= var_95].mean()
        var_99 = np.percentile(ret, 1)
        es_99 = ret[ret <= var_99].mean()

        print(f"\n  {nombre}:")
        print(f"    VaR 95%: {var_95*100:>+.3f}%   ES 95%: {es_95*100:>+.3f}%")
        print(f"    VaR 99%: {var_99*100:>+.3f}%   ES 99%: {es_99*100:>+.3f}%")
        print(f"    Ratio ES/VaR (95%): {es_95/var_95:.2f}x")

    print(f"\n  -> Mismo VaR 95% pero ES muy diferente!")
    print(f"  -> Fat tails: ES 99% es MUCHO peor")
    print(f"  -> ES captura el riesgo de cola que VaR ignora")


def demo_volatility_drag():
    """Demuestra que volatilidad destruye riqueza."""
    print("\n" + "=" * 65)
    print("3. VOLATILITY DRAG: LA VARIANZA DESTRUYE RIQUEZA")
    print("=" * 65)

    # Secuencias con media aritmetica = 0
    ejemplos = [
        ("+10%, -10%", [0.10, -0.10]),
        ("+20%, -20%", [0.20, -0.20]),
        ("+50%, -50%", [0.50, -0.50]),
        ("+100%, -100%", [1.00, -1.00]),
    ]

    print(f"\n  {'Secuencia':<20} {'Media arit.':<12} {'Riqueza final':<15} {'Retorno real'}")
    print(f"  {'-'*55}")
    for nombre, rets in ejemplos:
        media_arit = np.mean(rets)
        riqueza = 100 * np.prod([1 + r for r in rets])
        ret_real = riqueza / 100 - 1
        print(f"  {nombre:<20} {media_arit:>+8.0%}      ${riqueza:>10.2f}     {ret_real:>+8.1%}")

    # Simulacion masiva
    np.random.seed(42)
    n_tray = 5000
    n_pasos = 252

    print(f"\n  Simulacion: {n_tray} trayectorias, {n_pasos} dias, media=0, sigma variable:")
    print(f"\n  {'Sigma diaria':<15} {'Riqueza mediana':<18} {'P(perder dinero)':<18} {'Drag anual'}")
    print(f"  {'-'*60}")

    for sigma in [0.005, 0.010, 0.015, 0.020, 0.030]:
        retornos = np.random.normal(0, sigma, (n_tray, n_pasos))
        riqueza_final = 100 * np.exp(np.sum(np.log(1 + retornos), axis=1))
        mediana = np.median(riqueza_final)
        p_perdida = (riqueza_final < 100).mean()
        drag = sigma**2 / 2 * 252 * 100  # Aproximacion anual en %

        print(f"  {sigma*100:.1f}%{'':>10} ${mediana:>12.2f}     {p_perdida:>12.1%}      "
              f"~{drag:.1f}%")

    print(f"\n  -> Media aritmetica = 0 para TODOS")
    print(f"  -> Pero la riqueza BAJA con sigma^2")
    print(f"  -> Drag ~ sigma^2/2 (formula exacta)")
    print(f"  -> Esto es por que la preservacion de capital es PRIORIDAD #1")


def demo_path_dependence():
    """El orden de retornos importa."""
    print("\n" + "=" * 65)
    print("4. PATH DEPENDENCE: EL ORDEN IMPORTA")
    print("=" * 65)

    retornos = [0.20, 0.10, -0.30, 0.15, -0.05]

    # Mismo set de retornos, diferente orden
    np.random.seed(42)
    n_perms = 1000
    riquezas = []
    for _ in range(n_perms):
        perm = np.random.permutation(retornos)
        riqueza = 100 * np.prod(1 + np.array(perm))
        riquezas.append(riqueza)

    print(f"\n  Retornos: {retornos}")
    print(f"  Media aritmetica: {np.mean(retornos):+.1%}")
    print(f"  Riqueza final (cualquier orden): ${100 * np.prod(1 + np.array(retornos)):.2f}")
    print(f"  -> Con multiplicacion, el orden NO importa para riqueza final")
    print(f"  -> PERO con retiros/aportes intermedios, SI importa!")

    # Con retiro intermedio
    print(f"\n  Con retiro de $10 despues de cada periodo:")

    # Mejor caso: ganancias primero
    w = 100
    for r in sorted(retornos, reverse=True):
        w = w * (1 + r) - 10
    print(f"    Ganancias primero: ${max(w, 0):.2f}")

    # Peor caso: perdidas primero
    w = 100
    for r in sorted(retornos):
        w = max(w * (1 + r) - 10, 0)
    print(f"    Perdidas primero:  ${max(w, 0):.2f}")

    print(f"\n  -> Con flujos intermedios, el ORDEN destruye o crea riqueza")
    print(f"  -> Esto es path dependence: la secuencia importa tanto como el promedio")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: LOSS FUNCTIONS, VOLATILITY DRAG Y EXPECTED LOSS")
    print("  Modulo 8B")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_loss_functions()
    demo_var_es()
    demo_volatility_drag()
    demo_path_dependence()

    print("\n" + "=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
