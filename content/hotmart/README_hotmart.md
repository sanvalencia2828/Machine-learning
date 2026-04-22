# Curso Hotmart: ML Probabilistico para Finanzas e Inversion

**Basado en:** Kanungo, *Probabilistic ML for Finance and Investing* (O'Reilly 2023)
**source_ref:** turn0browsertab744690698
**Modulos:** 9 (Bienvenida + 8 capitulos)
**Duracion total:** ~7 horas de video + ~16 horas de practica

---

## Estructura del Curso

| Mod | Titulo | Video | Tier | Notebook |
|-----|--------|-------|------|----------|
| 0 | Bienvenida | 15 min | Basico | notebook_ch00_welcome.md |
| 1 | Necesidad del ML Probabilistico | 45 min | Basico | notebook_ch01_trifecta_errors.md |
| 2 | Analisis de Incertidumbre | 60 min | Basico | notebook_ch02_monty_hall_uncertainty.md |
| 2B | Probabilidades Relativas | 45 min | Basico | notebook_ch02_relative_probability.md |
| 2C | Black-Scholes y Trinidad de Incertidumbre | 50 min | Avanzado | notebook_ch02c_bsm_uncertainty_trinity.md |
| 2D | Bias-Variance y No Free Lunch | 45 min | Basico | notebook_ch02d_bias_variance_nfl.md |
| 2E | Problema de la Induccion | 40 min | Basico | notebook_ch02e_induction_problem.md |
| 3 | Simulacion Monte Carlo | 50 min | Basico | notebook_ch03_monte_carlo_finance.md |
| 3B | Conceptos Estadisticos y Volatilidad | 45 min | Basico | notebook_ch03b_stat_concepts.md |
| 3C | Normal vs Realidad | 40 min | Basico | notebook_ch03c_normal_vs_reality.md |
| 3D | LGN, TLC y Fundamentos MCS | 45 min | Basico | notebook_ch03d_lln_clt_mcs.md |
| 4 | Peligros de NHST (falacias, p-values, IC) | 55 min | Avanzado | notebook_ch04_nhst_dangers.md |
| 4B | NHST Aplicado: OLS, Base Rates, Indicadores | 50 min | Avanzado | notebook_ch04b_nhst_applied.md |
| 4C | IC, CAPM y la Trampa de Alpha | 50 min | Avanzado | notebook_ch04c_ci_capm_alpha.md |
| 5 | Framework PML (prior/posterior/predictive) | 50 min | Avanzado | notebook_ch05_pml_framework.md |
| 5B | Default de Bonos High-Yield (Bayes aplicado) | 45 min | Avanzado | notebook_ch05b_hy_default.md |
| 6 | MLE vs PML (correlaciones, grid, MCMC) | 55 min | Avanzado | notebook_ch06_mle_vs_probabilistic.md |
| 6B | Caso ZYX: MLE falla con pocos datos | 40 min | Avanzado | notebook_ch06b_zyx_mle_failure.md |
| 6C | Grid, Markov Chains y MCMC Metropolis | 50 min | Avanzado | notebook_ch06c_grid_mcmc.md |
| 7 | Ensambles Generativos con PyMC (PLE, HDI) | 65 min | Premium | notebook_ch07_pymc_ensembles.md |
| 7B | PLE Aplicado: Alpha, Hedging, CAPM | 55 min | Premium | notebook_ch07_pymc_ensembles.md |
| 7C | Retrodiccion, HMC y Evaluacion PLEs | 50 min | Premium | notebook_ch07_pymc_ensembles.md |
| 8 | Decisiones: Kelly, GVaR, Ergodicidad | 60 min | Premium | notebook_ch08_kelly_capital_allocation.md |
| 8B | Loss Functions, Volatility Drag, ES | 50 min | Premium | notebook_ch08_stress_testing.md |
| 8C | GVaR, GES y GTR: Riesgo Generativo | 45 min | Premium | notebook_ch08_kelly_capital_allocation.md |
| 8D | MPT, CAPM y Critica Probabilistica | 50 min | Premium | notebook_ch08_kelly_capital_allocation.md |

---

## Planes de Comercializacion

### Plan Basico — $29 USD
**Contenido:** Modulos 0-3
**Ideal para:** Estudiantes, curiosos, analistas junior
**Incluye:**
- 4 videos (~2h 50min)
- 4 notebooks interactivos
- 10 ejercicios practicos
- Acceso a datasets sinteticos
- Certificado basico

**Propuesta de valor:** Entender por que los modelos financieros convencionales fallan
y como la simulacion Monte Carlo ofrece mejores estimaciones.

### Plan Avanzado — $79 USD
**Contenido:** Modulos 0-6
**Ideal para:** Data scientists, analistas financieros, quants junior
**Incluye:**
- Todo del Plan Basico
- 3 videos adicionales (~2h 40min)
- 3 notebooks avanzados
- 10 ejercicios adicionales
- Visualizaciones HTML interactivas
- Acceso a comunidad Discord
- Certificado avanzado

**Propuesta de valor:** Dominar la inferencia probabilistica y entender por que NHST,
p-values e intervalos de confianza son fundamentalmente defectuosos.

### Plan Premium — $149 USD
**Contenido:** Modulos 0-8
**Ideal para:** Portfolio managers, traders, quants senior
**Incluye:**
- Todo del Plan Avanzado
- 2 videos adicionales (~2h 5min)
- 2 notebooks PyMC/ArviZ
- 8 ejercicios de nivel profesional
- Scripts ejecutables completos (src/)
- 1 sesion de mentoria grupal (mensual)
- Acceso a repositorio privado con actualizaciones
- Certificado premium

**Propuesta de valor:** Construir ensambles generativos con PyMC, aplicar criterio
de Kelly para asignacion de capital, y gestionar riesgo con VaR/ES generativos.

---

## Configuracion en Hotmart

### Producto
- **Tipo:** Curso online (Area de Miembros)
- **Formato:** Video + Material complementario (notebooks, scripts, datasets)
- **Idioma principal:** Espanol
- **Idioma secundario:** Ingles (subtitulos y materiales bilingues)
- **Garantia:** 7 dias

### Paginas de Venta
- Landing page con video introductorio (Modulo 0)
- Comparativa de planes (tabla de features)
- Testimonios / casos de uso
- FAQ sobre requisitos tecnicos

### Estructura en Area de Miembros
```
Modulo 0: Bienvenida (desbloqueado para todos)
├── Video: Introduccion (15 min)
├── PDF: Guia de instalacion Python
└── Link: Google Colab setup

Modulo 1-3: Plan Basico
├── Video por modulo
├── Notebook (.ipynb via Google Colab)
├── Ejercicios + soluciones
└── Quiz de autoevaluacion

Modulo 4-6: Plan Avanzado
├── Video por modulo
├── Notebook avanzado
├── Visualizaciones HTML descargables
└── Proyecto integrador: Indicador de recesion

Modulo 7-8: Plan Premium
├── Video por modulo
├── Notebook PyMC completo
├── Scripts src/ descargables
├── Proyecto final: Ensamble generativo + Kelly
└── Acceso a sesiones de mentoria
```

---

## Produccion de Videos

### Formato recomendado
- **Resolucion:** 1080p minimo, 4K preferido
- **Audio:** Microfono de condensador, sin eco
- **Pantalla:** Screencast con VS Code / Jupyter + camara PiP
- **Duracion:** 10-15 min por segmento, 3-5 segmentos por modulo
- **Edicion:** Cortes en transiciones, zoom en codigo clave

### Script de video (estructura por modulo)
1. **Gancho** (30s): Pregunta provocativa o dato sorprendente
2. **Contexto** (2-3 min): Por que importa este tema en finanzas
3. **Teoria** (5-8 min): Conceptos con diagramas y analogias
4. **Codigo en vivo** (10-15 min): Implementacion paso a paso
5. **Resultados** (3-5 min): Interpretacion de graficos y tablas
6. **Cierre** (1-2 min): Resumen + preview del siguiente modulo

### Video scripts disponibles en
```
hotmart/scripts_video/script_mod01.md
hotmart/scripts_video/script_mod02.md
hotmart/scripts_video/script_mod02b_relative_prob.md
...
```

---

## Requisitos Tecnicos para Estudiantes

### Minimos
- Navegador web (Chrome/Edge/Firefox)
- Cuenta Google (para Colab)
- Conocimientos basicos de Python

### Recomendados
- Python 3.9+ instalado localmente
- VS Code con extension Jupyter
- `pip install -r requirements.txt`

### Opcionales (Plan Premium)
- PyMC 5.0+ y ArviZ 0.15+
- GPU recomendada para MCMC rapido

---

## Metricas de Exito

| Metrica | Objetivo |
|---------|----------|
| Tasa de conversion landing | > 3% |
| Completitud curso basico | > 60% |
| Completitud curso premium | > 40% |
| NPS del curso | > 70 |
| Recompra (upgrade de plan) | > 15% |
| Rating Hotmart | > 4.5/5 |

---

## Estrategia de Lanzamiento

### Fase 1: Pre-lanzamiento (2 semanas)
- Crear landing page con video del Modulo 0
- Lista de espera con lead magnet (PDF: "5 Razones por las que tu Modelo Financiero esta Mal")
- Posts en LinkedIn/Twitter sobre errores de NHST

### Fase 2: Lanzamiento (1 semana)
- Descuento early bird 30%
- Webinar gratuito: "Por que LTCM Colapso" (contenido del Modulo 1)
- Email sequence a lista de espera

### Fase 3: Evergreen
- Funnel automatizado con anuncios Meta/Google
- Contenido organico semanal (clips de videos)
- Affiliates program en Hotmart (30% comision)

---

## Archivos del Paquete Hotmart

```
hotmart/
├── README_hotmart.md              ← Este archivo
├── course_modules.json            ← Metadatos de 9 modulos principales
├── mod02b_content.json            ← Metadatos del modulo 2B
├── mod02c_content.json            ← Metadatos del modulo 2C (BSM + Trinidad)
├── mod02d_content.json            ← Metadatos del modulo 2D (Bias-Variance + NFL)
├── mod02e_content.json            ← Metadatos del modulo 2E (Induccion)
├── scripts_video/                 ← Scripts de video por modulo
├── ejercicios/                    ← Ejercicios con datasets
├── viz_monty_hall_mcs.py          ← Monty Hall MCS (Plotly)
├── viz_relative_probability.py    ← Probabilidades relativas (Plotly)
├── viz_bsm_uncertainty_trinity.py ← BSM + Trinidad (Plotly)
├── viz_bias_variance_nfl.py       ← Bias-Variance + NFL (Plotly)
├── viz_induction_problem.py       ← Problema de la Induccion (Plotly)
├── viz_sp500_fat_tails.py         ← MCS + Fat Tails (Plotly)
├── relative_probability.html      ← Output HTML mod 2B
└── bsm_uncertainty_trinity.html   ← Output HTML mod 2C
```

**Nota:** Los notebooks, scripts src/, y visualizaciones del paquete MVP
se reutilizan directamente. No se duplican.
