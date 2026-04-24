# Ejercicios Practicos -- Modulo 8C: GVaR, GES y GTR
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: Calcular GVaR, GES, GTR de Cero
**Nivel:** Basico  |  **Tiempo:** 20 min

Genera 50,000 retornos Student-t(nu=4, mu=0.0005, sigma=0.015).
Calcula GVaR 95%, GES 95% y GTR. Si capital=$500K, cuanto puedes
perder en cada escenario?

---

## Ejercicio 2: VaR Normal vs GVaR Fat-Tailed
**Nivel:** Intermedio  |  **Tiempo:** 25 min

Calcula VaR asumiendo Normal y GVaR con Student-t(4).
Cuanto subestima el VaR Normal? Grafica ambos sobre el histograma.

---

## Ejercicio 3: GES para Diferentes Niveles
**Nivel:** Intermedio  |  **Tiempo:** 25 min

Calcula GVaR y GES para niveles 90%, 95%, 97.5%, 99%.
Grafica el ratio GES/GVaR vs nivel. Es constante o crece?

---

## Ejercicio 4: Stress Test con GTR
**Nivel:** Avanzado  |  **Tiempo:** 30 min

Portafolio de $2M. Calcula GTR. Si GTR arruina el portafolio
(perdida > 50%), cuanto hedge necesitas? Implementa con put sintetico.

---

## Ejercicio 5: 3 Metricas para 5 Activos
**Nivel:** Avanzado  |  **Tiempo:** 35 min

Genera posterior predictive para 5 activos con diferentes nu (3,4,5,8,30).
Calcula GVaR/GES/GTR para cada uno. Cual es mas riesgoso? Ranking.

---

## Ejercicio 6: GVaR Condicional (Regimenes)
**Nivel:** Avanzado  |  **Tiempo:** 30 min

Calcula GVaR separado para periodos de alta y baja volatilidad.
Diferencia? Deberia tu limite de riesgo cambiar con el regimen?
