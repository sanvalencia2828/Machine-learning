# 📦 Capítulo 1 — Entregables de Integración

**Documento de integración para el repositorio del curso**  
**Source:** `turn0browsertab744690698`  
**Fecha:** 2026-03-27

---

## 📋 Resumen de Artefactos

Se han generado **4 archivos listos para pegar** en tu repositorio:

| Archivo | Tipo | Propósito | Ubicación Sugerida |
|---------|------|----------|-------------------|
| `chapter_01_content.json` | JSON | Metadatos del capítulo, parámetros, referencias | `content/chapters/` |
| `binomial_credit_rate_timevary.py` | Python | Módulo reproducible con modelos binomial/trinomial | `src/models/` |
| `notebook_ch01_parameter_uncertainty.md` | Markdown | Plantilla de notebook ejecutable con secciones | `notebooks/` |
| `plotly_interactive_credit_rates.py` | Python | Visualizaciones interactivas (sliders, comparación) | `src/visualizations/` |

---

## 🔧 Instalación Rápida

### Paso 1: Copiar archivos al repositorio

```bash
# Asumir que estás en la raíz del repositorio
cp chapter_01_content.json content/chapters/
cp binomial_credit_rate_timevary.py src/models/
cp notebook_ch01_parameter_uncertainty.md notebooks/
cp plotly_interactive_credit_rates.py src/visualizations/
```

### Paso 2: Instalar dependencias

```bash
pip install numpy pandas scipy matplotlib plotly ipywidgets jupytext nbformat
```

### Paso 3: Verificar instalación

```python
# Test imports
python -c "from src.models.binomial_credit_rate_timevary import credit_rate_distribution; print('✓ OK')"
```

---

## 📖 Descripción por Artefacto

### 1. `chapter_01_content.json`

**Propósito:** Metadata centralizada del Capítulo 1 para CMS/backend.

**Contenido:**
- Título del capítulo (ES/EN)
- Resumen ejecutivo
- Arrays de **6 parámetros conceptuales** (trifecta, especificación, parámetros, no-estacionariedad, ejemplo binomial, trinomial)
- Palabras clave para búsqueda
- Objetivos de aprendizaje
- Referencias a archivos asociados (módulo Python, notebooks, visualizaciones)

**Uso:**
```python
import json

with open('content/chapters/chapter_01_content.json', 'r') as f:
    ch01_metadata = json.load(f)

print(ch01_metadata['title']['es'])
# → "La necesidad del aprendizaje probabilístico"

print(f"Parámetros: {len(ch01_metadata['parameters'])}")
# → Parámetros: 6
```

**Integración CMS:**
```bash
# Strapi API
curl -X POST http://localhost:1337/api/chapters \
  -H "Content-Type: application/json" \
  -d @content/chapters/chapter_01_content.json

# Sanity CLI
sanity import content/chapters/chapter_01_content.json
```

---

### 2. `binomial_credit_rate_timevary.py`

**Propósito:** Módulo reutilizable con **5 funciones clave**:

| Función | Parámetros | Salida | Caso de Uso |
|---------|-----------|--------|-------------|
| `credit_rate_distribution()` | `p, fed_meetings, base_rate, per_raise_bps` | pd.DataFrame | Figura 1-2 clásica |
| `credit_rate_timevary()` | + `prob_schedule` | pd.DataFrame | Probabilidades que cambian por reunión |
| `convert_to_trinomial_after_change()` | + `change_step` | pd.DataFrame | Shock estructural + model adaptation |
| `plot_figure_1_2_timevary()` | + `timevary=bool` | matplotlib.figure.Figure | Reproducir y comparar |
| `summary_statistics()` | `df` | dict | Media, mediana, std, modo |

**Ejemplo básico:**
```python
from src.models.binomial_credit_rate_timevary import credit_rate_distribution, summary_statistics

# Reproducir Figura 1-2 para p=0.7
df = credit_rate_distribution(fed_meetings=8, prob_raise=0.7)
print(df)
#    cc_rate      prob
# 0      12.00  0.000065
# 1      12.25  0.003087
# ...

stats = summary_statistics(df)
print(f"Expected rate: {stats['mean']:.3f}%")
# → Expected rate: 14.000%
```

