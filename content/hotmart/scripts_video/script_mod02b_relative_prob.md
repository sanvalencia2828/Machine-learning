# Script de Video — Modulo 2B: Probabilidades Relativas y la Critica a Riesgo vs Incertidumbre
# Duracion estimada: 45 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho — Knight se Equivoco (8 min)

### [CAMARA]
"En 1921, el economista Frank Knight propuso una distincion que domina los
libros de finanzas hasta hoy: riesgo es lo que puedes medir con
probabilidades, incertidumbre es lo que no. Suena elegante, pero es
completamente inutil en la practica financiera. Hoy vamos a destruir esa
distincion y reemplazarla con algo mucho mas poderoso."

### [SLIDE: La distincion clasica de Knight (1921)]
- **Riesgo**: resultado desconocido, probabilidades conocidas (ej: dado justo)
- **Incertidumbre**: resultado desconocido, probabilidades desconocidas (ej: guerra)
- Adoptado por: Keynes, Chicago School, CFA curriculum, reguladores

### [SLIDE: El problema con Knight]
- ¿Quien decide que probabilidades son "conocidas"?
- Un dado "justo" — ¿como sabes que es justo? ¡Lo mediste! (epistemico)
- Una recesion — ¿realmente no tiene probabilidad? Los mercados de bonos la estiman diario
- La frontera riesgo/incertidumbre es... incierta

### [CAMARA]
"La distincion de Knight crea una falsa dicotomia. En finanzas reales,
TODA probabilidad depende de la informacion que tienes. Es relativa a tu
conocimiento. Veamos que significa esto."

---

## Segmento 2: Probabilidades Relativas — Todo es Condicional (10 min)

### [SLIDE: Notacion fundamental]
- P(A) es una abreviacion. La escritura completa es P(A|I)
- I = toda la informacion de fondo que asumes como cierta
- No existe probabilidad "absoluta" — siempre depende del contexto

### [PIZARRA DIGITAL: Ejemplo del dado]
```
Informacion I₁: "Es un dado de 6 caras"
→ P(6|I₁) = 1/6

Informacion I₂: "Es un dado cargado que favorece al 6"
→ P(6|I₂) = 1/3

Informacion I₃: "Ya lo lance y salio 6" (te lo cuentan)
→ P(6|I₃) = 1

Misma pregunta, diferente informacion, diferente probabilidad
```

### [SLIDE: En finanzas]
- P(Apple sube mañana) — depende de QUE sabes
- Un insider tiene P(Apple|I_insider) ≠ P(Apple|I_publico)
- No es que uno tenga "riesgo" y otro "incertidumbre"
- Ambos tienen probabilidades — condicionadas a su informacion

### [SCREENCAST: Python demo]
```python
# Demostrar como cambia P(evento) con diferente informacion
# prior → dato 1 → dato 2 → posterior final
```

### [CAMARA]
"Esto no es filosofia abstracta. Es la base de todo trading de opciones:
la volatilidad implicita refleja la INFORMACION del mercado, no una
propiedad fisica del activo."

---

## Segmento 3: Frecuentista vs Epistemico — La Batalla de Siglos (12 min)

### [SLIDE: Dos interpretaciones de probabilidad]
| Dimension       | Frecuentista         | Epistemico              |
|-----------------|---------------------|-------------------------|
| Probabilidad es | Frecuencia de largo plazo | Grado de plausibilidad |
| Datos son       | Variables aleatorias | Constantes observadas   |
| Parametros son  | Constantes fijas desconocidas | Variables con distribucion |
| Inferencia usa  | MLE + p-values       | Regla de probabilidad inversa |
| Repetibilidad   | Requiere repeticion  | Aplica a eventos unicos |

### [PIZARRA: El problema del frecuentista con eventos unicos]
```
"¿Cual es la probabilidad de que la Fed suba tasas el 15 de marzo de 2026?"

Frecuentista: "No puedo responder — es un evento unico, no repetible"
Epistemico:   "Dada la inflacion actual, empleo, y comunicados: ~70%"

¿Cual es mas util para un inversor?
```

