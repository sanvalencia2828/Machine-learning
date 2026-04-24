# Arranque Rapido — ML Probabilistico para Finanzas

**Fuente:** Kanungo, *Probabilistic ML for Finance and Investing* (O'Reilly 2023)
**source_ref:** `turn0browsertab744690698`
**Fecha:** 2026-03-27

---

## Requisitos previos

```bash
# Python 3.9+ requerido
pip install -r requirements.txt
```

---

## Opcion A: Ver codigo directamente

Abre cualquier notebook en VS Code (ya son Markdown con celdas Python):

```bash
code notebooks/notebook_ch01_trifecta_errors.md
code notebooks/notebook_ch08_kelly_capital_allocation.md
```

O ejecuta un script directamente:

```bash
python src/ch01_tails_demo.py
python src/ltcm_simulator.py
python src/binomial_credit_rate_timevary.py
```

Los scripts generan graficos en `data/` automaticamente.

---

## Opcion B: Generar PNGs estaticos

```bash
# Fat tails vs distribucion normal
python src/ch01_tails_demo.py
# → data/fat_tails_plot.png

# Simulador LTCM (1x vs 5x vs 10x vs 25x leverage)
python src/ltcm_simulator.py
# → data/ltcm_comparison.png

# Tasas de credito con modelo binomial
python src/binomial_credit_rate_timevary.py
# → data/credit_rate_distributions.png
# → data/time_varying_comparison.png
```

---

## Opcion C: HTML interactivo (recomendado)

```bash
# Genera 3 archivos HTML interactivos con Plotly
python visualizations/plotly_credit_rates_snippet.py
# → visualizations/credit_rates_interactive.html
# → visualizations/credit_rates_comparison.html
# → visualizations/credit_rates_sensitivity.html

# Abre en el navegador
start visualizations/credit_rates_interactive.html
```

Para notebooks interactivos:

```bash
# Convertir Markdown a Jupyter notebook
pip install jupytext
jupytext --to notebook notebooks/notebook_ch03_monte_carlo_finance.md

# Abrir en Jupyter
jupyter lab notebooks/notebook_ch03_monte_carlo_finance.ipynb
```

---

## Opcion D: Ejecutar notebook completo

```bash
# Instalar jupytext y papermill
pip install jupytext papermill

# Convertir y ejecutar Ch08 (Kelly criterion)
jupytext --to notebook notebooks/notebook_ch08_kelly_capital_allocation.md
papermill notebooks/notebook_ch08_kelly_capital_allocation.ipynb \
         notebooks/output_ch08.ipynb

# O convertir todos los notebooks de una vez
for f in notebooks/notebook_ch0*.md; do
  jupytext --to notebook "$f"
done
```

En VS Code con extension Jupyter, puedes abrir los `.md` directamente como notebooks.

---

## Estructura del paquete

```
Machine learning/
├── content.json                  # Metadatos maestros (9 caps, 51 params)
├── chapters_index.json           # Indice de navegacion
├── pricing_features.csv          # 4 tiers de precios
├── requirements.txt              # Dependencias Python
├── README_MVP.md                 # Documentacion completa
├── README_quickstart.md          # ← Este archivo
│
├── notebooks/                    # 16 notebooks (8 primarios + 8 bonus)
│   ├── notebook_ch01_trifecta_errors.md
│   ├── notebook_ch02_monty_hall_uncertainty.md
│   ├── notebook_ch03_monte_carlo_finance.md
│   ├── notebook_ch04_nhst_dangers.md
│   ├── notebook_ch05_pml_framework.md
│   ├── notebook_ch06_mle_vs_probabilistic.md
│   ├── notebook_ch07_pymc_ensembles.md
│   ├── notebook_ch08_kelly_capital_allocation.md
│   └── ... (8 notebooks bonus)
│
├── src/                          # Scripts ejecutables
│   ├── ch01_tails_demo.py
│   ├── binomial_credit_rate_timevary.py
│   ├── ltcm_simulator.py
│   ├── mcmc_inverse_demo.py
│   └── mcs_forward_demo.py
│
├── visualizations/
│   └── plotly_credit_rates_snippet.py
│
├── qa/
│   └── qa_traceability_ch01-08.md
│
└── data/                         # Salidas generadas (auto-creado)
    ├── fat_tails_plot.png
    ├── ltcm_comparison.png
    └── ...
```

---

## Flujo recomendado para instructores

1. **Importar metadatos** → `content.json` al CMS (Strapi/Sanity/Next.js)
2. **Configurar tiers** → `pricing_features.csv` al sistema de pagos
3. **Publicar notebooks** → Convertir `.md` a `.ipynb` con jupytext
4. **Generar visualizaciones** → Opcion C para demos interactivos
5. **Validar QA** → Revisar `qa/qa_traceability_ch01-08.md`

## Flujo recomendado para estudiantes

1. `pip install -r requirements.txt`
2. Abrir notebook del capitulo actual en VS Code
3. Ejecutar celdas secuencialmente
4. Completar ejercicios al final de cada notebook
5. Comparar con los scripts en `src/` para ejemplos adicionales

---

## Referencias clave

- Kanungo, D.K. *Probabilistic ML for Finance and Investing*. O'Reilly, 2023.
- Orrell, D. & Wilmott, P. *The Money Formula*. Wiley, 2017.
- Sekerke, M. *Bayesian Risk Management*. Wiley, 2015.
- Jaynes, E.T. *Probability Theory: The Logic of Science*. Cambridge, 2003.
- Ioannidis, J.P.A. "Why Most Published Research Findings Are False." PLOS Med, 2005.
- Geron, A. *Hands-On ML with Scikit-Learn, Keras, and TensorFlow*. 3rd ed. O'Reilly, 2022.
- Lopez de Prado, M. *Advances in Financial Machine Learning*. Wiley, 2018.
- Taleb, N.N. *Fooled by Randomness*. Random House, 2005.
- Thompson et al. "Nobels For Nonsense." J Post Keynesian Econ, 2006.
- Simons, K. "Model Error." New England Economic Review, 1997.
- Peters, O. "The Ergodicity Problem in Economics." Nature Physics, 2019.
- Kelly, J.L. "A New Interpretation of Information Rate." Bell Sys Tech J, 1956.
