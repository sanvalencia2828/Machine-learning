---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Simulacion Monte Carlo para Finanzas

## Proposito

Implementar simulaciones Monte Carlo (MCS) desde la estimacion de pi hasta la
valoracion de un proyecto de software. Se cubren los fundamentos estadisticos
necesarios: LGN, TLC, momentos y distribuciones.

## Requisitos

```python
# Importar librerias necesarias
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Semilla para reproducibilidad
np.random.seed(42)
```

---

## 1. Prueba de concepto: estimacion de pi con Monte Carlo

Lanzamos puntos aleatorios en un cuadrado unitario y contamos cuantos caen
dentro del circulo inscrito.

```python
def estimar_pi(n_puntos):
    """Estimar pi lanzando puntos aleatorios en el cuadrado [-1,1] x [-1,1]."""
    x = np.random.uniform(-1, 1, n_puntos)
    y = np.random.uniform(-1, 1, n_puntos)
    dentro_circulo = (x**2 + y**2) <= 1.0
    pi_estimado = 4.0 * np.sum(dentro_circulo) / n_puntos
    return pi_estimado, x, y, dentro_circulo

# Estimar con distintas cantidades de puntos
for n in [100, 1_000, 10_000, 100_000, 1_000_000]:
    estimacion, _, _, _ = estimar_pi(n)
    error = abs(estimacion - np.pi)
    print(f"n = {n:>10,} -> pi ≈ {estimacion:.6f}  (error = {error:.6f})")
```

**Salida esperada**: El error disminuye conforme n crece, convergiendo a pi = 3.14159...

```python
# Visualizar la estimacion con 5,000 puntos
np.random.seed(42)
pi_est, x, y, dentro = estimar_pi(5_000)

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(x[dentro], y[dentro], s=1, c='blue', alpha=0.5, label='Dentro')
ax.scatter(x[~dentro], y[~dentro], s=1, c='red', alpha=0.5, label='Fuera')

# Dibujar el circulo unitario
theta = np.linspace(0, 2*np.pi, 200)
ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=1.5)

ax.set_aspect('equal')
ax.set_title(f'Estimacion de pi con MCS: {pi_est:.4f} (n=5,000)')
ax.legend(loc='upper right')
plt.tight_layout()
plt.savefig('../data/fig_ch03_pi_montecarlo.png', dpi=100)
plt.show()
```

---

## 2. Conceptos estadisticos: media, varianza, sesgo, curtosis

```python
# Generar retornos sinteticos que imiten un activo financiero
n_dias = 2500  # Aproximadamente 10 anios de trading

# Retornos con ligero sesgo negativo y curtosis elevada
retornos = np.concatenate([
    np.random.normal(0.0003, 0.012, int(n_dias * 0.85)),  # Dias normales
    np.random.normal(-0.002, 0.035, int(n_dias * 0.15))   # Dias de estres
])
np.random.shuffle(retornos)

# Calcular los cuatro momentos
media = np.mean(retornos)
varianza = np.var(retornos, ddof=1)
desv_est = np.std(retornos, ddof=1)

# Sesgo (skewness): tercer momento estandarizado
n = len(retornos)
sesgo = (n / ((n-1)*(n-2))) * np.sum(((retornos - media) / desv_est)**3)

# Curtosis (exceso): cuarto momento estandarizado menos 3
curtosis = ((n*(n+1)) / ((n-1)*(n-2)*(n-3))) * np.sum(((retornos - media) / desv_est)**4)
curtosis -= (3*(n-1)**2) / ((n-2)*(n-3))

print("=== Momentos estadisticos de retornos sinteticos ===")
print(f"Media diaria:          {media:.6f}")
print(f"Desviacion estandar:   {desv_est:.6f}")
print(f"Varianza:              {varianza:.8f}")
print(f"Sesgo (skewness):      {sesgo:.4f}")
print(f"Curtosis (exceso):     {curtosis:.4f}")
print(f"\nRetorno anualizado:    {media * 252:.4f}")
print(f"Volatilidad anualizada: {desv_est * np.sqrt(252):.4f}")
```

**Salida esperada**: Sesgo ligeramente negativo y curtosis mayor a 0 (leptocurtica).

---

## 3. Distribucion normal vs retornos reales

