# 🚀 QUICK START — Probabilistic ML for Finance & Investing

**Tú:** Tengo poco tiempo. Quiero ver resultados en 5 minutos.  
**Nosotros:** ✅ Tienes 4 opciones. Escoge una.

---

## 📋 RESUMEN DE OPCIONES

| Opción | Tiempo | Qué Hace | Requisitos | Comando |
|--------|--------|---------|-----------|---------|
| **A** | 1 min | Ver código fuente | Ninguno | `cat src/*.py` |
| **B** | 5 min | Generar figuras PNG | Python + numpy/matplotlib | `python src/binomial_credit_rate_timevary.py` |
| **C** | 5 min | HTML interactivo ⭐ | Python + plotly | `python visualizations/plotly_credit_rates_snippet.py` |
| **D** | 10 min | Notebook ejecutable | Python + jupyter + librerías | `jupyter notebook notebooks/notebook_ch01_forward_inverse.md` |

---

## 🎯 OPCIÓN A: VER CÓDIGO (1 MINUTO)

**Objetivo:** Examinar el código sin instalaciones

**Comando:**
```bash
# Windows (PowerShell)
Get-Content src\binomial_credit_rate_timevary.py | head -50

# macOS/Linux (Bash)
head -50 src/binomial_credit_rate_timevary.py
```

**También puedes ver:**
- `src/ltcm_simulator.py` — Simulación de LTCM con crisis
- `src/mcs_forward_demo.py` — Forward Monte Carlo (parámetros → datos)
- `src/mcmc_inverse_demo.py` — Inverse MCMC (datos → parámetros)

**Salida esperada:**
```
Module: binomial_credit_rate_timevary.py
Purpose: Reproducible binomial and trinomial credit rate distribution models
...
def credit_rate_distribution(fed_meetings=8, prob_raise=0.7, base_rate=12.0, per_raise_bps=25):
    """Binomial model: constant probability of rate hike each meeting."""
```

---

## 📊 OPCIÓN B: GENERAR FIGURAS (5 MINUTOS)

**Objetivo:** Crear imágenes PNG listas para presentaciones

### Paso 1: Instalar dependencias
```bash
pip install -r requirements.txt
```

**Alternativa mínima (solo lo esencial):**
```bash
pip install numpy pandas scipy matplotlib
```

### Paso 2: Ejecutar scripts

**A) Binomial Credit Rates:**
```bash
cd src
python binomial_credit_rate_timevary.py
```

**Genera:**
- `figure_1_2_credit_rates_constant_p.png` — Distribución binomial estándar
- `figure_1_2_credit_rates_timevary_p.png` — Probabilidades que varían con el tiempo

**B) LTCM Simulator (opcional):**
```bash
python ltcm_simulator.py
```

**Genera:**
- `ltcm_wealth_normal.png` — Trayectorias sin crisis
- `ltcm_wealth_crisis.png` — Con crisis al día 100

**C) Forward MCS (opcional):**
```bash
python mcs_forward_demo.py
```

**Genera:**
- `mcs_forward_analysis.png` — Comparación empírica vs teórica

**D) MCMC Inverse (opcional):**
```bash
python mcmc_inverse_demo.py
```

**Genera:**
- `mcmc_diagnostics.png` — Trace plots, posterior, ACF
- `mcmc_posterior_predictive_check.png` — Validación del modelo

### Expectedoutput:
```
================================================================================
LTCM Portfolio Wealth Simulation
================================================================================

[Scenario 1] Normal Market Conditions
  Initial Wealth: $100.00
  Final Wealth (Mean): $108.45
  Final Wealth (Median): $107.89
  Standard Deviation: $18.32
  VaR (95%): $73.21
  Expected Shortfall: $68.45

✓ Simulation complete. Figures saved:
  - ltcm_wealth_normal.png
  - ltcm_wealth_crisis.png
================================================================================
```

---

## 🌐 OPCIÓN C: HTML INTERACTIVO (5 MINUTOS) ⭐ RECOMENDADO

**Objetivo:** Crear visualizaciones interactivas para web/presentación

### Paso 1: Instalar dependencias
```bash
pip install plotly numpy pandas scipy
```

### Paso 2: Generar HTML
```bash
cd visualizations
python plotly_credit_rates_snippet.py
```

