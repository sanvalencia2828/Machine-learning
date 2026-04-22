# Ejercicios Practicos -- Modulo 6B: Caso ZYX -- MLE con Pocos Datos
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: MLE vs PML con 2, 3, 5, 10 Datos

**Nivel:** Basico
**Tiempo estimado:** 20 min

### Enunciado
Genera secuencias de beats (100% beats): n=2, 3, 5, 10.
Para cada n, calcula MLE y PML con prior Beta(1,1).
1. MLE es siempre 100%? PML converge a 100%?
2. Con que n la diferencia MLE-PML es < 5%?
3. Grafica media posterior vs n.

---

## Ejercicio 2: El Miss que Cambia Todo

**Nivel:** Intermedio
**Tiempo estimado:** 20 min

### Enunciado
Empresa con 5/5 beats. Luego un miss (Q6).
1. Calcula MLE antes y despues del miss
2. Calcula PML antes y despues (prior Beta(1,1))
3. Cual framework tiene el cambio mas brusco?
4. Si eres portfolio manager, cual preferiras?

---

## Ejercicio 3: Startup con 4 Trimestres

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Startup IPO reciente: 4 trimestres, 3 beats, 1 miss.
1. MLE: p = 3/4 = 75%
2. PML con prior Beta(1,1): posterior Beta(4, 2), media = 67%
3. PML con prior Beta(2,3) (esceptico de startups): media = ?
4. Calcula distribucion predictiva: P(beat proximo trimestre)?
5. Que prior elegirias para una startup sin track record?

---

## Ejercicio 4: Grid Approximation para ZYX

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Implementa grid approximation para el caso ZYX (3/3 beats):
1. Grilla: 1000 puntos en [0, 1]
2. Prior: Beta(2, 2)
3. Likelihood: Binomial(3, 3, p)
4. Posterior: prior * likelihood, normalizado
5. Compara con analitico Beta(5, 2)
6. Calcula P(p > 0.8) desde la grilla

---

## Ejercicio 5: Mini-Proyecto -- Evalua 5 Empresas

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
5 empresas con historiales de earnings beats:
- A: 3/3 beats (nueva)
- B: 7/10 beats (establecida)
- C: 2/2 beats (muy nueva)
- D: 15/20 beats (madura)
- E: 4/5 beats (crecimiento)

Para cada una:
1. Calcula MLE y PML (prior Beta(2,2))
2. Ordena por P(beat proximo trimestre) con PML
3. Compara con el ranking de MLE
4. Cual ranking usarias para asignar capital? Por que?

---

## Ejercicio 6 (Bonus): MLE Cero y el Problema Inverso

**Nivel:** Avanzado
**Tiempo estimado:** 20 min

### Enunciado
Empresa "RiskyCorp": 0 beats en 3 trimestres (miss total).
1. MLE dice p = 0/3 = 0%. Nunca volvera a beat?
2. PML con Beta(1,1): posterior Beta(1, 4), media = 20%
3. PML con Beta(2,2): posterior Beta(2, 5), media = 29%
4. Que tan diferente es el problema p=0 vs p=1?
5. Cual es mas peligroso para un inversor: MLE=100% o MLE=0%?
