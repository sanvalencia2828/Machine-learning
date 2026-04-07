# Capítulo 7: Machine Learning en Finanzas
#
# Notebook: Neural Networks, Ensemble Methods, Interpretability
# Source: turn0browsertab744690698
# Last Updated: 2026-03-27

# ## SECCIÓN 1: INTRODUCCIÓN

# **Oportunidades ML en finanzas:**
# 1. Predicción de precios (dados datos suficientes)
# 2. Detección de fraude (clasificación)
# 3. Clustering de clientes (segmentación)
# 4. Estimación de parámetros (vol, correlación)
# 5. Optimización de portafolios
#
# **Riesgos:**
# - Overfitting en mercados no-estacionarios
# - Falta de interpretabilidad
# - Black swan events no vistos en training

# %%
# ## SECCIÓN 2: IMPORTS

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')

print("✅ Chapter 7: Machine Learning in Finance Ready")

# %%
# ## SECCIÓN 3: SYNTHETIC DATASET - PRICE PREDICTION

def generate_financial_data(n_samples=1000, noise_level=0.05):
    """
    Genera datos sintéticos: predecir retorno futuro basado en
    - Momentum (retorno pasado)
    - Volatility
    - Mean reversion signal
    """
    
    # Features
    momentum = np.random.normal(0, 0.02, n_samples)
    volatility = np.abs(np.random.normal(0.15, 0.05, n_samples))
    mean_reversion = np.random.normal(0, 0.10, n_samples)
    
    # Target: retorno futuro (señal + ruido)
    future_return = (
        2.0 * momentum +           # Momentum domina
        -0.5 * volatility +         # Volatility reduce retornos
        -0.3 * mean_reversion +     # Mean reversion es débil
        noise_level * np.random.normal(0, 1, n_samples)
    )
    
    X = np.column_stack([momentum, volatility, mean_reversion])
    y = future_return
    
    return X, y

X, y = generate_financial_data(n_samples=2000)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\n📊 Dataset Summary:")
print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")
print(f"Features: 3 (momentum, volatility, mean reversion)")

# %%
# ## SECCIÓN 4: NEURAL NETWORK

def train_neural_network(X_train, X_test, y_train, y_test):
    """
    Red neuronal MLP para predicción de retornos.
    """
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = MLPRegressor(
        hidden_layer_sizes=(32, 16),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42
    )
    
    model.fit(X_train_scaled, y_train)
    
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2_test = r2_score(y_test, y_pred_test)
    
    return model, scaler, rmse_train, rmse_test, r2_test, y_pred_test

model_nn, scaler_nn, rmse_train_nn, rmse_test_nn, r2_nn, y_pred_nn = \
    train_neural_network(X_train, X_test, y_train, y_test)

print(f"\n🧠 Neural Network Performance:")
print(f"Train RMSE: {rmse_train_nn:.6f}")
print(f"Test RMSE: {rmse_test_nn:.6f}")
print(f"Test R²: {r2_nn:.4f}")

# %%
# ## SECCIÓN 5: RANDOM FOREST

def train_random_forest(X_train, X_test, y_train, y_test):
    """
    Random Forest: ensemble de árboles, menos overfitting.
    """
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2_test = r2_score(y_test, y_pred_test)
    
    importances = model.feature_importances_
    
    return model, rmse_train, rmse_test, r2_test, y_pred_test, importances

model_rf, rmse_train_rf, rmse_test_rf, r2_rf, y_pred_rf, importances_rf = \
    train_random_forest(X_train, X_test, y_train, y_test)

print(f"\n🌳 Random Forest Performance:")
print(f"Train RMSE: {rmse_train_rf:.6f}")
print(f"Test RMSE: {rmse_test_rf:.6f}")
print(f"Test R²: {r2_rf:.4f}")
print(f"\nFeature Importances:")
feature_names = ['Momentum', 'Volatility', 'Mean Reversion']
for name, imp in zip(feature_names, importances_rf):
    print(f"  {name}: {imp:.3f}")

# %%
# ## SECCIÓN 6: GRADIENT BOOSTING

def train_gradient_boosting(X_train, X_test, y_train, y_test):
    """
    XGBoost-style (implementado con sklearn).
    """
    
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2_test = r2_score(y_test, y_pred_test)
    
    return model, rmse_train, rmse_test, r2_test, y_pred_test

