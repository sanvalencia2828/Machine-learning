# Capítulo 1 — Incertidumbre de Parámetros y Adaptación a Cambios Estructurales

**Notebook Template** | Convertible a `.ipynb` con Jupytext o nbformat  
**Source:** `turn0browsertab744690698`  
**Created:** 2026-03-27

---

## 📚 Propósito

Explorar empíricamente cómo la **incertidumbre paramétrica** afecta las predicciones de tasa de crédito; demostrar modelos con:
- **Probabilidad constante** (Figura 1-2 clásica)
- **Probabilidad tiempo-variable** (cambios graduales en la política de la Fed)
- **Conversión a trinomial** (pivote abrupto tras un shock estructural: p. ej., cambio de vol hiked a cuts)

---

## 🔧 Requisitos

```
Python 3.9+
numpy, pandas, scipy, matplotlib
plotly (opcional, para interactividad)
ipywidgets (opcional, para sliders)
```

**Instalación:**
```bash
pip install numpy pandas scipy matplotlib plotly ipywidgets
```

---

## 📖 Secciones del Notebook

### Sección 1: Introducción y Motivación

**Markdown Cell:**

```markdown
## Introducción

En este capítulo, exploramos la **tríada de errores** en modelado financiero:
1. **Errores de especificación**: La mayoría de las finanzas asumen distribuciones gaussianas; en realidad, los retornos tienen colas gruesas.
2. **Errores de parámetros**: Los parámetros estimados del pasado pueden ser obsoletos en mercados que cambian.
3. **Falta de adaptación a cambios estructurales**: El régimen de datos puede cambiar (p. ej., pivot de tightening a cutting); nuestros modelos deben adaptarse.

### Caso de estudio: Tasas de tarjeta de crédito

- **Base:** Tarjeta de crédito con tasa inicial de 12%
- **Mecanismo:** Cada reunión de la Fed, probabilidad p de subida de 25 bps
- **Pregunta:** ¿Cuál es la distribución de tasas después de 8 reuniones?

**Figura 1-2: Predicted range of credit card rates** muestra esta distribución para cuatro valores de p (0.6, 0.7, 0.8, 0.9).
```

---

### Sección 2: Importar funciones reutilizables

**Python Cell:**

```python
# Importar el módulo binomial_credit_rate_timevary
# Opción A: si el archivo está en src/
import sys
sys.path.insert(0, '../src')  # ajustar ruta según estructura
from binomial_credit_rate_timevary import (
    credit_rate_distribution,
    credit_rate_timevary,
    convert_to_trinomial_after_change,
    plot_figure_1_2_timevary,
    summary_statistics
)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

print("✓ Librerías cargadas exitosamente")
```

---

### Sección 3: Reproducir Figura 1-2 (Probabilidad constante)

**Python Cell:**

```python
# Reproducir Figura 1-2 con probabilidad constante
fig = plot_figure_1_2_timevary(probs=[0.6, 0.7, 0.8, 0.9], timevary=False)
fig.savefig("outputs/figure_1_2_constant_p.png", dpi=150, bbox_inches='tight')
plt.show()

print("✓ Figura 1-2 reproducida")
```

**Markdown Cell:**

```markdown
### Análisis de Figura 1-2

Observaciones clave:
- Para **p=0.6**: distribución amplia, muchos escenarios posibles (12% a 13.5%).
- Para **p=0.9**: masa de probabilidad concentrada en tasas altas (>13%).
- La **media** y **mediana** aumentan con p, indicando que mayor probabilidad de subida → mayor tasa esperada.

¿Qué pasaría si la Fed cambiar de política a mitad de camino?
```

---

### Sección 4: Probabilidad tiempo-variable

**Python Cell:**

```python
# Modelo 1: Tightening gradient (probabilities increase over meetings)
schedule_tightening = np.array([0.4, 0.5, 0.6, 0.7, 0.75, 0.75, 0.7, 0.6])

df_tightening = credit_rate_timevary(
    fed_meetings=8,
    prob_schedule=schedule_tightening,
    base_rate=12.0,
    per_raise_bps=25
)

# Modelo 2: Pivot (tightening then cutting)
schedule_pivot = np.array([0.8, 0.8, 0.7, 0.5, 0.3, 0.2, 0.2, 0.2])

df_pivot = credit_rate_timevary(
    fed_meetings=8,
    prob_schedule=schedule_pivot,
    base_rate=12.0,
    per_raise_bps=25
)

# Visualizar ambos
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.bar(df_tightening['cc_rate'], df_tightening['prob'], width=0.18, alpha=0.7, edgecolor='black')
ax1.set_title('Tightening Cycle (gradually higher p)')
ax1.set_xlabel('Credit Card Rate (%)')
ax1.set_ylabel('Probability')
ax1.grid(axis='y', alpha=0.3)

ax2.bar(df_pivot['cc_rate'], df_pivot['prob'], width=0.18, alpha=0.7, color='orange', edgecolor='black')
ax2.set_title('Policy Pivot (cut after tightening)')
ax2.set_xlabel('Credit Card Rate (%)')
ax2.set_ylabel('Probability')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

# Estadísticas
stats_tight = summary_statistics(df_tightening)
stats_pivot = summary_statistics(df_pivot)

print("📊 Estádística – Tightening cycle:")
print(f"  Mean: {stats_tight['mean']:.3f}% | Median: {stats_tight['median']:.3f}% | Std: {stats_tight['std']:.3f}%")
print("\n📊 Estádística – Policy Pivot:")
print(f"  Mean: {stats_pivot['mean']:.3f}% | Median: {stats_pivot['median']:.3f}% | Std: {stats_pivot['std']:.3f}%")
```

