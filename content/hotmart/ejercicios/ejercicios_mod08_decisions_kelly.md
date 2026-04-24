# Ejercicios Practicos -- Modulo 8: Decisiones Probabilisticas y Kelly
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Ergodicidad -- El Juego Enganoso

**Nivel:** Basico  |  **Tiempo:** 20 min

Simula el juego +50%/-40% (p=0.5) con 10,000 jugadores, 100 rondas.
1. E[R] por ronda? Media del ensamble final?
2. Mediana final? P(perder dinero)?
3. Por que E[R]>0 pero la mayoria pierde?

---

## Ejercicio 2: GVaR vs VaR Clasico

**Nivel:** Intermedio  |  **Tiempo:** 25 min

Genera 50,000 retornos desde posterior predictive (Student-t con incertidumbre en nu).
1. VaR 95% frecuentista (asume Normal)
2. GVaR 95% (percentil directo de posterior predictive)
3. GES 95%, GTR (P(r < -5%))
4. Cuanto subestima el VaR Normal?

---

## Ejercicio 3: Kelly Basico -- Moneda Sesgada

**Nivel:** Intermedio  |  **Tiempo:** 20 min

Moneda sesgada: P(cara)=0.6, ganas +100% (2x), pierdes -100% (0x).
1. f* de Kelly = (p*b - q) / b = ?
2. Simula 1000 jugadores con f*, f*/2, 2*f*
3. Cual estrategia sobrevive mejor?

---

## Ejercicio 4: Kelly con Distribucion Continua

**Nivel:** Avanzado  |  **Tiempo:** 30 min

Retornos diarios Student-t(nu=4, mu=0.0005, sigma=0.015).
1. Para f = 0.1, 0.3, 0.5, 0.7, 1.0, 1.5: calcula E[log(1+f*R)]
2. Grafica la curva. Donde esta f*?
3. Simula 500 trayectorias de 252 dias con f* y con f=1
4. Media y mediana final. Cual es mejor?

---

## Ejercicio 5: Kelly vs Markowitz

**Nivel:** Avanzado  |  **Tiempo:** 35 min

2 activos: Activo A (mu=0.08%, sigma=1.2%) y Activo B (mu=0.04%, sigma=0.8%).
Correlacion = 0.3.
1. Portafolio Markowitz (min varianza para retorno objetivo)
2. Portafolio Kelly (max E[log(W)])
3. Simula 1000 trayectorias de 1 ano para ambos
4. Cual tiene menor P(perder > 20%)?
5. Cual tiene mayor mediana final?

---

## Ejercicio 6: Mini-Proyecto -- Portafolio Completo

**Nivel:** Avanzado  |  **Tiempo:** 40 min

Construye un portafolio PML completo:
1. Genera posterior predictive para 3 activos
2. Calcula GVaR, GES para cada activo
3. Calcula Kelly f* para cada activo
4. Combina en portafolio con restriccion sum(f) <= 1
5. Simula 252 dias. Reporta: media, mediana, P(ruina), drawdown max
