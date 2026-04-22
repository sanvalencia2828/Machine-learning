# Script de Video -- Modulo 2D: Bias-Variance Tradeoff y Teoremas No Free Lunch
# Duracion estimada: 45 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- El Modelo Perfecto No Existe (7 min)

### [CAMARA]
"Imagina que construyes un modelo que predice perfectamente los retornos
pasados del S&P 500. Lo pones en produccion y... pierde dinero. Por que?
Porque memorizaste el pasado en vez de aprender los patrones. Hoy vamos
a entender el dilema fundamental de TODO modelo: el tradeoff entre
simplificar demasiado y complicar demasiado."

### [SLIDE: El dilema fundamental]
- Modelo muy simple -> no captura la realidad (BIAS alto)
- Modelo muy complejo -> memoriza el ruido (VARIANCE alta)
- No existe un punto optimo universal
- Y ademas: no existe un algoritmo que sea el mejor para todo

### [SLIDE: Dos teoremas que cambian todo]
1. **Bias-Variance Decomposition**: Error = Bias^2 + Variance + Ruido
2. **No Free Lunch (Wolpert 1996)**: sin conocimiento previo, todos los
   algoritmos rinden igual en promedio

### [CAMARA]
"Estos dos resultados matematicos tienen consecuencias devastadoras para
quienes creen que pueden encontrar 'el mejor modelo' sin entender finanzas.
Veamos por que."

---

## Segmento 2: Bias-Variance Tradeoff -- La Teoria (10 min)

### [PIZARRA DIGITAL: Descomposicion del error]
```
Error_total = Bias^2 + Varianza + Ruido_irreducible

Bias = E[f_hat(x)] - f(x)
  -> Error sistematico: tu modelo es demasiado simple
  -> Ejemplo: usar una linea recta para modelar retornos no lineales

Varianza = E[(f_hat(x) - E[f_hat(x)])^2]
  -> Sensibilidad a los datos de entrenamiento
  -> Ejemplo: un arbol de decision profundo cambia radicalmente
     con cada muestra nueva

Ruido = Var(epsilon)
  -> Irreducible: la realidad es ruidosa
  -> En finanzas: microestructura, eventos aleatorios, HFT
```

### [SLIDE: Espectro de modelos financieros]
| Modelo | Bias | Varianza | Ejemplo |
|--------|------|----------|---------|
| Media historica | Alto | Bajo | "S&P sube 10% al ano" |
| Regresion lineal (CAPM) | Medio | Bajo | beta * mercado |
| Random Forest | Bajo | Alto | 1000 arboles sobre features |
| Red neuronal profunda | Muy bajo | Muy alto | LSTM con 10M parametros |

### [CAMARA]
"En finanzas, el ruido irreducible es ENORME. Los mercados son ruidosos
por naturaleza. Eso significa que la varianza te mata mas rapido que el
bias. Por eso modelos simples con buen conocimiento previo suelen
superar a redes neuronales complejas en prediccion financiera."

---

## Segmento 3: No Free Lunch -- La Demostracion (10 min)

### [SLIDE: Teorema NFL (Wolpert & Macready 1997)]
- "Para cualquier par de algoritmos A y B, si A supera a B en un
  conjunto de problemas, entonces B supera a A en otro conjunto"
- En promedio sobre TODOS los problemas posibles: rendimiento identico
- No existe el 'mejor algoritmo' universal

### [PIZARRA: Implicaciones para finanzas]
```
Sin NFL:
  "Usa XGBoost para todo" o "Las redes neuronales siempre ganan"

Con NFL:
  "XGBoost es mejor PARA ESTE TIPO de problema financiero
   DADO lo que sabemos sobre la estructura de los datos"

La clave: conocimiento del dominio selecciona el algoritmo
```

### [SLIDE: Por que NFL importa para ML en finanzas]
1. No puedes hacer AutoML ciego en datos financieros
2. Los datos financieros tienen propiedades especificas:
   - No estacionariedad
   - Baja relacion senal/ruido
   - Colas pesadas
   - Dependencia temporal