---

### Sección 5: Cambio estructural → Trinomial

**Python Cell:**

```python
# Escenario: Fed sube en 4 primeras reuniones, luego cambia a cortes
prob_schedule = np.concatenate([
    np.repeat(0.8, 4),  # primeras 4: alta probabilidad de subida
    np.repeat(0.2, 4)   # últimas 4: baja probabilidad de subida (alta de cortes)
])

df_trinomial = convert_to_trinomial_after_change(
    fed_meetings=8,
    prob_schedule=prob_schedule,
    change_step=4,  # cambio después de reunión 4
    base_rate=12.0,
    per_raise_bps=25
)

# Visualización
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(df_trinomial['cc_rate'], df_trinomial['prob'], width=0.18, alpha=0.7, 
       color='red', edgecolor='black', label='Trinomial (with cuts)')
ax.set_title('Credit Card Rate Distribution: Shock at Meeting 5\n(Tightening → Cutting)', fontsize=12)
ax.set_xlabel('Credit Card Rate (%)')
ax.set_ylabel('Probability')
ax.grid(axis='y', alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()

stats_tri = summary_statistics(df_trinomial)
print("📊 Estádística – Trinomial (Shock at meeting 5):")
print(f"  Mean: {stats_tri['mean']:.3f}%")
print(f"  Median: {stats_tri['median']:.3f}%")
print(f"  Std: {stats_tri['std']:.3f}%")
print(f"  Min: {stats_tri['min']:.3f}% | Max: {stats_tri['max']:.3f}%")

# Pregunta: ¿Probabilidad de que la tasa final < 12.5%?
prob_below_12_5 = df_trinomial[df_trinomial['cc_rate'] <= 12.5]['prob'].sum()
print(f"\n✓ P(final rate ≤ 12.5%) = {prob_below_12_5:.2%}")
```

---

### Sección 6: Interactividad (Plotly + slider)

**Python Cell:**

```python
# Slider interactivo: variar p_raise en tiempo real
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def make_interactive_figure():
    """Crea figura Plotly con slider para p_raise"""
    initial_p = 0.7
    df_init = credit_rate_distribution(8, initial_p, 12.0, 25)
    
    fig = go.Figure()
    
    # Add initial trace
    fig.add_trace(
        go.Bar(x=df_init['cc_rate'], y=df_init['prob'], 
               name=f'p={initial_p}', marker_color='blue')
    )
    
    # Create frames for slider (p from 0.0 to 1.0)
    ps = np.round(np.arange(0.0, 1.01, 0.05), 2).tolist()
    frames = []
    
    for p in ps:
        df_p = credit_rate_distribution(8, p, 12.0, 25)
        frames.append(
            go.Frame(
                data=[go.Bar(x=df_p['cc_rate'], y=df_p['prob'], marker_color='blue')],
                name=str(p)
            )
        )
    
    fig.frames = frames
    
    # Add slider
    sliders = [
        dict(
            active=int(initial_p / 0.05),
            steps=[
                dict(
                    args=[[str(p)], 
                          {'frame': {'duration': 200, 'redraw': True}, 'mode': 'immediate'}],
                    label=f'{p:.2f}',
                    method='animate'
                )
                for p in ps
            ],
            x=0.0, y=-0.15, len=1.0, xanchor='left', yanchor='top',
            currentvalue={'xanchor': 'center', 'prefix': 'p = ', 'visible': True}
        )
    ]
    
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                buttons=[
                    dict(label='Play', method='animate',
                         args=[None, {'frame': {'duration': 300, 'redraw': True}, 'fromcurrent': True}])
                ],
                x=0.0, y=-0.1
            )
        ],
        sliders=sliders,
        xaxis_title='Credit Card Rate (%)',
        yaxis_title='Probability',
        title='Interactive: Credit Card Rate Distribution (Binomial)',
        height=600
    )
    
    return fig

fig_interactive = make_interactive_figure()
fig_interactive.write_html('outputs/interactive_credit_rates.html')
print("✓ Saved: outputs/interactive_credit_rates.html")
fig_interactive.show()
```

---

### Sección 7: Análisis de sensibilidad

**Python Cell:**