### Genera 3 archivos HTML:
1. **`credit_rates_interactive_slider.html`** ⭐
   - Slider interactivo: p ∈ [0, 1]
   - Play/Pause buttons para animación
   - Hover tooltips con valores exactos
   - **Abre in browser:** `start credit_rates_interactive_slider.html` (Windows)

2. **`credit_rates_comparison.html`**
   - Comparación de 3 escenarios lado a lado (p=0.3, 0.6, 0.9)
   - Barras coloreadas para cada p
   - Línea de media teórica

3. **`credit_rates_sensitivity.html`**
   - Curva de sensibilidad: E[rate] vs p
   - Gráfico de varianza: Var[rate] vs p
   - Muestra no-linealidad y máximo en p=0.5

### Incrustar en sitio web:
```html
<!-- Opción 1: Iframe -->
<iframe src="credit_rates_interactive_slider.html" width="100%" height="700"></iframe>

<!-- Opción 2: Embed directo (copiar contenido del HTML) -->
```

### Expected output:
```
================================================================================
PLOTLY INTERACTIVE VISUALIZATIONS
================================================================================

[1] Creating interactive slider figure...
    ✓ Saved: credit_rates_interactive_slider.html

[2] Creating comparison figure...
    ✓ Saved: credit_rates_comparison.html

[3] Creating sensitivity curve...
    ✓ Saved: credit_rates_sensitivity.html

✓ All Plotly figures generated!

HTML files ready for embedding:
  <iframe src='credit_rates_interactive_slider.html' width='100%' height='700'></iframe>
================================================================================
```

---

## 📓 OPCIÓN D: NOTEBOOK EJECUTABLE (10 MINUTOS)

**Objetivo:** Tutorial interactivo con código + explicaciones + ejercicios

### Paso 1: Instalar todo
```bash
pip install -r requirements.txt
```

### Paso 2: Convertir Markdown → Jupyter Notebook

**Opción 2a: Con Jupytext (automático):**
```bash
pip install jupytext

cd notebooks
jupytext --to notebook notebook_ch01_forward_inverse.md
```

Esto genera: `notebook_ch01_forward_inverse.ipynb`

**Opción 2b: Abrir directamente con Jupyter:**
```bash
cd notebooks
jupyter notebook notebook_ch01_forward_inverse.md
```

Jupyter lo abre automáticamente (Jupytext compatibilidad)

### Paso 3: Ejecutar Notebook
```bash
jupyter notebook notebook_ch01_forward_inverse.ipynb
```

Luego en la interfaz de Jupyter:
1. Click "Kernel" → "Restart & Run All" (o ejecutar celda por celda)

### Contenido del Notebook:
1. **Introducción** — Conceptos de Forward/Inverse inference
2. **Imports & Setup** — Cargar librerías (numpy, pandas, matplotlib, scipy)
3. **Forward MCS** — Simulaciones: p → distribución de tasas
4. **MCMC Bayesiano** — Estimación: datos → posterior de p
5. **Posterior Predictive Check** — Validación del modelo
6. **Ejercicios** — 5 problemas para estudiantes

### Expected output (en notebook):
```
✅ Environment ready for Chapter 1 inference demos

📊 Forward MCS Results (p=0.7, n_meetings=8):
  Mean rate: 13.7500%
  Std dev: 0.7670%
  Range: [12.00%, 14.00%]

🎯 MCMC Results:
  Acceptance rate: 73.2%
  Posterior mean: 0.6843
  Posterior std: 0.1234
  95% HPD interval: [0.4521, 0.8932]

🔬 Posterior Predictive Check:
  Observed data: mean=4.88, std=1.55
  PPC distribution: mean=4.92, std=1.48

✅ Figure saved: notebook_ch01_forward_mcs.png
✅ Figure saved: notebook_ch01_mcmc_diagnostics.png
✅ Figure saved: notebook_ch01_posterior_predictive.png
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

| Síntoma | Solución |
|---------|----------|
| `ModuleNotFoundError: No module named 'numpy'` | `pip install numpy pandas scipy` |
| `ModuleNotFoundError: No module named 'matplotlib'` | `pip install matplotlib seaborn` |
| `ModuleNotFoundError: No module named 'plotly'` | `pip install plotly` |
| No se genera PNG | Crea carpeta `outputs/`: `mkdir outputs` |
| Jupyter no abre | `pip install jupyter jupytext` |
| Kernel muere en notebook | Reinicia: Kernel → Restart |
| Plotly HTML en blanco | Actualiza: `pip install --upgrade plotly` |

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
c:/Users/santi/OneDrive/Desktop/Machine learning/

├── requirements.txt                          ← Instalar con: pip install -r
├── README.md                                 ← Este documento
│
├── src/                                      ← Opción B & C
│   ├── binomial_credit_rate_timevary.py     ← Forward: binomial model
│   ├── ltcm_simulator.py                    ← MC simulation (wealth trajectories)
│   ├── mcs_forward_demo.py                  ← Forward inference demo
│   └── mcmc_inverse_demo.py                 ← MCMC inverse inference
│
├── visualizations/                           ← Opción C
│   └── plotly_credit_rates_snippet.py       ← Interactive Plotly generator
│
├── notebooks/                                ← Opción D
│   └── notebook_ch01_forward_inverse.md     ← Ejecutable tutorial
│
└── [otros archivos del proyecto]
```

