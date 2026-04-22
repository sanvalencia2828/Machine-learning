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

# Analisis de Incertidumbre: Del Problema de Monty Hall a los Mercados

## Proposito

Estudiar las bases de la teoria de probabilidad a traves del problema de Monty Hall,
la regla de probabilidad inversa (Bayes) y la trinidad de incertidumbre. Se conectan
estos conceptos con aplicaciones en mercados financieros y machine learning.

## Requisitos

```python
# Importar librerias necesarias
import numpy as np
import matplotlib.pyplot as plt
import random

# Semilla para reproducibilidad
random.seed(42)
np.random.seed(42)
```

---

## 1. Problema de Monty Hall: solucion analitica

Hay 3 puertas: detras de una hay un premio, detras de las otras nada.
El concursante elige una puerta, el presentador abre otra (sin premio),
y ofrece cambiar.

**Usando los axiomas de probabilidad:**

- P(premio en puerta elegida) = 1/3
- P(premio en otra puerta) = 2/3
- Al abrir una puerta vacia, toda la probabilidad 2/3 se concentra en la restante.

```python
# Demostracion analitica con enumeracion exhaustiva
# Enumeramos todos los escenarios posibles

puertas = [0, 1, 2]
escenarios = []

for puerta_premio in puertas:
    for eleccion_inicial in puertas:
        # Puerta que el presentador puede abrir (no tiene premio y no fue elegida)
        opciones_presentador = [
            p for p in puertas
            if p != puerta_premio and p != eleccion_inicial
        ]
        # El presentador elige al azar entre sus opciones validas
        for puerta_abierta in opciones_presentador:
            puerta_cambio = [
                p for p in puertas
                if p != eleccion_inicial and p != puerta_abierta
            ][0]

            gana_sin_cambiar = (eleccion_inicial == puerta_premio)
            gana_cambiando = (puerta_cambio == puerta_premio)

            escenarios.append({
                'premio': puerta_premio,
                'eleccion': eleccion_inicial,
                'abierta': puerta_abierta,
                'cambio_a': puerta_cambio,
                'gana_sin_cambiar': gana_sin_cambiar,
                'gana_cambiando': gana_cambiando
            })

# Calcular probabilidades
total = len(escenarios)
victorias_sin_cambiar = sum(e['gana_sin_cambiar'] for e in escenarios)
victorias_cambiando = sum(e['gana_cambiando'] for e in escenarios)

print(f"Total de escenarios equiprobables: {total}")
print(f"Victorias sin cambiar: {victorias_sin_cambiar}/{total} = {victorias_sin_cambiar/total:.4f}")
print(f"Victorias cambiando:   {victorias_cambiando}/{total} = {victorias_cambiando/total:.4f}")
```

**Salida esperada**: Victorias sin cambiar = 1/3, cambiando = 2/3.

---

## 2. Regla de probabilidad inversa (Bayes): derivacion paso a paso

La regla de Bayes permite actualizar creencias a la luz de nueva evidencia:

P(H|E) = P(E|H) * P(H) / P(E)

```python
# Ejemplo: prueba de deteccion de fraude en transacciones
# P(fraude) = 0.01 (prevalencia)
# P(alerta | fraude) = 0.95 (sensibilidad)
# P(alerta | no fraude) = 0.05 (falsa alarma)

p_fraude = 0.01
p_alerta_dado_fraude = 0.95
p_alerta_dado_no_fraude = 0.05

# Paso 1: probabilidad total de recibir alerta
p_alerta = (p_alerta_dado_fraude * p_fraude +
            p_alerta_dado_no_fraude * (1 - p_fraude))

# Paso 2: aplicar regla de Bayes
p_fraude_dado_alerta = (p_alerta_dado_fraude * p_fraude) / p_alerta

print("=== Regla de Bayes: deteccion de fraude ===")
print(f"P(fraude)                = {p_fraude:.4f}")
print(f"P(alerta)                = {p_alerta:.4f}")
print(f"P(fraude | alerta)       = {p_fraude_dado_alerta:.4f}")
print(f"\nConclusion: solo el {p_fraude_dado_alerta:.1%} de las alertas son fraude real.")
```

**Salida esperada**: P(fraude|alerta) ~ 0.16, mostrando que la mayoria de alertas son falsas.

---

## 3. Simulacion Monte Carlo del problema de Monty Hall