```python
# Sensibilidad: para cada p, calcular media y desviación estándar
ps = np.arange(0.0, 1.01, 0.1)
means = []
stds = []

for p in ps:
    df = credit_rate_distribution(8, p, 12.0, 25)
    stats = summary_statistics(df)
    means.append(stats['mean'])
    stds.append(stats['std'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Mean sensitivity
ax1.plot(ps, means, 'o-', linewidth=2, markersize=8, color='blue')
ax1.set_xlabel('Probability of rate hike (p)')
ax1.set_ylabel('Expected credit card rate (%)')
ax1.set_title('Expected rate increases with p')
ax1.grid(True, alpha=0.3)

# Std dev sensitivity
ax2.plot(ps, stds, 's-', linewidth=2, markersize=8, color='red')
ax2.set_xlabel('Probability of rate hike (p)')
ax2.set_ylabel('Std Dev of credit card rate (%)')
ax2.set_title('Uncertainty (std dev) peaks near p=0.5')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Crear tabla
df_sensitivity = pd.DataFrame({
    'p': ps,
    'E[rate]': means,
    'Std[rate]': stds
})
print("\n📈 Sensibilidad de parámetros:")
print(df_sensitivity.to_string(index=False))
```

---

### Sección 8: Ejercicios propuestos

**Markdown Cell:**

```markdown
## 🎯 Ejercicios

### Ejercicio 1: Cálculo manual
Para p=0.8 y 3 reuniones (en lugar de 8), calcula a mano la distribución binomial de tasas.
- ¿Cuál es la media?
- ¿Cuál es la probabilidad de que la tasa final > 12.5%?

### Ejercicio 2: Regla de provisión
Diseña una regla de provisión (reserve requirement) que dependa de la distribución de tasas:
- Si P(rate > 13%) > 0.3, reserva 5% de ingresos
- Si P(rate > 13%) ≤ 0.2, reserva 2% de ingresos

Implementa en código y evalúa bajo diferentes escenarios (constante p, time-varying, trinomial).

### Ejercicio 3: Robusted a cambios estructurales
Compara la utilidad de un modelo binomial vs. trinomial tras un shock:
- Toma datos simulados en regime 1 (tightening)
- Aplica choque → regime 2 (cutting)
- ¿Qué porcentaje de error comete el binomial al no adaptar a trinomial?

### Ejercicio 4: Extensión a multinomial
Extiende el código para **m-nomial** (m > 3 outcomes). Por ejemplo, 5 outcomes: strong cut, mild cut, neutral, mild hike, strong hike.
```

---

### Sección 9: Conclusiones y referencias

**Markdown Cell:**

```markdown
## 📚 Conclusiones

1. **Incertidumbre paramétrica importa:** Cambios pequeños en p → cambios significativos en E[rate] y Std[rate].
2. **Adaptación es crucial:** Modelos que no detectan cambios estructurales se quedan atrás (vea trinomial vs. binomial).
3. **Binomial es un buen punto de partida**, pero trinomial/multinomial son extensiones naturales cuando hay evidencia de cambios de régimen.

## 🔗 Referencias

- Sekerke, M. (2015). *Bayesian Risk Management: A Bayesian Perspective on Risks and Return Risks*.
- Orrell, D., & Wilmott, P. (2017). *The Money Formula: Dodgy Finance, Pseudo Science, and How Mathematicians Got It Wrong*.
- Capítulo 1 del curso: The Need for Probabilistic Machine Learning.

**Source:** `turn0browsertab744690698`  
**Last Updated:** 2026-03-27
```

---

## 📁 Archivos de Salida Esperados

Después de ejecutar este notebook, espera:
- `outputs/figure_1_2_constant_p.png` (Figura 1-2 clásica)
- `outputs/figure_1_2_timevary_p.png` (con probabilidades tiempo-variable)
- `outputs/interactive_credit_rates.html` (gráfico Plotly interactivo)
- `outputs/sensitivity_analysis.csv` (parámetros sensibilidad)

---

## 🚀 Conversión a Jupyter Notebook

Para convertir esta plantilla a `.ipynb` ejecutable:

**Opción A: Jupytext**
```bash
jupytext --to notebook notebook_ch01_parameter_uncertainty.md
```

**Opción B: nbformat (manual)**
```python
import nbformat as nbf
nb = nbf.v4.new_notebook()

# Agregar celdas de markdown y código...
nb.cells.append(nbf.v4.new_markdown_cell("# Capítulo 1..."))
nb.cells.append(nbf.v4.new_code_cell("import numpy as np..."))

with open('notebook_ch01_parameter_uncertainty.ipynb', 'w') as f:
    nbf.write(nb, f)
```

---

## ✅ Checklist pre-producción

- [ ] Ejecutar todas las celdas sin errores
- [ ] Generar figuras y guardar en `outputs/`
- [ ] Validar que el código se ejecuta con variaciones de parámetros
- [ ] Revisar traducción ES/EN
- [ ] Incluir `source_ref` en todas las celdas de código
- [ ] Documentar requisitos en `requirements.txt`
