# Ejercicios Practicos -- Modulo 4B: NHST Aplicado
# source_ref: turn0browsertab744690698

---

## Ejercicio 1: OLS con Statsmodels -- Tu Primer Modelo de Mercado

**Nivel:** Basico
**Tiempo estimado:** 25 min

### Enunciado
Genera retornos sinteticos para un activo con beta=1.0 y alpha=0.
1. Ajusta OLS con `sm.OLS(y, sm.add_constant(x)).fit()`
2. Lee el summary: p-value de alpha, p-value de beta, R-squared
3. El alpha es significativo? (Deberia ser ~0 con p alto)
4. Repite 100 veces. En cuantas el alpha da p < 0.05?
   (Deberia ser ~5% -- falsos positivos por azar)

```python
import statsmodels.api as sm
import numpy as np

np.random.seed(42)
n = 252
r_mkt = np.random.normal(0.0003, 0.012, n)
r_asset = 0 + 1.0 * r_mkt + np.random.normal(0, 0.008, n)  # alpha=0!

X = sm.add_constant(r_mkt)
modelo = sm.OLS(r_asset, X).fit()
print(modelo.summary())
# TODO: repetir 100 veces y contar falsos positivos
```

---

## Ejercicio 2: Diagnosticos que Fallan -- Fat Tails en Residuales

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Genera residuales con Student-t(nu=3) en vez de Normal.
1. Ajusta OLS y mira los p-values
2. Ejecuta Jarque-Bera: rechaza normalidad?
3. Ejecuta Breusch-Pagan: hay heterocedasticidad?
4. Si ambos tests fallan, son validos los p-values?
5. Repite con residuales Normal. Ahora los tests pasan?

### Pregunta clave
Si un paper reporta "alpha significativo con p=0.03" pero NO
reporta diagnosticos, deberas creerle?

---

## Ejercicio 3: Confusion Matrix de un Indicador (Yield Curve)

**Nivel:** Intermedio
**Tiempo estimado:** 30 min

### Enunciado
La inversion de la yield curve ha predicho recesiones con:
- Sensibilidad ~85% (detecta 85% de las recesiones)
- Especificidad ~75% (FPR ~25%)
- Base rate de recesion: ~15%

1. Construye la confusion matrix para 1000 meses
2. Calcula PPV, NPV, accuracy, F1
3. Si la yield curve se invierte HOY, cual es P(recesion)?
4. Cambia FPR a 10%. Como cambia el PPV?
5. Cambia base rate a 5% (economia muy estable). PPV?

```python
def confusion_matrix_bayes(sens, fpr, base_rate, n=1000):
    tp = int(sens * base_rate * n)
    fp = int(fpr * (1 - base_rate) * n)
    fn = int((1 - sens) * base_rate * n)
    tn = n - tp - fp - fn
    ppv = tp / max(tp + fp, 1)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "ppv": ppv}
# TODO: calcular para los 3 escenarios
```

---

## Ejercicio 4: PPV vs FPR -- Grafica Interactiva

**Nivel:** Intermedio
**Tiempo estimado:** 25 min

### Enunciado
Crea un grafico con 4 curvas de PPV vs FPR, una por cada base rate:
5%, 10%, 15%, 25%.

1. Fija sensibilidad en 90%
2. Varia FPR de 1% a 40%
3. Grafica las 4 curvas
4. Marca donde cada curva cruza PPV = 50% (punto de inutilidad)
5. Conclusion: para que base rate un indicador con FPR=15% es util?

```python
import numpy as np
import matplotlib.pyplot as plt

sens = 0.90
fprs = np.linspace(0.01, 0.40, 50)
for br in [0.05, 0.10, 0.15, 0.25]:
    ppvs = (sens * br) / (sens * br + fprs * (1 - br))
    plt.plot(fprs * 100, ppvs * 100, label=f'BR={br:.0%}')
# TODO: completar y analizar
```

---

## Ejercicio 5: Mini-Proyecto -- Evalua tu Propio Indicador

**Nivel:** Avanzado
**Tiempo estimado:** 40 min

### Enunciado
Elige uno de estos indicadores y evalualo:

**Opcion A: PMI < 50 como senal de recesion**
- Sensibilidad estimada: ~80%
- FPR estimada: ~15%
- Base rate: 15%

**Opcion B: S&P 500 cae > 20% (bear market) como senal de recesion**
- Sensibilidad estimada: ~70%
- FPR estimada: ~10%
- Base rate: 15%

**Opcion C: Unemployment claims > 300K**
- Sensibilidad estimada: ~90%
- FPR estimada: ~20%
- Base rate: 15%

Para tu indicador:
1. Construye confusion matrix
2. Calcula PPV con Bayes
3. Simula 10000 meses y verifica PPV empiricamente
4. Compara PPV con lo que un "fiscal" reportaria (sensibilidad)
5. Que decision tomarias si el indicador da senal HOY?

---

## Ejercicio 6 (Bonus): FRED API -- Datos Reales

**Nivel:** Avanzado
**Tiempo estimado:** 35 min

### Enunciado
Si tienes acceso a la FRED API (fredapi o pandas_datareader):

1. Descarga la serie USREC (indicador binario de recesion NBER)
2. Descarga T10Y2Y (spread 10y-2y Treasury yield)
3. Define "senal" como T10Y2Y < 0 (inversion)
4. Calcula la confusion matrix REAL historica
5. Compara PPV real vs PPV teorico con Bayes

```python
# Opcion sin API: usar datos sinteticos que simulen las propiedades
# reales de la yield curve
# Base rate real USA (1954-2024): ~14.5%
# Sensibilidad historica yield curve inversion: ~85%
# FPR historica: ~25%
```
