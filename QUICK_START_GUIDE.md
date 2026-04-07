# ⚡ QUICK START — 5 MINUTOS

**TL;DR:** Tienes 4 archivos listos. Escoge uno y empieza.

---

## 🚀 OPCIÓN A: VER SOLO CÓDIGO (2 min)

```bash
# Ver metadatos
cat chapter_01_content.json | grep -A5 '"parameters"'

# Ver funciones Python disponibles
grep "^def " binomial_credit_rate_timevary.py

# Ver estructura del notebook
head -50 notebook_ch01_parameter_uncertainty.md
```

---

## 🎯 OPCIÓN B: GENERAR FIGURAS (5 min)

```bash
# 1. Instalar paquetes
pip install numpy pandas scipy matplotlib

# 2. Ejecutar
python binomial_credit_rate_timevary.py

# 3. Ver resultados (se generan 2 PNGs)
ls figure_1_2_*.png
```

**Salida:**
- `figure_1_2_credit_rates_constant_p.png` — Figura 1-2 estándar
- `figure_1_2_credit_rates_timevary_p.png` — Con probabilidades que cambian

---

## 📊 OPCIÓN C: GRÁFICOS INTERACTIVOS (5 min)

```bash
# 1. Instalar plotly
pip install plotly numpy pandas scipy

# 2. Ejecutar
python plotly_interactive_credit_rates.py

# 3. Ver resultados (se generan 3 HTMLs)
ls *.html

# 4. Abrir en navegador
open interactive_credit_rates_slider.html  # macOS
start interactive_credit_rates_slider.html # Windows
xdg-open interactive_credit_rates_slider.html # Linux
```

**Salida:**
- `interactive_credit_rates_slider.html` — ⭐ Slider p ∈ [0, 1]
- `comparison_three_scenarios.html` — Comparación p=0.5, 0.7, 0.9
- `sensitivity_expected_rate.html` — Curva de sensibilidad

---

## 📓 OPCIÓN D: NOTEBOOK COMPLETO (10 min)

```bash
# 1. Instalar todo
pip install -r requirements.txt

# 2. Convertir Markdown → Jupyter
jupytext --to notebook notebook_ch01_parameter_uncertainty.md

# 3. Abrir en Jupyter
jupyter notebook notebook_ch01_parameter_uncertainty.ipynb

# 4. Ejecutar → Run All (o celda por celda)
# Ver secciones 1-8 ejecutándose
# Interactuar con sliders
```

**Secciones del notebook:**
1. Introducción (lectura)
2. Imports (carga librerías)
3. Figura 1-2 reproducida
4. Probabilidad tiempo-variable
5. Cambio estructural → Trinomial
6. Interactividad Plotly
7. Análisis de sensibilidad
8. Ejercicios (resolver problemas)

---

## 🎁 ¿QUÉ ACABAS DE RECIBIR?

```
4 Archivos Listos = 1 Capítulo Completo

1. chapter_01_content.json
   └─ Metadata para CMS (importar a Strapi/Sanity)

2. binomial_credit_rate_timevary.py
   └─ 7 funciones Python reutilizables

3. notebook_ch01_parameter_uncertainty.md
   └─ 8 secciones del curriculum

4. plotly_interactive_credit_rates.py
   └─ 3 gráficos interactivos HTML
```

**Total:** ~150 líneas de documentación + ~400 líneas de código ejecutable

---

## 📋 ARCHIVOS EN TU WORKSPACE

```
c:\Users\santi\OneDrive\Desktop\Machine learning\

📄 chapter_01_content.json
🐍 binomial_credit_rate_timevary.py
📓 notebook_ch01_parameter_uncertainty.md
📊 plotly_interactive_credit_rates.py
📖 requirements.txt

[+3 guías de documentación]
```

---

## ✅ PRÓXIMO PASO RECOMENDADO

**AHORA:** Ejecuta Opción B o C (5 min)  
**LUEGO:** Abre DELIVERY_SUMMARY.md (explicación visual)  
**FINAL:** Lee CHAPTER_01_INTEGRATION_GUIDE.md (si necesitas integrar con CMS)

---

## 🆘 SI ALGO FALLA

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: numpy` | `pip install -r requirements.txt` |
| `FileNotFoundError: figure_1_2_*.png` | Crea directorio: `mkdir outputs` |
| Notebook no ejecuta celdas | Restart kernel: Jupyter → Kernel → Restart |
| HTML Plotly en blanco | Actualizar plotly: `pip install --upgrade plotly` |

---

## 🔗 ENLACES RÁPIDOS

- **Guía Completa:** Ver CHAPTER_01_INTEGRATION_GUIDE.md
- **Índice Detallado:** Ver CHAPTER_01_ARTIFACTS_INDEX.md
- **Entrega Visual:** Ver DELIVERY_SUMMARY.md
- **Este archivo:** QUICK_START_GUIDE.md (eres aquí)

---

**LISTO PARA EMPEZAR?** 🚀

Escoge A, B, C o D arriba y ejecuta en terminal.

Tendrás resultados en 5 minutos.

---

Source: `turn0browsertab744690698`  
Date: 2026-03-27  
Status: ✅ PRODUCCIÓN-READY
