# Script de Video -- Modulo 7B: PLE Aplicado -- Jensen's Alpha y PyMC/ArviZ
# Duracion estimada: 55 minutos (5 segmentos)
# source_ref: turn0browsertab744690698

---

## Segmento 1: Gancho -- 4 Preguntas, 1 Modelo (8 min)

### [CAMARA]
"Con un solo modelo probabilistico, puedes responder 4 preguntas
que los fondos de inversion pagan millones por responder: tiene
este gestor alpha real? Cuanto beta necesito para cubrir mi posicion?
Cual es el costo de capital de esta empresa? Y es este fondo realmente
market neutral? Hoy construimos ese modelo con PyMC y ArviZ."

### [SLIDE: 4 aplicaciones del Market Model PLE]
1. **Jensen's alpha**: P(alpha > 0) -- tiene el gestor skill real?
2. **Cross-hedging**: distribucion de beta optimo para cobertura
3. **Market neutral**: P(|beta| < 0.1) -- es realmente neutral?
4. **Cost of equity**: CAPM probabilistico, r_e con incertidumbre

---

## Segmento 2: Formulacion Completa del PLE (12 min)

### [PIZARRA: MLE vs PLE]
```
MLE (OLS):
  Parametros son CONSTANTES desconocidas
  Datos son VARIABLES aleatorias
  Resultado: UN punto (alpha_hat, beta_hat, sigma_hat)

PLE (PyMC):
  Parametros son VARIABLES con distribucion
  Datos son CONSTANTES observadas
  Resultado: MILES de (alpha_i, beta_i, sigma_i)
```

### [SLIDE: Modelo PyMC completo]
```python
with pm.Model() as ple_model:
    # Priors informativos
    alpha = pm.Normal("alpha", mu=0, sigma=0.001)   # Esceptico sobre alpha
    beta = pm.Normal("beta", mu=1, sigma=0.5)       # Beta cercano a mercado
    sigma = pm.HalfStudentT("sigma", nu=4, sigma=0.02) # Vol positiva, fat-tailed
    nu = pm.Exponential("nu", lam=1/30) + 2         # Grados libertad > 2

    # Likelihood Student-t (fat tails)
    mu = alpha + beta * r_market_data
    y = pm.StudentT("returns", nu=nu, mu=mu, sigma=sigma, observed=r_asset_data)

    # Inferencia
    trace = pm.sample(2000, tune=1000, target_accept=0.95)
```

---

## Segmento 3: ArviZ -- Analisis del Posterior (12 min)

### [SCREENCAST: ArviZ en accion]
```python
import arviz as az

# Summary: media, HDI, Rhat, ESS
az.summary(trace, hdi_prob=0.95)

# Trace plot: convergencia visual
az.plot_trace(trace)

# Posterior: distribuciones de alpha, beta, sigma
az.plot_posterior(trace, ref_val={"alpha": 0, "beta": 1})

# Forest plot: comparar multiples activos
az.plot_forest(trace)

# Pair plot: correlacion entre parametros
az.plot_pair(trace, var_names=["alpha", "beta"])
```

### [SLIDE: Diagnosticos clave]
| Metrica | Bueno | Problema |
|---------|-------|----------|
| Rhat | < 1.01 | > 1.05 = no converge |
| ESS | > 400 | < 100 = muestras insuficientes |
| Divergences | 0 | > 0 = geometria complicada |

---

## Segmento 4: 4 Aplicaciones Financieras (15 min)

### [SCREENCAST: Aplicacion 1 -- Jensen's Alpha]
```python
# Posterior de alpha
p_alpha_pos = (trace.posterior["alpha"] > 0).mean()
# "P(alpha > 0) = 52% -- no hay evidencia de skill"
```

### [SCREENCAST: Aplicacion 2 -- Cross-hedging beta]
```python
# Para cubrir posicion: necesitas beta del hedge ratio
# HDI de beta = rango de hedge ratios plausibles
# Si HDI es (1.1, 1.4): necesitas 1.1-1.4x de cobertura
```

### [SCREENCAST: Aplicacion 3 -- Market neutral]
```python
# Un fondo dice ser "market neutral" (beta ~ 0)
# P(|beta| < 0.1) = ???
# Si < 50%: el fondo NO es neutral con la evidencia disponible
```

### [SCREENCAST: Aplicacion 4 -- CAPM cost of equity]
```python
# r_e = r_f + beta * (r_m - r_f)
# Con beta como distribucion: r_e es DISTRIBUCION
# HDI de r_e = rango de costo de capital plausible
```

---

## Segmento 5: Cierre (8 min)

### [SLIDE: PLE cambia el paradigma]
| Paradigma MLE | Paradigma PLE |
|--------------|--------------|
| alpha = 0.02% | alpha ~ N(0.0002, 0.0006), P(>0) = 52% |
| beta = 1.25 | beta ~ N(1.25, 0.06), P(>1) = 100% |
| R2 = 0.45 | R2 ~ N(0.44, 0.03), HDI (0.38, 0.50) |
| Decision: binaria | Decision: probabilistica |

### [CTA]
"Elige un activo. Construye su PLE con priors razonables.
P(alpha > 0)? P(beta > 1)? P(R2 > 0.5)?"

---

## Notas de Produccion
- Mostrar ArviZ plots reales (trace, posterior, forest)
- Comparacion lado a lado: OLS summary vs PyMC summary
- Animar las 4 aplicaciones como "preguntas que OLS no responde"
- source_ref: turn0browsertab744690698