```python
# Comparar retornos sinteticos con una normal teorica
from scipy import stats

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histograma con densidad normal superpuesta
x_rango = np.linspace(retornos.min(), retornos.max(), 200)
densidad_normal = stats.norm.pdf(x_rango, media, desv_est)

axes[0].hist(retornos, bins=100, density=True, alpha=0.6, label='Retornos sinteticos')
axes[0].plot(x_rango, densidad_normal, 'r-', linewidth=2, label='Normal teorica')
axes[0].set_title('Histograma vs Normal')
axes[0].set_xlabel('Retorno diario')
axes[0].set_ylabel('Densidad')
axes[0].legend()

# Zoom en las colas (retornos < -3 desviaciones)
umbral_cola = -3 * desv_est
cola_observada = np.sum(retornos < umbral_cola) / len(retornos)
cola_teorica = stats.norm.cdf(umbral_cola, media, desv_est)

axes[1].hist(retornos[retornos < -2*desv_est], bins=40, density=True, alpha=0.6,
             label=f'Cola observada: {cola_observada:.4f}')
x_cola = np.linspace(retornos.min(), -2*desv_est, 100)
axes[1].plot(x_cola, stats.norm.pdf(x_cola, media, desv_est), 'r-', linewidth=2,
             label=f'Cola normal: {cola_teorica:.4f}')
axes[1].set_title('Zoom en la cola izquierda')
axes[1].set_xlabel('Retorno diario')
axes[1].legend()

plt.suptitle('Normal vs retornos reales: las colas importan', fontsize=13)
plt.tight_layout()
plt.savefig('../data/fig_ch03_normal_vs_real.png', dpi=100)
plt.show()

print(f"Eventos extremos (<-3σ): observados={cola_observada:.4%}, normal teorica={cola_teorica:.4%}")
```

---

## 4. Ley de Grandes Numeros: convergencia del promedio de dados

```python
# Simular lanzamientos de un dado justo y observar convergencia de la media
n_lanzamientos = 10_000
lanzamientos = np.random.randint(1, 7, size=n_lanzamientos)

# Calcular media acumulada despues de cada lanzamiento
media_acumulada = np.cumsum(lanzamientos) / np.arange(1, n_lanzamientos + 1)

# Valor esperado teorico de un dado justo
valor_esperado = 3.5

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(media_acumulada, linewidth=0.8, label='Media acumulada')
ax.axhline(valor_esperado, color='red', linestyle='--', linewidth=1.5,
           label=f'E[X] = {valor_esperado}')
ax.fill_between(range(n_lanzamientos),
                valor_esperado - 0.1, valor_esperado + 0.1,
                alpha=0.2, color='red', label='Banda ±0.1')
ax.set_xlabel('Numero de lanzamientos')
ax.set_ylabel('Media acumulada')
ax.set_title('Ley de Grandes Numeros: convergencia del promedio de un dado')
ax.set_xscale('log')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('../data/fig_ch03_lgn_dado.png', dpi=100)
plt.show()
```

**Salida esperada**: La media acumulada oscila ampliamente al inicio y converge a 3.5.

---

## 5. Teorema del Limite Central: de uniforme a normal

```python
# Demostrar el TLC: la media de variables uniformes converge a una normal
tamanos_muestra = [1, 2, 5, 30]
n_repeticiones = 10_000

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for i, k in enumerate(tamanos_muestra):
    # Generar n_repeticiones medias de k variables uniformes(0,1)
    medias = np.mean(
        np.random.uniform(0, 1, size=(n_repeticiones, k)),
        axis=1
    )

    axes[i].hist(medias, bins=60, density=True, alpha=0.6, edgecolor='black', linewidth=0.3)

    # Superponer la normal teorica segun TLC
    mu_teorica = 0.5  # Media de Uniform(0,1)
    sigma_teorica = (1/np.sqrt(12)) / np.sqrt(k)  # Desv de la media
    x_plot = np.linspace(medias.min(), medias.max(), 200)
    axes[i].plot(x_plot, stats.norm.pdf(x_plot, mu_teorica, sigma_teorica),
                 'r-', linewidth=2, label='Normal teorica')

    axes[i].set_title(f'Media de k={k} uniformes (n={n_repeticiones:,})')
    axes[i].set_xlabel('Valor de la media')
    axes[i].set_ylabel('Densidad')
    axes[i].legend()

plt.suptitle('Teorema del Limite Central: de uniforme a normal', fontsize=13)
plt.tight_layout()
plt.savefig('../data/fig_ch03_tlc.png', dpi=100)
plt.show()
```

**Salida esperada**: Con k=1 la distribucion es uniforme; con k=30 es practicamente normal.

---

## 6. Aplicacion: valoracion de proyecto de software con DCF + MCS

Valorar un proyecto de desarrollo de software donde 5 variables son inciertas.

