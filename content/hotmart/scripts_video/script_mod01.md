# Script de Video — Modulo 1: La Necesidad del ML Probabilistico
# Duracion estimada: 45 minutos (4 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho + Contexto (8 min)

### [CAMARA]
"Imagina que eres Newton, el genio que descifro las leyes de la gravedad.
Inviertes tu fortuna en la South Sea Company... y lo pierdes todo.
Newton dijo: 'Puedo calcular el movimiento de las estrellas, pero no la locura
de los hombres.' Hoy vamos a entender por que tenia razon."

### [SLIDE: Finanzas vs Fisica]
- Fisica: predice movimiento de la luna con precision de milimetros
- Finanzas: no puede explicar movimientos diarios del mercado
- Por que? Personas son complejas, emocionales, creativas, con libre albedrio
- Reaccionan unas a otras de formas impredecibles
- Participantes del mercado lucran al vencer o manipular los sistemas

### [SLIDE: Nobel de Economia]
- Alfred Nobel NO creo un premio de economia
- Sveriges Riksbank lo creo en 1968 y paga a la Fundacion Nobel para administrarlo
- Friedrich Hayek (1974): "El Nobel confiere una autoridad que en economia nadie
  deberia poseer"

### [TRANSICION]
"Pero si las finanzas no son fisica, por que seguimos usando los mismos modelos?
Veamos que pasa cuando lo hacemos..."

---

## Segmento 2: La Trifecta de Errores (12 min)

### [SLIDE: Tres tipos de errores]
1. Errores de especificacion del modelo
2. Errores en estimacion de parametros
3. Errores por no adaptarse a cambios estructurales

### [SCREENCAST: codigo Python — tasas de credito]
"Vamos a hacer un ejemplo practico. Imagina que quieres estimar la tasa de
tu tarjeta de credito dentro de 12 meses..."

```python
# Abrir src/binomial_credit_rate_timevary.py
# Ejecutar y mostrar graficos
# Explicar como la distribucion cambia con diferentes probabilidades
```

### [SLIDE: LTCM — El Desastre]
- Fundado en 1994 por Scholes y Merton (futuros "Nobel")
- Leverage extremo basado en confianza ciega en modelos
- Rusia defaultea en 1998 — evento no anticipado por modelos
- Fed + bancos rescatan LTCM para evitar crisis global
- Leccion: leverage magnifica perdidas tanto como ganancias

### [SLIDE: Renaissance Technologies — El Contraste]
- Contrata fisicos, matematicos, informaticos — NO financieros
- Usa teoria de informacion, data science, ML
- El hedge fund mas exitoso de la historia
- Leccion: critica de teorias financieras puesta en practica

---

## Segmento 3: El Framework Probabilistico (15 min)

### [SLIDE: 5 Caracteristicas del ML Probabilistico]
1. Distribuciones de probabilidad (no estimaciones puntuales)
2. Integracion de conocimiento previo
3. Inferencia de parametros (regla inversa)
4. Ensambles generativos (simula datos nuevos)
5. Conciencia de incertidumbre (sabe lo que no sabe)

### [SCREENCAST: demostrar cada caracteristica]
- Mostrar como un punto vs distribucion cambia la decision
- Ejemplo: tasa de credito como distribucion, no como 12.5%

### [SLIDE: AI vs ML vs Probabilistic ML]
- IA: campo general (incluye sistemas expertos + ML)
- ML: modelos descubiertos por computadoras desde datos
- PML: ML generativo que cuantifica incertidumbre
- Comparar con ChatGPT: "alucinaciones confiantes" vs "dudas cuantificadas"

---

## Segmento 4: Cierre + Preview (5 min)

### [CAMARA]
"Hoy aprendimos que todos los modelos financieros estan mal, pero algunos
son utiles. La clave es cuantificar QUE TAN MAL estan, no pretender que
son perfectos."

### [SLIDE: Resumen]
- Las finanzas tratan con personas, no particulas
- Tres tipos de errores afectan TODOS los modelos
- El ML probabilistico trata incertidumbres como features, no bugs
- Distribuciones de probabilidad > estimaciones puntuales

### [SLIDE: Preview Modulo 2]
"En el siguiente modulo, usaremos el famoso problema de Monty Hall para
explorar los tres tipos de incertidumbre y derivar la regla de probabilidad
inversa — el fundamento matematico de todo lo que haremos en este curso."

### [CTA]
"Si te parecio util, comparte con un colega que trabaje en finanzas.
Nos vemos en el Modulo 2."

---

## Notas de Produccion
- Insertar grafico LTCM (Figura 1-1 del libro) como referencia visual
- Animar la trifecta de errores como diagrama
- Mostrar codigo en vivo con VS Code (tema oscuro, fuente 16pt)
- Usar datos reales de Yahoo Finance para el ejemplo de tasas
