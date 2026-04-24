# Script de Video -- Modulo 8B: Loss Functions, Volatility Drag y Expected Loss
# Duracion estimada: 50 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- Ganar 10% y Perder 10% NO es Empatar (7 min)

### [CAMARA]
"Si tu portafolio sube 10% y luego baja 10%, tu retorno NO es cero.
Es -1%. Y si sube 50% y baja 50%: -25%. Esto se llama volatility drag
y es la razon por la cual la volatilidad destruye riqueza incluso cuando
los retornos PROMEDIAN cero. Hoy vamos a construir un framework completo
para tomar decisiones que protegen tu capital: loss functions, expected
loss, y la preservacion del capital como prioridad numero uno."

### [SLIDE: El plan]
1. **Loss functions**: cuantificar el costo de cada decision
2. **Expected loss**: E[L] = sum P(estado) * L(decision, estado)
3. **VaR y ES desde distribuciones predictivas**
4. **Volatility drag**: por que la varianza destruye riqueza
5. **Capital preservation**: el primer mandamiento del inversor

---

## Segmento 2: Loss Functions y Expected Loss (12 min)

### [PIZARRA: Framework de decisiones]
```
3 componentes:
  1. Estados posibles: {default, no default}
  2. Decisiones posibles: R1 (invertir), R2 (no invertir), R3 (cubrir)
  3. Loss function: L(decision, estado) = perdida si tomas D y ocurre S

Ejemplo bonos corporativos:
                Default     No Default
  R1 (invertir)   -100K       +15K
  R2 (no invertir)   0K         0K
  R3 (cubrir)       -5K        +10K

Expected Loss de R1:
  E[L(R1)] = P(default) * (-100K) + P(no default) * (+15K)
  Si P(default) = 20%: E[L(R1)] = -20K + 12K = -8K
  Si P(default) = 10%: E[L(R1)] = -10K + 13.5K = +3.5K

La decision OPTIMA depende de P(default)
Y esa P viene del posterior predictive (Modulo 5B)
```

### [CAMARA]
"La loss function convierte distribuciones en decisiones. Sin ella,
tienes un modelo bonito pero no puedes actuar. Con ella, cada
distribucion predictiva se traduce en una accion concreta."

---

## Segmento 3: VaR y ES desde Predictive Distributions (10 min)

### [SCREENCAST]
```python
# Diferencia clave:
# VaR clasico: percentil de retornos HISTORICOS
# VaR predictivo: percentil de POSTERIOR PREDICTIVE

# VaR te dice: "el peor caso al 95% es -X%"
# ES te dice: "SI caes mas alla del VaR, pierdes en promedio -Y%"
# ES es estrictamente mas informativo que VaR
```

### [SLIDE: Por que ES > VaR]
- VaR ignora lo que pasa MAS ALLA del umbral
- Dos portafolios con mismo VaR pueden tener ES muy diferente
- ES es "coherente" (propiedad matematica): VaR no lo es
- Reguladores (Basilea III.5) estan migrando de VaR a ES

---

## Segmento 4: Volatility Drag y Preservacion de Capital (13 min)

### [PIZARRA: Volatility drag]
```
Retorno aritmetico: r_a = (r1 + r2) / 2
Retorno geometrico: r_g = sqrt((1+r1)*(1+r2)) - 1

Ejemplo:
  +10%, -10%: r_a = 0%, r_g = sqrt(1.1*0.9)-1 = -0.5%
  +50%, -50%: r_a = 0%, r_g = sqrt(1.5*0.5)-1 = -13.4%
  +100%,-100%: r_a = 0%, r_g = ruina total

Formula: r_g ~ r_a - sigma^2/2
  El "drag" es proporcional a sigma^2
  Mayor volatilidad = mayor destruccion de riqueza
```

### [SCREENCAST: Demo volatility drag]
```python
# 1. Generar 1000 secuencias de retornos con media 0 y sigma variable
# 2. Calcular riqueza final para sigma = 5%, 10%, 20%, 40%
# 3. Resultado: TODAS las medias de retorno son 0
#    pero la riqueza final baja con sigma^2
# 4. El ORDEN de los retornos importa (path dependence)
```

### [CAMARA]
"Volatility drag es la razon por la que la preservacion del capital
es el PRIMER mandamiento de la inversion. No es conservadurismo --
es matematica. Cada 1% de perdida requiere 1.01% de ganancia para
recuperar. Pero cada 50% de perdida requiere 100% para recuperar.
La asimetria es brutal."

---

## Segmento 5: Cierre -- El Framework Completo (8 min)

### [SLIDE: Pipeline de decision probabilistica]
```
1. Modelo PML (Modulos 5-7) -> Posterior Predictive Distribution
2. Loss function: definir costos de cada decision-estado
3. Expected loss: E[L] = integral L(d,s) * P(s|datos) ds
4. Decision optima: d* = argmin E[L(d)]
5. Risk management: GVaR, GES, Kelly (Modulo 8)
6. Capital preservation: reducir volatility drag via Kelly
```

### [CTA]
"Define una loss function para una decision de inversion real.
Calcula expected loss usando tu posterior predictive.
Cual decision minimiza E[L]?"

---

## Notas de Produccion
- Tabla de decisiones R1/R2/R3 como build progresivo
- Animar volatility drag: dos trayectorias con mismo retorno promedio
- VaR vs ES como areas en histograma
- source_ref: turn0browsertab744690698