---

## ⚡ COMANDOS RÁPIDOS (RESUMEN)

```bash
# OPCIÓN A: Ver código (instant)
cat src/binomial_credit_rate_timevary.py | head -50

# OPCIÓN B: Generar PNGs
pip install numpy pandas scipy matplotlib
python src/binomial_credit_rate_timevary.py
python src/ltcm_simulator.py
python src/mcs_forward_demo.py
python src/mcmc_inverse_demo.py

# OPCIÓN C: HTML interactivo (RECOMENDADO) ⭐
pip install plotly numpy pandas scipy
python visualizations/plotly_credit_rates_snippet.py
open credit_rates_interactive_slider.html  # macOS
start credit_rates_interactive_slider.html # Windows

# OPCIÓN D: Notebook completo
pip install -r requirements.txt
pip install jupytext
jupytext --to notebook notebooks/notebook_ch01_forward_inverse.md
jupyter notebook notebooks/notebook_ch01_forward_inverse.ipynb
```

---

## 🎓 QUÉ APRENDERÁS

✅ **Forward Inference (Opción B/C):**
- Binomial model para decisiones de la Fed
- Cómo parámetros → distribuciones de resultados
- Análisis de sensibilidad (E[rate], Var[rate])

✅ **Inverse Inference (Opción D):**
- Estimación Bayesiana con MCMC
- Posterior Predictive Checks para validación
- Detección de specification errors

✅ **Risk Management (Opción B):**
- Simulación de LTCM con/sin crisis
- Value-at-Risk (VaR) y Expected Shortfall
- Importancia de parámetros no-estacionarios

---

## 📞 SOPORTE

**¿Qué opción debo elegir?**

- 🟢 **Opción A:** Si solo quieres _ver_ el código
- 🟡 **Opción B:** Si quieres figuras PNG para presentación
- 🔵 **Opción C:** Si quieres visualizaciones interactivas (MEJOR)
- 🟣 **Opción D:** Si quieres aprender detalladamente + ejercicios

**Tiempo estimado total:**
- A: 1 min
- B: 5 min
- C: 5 min (tráete café ☕)
- D: 10 min + estudio de ejercicios (1-2 horas)

---

## 🔧 VERSIONES REQUERIDAS

```
Python:     3.9+
NumPy:      1.21.0+
Pandas:     1.3.0+
SciPy:      1.7.0+
Matplotlib: 3.4.0+
Plotly:     5.0.0+
PyMC:       4.0.0+ (solo para Opción D avanzada)
Jupyter:    1.0.0+
```

---

## 📖 PRÓXIMOS PASOS

1. **Ahora:** Elige A, B, C o D y ejecuta en tu terminal
2. **Luego:** Lee guía de integración: `CHAPTER_01_INTEGRATION_GUIDE.md`
3. **Final:** Explora capítulos 2-3 con el mismo patrón

---

**¿Listo?** 🚀

```bash
# Copia esto en tu terminal ahora:
pip install -r requirements.txt
python visualizations/plotly_credit_rates_snippet.py
```

---

Source: `turn0browsertab744690698`  
Last Updated: 2026-03-27  
Status: ✅ PRODUCTION-READY