```python
# Parametros del proyecto (valores inciertos modelados como distribuciones)
n_simulaciones = 50_000
tasa_descuento = 0.10  # Tasa de descuento anual
horizonte_anios = 5

# Variable 1: Ingresos anuales iniciales (distribucion triangular)
ingresos_iniciales = np.random.triangular(500_000, 800_000, 1_200_000, n_simulaciones)

# Variable 2: Tasa de crecimiento anual de ingresos (normal truncada)
crecimiento_ingresos = np.clip(np.random.normal(0.15, 0.08, n_simulaciones), -0.10, 0.50)

# Variable 3: Costos operativos como fraccion de ingresos (uniforme)
ratio_costos = np.random.uniform(0.40, 0.70, n_simulaciones)

# Variable 4: Inversion inicial (lognormal)
inversion_inicial = np.random.lognormal(np.log(300_000), 0.3, n_simulaciones)

# Variable 5: Probabilidad de exito del proyecto (bernoulli implícita)
prob_exito = np.random.uniform(0.60, 0.95, n_simulaciones)
exito = np.random.random(n_simulaciones) < prob_exito

# Calcular flujos de caja descontados para cada simulacion
vpn_simulaciones = np.zeros(n_simulaciones)

for anio in range(1, horizonte_anios + 1):
    ingresos_anio = ingresos_iniciales * (1 + crecimiento_ingresos) ** anio
    costos_anio = ingresos_anio * ratio_costos
    flujo_neto = (ingresos_anio - costos_anio) * exito  # Cero si el proyecto falla
    factor_descuento = 1 / (1 + tasa_descuento) ** anio
    vpn_simulaciones += flujo_neto * factor_descuento

# Restar inversion inicial
vpn_simulaciones -= inversion_inicial

# Resultados
vpn_medio = np.mean(vpn_simulaciones)
vpn_mediano = np.median(vpn_simulaciones)
prob_vpn_positivo = np.mean(vpn_simulaciones > 0)
var_5 = np.percentile(vpn_simulaciones, 5)

print("=== Valoracion MCS del proyecto de software ===")
print(f"VPN medio:              ${vpn_medio:>14,.0f}")
print(f"VPN mediano:            ${vpn_mediano:>14,.0f}")
print(f"P(VPN > 0):             {prob_vpn_positivo:>14.2%}")
print(f"VaR al 5%:              ${var_5:>14,.0f}")
print(f"VPN minimo:             ${np.min(vpn_simulaciones):>14,.0f}")
print(f"VPN maximo:             ${np.max(vpn_simulaciones):>14,.0f}")
```

**Salida esperada**: Distribucion de VPN con media positiva, pero probabilidad
no despreciable de perdida.

```python
# Visualizar la distribucion de VPN
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histograma del VPN
axes[0].hist(vpn_simulaciones, bins=100, density=True, alpha=0.6, edgecolor='black', linewidth=0.3)
axes[0].axvline(vpn_medio, color='red', linestyle='--', linewidth=2, label=f'Media=${vpn_medio:,.0f}')
axes[0].axvline(0, color='black', linestyle='-', linewidth=1.5, label='Punto de equilibrio')
axes[0].axvline(var_5, color='orange', linestyle=':', linewidth=2, label=f'VaR 5%=${var_5:,.0f}')
axes[0].set_title('Distribucion del VPN del proyecto')
axes[0].set_xlabel('Valor Presente Neto ($)')
axes[0].set_ylabel('Densidad')
axes[0].legend(fontsize=8)

# Funcion de distribucion acumulada (CDF)
vpn_ordenado = np.sort(vpn_simulaciones)
cdf = np.arange(1, len(vpn_ordenado) + 1) / len(vpn_ordenado)
axes[1].plot(vpn_ordenado, cdf, linewidth=0.8)
axes[1].axhline(0.05, color='orange', linestyle=':', label='Percentil 5%')
axes[1].axvline(0, color='black', linestyle='-', linewidth=1.5, label='Punto de equilibrio')
axes[1].set_title('CDF del VPN')
axes[1].set_xlabel('Valor Presente Neto ($)')
axes[1].set_ylabel('Probabilidad acumulada')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('../data/fig_ch03_dcf_mcs.png', dpi=100)
plt.show()
```

---

## 7. Ejercicio: extender MCS para incluir correlacion entre variables

El modelo anterior asume que las 5 variables son independientes. En la realidad,
ingresos altos suelen correlacionarse con costos mas altos, y la inversion
inicial con la probabilidad de exito.

Tareas:
1. Definir una matriz de correlacion 5x5 razonable.
2. Usar la descomposicion de Cholesky (`np.linalg.cholesky`) para generar
   variables correlacionadas a partir de variables normales independientes.
3. Transformar las normales correlacionadas a las distribuciones originales
   usando la funcion inversa de la CDF (transformacion de probabilidad integral).
4. Repetir la valoracion y comparar la distribucion de VPN con el caso independiente.

```python
# Espacio para la solucion del ejercicio
# Pista: generar Z ~ N(0, Sigma) con Cholesky, luego
# transformar cada marginal con stats.norm.cdf(z) -> u ~ Uniform(0,1) -> quantil original

# Paso 1: definir matriz de correlacion
# correlacion = np.array([...])

# Paso 2: descomposicion de Cholesky
# L = np.linalg.cholesky(correlacion)

# Completar la implementacion aqui
# ...
```

---

## Referencias

- Metropolis, N. & Ulam, S. (1949). *The Monte Carlo Method*.
- Glasserman, P. (2003). *Monte Carlo Methods in Financial Engineering*.
- Damodaran, A. (2012). *Investment Valuation*.
