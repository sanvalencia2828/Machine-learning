# Ejercicios Practicos -- Modulo 8B: Loss Functions y Volatility Drag
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Construye tu Loss Matrix

**Nivel:** Basico  |  **Tiempo:** 20 min

Define loss matrix para: comprar accion tech (3 estados: sube 20%,
lateral, cae 30%). 3 decisiones: comprar, no comprar, comprar con stop-loss.
Calcula E[L] para P(sube)=40%, P(lateral)=35%, P(cae)=25%.

---

## Ejercicio 2: VaR vs ES en 2 Portafolios

**Nivel:** Intermedio  |  **Tiempo:** 25 min

Genera 50,000 retornos Normal y Student-t(3) con misma media y std.
Calcula VaR y ES al 95% y 99%. Cual portafolio es mas peligroso
segun VaR? Y segun ES? Por que ES es mas informativo?

---

## Ejercicio 3: Volatility Drag Cuantitativo

**Nivel:** Intermedio  |  **Tiempo:** 25 min

Para sigma = 1%, 2%, 3%, 5%, 10% diario (media=0), simula 1000
trayectorias de 252 dias. Grafica riqueza mediana final vs sigma.
Verifica que drag ~ sigma^2/2 * T.

---

## Ejercicio 4: Decision Optima con Posterior Predictive

**Nivel:** Avanzado  |  **Tiempo:** 30 min

Tienes posterior Beta(5, 25) para P(default) (Modulo 5B).
Loss matrix: invertir (gana $50K si no default, pierde $500K si default).
No invertir (gana $0). Cubrir (pierde $20K si no default, pierde $50K si default).
1. Calcula E[L] para cada decision usando 50,000 muestras del posterior
2. Cual es la decision optima?
3. Como cambia si el prior es mas pesimista?

---

## Ejercicio 5: Path Dependence con Retiros

**Nivel:** Avanzado  |  **Tiempo:** 30 min

Portafolio de $100K con retiro mensual de $1K.
Retornos mensuales: Student-t(4, 0.008, 0.04).
1. Simula 1000 trayectorias de 10 anos
2. P(ruina)? (riqueza < $10K)
3. Mediana de riqueza a los 10 anos?
4. Compara con el mismo sin retiros

---

## Ejercicio 6: Loss Function Asimetrica

**Nivel:** Avanzado  |  **Tiempo:** 25 min

En finanzas, perder $1 duele mas que ganar $1.
Implementa loss function asimetrica: L = -2 * min(r, 0) + max(r, 0).
1. Calcula E[L] para retornos Normal vs Student-t
2. Cual distribucion tiene mayor expected loss asimetrica?
3. Conecta con por que la preservacion de capital es prioridad #1