3. Sin integrar estas propiedades -> rendimiento = azar
4. PML integra conocimiento via priors = ventaja sobre ML ciego

### [SCREENCAST: Analogia interactiva]
```python
# Demostrar NFL: 3 algoritmos en 3 problemas diferentes
# Ningun algoritmo gana en todos
# El que "sabe" sobre el problema gana
```

### [CAMARA]
"NFL no dice que no puedes construir buenos modelos. Dice que no puedes
hacerlo SIN conocimiento del dominio. En finanzas, eso significa que un
quant que entiende mercados siempre superara a un data scientist que
solo sabe optimizar hiperparametros."

---

## Segmento 4: Demo Interactiva -- Bias-Variance en Accion (12 min)

### [SCREENCAST: Abrir notebook]
```python
# notebook_ch02d_bias_variance_nfl.md / .ipynb
# 1. Generar datos sinteticos con patron no lineal + ruido
# 2. Ajustar polinomios de grado 1, 3, 5, 10, 20
# 3. Visualizar underfitting vs overfitting
# 4. Calcular bias^2, varianza y error total para cada grado
# 5. Demostrar NFL con 3 algoritmos en 3 problemas
```

### [SLIDE: Resultados clave]
- Grado 1 (lineal): bias alto, varianza baja, error moderado
- Grado 3-5: bias moderado, varianza moderada, ERROR MINIMO
- Grado 20: bias ~0, varianza altisima, error explota
- Con regularizacion (priors): el optimo se desplaza hacia modelos
  mas simples -- exactamente lo que hace PML

### [SLIDE: Visualizacion Plotly]
- Panel 1: Curva de complejidad (bias^2, varianza, error total)
- Panel 2: Polinomios ajustados a diferentes grados
- Panel 3: NFL -- rendimiento de 3 algoritmos en 3 problemas

### [CAMARA]
"Mira lo que pasa con el polinomio de grado 20: ajusta perfecto los
datos de entrenamiento pero falla catastroficamente en datos nuevos.
Esto es EXACTAMENTE lo que pasa cuando haces backtesting excesivo
de una estrategia de trading."

---

## Segmento 5: Cierre -- Conexion con PML (6 min)

### [SLIDE: Como PML resuelve bias-variance]
1. **Priors** = regularizacion informada por conocimiento del dominio
2. Los priors REDUCEN la varianza sin aumentar demasiado el bias
3. Equivalente a decir: "antes de ver datos, se algo sobre finanzas"
4. NFL dice que necesitas conocimiento previo -> PML lo formaliza

### [SLIDE: Resumen conceptual]
| Concepto | Implicacion practica |
|----------|---------------------|
| Bias alto | Tu modelo es demasiado simple. Anade features o no-linealidad |
| Varianza alta | Tu modelo memoriza ruido. Usa regularizacion o priors |
| NFL | No hay atajo: debes entender el dominio financiero |
| PML | Integra conocimiento via priors para navegar el tradeoff |

### [SLIDE: Conexion con el resto del curso]
- Modulo 5: Priors como regularizacion bayesiana
- Modulo 6: MLE = varianza maxima (sin priors)
- Modulo 7: Ensambles generativos con priors informativos
- Modulo 8: Kelly criterion navega el tradeoff en asignacion de capital

### [CAMARA]
"El bias-variance tradeoff no es un problema que resuelves una vez.
Es una tension que manejas constantemente. Y NFL te recuerda que la
unica ventaja real es el conocimiento: sobre los mercados, sobre los
datos, sobre las limitaciones de tu modelo."

### [CTA]
"Ejercicio: toma tu modelo favorito de ML. Argumenta donde cae en el
espectro bias-varianza. Que conocimiento financiero usarias para
moverlo al punto optimo? Comparte en la comunidad."

---

## Notas de Produccion
- Animar la curva bias-variance como build progresivo
- Mostrar overfitting/underfitting con graficos en vivo
- Usar datos sinteticos -- NO datos reales con copyright
- Citar Wolpert (1996) y Wolpert & Macready (1997) como referencia
- source_ref: turn0browsertab744690698
