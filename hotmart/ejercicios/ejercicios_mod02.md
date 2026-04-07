# Ejercicios Practicos — Modulo 2: Analisis y Cuantificacion de Incertidumbre
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Monty Hall con 100 Puertas

**Nivel:** Basico
**Tiempo estimado:** 15 min

### Enunciado
Modifica la simulacion de Monty Hall para 100 puertas:
- Hay 1 auto y 99 cabras
- Eliges 1 puerta
- Monty abre 98 puertas con cabras
- Te ofrece cambiar a la unica puerta cerrada restante

1. Calcula analticamente P(ganar | cambiar)
2. Simula 10,000 iteraciones y verifica
3. Como se generaliza a N puertas?

### Codigo inicial
```python
import random

def monty_hall_n_doors(n_doors, n_simulations=10000):
    """Simula Monty Hall con n_doors puertas."""
    switch_wins = 0
    for _ in range(n_simulations):
        car = random.randint(0, n_doors - 1)
        choice = random.randint(0, n_doors - 1)
        # Si cambias, ganas cuando NO elegiste el auto originalmente
        if choice != car:
            switch_wins += 1
    return switch_wins / n_simulations

# TODO: probar con n=3, n=10, n=100, n=1000
# TODO: graficar P(ganar|cambiar) vs numero de puertas
```

### Respuesta esperada
P(ganar|cambiar) = (N-1)/N. Para 100 puertas: 99%.

---

## Ejercicio 2: Indicador de Recesion y Falacia del Fiscal

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
Tu indicador propietario de recesion tiene:
- True positive rate: 95% (detecta recesiones correctamente)
- False positive rate: 15% (alarmas falsas)

La base rate de recesiones en USA (1982-2022) es ~9.6%.

1. Si tu indicador dispara una alarma, cual es P(recesion|alarma)?
2. Que false positive rate necesitas para que P(recesion|alarma) > 50%?
3. Implementa la solucion usando la regla de probabilidad inversa.

### Codigo inicial
```python
def posterior_recession(true_positive, false_positive, base_rate):
    """Calcula P(recesion|alarma) usando regla inversa."""
    p_alarm = true_positive * base_rate + false_positive * (1 - base_rate)
    p_recession_given_alarm = true_positive * base_rate / p_alarm
    return p_recession_given_alarm

# TODO: calcular con los valores dados
# TODO: encontrar false_positive_max tal que resultado > 0.5
# TODO: graficar P(recesion|alarma) vs false_positive_rate
```

---

## Ejercicio 3: Tipos de Incertidumbre en tu Portafolio

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Clasifica cada uno de los siguientes eventos en aleatoria, epistemica
u ontologica. Justifica tu respuesta.

1. Apple pierde 3% manana
2. La Fed sube tasas en la proxima reunion
3. Una pandemia global cierra mercados por semanas
4. La volatilidad de Tesla el proximo mes
5. China invade Taiwan
6. Tu estimacion de beta para Apple es 1.33
7. El S&P 500 cae 20% en un dia

### Reflexion
Para cada tipo de incertidumbre, que herramienta probabilistica usarias?
- Aleatoria → ?
- Epistemica → ?
- Ontologica → ?

---

## Ejercicio 4: Simulacion MCS Personalizada

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Modifica la simulacion de Monty Hall para modelar una decision de inversion:

- 3 oportunidades de inversion (A, B, C)
- Solo 1 generara retorno positivo (el "auto")
- Tu due diligence te da informacion parcial
  (equivalente a que Monty abra una puerta)
- Modela con probabilidades no uniformes: P(A)=0.5, P(B)=0.3, P(C)=0.2

1. Calcula P(B es ganadora | A eliminada) usando regla inversa
2. Simula 10,000 iteraciones
3. Como cambia el resultado si tus priors son incorrectos?

```python
# Hint: usar np.random.choice con probabilidades no uniformes
# Comparar resultado con priors uniformes vs informados
```
