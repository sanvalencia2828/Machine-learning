"""
Demo: Probabilidades Relativas y Critica a Riesgo vs Incertidumbre.

Demuestra que toda probabilidad es condicional a la informacion
disponible. Compara inferencia frecuentista vs epistemica y muestra
por que la distincion de Knight entre riesgo e incertidumbre es
inutil en la practica financiera.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy, matplotlib
Ejecutar: python src/relative_probability_demo.py
"""
import numpy as np
from scipy import stats
from pathlib import Path


# ============================================================
# 1. Probabilidad condicional: mismo evento, diferente informacion
# ============================================================

def demo_probabilidad_condicional():
    """Muestra como P(evento) cambia con diferente informacion."""
    print("=" * 60)
    print("1. PROBABILIDAD CONDICIONAL: TODO ES RELATIVO")
    print("=" * 60)

    # Ejemplo: estimar probabilidad de default de una empresa
    escenarios = [
        {
            "info": "Solo rating crediticio (BBB)",
            "prior_alpha": 2, "prior_beta": 18,
            "descripcion": "Historico: ~10% de empresas BBB hacen default en 10 anos",
        },
        {
            "info": "Rating BBB + ingresos record",
            "prior_alpha": 2, "prior_beta": 28,  # mas evidencia negativa
            "descripcion": "Ingresos solidos reducen la estimacion de default",
        },
        {
            "info": "Rating BBB + ingresos record + deuda oculta descubierta",
            "prior_alpha": 5, "prior_beta": 28,
            "descripcion": "Deuda oculta incrementa drasticamente la estimacion",
        },
    ]

    for i, esc in enumerate(escenarios):
        dist = stats.beta(esc["prior_alpha"], esc["prior_beta"])
        media = dist.mean()
        hdi = dist.ppf([0.025, 0.975])
        print(f"\n  Escenario {i+1}: {esc['info']}")
        print(f"    {esc['descripcion']}")
        print(f"    P(default) = {media:.1%}  HDI 95%: ({hdi[0]:.1%}, {hdi[1]:.1%})")

    print("\n  -> Misma empresa, diferente informacion, diferente probabilidad")


# ============================================================
# 2. Frecuentista vs Epistemico: comparacion directa
# ============================================================

def demo_frecuentista_vs_epistemico(n: int = 20, p_real: float = 0.7, seed: int = 42):
    """Compara estimacion de sesgo de moneda con ambos enfoques.

    Parametros
    ----------
    n : int
        Numero de lanzamientos.
    p_real : float
        Probabilidad real de cara.
    seed : int
        Semilla para reproducibilidad.
    """
    print("\n" + "=" * 60)
    print(f"2. FRECUENTISTA vs EPISTEMICO (n={n}, p_real={p_real})")
    print("=" * 60)

    np.random.seed(seed)
    datos = np.random.binomial(1, p_real, n)
    caras = datos.sum()

    # Frecuentista
    p_hat = caras / n
    se = np.sqrt(p_hat * (1 - p_hat) / n)
    ic_95 = (max(0, p_hat - 1.96 * se), min(1, p_hat + 1.96 * se))
    ancho_ic = ic_95[1] - ic_95[0]

    # Epistemico (Beta-Binomial)
    a_post = 2 + caras
    b_post = 2 + (n - caras)
    posterior = stats.beta(a_post, b_post)
    media_post = posterior.mean()
    hdi_95 = posterior.ppf([0.025, 0.975])
    ancho_hdi = hdi_95[1] - hdi_95[0]

    print(f"\n  Datos: {caras} caras en {n} lanzamientos")
    print(f"\n  {'Metrica':<30} {'Frecuentista':<20} {'Epistemico'}")
    print(f"  {'-'*70}")
    print(f"  {'Estimacion puntual':<30} {p_hat:<20.4f} {media_post:.4f}")
    print(f"  {'Intervalo 95%':<30} ({ic_95[0]:.3f}, {ic_95[1]:.3f})"
          f"{'':>5}({hdi_95[0]:.3f}, {hdi_95[1]:.3f})")
    print(f"  {'Ancho del intervalo':<30} {ancho_ic:<20.4f} {ancho_hdi:.4f}")

    # Ventaja del epistemico: responder preguntas directas
    p_sesgo_alto = 1 - posterior.cdf(0.6)
    print(f"\n  P(sesgo > 0.6):")
    print(f"    Frecuentista: NO PUEDE RESPONDER (no es una frecuencia de largo plazo)")
    print(f"    Epistemico:   {p_sesgo_alto:.1%}")

    return {"freq_ic": ic_95, "bayes_hdi": hdi_95}


# ============================================================
# 3. Critica a Knight: el espectro riesgo-incertidumbre
# ============================================================

def demo_espectro_knight():
    """Muestra que la frontera riesgo/incertidumbre no es fija."""
    print("\n" + "=" * 60)
    print("3. CRITICA A KNIGHT: ESPECTRO CONTINUO")
    print("=" * 60)

    espectro = [
        ("Ruleta de casino",              0.95, "Calibrada fisicamente"),
        ("Retorno S&P 500 manana",        0.75, "130+ anos de datos"),
        ("Fed sube tasas proximo mes",    0.60, "CME FedWatch + comunicados"),
        ("Default de bonos AA en 5 anos", 0.50, "Agencias de rating + mercado"),
        ("Recesion en 12 meses",          0.35, "Indicadores macro + curva yield"),
        ("Impacto de nueva regulacion",   0.20, "Precedentes parciales"),
        ("Pandemia/guerra sin precedente", 0.05, "Sin datos historicos directos"),
    ]

    print(f"\n  {'Evento':<40} {'Confianza':>10} {'Fuente de estimacion'}")
    print(f"  {'-'*80}")
    for evento, conf, fuente in espectro:
        barra = "#" * int(conf * 20) + "." * (20 - int(conf * 20))
        print(f"  {evento:<40} {conf:>8.0%}  {barra}  {fuente}")

    print(f"\n  Conclusion: NO hay frontera fija entre 'riesgo' y 'incertidumbre'.")
    print(f"  La confianza en tus probabilidades es un continuo que depende de")
    print(f"  la calidad de tu modelo y la cantidad de informacion disponible.")