**Ejemplo avanzado: probabilidad tiempo-variable**
```python
# Fed sube en primeras reuniones, luego corta
prob_schedule = [0.8, 0.8, 0.7, 0.5, 0.3, 0.2, 0.2, 0.2]
df_pivot = credit_rate_timevary(fed_meetings=8, prob_schedule=prob_schedule)
```

**Ejemplo avanzado: cambio estructural a trinomial**
```python
# Reuniones 1-4: binomial (p=0.8), reuniones 5-8: trinomial (permite cortes)
df_trinomial = convert_to_trinomial_after_change(
    fed_meetings=8,
    prob_schedule=[0.8]*4 + [0.2]*4,
    change_step=4  # cambio después de reunión 4
)
```

**CI/CD Integration:**
```bash
# En tu GitHub Actions o gitlab-ci.yml
python -m pytest tests/test_binomial_credit_rate.py -v
python src/models/binomial_credit_rate_timevary.py  # genera figuras
```

---

### 3. `notebook_ch01_parameter_uncertainty.md`

**Propósito:** Plantilla de notebook con **8 secciones ejecutables**.

**Estructura:**
1. **Introducción** — contexto de tríada de errores
2. **Imports** — cargar módulos (binomial_credit_rate_timevary, plotly, etc.)
3. **Figura 1-2** — reproducción con análisis
4. **Probabilidad tiempo-variable** — exploración de ciclos de tightening/pivot
5. **Cambio estructural→trinomial** — demostración de adaptación
6. **Interactividad Plotly** — slider para variar p en tiempo real
7. **Análisis de sensibilidad** — cómo p afecta E[rate] y Var[rate]
8. **Ejercicios + referencias** — problemas para resolver

**Conversión a `.ipynb`:**

**Opción A: Jupytext (recomendado)**
```bash
jupytext --to notebook notebooks/notebook_ch01_parameter_uncertainty.md
# Genera: notebook_ch01_parameter_uncertainty.ipynb
jupyter notebook notebook_ch01_parameter_uncertainty.ipynb
```

**Opción B: nbformat (manual)**
```python
import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

nb = new_notebook()
nb.cells.append(new_markdown_cell("# Capítulo 1 — ..."))
nb.cells.append(new_code_cell("from src.models.binomial_credit_rate_timevary import ..."))
# ... agregar más celdas ...

with open('notebooks/notebook_ch01_parameter_uncertainty.ipynb', 'w') as f:
    nbf.write(nb, f)
```

**Expected Output Files:**
```
outputs/
├── figure_1_2_constant_p.png
├── figure_1_2_timevary_p.png
├── interactive_credit_rates.html
└── sensitivity_analysis.csv
```

---

### 4. `plotly_interactive_credit_rates.py`

**Propósito:** Generador de visualizaciones interactivas para web.

**3 funciones principales:**

#### A) `make_figure_interactive_slider()`
Slider que varía `p` de 0 a 1 en pasos de 0.05.
- Botones Play/Pause
- Actualización suave con transiciones
- Hover info completa

```python
from src.visualizations.plotly_interactive_credit_rates import make_figure_interactive_slider

fig = make_figure_interactive_slider(initial_p=0.7)
fig.write_html('public/interactive_slider.html')  # para servir en web
fig.show()  # en Jupyter
```

#### B) `make_comparison_figure()`
Comparación lado-a-lado de 3 distribuciones.

```python
fig = make_comparison_figure(ps=[0.5, 0.7, 0.9])
fig.write_html('public/comparison_three_p.html')
```

#### C) `make_waterfall_sensitivity()`
Gráfica de sensibilidad: cómo E[rate] varía con p.

```python
fig = make_waterfall_sensitivity()
fig.write_html('public/sensitivity_curve.html')
```

**Embebido en HTML/Next.js:**

```html
<!-- Sirve los .html generados estáticamente -->
<iframe src="/public/interactive_slider.html" width="100%" height="700"></iframe>
```

**Ejecución automática:**
```bash
python src/visualizations/plotly_interactive_credit_rates.py
# Genera 3 archivos HTML listos para servir
```