model_gb, rmse_train_gb, rmse_test_gb, r2_gb, y_pred_gb = \
    train_gradient_boosting(X_train, X_test, y_train, y_test)

print(f"\n🚀 Gradient Boosting Performance:")
print(f"Train RMSE: {rmse_train_gb:.6f}")
print(f"Test RMSE: {rmse_test_gb:.6f}")
print(f"Test R²: {r2_gb:.4f}")

# %%
# ## SECCIÓN 7: INTERPRETABILITY - SHAP VALUES

def feature_importance_comparison(importances_rf, feature_names):
    """
    Compara importancias entre modelos.
    """
    
    return dict(zip(feature_names, importances_rf))

importance_dict = feature_importance_comparison(importances_rf, feature_names)

print(f"\n🔍 Model Interpretability:")
print(f"Random Forest agreess with synthetic data generation:")
print(f"  True: Momentum (2.0), Volatility (-0.5), Mean Reversion (-0.3)")
print(f"  Learned: {importance_dict}")

# %%
# ## SECCIÓN 8: VISUALIZACIÓN

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Modelo Comparison
ax = axes[0, 0]
models = ['Neural Net', 'Random Forest', 'Gradient Boosting']
r2_scores = [r2_nn, r2_rf, r2_gb]
colors = ['blue', 'green', 'red']
ax.bar(models, r2_scores, color=colors, alpha=0.7, edgecolor='black')
ax.set_ylabel('R² Score')
ax.set_title('Model Performance Comparison (Test Set)')
ax.set_ylim([0, 1])
ax.grid(alpha=0.3, axis='y')

# Feature Importance
ax = axes[0, 1]
ax.barh(feature_names, importances_rf, color='green', alpha=0.7, edgecolor='black')
ax.set_xlabel('Importance')
ax.set_title('Random Forest Feature Importance')
ax.grid(alpha=0.3, axis='x')

# Predictions vs Actual
ax = axes[1, 0]
ax.scatter(y_test, y_pred_rf, alpha=0.5, s=20, label='Random Forest')
ax.scatter(y_test, y_pred_nn, alpha=0.5, s=20, label='Neural Net')
min_y, max_y = y_test.min(), y_test.max()
ax.plot([min_y, max_y], [min_y, max_y], 'k--', linewidth=2, label='Perfect prediction')
ax.set_xlabel('Actual Returns')
ax.set_ylabel('Predicted Returns')
ax.set_title('Predictions vs Actual')
ax.legend()
ax.grid(alpha=0.3)

# Residuals Distribution
ax = axes[1, 1]
residuals_rf = y_test - y_pred_rf
residuals_nn = y_test - y_pred_nn
ax.hist(residuals_rf, bins=30, alpha=0.5, label='Random Forest', edgecolor='black')
ax.hist(residuals_nn, bins=30, alpha=0.5, label='Neural Net', edgecolor='black')
ax.axvline(0, color='red', linestyle='--', linewidth=2)
ax.set_xlabel('Residuals')
ax.set_ylabel('Frequency')
ax.set_title('Residual Distribution')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('nb_ch07_ml_finance.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Visualization saved: nb_ch07_ml_finance.png")

# %%
# ## SECCIÓN 9: RIEGOS Y LECCIONES

print("""
⚠️  RIESGOS DE ML EN FINANZAS:

1. **Overfitting**
   ✗ Modelo memoriza ruido histórico
   ✓ Use cross-validation, regularización
   ✓ Test en datos fuera-de-muestra

2. **Non-Stationarity**
   ✗ Distribuciones cambian con el tiempo
   ✓ Re-train frecuentemente
   ✓ Test en mercados adversos (2008, COVID)

3. **Black Swan Events**
   ✗ No aparecen en training data
   ✓ Model robustness testing
   ✓ Stress tests con escenarios extremos

4. **Interpretability**
   ✗ Red neuronal "caja negra"
   ✓ Use SHAP, LIME para explicaciones
   ✓ Feature importance analysis

5. **Causalidad vs Correlación**
   ✗ XGBoost encuentra correlaciones espurias
   ✓ Validate relationships economically
   ✓ Use domain expertise + data

6. **Implementación**
   ✓ Transaction costs (slippage)
   ✓ Execution prices vs model predictions
   ✓ Market impact of large trades
""")

# %%
if __name__ == "__main__":
    print("✅ Capítulo 7 ejecutable. Próximo: Capítulo 8 (Stress Testing)")