Verificar el resultado analitico mediante simulacion con cantidades crecientes.

```python
def simular_monty_hall(n_juegos):
    """Simular n juegos de Monty Hall, retornar tasa de victoria al cambiar."""
    victorias_cambio = 0

    for _ in range(n_juegos):
        puertas = [0, 1, 2]
        premio = random.choice(puertas)
        eleccion = random.choice(puertas)

        # El presentador abre una puerta sin premio y distinta de la elegida
        opciones = [p for p in puertas if p != eleccion and p != premio]
        abierta = random.choice(opciones)

        # La puerta a la que cambiamos
        cambio = [p for p in puertas if p != eleccion and p != abierta][0]

        if cambio == premio:
            victorias_cambio += 1

    return victorias_cambio / n_juegos

# Ejecutar con distintas cantidades de iteraciones
iteraciones = [10, 100, 1_000, 10_000]
resultados = {}

for n in iteraciones:
    tasa = simular_monty_hall(n)
    resultados[n] = tasa
    print(f"n = {n:>6,} juegos -> tasa de victoria al cambiar: {tasa:.4f}")

print(f"\nValor teorico: {2/3:.4f}")
```

**Salida esperada**: La tasa converge a 0.6667 conforme n crece.

```python
# Visualizar convergencia hacia el valor teorico
tamanos = np.arange(10, 5001, 10)
tasas_acumuladas = []

victorias = 0
for i in range(1, len(tamanos) * 10 + 1):
    puertas = [0, 1, 2]
    premio = random.choice(puertas)
    eleccion = random.choice(puertas)
    opciones = [p for p in puertas if p != eleccion and p != premio]
    abierta = random.choice(opciones)
    cambio = [p for p in puertas if p != eleccion and p != abierta][0]
    if cambio == premio:
        victorias += 1
    if i % 10 == 0:
        tasas_acumuladas.append(victorias / i)

plt.figure(figsize=(10, 5))
plt.plot(tamanos, tasas_acumuladas, linewidth=0.8, label='Tasa observada')
plt.axhline(2/3, color='red', linestyle='--', label='Valor teorico (2/3)')
plt.xlabel('Numero de simulaciones')
plt.ylabel('Tasa de victoria al cambiar')
plt.title('Convergencia de la simulacion Monte Carlo - Monty Hall')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('../data/fig_ch02_monty_hall_convergencia.png', dpi=100)
plt.show()
```

---

## 4. Trinidad de incertidumbre: aleatoria, epistemica y ontologica

| Tipo | Definicion | Ejemplo financiero |
|------|-----------|-------------------|
| **Aleatoria** | Variabilidad inherente al sistema | Fluctuaciones diarias de precios |
| **Epistemica** | Falta de conocimiento o datos | Parametros desconocidos de un modelo |
| **Ontologica** | Eventos fuera del modelo mental | Crisis del 2008, COVID-19 |

```python
# Ilustracion: tres tipos de incertidumbre con datos sinteticos
np.random.seed(42)
n = 1000

# Aleatoria: ruido puro de mercado, predecible en distribucion
retornos_aleatorios = np.random.normal(0, 0.02, n)

# Epistemica: no sabemos la volatilidad real (simulamos con vol incorrecta)
vol_real = 0.03
vol_estimada = 0.02
retornos_epistemicos = np.random.normal(0, vol_real, n)
modelo_epistemico = np.random.normal(0, vol_estimada, n)

# Ontologica: evento cisne negro que ningun modelo anticipo
retornos_ontologicos = np.random.normal(0, 0.02, n)
# Insertar shock inesperado en posiciones aleatorias
indices_shock = np.random.choice(n, size=5, replace=False)
retornos_ontologicos[indices_shock] = np.random.uniform(-0.15, -0.08, size=5)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
titulos = ['Aleatoria\n(ruido de mercado)',
           'Epistemica\n(vol mal estimada)',
           'Ontologica\n(cisnes negros)']
datos = [retornos_aleatorios, retornos_epistemicos, retornos_ontologicos]

for ax, titulo, d in zip(axes, titulos, datos):
    ax.hist(d, bins=60, alpha=0.7, density=True, edgecolor='black', linewidth=0.3)
    ax.set_title(titulo)
    ax.set_xlabel('Retorno')
    ax.set_ylabel('Densidad')

plt.suptitle('Trinidad de incertidumbre: ejemplos financieros', fontsize=13)
plt.tight_layout()
plt.savefig('../data/fig_ch02_trinidad_incertidumbre.png', dpi=100)
plt.show()
```

