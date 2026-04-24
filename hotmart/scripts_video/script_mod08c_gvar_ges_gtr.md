# Script de Video -- Modulo 8C: GVaR, GES y GTR -- Riesgo Generativo
# Duracion estimada: 45 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- 3 Numeros que Reemplazan Toda la Gestion de Riesgo (7 min)

### [CAMARA]
"Un analista de riesgo tradicional te dice: 'VaR de Apple al 95% es
-2.5%'. Eso suena preciso pero esconde 3 problemas: ignora que pasa
MAS ALLA del -2.5%, asume que los retornos son normales, y no propaga
la incertidumbre del modelo. Hoy calculamos 3 metricas que resuelven
todo esto: GVaR, GES y GTR -- las versiones GENERATIVAS de VaR, ES
y tail risk, calculadas directamente desde distribuciones predictivas."

### [SLIDE: 3 metricas generativas]
```
GVaR (Generative VaR):
  Percentil alpha de la posterior predictive
  Ejemplo Apple: GVaR 95% = -3.79%

GES (Generative Expected Shortfall):
  Media de retornos PEORES que GVaR
  Ejemplo Apple: GES 95% = -4.50%

GTR (Generative Tail Risk):
  Retorno del PEOR caso en la predictive
  Ejemplo Apple: GTR = -10.25%
```

---

## Segmento 2: De VaR Clasico a GVaR (10 min)

### [PIZARRA: VaR clasico vs GVaR]
```
VaR clasico:
  VaR = mu + z_alpha * sigma  (asume Normal)
  o VaR = percentil(datos_historicos, alpha)
  Problemas: asume normalidad, usa datos pasados, no propaga incertidumbre

GVaR:
  1. Generar N muestras de posterior predictive
     (cada muestra usa parametros DIFERENTES del posterior)
  2. GVaR = percentil(muestras, alpha)
  Ventaja: propaga incertidumbre parametrica Y aleatoria
```

### [SCREENCAST]
```python
# Posterior predictive para Apple:
# Para cada (alpha_i, beta_i, sigma_i, nu_i) del posterior:
#   r_i = alpha_i + beta_i * r_mkt_sim + sigma_i * t(nu_i)
# GVaR = percentile(r_i, 5)
```

---

## Segmento 3: GES -- Lo que VaR Esconde (10 min)

### [SLIDE: VaR vs ES]
```
VaR dice: "Con 95% de confianza, no perderas mas de X%"
  -> Pero que pasa el otro 5%??? VaR calla.

ES dice: "Si caes mas alla del VaR, perderas en promedio Y%"
  -> Captura la severidad de las PEORES perdidas.

GES: ES pero desde la posterior predictive
  -> Propaga toda la incertidumbre del modelo
```

### [SLIDE: Ejemplo Apple]
```
GVaR 95%: -3.79%  (1 en 20 dias sera PEOR que esto)
GES 95%:  -4.50%  (si es un dia malo, perderas -4.50% en promedio)
Gap:       0.71%  (la "cola" mas alla del GVaR)

Si tu capital = $1M:
  GVaR dice: podrias perder hasta $37,900 en un dia malo
  GES dice: si es un dia REALMENTE malo, perderas $45,000
```

---

## Segmento 4: GTR -- El Peor Caso Generativo (10 min)

### [SLIDE: GTR]
```
GTR = minimo de la posterior predictive

No es un percentil -- es el PEOR retorno simulado
Depende del numero de simulaciones y de las colas

Ejemplo Apple:
  Con 50,000 simulaciones: GTR = -10.25%
  Esto es un retorno que PODRIA ocurrir bajo el modelo
  No es "imposible" -- es el escenario de cola extrema

Uso practico:
  Si tu portafolio sobrevive GTR: estas preparado
  Si no: necesitas reducir exposicion o cubrir
```

### [SCREENCAST: Calcular GVaR, GES, GTR]
```python
# 50,000 retornos desde posterior predictive
posterior_returns = simular_posterior_predictive(50000)

gvar_95 = np.percentile(posterior_returns, 5)
ges_95 = posterior_returns[posterior_returns <= gvar_95].mean()
gtr = posterior_returns.min()

print(f"GVaR 95%: {gvar_95:.2%}")
print(f"GES 95%:  {ges_95:.2%}")
print(f"GTR:      {gtr:.2%}")
```

---

## Segmento 5: Cierre (8 min)

### [SLIDE: Comparacion final]
| Metrica | Clasica | Generativa | Ventaja PML |
|---------|---------|-----------|-------------|
| VaR | Percentil historico | GVaR (posterior pred) | Propaga incertidumbre |
| ES | Media condicional | GES (posterior pred) | Captura fat tails reales |
| Tail risk | Peor historico | GTR (min predictive) | Escenarios no vistos |

### [CTA]
"Calcula GVaR, GES y GTR para tu portafolio. Si GTR te arruina,
necesitas mas cobertura. Si GES es 2x tu GVaR, tienes fat tails
serias. Estos 3 numeros te dicen mas que 100 backtests."

---

## Notas de Produccion
- Histograma con GVaR, GES, GTR como lineas verticales
- Zoom en la cola izquierda
- Tabla resumen Apple: 3 metricas con contexto en dolares
- source_ref: turn0browsertab744690698