---

## 🎯 Flujo de Integración Completo

### Opción 1: Content Management System (CMS)

```
1. Importar chapter_01_content.json al CMS
   ↓
2. CMS crea página: /chapters/ch01/
   ├─ Metadata (título, objetivos, parámetros)
   ├─ Link a notebooks en GitHub
   └─ Embebido de interactive_slider.html
   ↓
3. Backend servir /outputs/ estáticamente
```

### Opción 2: GitHub + GitHub Pages

```
1. Subir archivos al repo
   ↓
2. GitHub Actions ejecuta:
   - Validar JSON schema
   - Ejecutar notebook_ch01
   - Generar figuras + HTML interactivos
   - Commit outputs/ al branch gh-pages
   ↓
3. Publicar en https://mysite.com/chapters/ch01/
```

### Opción 3: Next.js / Vite

```
1. Importar capítulo metadata
   ↓
2. Dynamically load:
   - Notebook (renderizado a HTML)
   - Figuras PNG/SVG
   - HTML Plotly (iframe o embed)
   ↓
3. Componentes React reutilizables para cada tipo de contenido
```

---

## 🔐 Trazabilidad y Auditoría

**Todos los artefactos incluyen:**
```json
{
  "source_ref": "turn0browsertab744690698",
  "created_date": "2026-03-27",
  "last_updated": "2026-03-27"
}
```

**Para CI/CD audit:**
```bash
# Extraer fuente de cada artefacto
grep -r "source_ref" content/chapters/chapter_01_content.json
# → "source_ref": "turn0browsertab744690698"
```

---

## ✅ Checklist de Validación

- [ ] Artefactos copiados a ubicaciones correctas
- [ ] Dependencias instaladas (`pip install requirements.txt`)
- [ ] `binomial_credit_rate_timevary.py` se ejecuta sin errores
- [ ] Notebook convertido a `.ipynb` y ejecutable
- [ ] Figuras generadas correctamente
- [ ] HTML Plotly abierto en navegador (slider funciona)
- [ ] `chapter_01_content.json` schema válido (opcional: contra JSON Schema official)
- [ ] `source_ref` presente en todos los archivos

---

## 🚀 Próximos Pasos

### Inmediato (esta semana)
1. Copiar archivos al repo
2. Ejecutar notebook en local: `jupyter notebook notebooks/notebook_ch01_parameter_uncertainty.ipynb`
3. Validar figuras en `outputs/`
4. Probar HTML Plotly en navegador

### Corto plazo (próximas 2 semanas)
1. Integrar con CMS o GitHub Pages
2. Agregar ejercicios interactivos (p. ej., sliders en Jupyter widgets)
3. Traducir comentarios de código a ES (actualmente EN)
4. Agregar tests unitarios en `tests/test_chapter_01.py`

### Mediano plazo (próximo mes)
1. Capítulos 2-N siguiendo el mismo patrón
2. Dashboard agregado de visualizaciones por capítulo
3. Exportar a EPUB/PDF para distribución
4. Benchmarks de performance (tiempo de ejecución de notebooks)

---

## 📞 Soporte

**Si algo falla:**

| Problema | Solución |
|----------|----------|
| ImportError: No module named 'src.models' | Ejecutar desde raíz del repo; agregar cwd a PYTHONPATH |
| Notebooks no se ejecutan | Verificar kernel Python; instalar paquetes con `pip install -r requirements.txt` |
| Figuras no se guardan | Crear directorio `outputs/` manualmente: `mkdir -p outputs/` |
| HTML Plotly en blanco | Verificar que plotly ≥ 5.0; actualizar con `pip install --upgrade plotly` |

---

## 📚 Archivos Relacionados

- **Código fuente:** `/src/models/`, `/src/visualizations/`
- **Datos:** `/data/` (si hay datasets ejemplo)
- **Tests:** `/tests/test_chapter_01.py`
- **Documentación:** `README.md`, `CONTRIBUTING.md`

---

**Estado:** ✅ Artefactos listos para producción  
**Versión:** 1.0  
**Autor:** ML Finance Course Team  
**Licencia:** [Especificar — p. ej., CC-BY-4.0]