---

## 5. Probabilidad frecuentista vs epistemica

```python
# Tabla comparativa implementada como DataFrame
import pandas as pd  # Necesario solo para esta celda si no se cargo arriba

comparacion = pd.DataFrame({
    'Aspecto': [
        'Definicion de probabilidad',
        'Interpretacion de P=0.6',
        'Requiere experimento repetible',
        'Permite creencias previas',
        'Herramienta principal',
        'Aplicacion tipica en finanzas'
    ],
    'Frecuentista': [
        'Limite de frecuencia relativa',
        '60% de veces en infinitas repeticiones',
        'Si',
        'No',
        'Test de hipotesis (NHST)',
        'Backtesting de estrategias'
    ],
    'Epistemica (Bayesiana)': [
        'Grado de creencia racional',
        'Confianza del 60% en el evento',
        'No',
        'Si (prior)',
        'Teorema de Bayes',
        'Estimacion de riesgo crediticio'
    ]
})

print(comparacion.to_string(index=False))
```

---

## 6. Teoremas No Free Lunch: implicaciones para ML financiero

No existe un algoritmo de ML que sea universalmente superior. Cada modelo hace
supuestos implicitos sobre la estructura de los datos.

```python
# Demostracion: dos modelos simples funcionan mejor en distintos regimenes
np.random.seed(123)

# Regimen 1: relacion lineal (modelo lineal gana)
x_lineal = np.linspace(0, 10, 200)
y_lineal = 2.5 * x_lineal + np.random.normal(0, 3, 200)

# Regimen 2: relacion no lineal (modelo lineal pierde)
x_nolineal = np.linspace(0, 10, 200)
y_nolineal = 5 * np.sin(x_nolineal) + np.random.normal(0, 1.5, 200)

# Ajuste lineal simple a ambos regimenes
coef_lin1 = np.polyfit(x_lineal, y_lineal, 1)
coef_lin2 = np.polyfit(x_nolineal, y_nolineal, 1)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].scatter(x_lineal, y_lineal, alpha=0.4, s=10)
axes[0].plot(x_lineal, np.polyval(coef_lin1, x_lineal), 'r-', linewidth=2, label='Modelo lineal')
axes[0].set_title('Regimen lineal: modelo lineal FUNCIONA')
axes[0].legend()

axes[1].scatter(x_nolineal, y_nolineal, alpha=0.4, s=10)
axes[1].plot(x_nolineal, np.polyval(coef_lin2, x_nolineal), 'r-', linewidth=2, label='Modelo lineal')
axes[1].set_title('Regimen no lineal: modelo lineal FALLA')
axes[1].legend()

plt.suptitle('No Free Lunch: ningun modelo domina en todos los regimenes', fontsize=13)
plt.tight_layout()
plt.savefig('../data/fig_ch02_no_free_lunch.png', dpi=100)
plt.show()
```

**Salida esperada**: El modelo lineal ajusta bien en el primer caso pero falla
completamente en el segundo.

---

## 7. Ejercicio: regla inversa aplicada a deteccion de fraude

Un banco procesa 100,000 transacciones diarias. El 0.1% son fraudulentas.
El sistema de deteccion tiene:
- Sensibilidad (true positive rate): 98%
- Especificidad (true negative rate): 97%

Calcular:
1. P(fraude | alerta positiva)
2. Numero esperado de falsas alarmas por dia
3. Si se mejora la especificidad a 99.5%, como cambia P(fraude | alerta)?
4. Graficar P(fraude | alerta) como funcion de la especificidad (de 0.90 a 0.999)

```python
# Espacio para la solucion del ejercicio
# Pista: aplicar la regla de Bayes con los parametros dados
# y luego iterar sobre distintos valores de especificidad

p_fraude_banco = 0.001
sensibilidad = 0.98
transacciones_diarias = 100_000

# Completar la implementacion aqui
# ...
```

---

## Referencias

- Monty Hall problem: vos Savant, M. (1990). *Parade Magazine*.
- Jaynes, E.T. (2003). *Probability Theory: The Logic of Science*.
- Wolpert, D.H. (1996). *The Lack of A Priori Distinctions Between Learning Algorithms*.