### [SLIDE: Por que lo epistemico gana en finanzas]
1. Eventos financieros son mayormente unicos (crisis 2008 no se "repite")
2. La informacion es asimetrica y cambiante
3. Necesitas tomar decisiones HOY, no despues de infinitos ensayos
4. Las probabilidades frecuentistas son un caso especial de las epistemicas

### [SCREENCAST: Comparacion lado a lado]
```python
# Mismo dataset, dos enfoques:
# 1. IC frecuentista 95%: "si repito el exp infinitas veces..."
# 2. Intervalo credible 95%: "hay 95% de probabilidad de que el parametro este aqui"
# ¿Cual responde TU pregunta?
```

---

## Segmento 4: Demo Interactiva — Portafolio bajo los Dos Paradigmas (10 min)

### [SCREENCAST: Abrir notebook]
```python
# notebook_ch02_relative_probability.md / .ipynb
# 1. Generar retornos sinteticos con fat tails
# 2. Estimar riesgo con framework frecuentista (VaR clasico)
# 3. Estimar riesgo con framework epistemico (distribucion completa)
# 4. Comparar decisiones de portafolio
```

### [SLIDE: Resultados clave]
- VaR clasico: asume normalidad → subestima riesgo
- Enfoque epistemico: distribucion completa → captura colas pesadas
- Diferencia en asignacion optima: hasta 30% menos en activos riesgosos
- Cuando el modelo "no sabe", lo DICE (intervalos mas anchos)

### [CAMARA]
"Fijate en lo que acaba de pasar. El modelo epistemico no elimino la
incertidumbre — la CUANTIFICO. Cuando tiene poca informacion, sus
intervalos se ensanchan. Cuando tiene mucha informacion, se estrechan.
Eso es exactamente lo que Knight queria pero no logro formalizar."

### [SLIDE: Visualizacion Plotly]
- Mostrar `viz_relative_probability.html` interactivo
- Panel 1: Actualizacion prior → posterior con slider de datos
- Panel 2: IC frecuentista vs intervalo credible bayesiano
- Panel 3: Espectro riesgo-incertidumbre con ejemplos financieros

---

## Segmento 5: Cierre — Por que Esto Importa para tu Dinero (5 min)

### [SLIDE: Resumen conceptual]
1. Toda probabilidad es relativa a la informacion disponible: P(A|I)
2. La distincion riesgo/incertidumbre de Knight es una falsa dicotomia
3. La interpretacion epistemica es estrictamente mas general que la frecuentista
4. Los modelos probabilisticos cuantifican lo que no saben

### [SLIDE: Implicaciones practicas]
- No confies en VaR parametrico → usa distribuciones completas
- Los "cisnes negros" no son impredecibles — son impredecibles para tu MODELO
- Mas informacion = probabilidades mas precisas (Bayes actualiza)
- Menos informacion = intervalos mas anchos (el modelo es honesto)

### [CAMARA]
"La proxima vez que alguien te diga 'eso es incertidumbre, no riesgo',
preguntale: ¿relativa a que informacion? Esa pregunta cambiara como
piensas sobre cada decision financiera que tomes."

### [CTA]
"Ejercicio: toma un activo de tu portafolio. Estima su retorno esperado
con un intervalo — no un numero. ¿Que tan ancho es tu intervalo?
Eso mide tu ignorancia. Comparte tu resultado en la comunidad."

---

## Notas de Produccion
- Insertar cita de Knight (1921) como referencia visual, no texto completo
- Animar la tabla frecuentista vs epistemico como build progresivo
- Mostrar notebook en vivo con VS Code o Google Colab (tema oscuro, fuente 16pt)
- Usar datos sinteticos — NO datos reales con copyright
- source_ref: turn0browsertab744690698
