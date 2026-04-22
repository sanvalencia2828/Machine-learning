# Script de Video -- Modulo 2E: El Problema de la Induccion en Finanzas
# Duracion estimada: 40 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Pavo de Russell (7 min)

### [CAMARA]
"Un pavo es alimentado todos los dias durante 364 dias. Cada dia refuerza
su creencia: 'el granjero me alimenta'. El dia 365 es Accion de Gracias.
Esta historia de Bertrand Russell resume el problema mas profundo de toda
la ciencia, y especialmente de las finanzas: el problema de la induccion."

### [SLIDE: El problema de la induccion (Hume, 1739)]
- Observar que algo ocurrio N veces NO garantiza que ocurrira la vez N+1
- "El sol salio ayer" no DEMUESTRA que saldra manana
- Solo tienes evidencia, nunca certeza
- En finanzas: "el mercado subio los ultimos 10 anos" no significa nada
  sobre el proximo ano

### [SLIDE: Ejemplos financieros del pavo]
- LTCM: 4 anos de ganancias estables -> colapso en semanas
- Madoff: retornos consistentes por decadas -> fraude total
- Lehman Brothers: 158 anos de historia -> quiebra en dias
- "Carry trade": funciona... hasta que no funciona

### [CAMARA]
"Cada vez que alguien dice 'esto siempre ha funcionado', esta siendo
el pavo de Russell. La pregunta no es SI el patron se rompe, sino
CUANDO. Y ahi es donde el ML probabilistico entra."

---

## Segmento 2: Hume, Popper y la Logica de la Induccion (10 min)

### [SLIDE: David Hume (1739)]
- La induccion NO es logicamente valida
- "Todos los cisnes que vi son blancos" no implica "todos los cisnes son blancos"
- La costumbre (habito) nos hace creer en patrones
- En finanzas: confundimos correlacion historica con ley natural

### [SLIDE: Karl Popper (1934) -- Falsacionismo]
- No podemos PROBAR una teoria con datos, solo REFUTARLA
- Un solo cisne negro refuta "todos los cisnes son blancos"
- Buena ciencia: busca refutaciones, no confirmaciones
- En finanzas: un solo crash refuta "los mercados son eficientes"

### [PIZARRA: Asimetria logica fundamental]
```
DEDUCCION (valida):
  Premisa: Todos los mercados eficientes no tienen crashes
  Premisa: El mercado tuvo un crash
  Conclusion: El mercado NO es eficiente  [VALIDO]

INDUCCION (invalida):
  Premisa: El mercado no tuvo crash en 10 anos
  Conclusion: El mercado no tendra crash  [INVALIDO!]
```

### [SLIDE: Nassim Taleb y los cisnes negros]
- "Black Swan" (2007): eventos de alto impacto, baja probabilidad
- El problema no es que no los predijimos -- es que creimos
  que nuestros modelos los excluian
- Los modelos frecuentistas asignan P ~ 0 a eventos raros
  y luego se sorprenden cuando ocurren

### [CAMARA]
"Popper nos enseno que los datos solo pueden refutar, nunca confirmar.
Pero en finanzas necesitamos tomar decisiones HOY con datos del PASADO.
Como lo hacemos? Con grados de plausibilidad, no con certezas."

---

## Segmento 3: El Problema de la Induccion en ML (8 min)

### [SLIDE: Induccion en Machine Learning]
- Todo modelo de ML usa datos pasados para predecir el futuro
- Supuesto implicito: el proceso que genero los datos NO cambio
- Esto se llama "estacionariedad" -- y en finanzas es FALSO

### [SLIDE: Tres formas en que la induccion falla en finanzas]
1. **Cambio de regimen**: la estructura del mercado cambia
   (ej: pre y post-2008, pre y post-COVID)
2. **Reflexividad (Soros)**: los modelos cambian el mercado
   que intentan predecir
3. **Fat tails**: eventos "imposibles" ocurren regularmente
   porque el modelo de probabilidad esta mal

### [SLIDE: Conexion con modulos anteriores]
| Modulo | Concepto | Relacion con induccion |
|--------|----------|----------------------|
| 2B | Probabilidad relativa | P(futuro|pasado) depende de la informacion |
| 2C | Trinidad incertidumbre | Ontologica = induccion falla completamente |
| 2D | No Free Lunch | Sin conocimiento previo, induccion ciega falla |

### [CAMARA]
"El ML convencional ignora el problema de la induccion. Entrena con
datos pasados, asume estacionariedad, y espera lo mejor. PML lo
enfrenta directamente: cuantifica QUE TAN CONFIABLE es cada
extrapolacion del pasado al futuro."

---

## Segmento 4: Demo -- Cuantificar la Fragilidad Inductiva (10 min)

### [SCREENCAST: Abrir notebook]
```python
# notebook_ch02e_induction_problem.md
# 1. Simular "pavo de Russell": patron estable + colapso
# 2. Medir confianza acumulada del modelo vs realidad
# 3. Comparar modelo frecuentista (no aprende) vs bayesiano (actualiza)
# 4. Ventana deslizante: como detectar cambio de regimen
# 5. Stress testing: que pasa si la induccion falla?
```

### [SLIDE: Resultados clave]
- Modelo frecuentista: confianza CRECE con mas datos (pavo mas gordo)
- Modelo bayesiano: confianza se estabiliza Y se puede resetear
- Ventana deslizante: detecta cambio de regimen ~30 dias despues
- Stress test: cuantifica perdidas bajo falla inductiva

### [CAMARA]
"El modelo bayesiano no es inmune a la induccion -- nadie lo es. Pero
tiene dos ventajas: puede expresar incertidumbre sobre sus propios
supuestos, y puede actualizar rapidamente cuando llegan datos que
contradicen el patron."

---

## Segmento 5: Cierre -- Como PML Navega la Induccion (5 min)

### [SLIDE: Estrategias contra la trampa inductiva]
1. **Priors escepticos**: no confiar ciegamente en datos pasados
2. **Distribucion predictiva**: el modelo propaga su incertidumbre
3. **Actualizacion continua**: nuevos datos actualizan creencias
4. **Stress testing**: simular escenarios donde la induccion falla
5. **Humildad cuantificada**: intervalos que se ENSANCHAN con incertidumbre

### [SLIDE: Resumen conceptual]
| Enfoque | Ante datos consistentes | Ante cisne negro |
|---------|------------------------|------------------|
| Frecuentista | Confianza crece sin limite | Colapso total |
| Inductivista ingenuo | "Siempre funciona" | "Imposible" |
| PML/Bayesiano | Confianza acotada por priors | Actualiza y se adapta |

### [CAMARA]
"El problema de la induccion no tiene solucion -- Hume tenia razon.
Pero tiene una estrategia: en vez de pretender que el pasado garantiza
el futuro, CUANTIFICA que tan fragil es tu creencia. Eso es exactamente
lo que hace el ML probabilistico."

### [CTA]
"Ejercicio: piensa en una 'verdad' de tu portafolio que nunca has
cuestionado. 'Las acciones siempre suben a largo plazo.' 'La
diversificacion siempre protege.' Ahora preguntate: que evidencia
la REFUTARIA? Si no puedes responder, eres el pavo."

---

## Notas de Produccion
- Ilustrar el pavo de Russell con animacion simple
- Mostrar timeline visual: LTCM, Lehman, COVID como "pavos"
- Codigo en vivo: ventana deslizante detectando cambio de regimen
- Tono: provocativo pero riguroso, no alarmista
- source_ref: turn0browsertab744690698
