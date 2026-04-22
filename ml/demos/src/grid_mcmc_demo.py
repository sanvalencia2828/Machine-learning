"""
Demo: Grid Approximation, Markov Chains y MCMC Metropolis.

Implementa grid approx, simula Markov chains de estados de mercado,
y ejecuta MCMC Metropolis para estimar nu de Student-t.

source_ref: turn0browsertab744690698

Requisitos: numpy, scipy
Ejecutar: python src/grid_mcmc_demo.py
"""
import numpy as np
from scipy import stats


def demo_grid():
    """Grid approximation para Beta-Binomial."""
    print("=" * 65)
    print("1. GRID APPROXIMATION")
    print("=" * 65)

    theta = np.linspace(0.001, 0.999, 1000)
    prior = stats.beta.pdf(theta, 2, 2)
    likelihood = stats.binom.pmf(7, 8, theta)
    posterior = prior * likelihood
    posterior /= (posterior.sum() * (theta[1] - theta[0]))

    media_grid = np.sum(theta * posterior * (theta[1] - theta[0]))
    media_exact = (2 + 7) / (2 + 7 + 2 + 1)

    print(f"\n  Caso: 7 beats en 8 trimestres, prior Beta(2,2)")
    print(f"  Grid (1000 pts): media = {media_grid:.4f}")
    print(f"  Exacto Beta(9,3): media = {media_exact:.4f}")
    print(f"  Error: {abs(media_grid - media_exact):.6f}")

    print(f"\n  Maldicion de la dimensionalidad:")
    for d in [1, 2, 3, 5, 10]:
        e = 100**d
        status = "factible" if e < 1e6 else "IMPOSIBLE" if e > 1e9 else "lento"
        print(f"    {d} param: {e:>20,} evaluaciones  ({status})")


def demo_markov():
    """Markov chain de estados de mercado."""
    print("\n" + "=" * 65)
    print("2. MARKOV CHAIN: ESTADOS DE MERCADO")
    print("=" * 65)

    np.random.seed(42)
    T = np.array([[0.6, 0.3, 0.1], [0.2, 0.5, 0.3], [0.1, 0.3, 0.6]])
    estados = ["Bear", "Stagnant", "Bull"]

    cadena = [1]
    for _ in range(999):
        cadena.append(np.random.choice(3, p=T[cadena[-1]]))
    cadena = np.array(cadena)

    freq = np.bincount(cadena, minlength=3) / len(cadena)
    evals, evecs = np.linalg.eig(T.T)
    idx = np.argmin(np.abs(evals - 1))
    estac = np.abs(evecs[:, idx])
    estac /= estac.sum()

    print(f"\n  {'Estado':<12} {'Frecuencia':<15} {'Estacionaria'}")
    print(f"  {'-'*40}")
    for i, e in enumerate(estados):
        print(f"  {e:<12} {freq[i]:<15.1%} {estac[i]:.1%}")
    print(f"\n  -> La cadena converge a la distribucion estacionaria")


def demo_metropolis():
    """MCMC Metropolis para nu de Student-t."""
    print("\n" + "=" * 65)
    print("3. MCMC METROPOLIS: ESTIMAR nu")
    print("=" * 65)

    np.random.seed(42)
    nu_real = 4.0
    datos = 0.012 * np.random.standard_t(nu_real, 500)
    mu_d = np.median(datos)
    scale_d = np.median(np.abs(datos - mu_d)) * 1.4826

    def log_post(nu):
        if nu <= 2: return -np.inf
        return (stats.expon.logpdf(nu, scale=30) +
                np.sum(stats.t.logpdf(datos, nu, mu_d, scale_d)))

    n_iter, burn = 30000, 5000
    chain = np.zeros(n_iter)
    chain[0] = 10.0
    acc = 0

    for i in range(1, n_iter):
        prop = chain[i-1] + np.random.normal(0, 0.8)
        if prop > 2 and np.log(np.random.random()) < log_post(prop) - log_post(chain[i-1]):
            chain[i] = prop
            acc += 1
        else:
            chain[i] = chain[i-1]

    post = chain[burn:]
    print(f"\n  Datos: 500 retornos ~ Student-t(nu={nu_real})")
    print(f"  Iteraciones: {n_iter:,}, burn-in: {burn:,}")
    print(f"  Tasa aceptacion: {acc/n_iter:.1%}")
    print(f"\n  nu posterior:")
    print(f"    Media:   {post.mean():.2f}")
    print(f"    Mediana: {np.median(post):.2f}")
    print(f"    HDI 95%: ({np.percentile(post, 2.5):.2f}, {np.percentile(post, 97.5):.2f})")
    print(f"    Real:    {nu_real}")


def demo_resumen():
    """Tabla resumen de metodos."""
    print("\n" + "=" * 65)
    print("4. RESUMEN: GRID vs METROPOLIS vs HMC")
    print("=" * 65)
    print("""
  Metodo        Parametros    Velocidad     Cuando usar
  -----------------------------------------------------------
  Conjugados    1-2           Instantaneo   Beta-Binomial, Normal-Normal
  Grid          1-2           Rapido        Cualquier modelo simple
  Metropolis    1-10          Moderado      Posteriors no-analiticos
  HMC/NUTS      10-1000+      Rapido*       Modelos complejos (PyMC)

  * HMC es rapido POR MUESTRA, no en total
  * PyMC implementa NUTS (HMC adaptativo) automaticamente
  * Modulo 7: usaremos PyMC para todo esto
""")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  DEMO: GRID, MARKOV CHAINS Y MCMC METROPOLIS")
    print("  Modulo 6C")
    print("  source_ref: turn0browsertab744690698")
    print("=" * 65)

    demo_grid()
    demo_markov()
    demo_metropolis()
    demo_resumen()

    print("=" * 65)
    print("  DEMO COMPLETADA")
    print("=" * 65)