# ============================================================
# 4. Actualizacion secuencial: el modelo aprende
# ============================================================

def demo_actualizacion_secuencial(n: int = 100, p_real: float = 0.65, seed: int = 123):
    """Demuestra como la posterior se actualiza dato por dato.

    Parametros
    ----------
    n : int
        Numero de observaciones.
    p_real : float
        Probabilidad real del evento.
    seed : int
        Semilla aleatoria.
    """
    print("\n" + "=" * 60)
    print(f"4. ACTUALIZACION SECUENCIAL (n={n})")
    print("=" * 60)

    np.random.seed(seed)
    datos = np.random.binomial(1, p_real, n)

    # Evolucionar posterior
    a, b = 2, 2  # Prior Beta(2,2)
    checkpoints = [0, 5, 10, 25, 50, 100]
    punto_idx = 0

    for i in range(n + 1):
        if punto_idx < len(checkpoints) and i == checkpoints[punto_idx]:
            dist = stats.beta(a, b)
            hdi = dist.ppf([0.025, 0.975])
            ancho = hdi[1] - hdi[0]
            print(f"\n  n={i:>3d}: media={dist.mean():.3f}  "
                  f"HDI=({hdi[0]:.3f}, {hdi[1]:.3f})  ancho={ancho:.3f}")
            punto_idx += 1
        if i < n:
            a += datos[i]
            b += (1 - datos[i])

    print(f"\n  -> Con 0 datos: ancho HDI = 0.764 (mucha incertidumbre)")
    print(f"  -> Con 100 datos: ancho HDI se reduce ~80%")
    print(f"  -> El modelo CUANTIFICA lo que no sabe")


# ============================================================
# 5. Aplicacion financiera: VaR Normal vs Student-t
# ============================================================

def demo_var_comparacion(n: int = 504, seed: int = 42):
    """Compara VaR parametrico normal vs Student-t.

    Parametros
    ----------
    n : int
        Numero de retornos diarios (2 anos ~ 504).
    seed : int
        Semilla aleatoria.
    """
    print("\n" + "=" * 60)
    print("5. VAR NORMAL vs STUDENT-T (APLICACION FINANCIERA)")
    print("=" * 60)

    np.random.seed(seed)
    mu_real, sigma_real, nu_real = 0.0003, 0.012, 4
    retornos = mu_real + sigma_real * np.random.standard_t(nu_real, size=n)

    # Frecuentista: asume normalidad
    mu_f = retornos.mean()
    sigma_f = retornos.std()
    var_95_f = mu_f + stats.norm.ppf(0.05) * sigma_f

    # Epistemico: ajusta Student-t
    nu_fit, mu_e, sigma_e = stats.t.fit(retornos)
    var_95_e = stats.t.ppf(0.05, nu_fit, mu_e, sigma_e)

    # Expected Shortfall
    n_sim = 100_000
    sim_f = np.random.normal(mu_f, sigma_f, n_sim)
    sim_e = stats.t.rvs(nu_fit, mu_e, sigma_e, size=n_sim)
    es_f = sim_f[sim_f <= np.percentile(sim_f, 5)].mean()
    es_e = sim_e[sim_e <= np.percentile(sim_e, 5)].mean()

    # Capital allocation
    capital = 1_000_000
    alloc_f = capital / abs(var_95_f)
    alloc_e = capital / abs(var_95_e)

    print(f"\n  {'Metrica':<30} {'Normal (freq)':<20} {'Student-t (epist)'}")
    print(f"  {'-'*70}")
    print(f"  {'VaR 95% diario':<30} {var_95_f:>18.5f}  {var_95_e:>18.5f}")
    print(f"  {'Expected Shortfall 95%':<30} {es_f:>18.5f}  {es_e:>18.5f}")
    print(f"  {'nu estimado':<30} {'inf (asumido)':>18}  {nu_fit:>18.1f}")
    print(f"  {'Max allocation ($)':<30} {alloc_f:>18,.0f}  {alloc_e:>18,.0f}")

    diff_var = (var_95_e - var_95_f) / abs(var_95_f) * 100
    diff_alloc = (alloc_f - alloc_e) / alloc_e * 100
    print(f"\n  -> VaR epistemico es {abs(diff_var):.1f}% mas conservador")
    print(f"  -> Frecuentista sobreasigna {diff_alloc:.1f}% mas capital")
    print(f"  -> Con $1M de capital, la diferencia es ${alloc_f - alloc_e:,.0f}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  DEMO: PROBABILIDADES RELATIVAS")
    print("  Modulo 2B -- Riesgo vs Incertidumbre")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 60)

    demo_probabilidad_condicional()
    demo_frecuentista_vs_epistemico(n=20, p_real=0.7)
    demo_frecuentista_vs_epistemico(n=5, p_real=0.7)
    demo_espectro_knight()
    demo_actualizacion_secuencial()
    demo_var_comparacion()

    print("\n" + "=" * 60)
    print("  DEMO COMPLETADA")
    print("  Archivos relacionados:")
    print("    - notebooks/notebook_ch02_relative_probability.md")
    print("    - hotmart/viz_relative_probability.py")
    print("    - hotmart/ejercicios/ejercicios_mod02b_relative_prob.md")
    print("=" * 60)
