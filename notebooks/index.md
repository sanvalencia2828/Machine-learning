# ML Probabilístico para Finanzas e Inversión

<div style="background: linear-gradient(135deg, #1a237e22 0%, #0d47a133 100%); border: 1px solid #1a237e44; border-radius: 12px; padding: 24px 28px; margin-bottom: 32px;">

**Autor:** Deepak K. Kanungo &nbsp;·&nbsp; **Editorial:** O'Reilly Media, 2023 &nbsp;·&nbsp; **ISBN:** 978-1-492-09767-9

Implementación práctica en Python de los 8 capítulos del libro con ejemplos financieros reales, inferencia bayesiana y ensambles generativos.

</div>

---

## ¿Qué encontrarás aquí?

Este sitio compila **28 notebooks interactivos** organizados en 8 capítulos. Cada notebook integra:

- 📐 **Derivaciones matemáticas** paso a paso (fórmulas de Bayes, BSM, Kelly)
- 🐍 **Código Python ejecutable** con PyMC, NumPy, SciPy, Matplotlib
- 📊 **Visualizaciones** de distribuciones, diagnósticos MCMC y volatility surfaces
- 🎯 **Ejercicios aplicados** con datos financieros sintéticos y reales

---

## Estructura del Libro

| Capítulo | Título Español | Notebooks |
|:--------:|----------------|:---------:|
| 0 | Prefacio | 1 |
| 1 | La necesidad del aprendizaje automático probabilístico | 2 |
| 2 | Análisis y cuantificación de la incertidumbre | 6 |
| 3 | Cuantificación de incertidumbre de salida con simulación Monte Carlo | 5 |
| 4 | Los peligros de las metodologías estadísticas convencionales | 4 |
| 5 | El marco del aprendizaje automático probabilístico | 3 |
| 6 | Los peligros de los sistemas de IA convencionales | 4 |
| 7 | ML probabilístico con ensambles generativos | 2 |
| 8 | Toma de decisiones probabilísticas con ensambles generativos | 2 |

---

## Stack Tecnológico

```python
# Inferencia bayesiana y probabilística
import pymc as pm            # Modelado probabilístico
import arviz as az           # Diagnósticos MCMC y visualización

# Computación científica
import numpy as np           # Álgebra lineal y simulación
import scipy.stats as st     # Distribuciones y tests estadísticos
import pandas as pd          # Manipulación de datos

# Visualización
import matplotlib.pyplot as plt
import seaborn as sns
```

---

## Navegación

Para acceder a los contenidos:

1. **Barra lateral izquierda**: Navegación jerárquica por capítulos y notebooks
2. **Tabs superiores**: Acceso directo a cada capítulo
3. **Buscador 🔍**: Para encontrar temas específicos en todos los notebooks

---

## Consejos de Uso

!!! tip "Flujo recomendado"
    Sigue los capítulos en orden — cada uno construye sobre el anterior.
    Usa las **tabs superiores** para saltar entre capítulos o la **barra lateral**
    para moverte entre notebooks dentro de un capítulo.

!!! note "Código vs. Outputs"
    Los bloques de código muestran la implementación Python exacta del libro.
    Los outputs (gráficas, tablas) se generan al ejecutar el código en tu
    entorno local con `jupyter lab` o en Google Colab.

!!! info "Reproducibilidad"
    Todos los notebooks usan `np.random.seed(42)` o semillas explícitas
    para garantizar resultados reproducibles.

---

## Referencia Bibliográfica

> Kanungo, D. K. (2023). *Probabilistic Machine Learning for Finance and Investing:
> A Primer to Generative AI with Python*.
> O'Reilly Media. ISBN: 978-1-492-09767-9.
> [`source_ref: turn0browsertab744690698`]

---

<div style="text-align:center; color: #666; font-size: 0.85em; margin-top: 48px;">
Sitio generado con <strong>MkDocs Material</strong> · Contenido bajo licencia educativa
</div>