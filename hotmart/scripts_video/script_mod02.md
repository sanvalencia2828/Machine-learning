# Script de Video — Modulo 2: Analisis y Cuantificacion de Incertidumbre
# Duracion estimada: 60 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho — El Problema de Monty Hall (10 min)

### [CAMARA]
"Estas en un concurso de TV. Hay un auto detras de una de tres puertas y
cabras detras de las otras dos. Eliges la puerta 1. El presentador, que sabe
donde esta el auto, abre la puerta 3 y muestra una cabra. Te ofrece
cambiar a la puerta 2. Que haces?"

### [SLIDE: Reglas del juego]
1. Auto detras de 1 de 3 puertas, cabras en las otras 2
2. Solo Monty sabe donde esta el auto
3. Tu eliges una puerta
4. Monty abre otra puerta mostrando una cabra
5. Te ofrece cambiar

### [CAMARA]
"La mayoria dice que no importa — 50/50. Yo tambien pense eso la primera
vez. Pero estaba equivocado. Cambiar DUPLICA tu probabilidad de ganar.
Veamos por que."

---

## Segmento 2: Solucion Analitica (12 min)

### [SLIDE: Axiomas de probabilidad]
- Axioma 1: P(S) >= 0
- Axioma 2: P(S1) + P(S2) + P(S3) = 1
- Axioma 3 (suma): P(S2 o S3) = P(S2) + P(S3)

### [PIZARRA DIGITAL: resolver paso a paso]
- Antes: P(S1) = P(S2) = P(S3) = 1/3
- P(S2 o S3) = 2/3
- Monty abre puerta 3: P(S3) = 0
- P(S2) = 2/3 - 0 = 2/3
- Cambiar duplica la probabilidad!

### [SLIDE: Teoria de juegos]
- Juego secuencial competitivo de 2 personas
- Equilibrio de Nash: cambiar puertas
- Analogia con trading: la informacion nueva cambia las probabilidades

### [SLIDE: Psicologia financiera]
- Efecto dotacion: valoramos mas lo que poseemos
- Aversion a perdidas: perder duele mas que ganar
- Inercia: preferimos error de omision a error de comision
- Mismos sesgos en inversiones y trading

---

## Segmento 3: Regla de Probabilidad Inversa (15 min)

### [SLIDE: Probabilidad condicional]
- P(H|D) = P(H y D) / P(D)
- Regla del producto: P(H y D) = P(H|D) x P(D)

### [PIZARRA: derivar la regla inversa]
- P(H y D) = P(D y H)  [conmutan]
- P(H|D) x P(D) = P(D|H) x P(H)
- P(H|D) = P(D|H) x P(H) / P(D)  ← regla inversa

### [CAMARA]
"Eso es TODO. La prueba del mal llamado 'Teorema de Bayes' es tan facil
como multiplicar dos numeros y despejar uno. Es una reformulacion trivial
de la regla del producto."

### [SLIDE: Bayes NO descubrio el teorema de Bayes]
- Laplace lo descubrio independientemente y escribio la formula general
- Bayes nunca generalizo su resultado
- Fisher lo renombro peyorativamente en el siglo XX
- En este curso: regla de probabilidad inversa

### [SCREENCAST: aplicar al Monty Hall]
```python
# Calcular P(S2|D) usando la regla inversa
# P(D|S1) = 1/2, P(D|S2) = 1, P(D|S3) = 0
# P(D) = 1/2*1/3 + 1*1/3 + 0*1/3 = 1/2
# P(S2|D) = 1*1/3 / 1/2 = 2/3
```

---

## Segmento 4: Simulacion Monte Carlo + Tipos de Incertidumbre (15 min)

### [SCREENCAST: simular Monty Hall]
```python
# Abrir notebook_ch02_monty_hall_uncertainty.md
# Ejecutar simulacion con 10, 100, 1000, 10000 iteraciones
# Mostrar convergencia a 2/3
```

### [SLIDE: Trinidad de incertidumbre]
1. **Aleatoria** (datos): irreducible, como lanzar dados
   - Pero: dados y monedas son FISICA, no aleatoriedad!
   - La aleatoriedad viene de nuestra ignorancia de las condiciones iniciales
2. **Epistemica** (conocimiento): reducible con mas informacion
   - Monty nos da informacion → actualizamos probabilidades
   - Asimetria de informacion en mercados financieros
3. **Ontologica** (realidad): el futuro es inherentemente impredecible
   - Monty cambia las reglas del juego
   - Mercados cambian estructuralmente sin previo aviso

### [SLIDE: Teoremas No Free Lunch]
- No existe un algoritmo optimo para TODOS los problemas
- Necesitas conocimiento previo del dominio
- Sin conocimiento previo → performance = azar
- Implicacion: integrar conocimiento financiero es OBLIGATORIO, no opcional

---

## Segmento 5: Cierre (8 min)

### [SLIDE: Frecuentista vs Epistemico — resumen]
| Dimension | Frecuentista | Epistemico |
|-----------|-------------|------------|
| Probabilidad | Frecuencia de largo plazo | Propiedad de la informacion |
| Datos | Variables aleatorias | Constantes conocidas |
| Parametros | Constantes desconocidas | Variables desconocidas |
| Inferencia | MLE | Regla inversa |
| Tests | NHST + p-values | Grados de plausibilidad |

### [CAMARA]
"Ahora entiendes los tres tipos de incertidumbre y tienes la herramienta
matematica fundamental: la regla de probabilidad inversa. En el siguiente
modulo, la aplicaremos con simulaciones Monte Carlo para cuantificar la
incertidumbre de salida de modelos financieros."

### [CTA]
"Ejercicio: modifica la simulacion de Monty Hall para 100 puertas
(Monty abre 98). Que probabilidad tiene cambiar? Comparte tu resultado
en la comunidad."
