# KrishiMulya AI (ಕೃಷಿಮೌಲ್ಯ AI)
### AI-Based Crop Price Prediction & Explainable Decision Support System for Farmers
**MCA Final Year Capstone Project · Karnataka APMC Market Intelligence Platform**

---

## 1. Executive Summary

**KrishiMulya AI** is an advanced, production-grade agricultural technology platform developed to solve price volatility and market asymmetry for farmers across Karnataka. Unlike black-box ML predictors or simple demo prototypes, this system integrates **verified AGMARKNET mandi records**, direct **multi-horizon XGBoost forecasting (7, 15, 30 days)**, **Explainable AI via SHAP (TreeExplainer)**, and a **comprehensive Smart Selling Decision Support Engine** that accounts for post-harvest holding costs, crop perishability, and freight distance.

---

## 2. Key Modules & Features

| Module | Features & Capabilities |
| :--- | :--- |
| **Farmer Dashboard** | Real-time Karnataka APMC ticker (Tomato, Onion, Potato, etc.), key statistics, quick-predict shortcuts, recent forecasts, and target price alerts. |
| **Multi-Horizon Prediction** | Direct horizon regression models ($t+7\text{d}$, $t+15\text{d}$, $t+30\text{d}$) avoiding recursive data leakage. Lag prices (1, 7, 15, 30), moving averages, supply arrival dynamics, and weather indices. |
| **Explainable AI (SHAP)** | Calculates exact SHAP values per prediction via `shap.TreeExplainer`. Interactive Waterfall Plot, top positive/negative drivers in ₹/quintal, and dual-language (English / Kannada) natural language summaries. Reconciled to $Base + \sum SHAP = Predicted$. |
| **Smart Selling Recommendation** | Decision tree accounting for **Crop Perishability** (e.g. 5-day shelf life of Tomato vs 180-day Maize), storage rates (₹/Q/day), post-harvest spoilage buffers, and farmer liquidity urgency. |
| **Market Comparison** | Cross-mandi price matrix comparing Bengaluru, Mysuru, Hubballi, and Mandya. Evaluates raw mandi prices against net proceeds after deducting farm-gate transport freight. |
| **Saved Crops & Alerts** | Farmer personalized watchlist with target price thresholds and automated notifications. |
| **Admin Operations** | User management, CSV dataset ingestion with schema and price integrity validation, chronological model retraining triggers, and test set accuracy dashboards. |
| **Dual Language UI** | Instant 1-click toggle between **English** and **ಕನ್ನಡ (Kannada)** across all pages and AI explanations. |

---

## 3. Technology Stack

- **Frontend:** React.js 19, Recharts 3.11, Lucide React, Axios, React Router 7, Modern Agricultural Design System (`index.css`)
- **Backend:** Python 3.13 Flask, RESTful APIs, Flask-CORS, PyJWT, Werkzeug Security
- **Database:** MongoDB (`crop_price_ai`) with seamless local persistent fallback (`local_store.json`) for offline grading
- **Machine Learning & XAI:** Scikit-learn, XGBoost Regressor (Primary), Random Forest Regressor, Seasonal Baseline, SHAP (TreeExplainer), Joblib

---

## 4. Supported Karnataka Commodities & APMC Mandis

- **Crops (8 Commodities):**
  1. Tomato *(Highly Perishable, ~5d shelf life)*
  2. Onion *(Semi-Perishable, ~45d shelf life)*
  3. Potato *(Semi-Perishable, ~60d shelf life)*
  4. Cabbage *(Medium-High Perishable, ~10d shelf life)*
  5. Green Chilli *(Highly Perishable, ~6d shelf life)*
  6. Rice *(Non-Perishable Cereal, ~365d shelf life)*
  7. Maize *(Non-Perishable Cereal, ~180d shelf life)*
  8. Groundnut *(Non-Perishable Oilseed, ~180d shelf life)*
- **Agricultural Markets:**
  - Bengaluru APMC (Bengaluru Urban)
  - Mysuru Bandipalya APMC (Mysuru)
  - Hubballi Amargol APMC (Dharwad)
  - Mandya APMC (Mandya)

---

## 5. Model Evaluation Metrics (Out-of-Sample Test Set: 2025 Unseen Data)

Evaluated chronologically across 11,400+ daily mandi observations:

| Model Architecture | 7-Day MAE (₹/Q) | 7-Day RMSE (₹/Q) | 7-Day $R^2$ Score | 15-Day MAE | 30-Day MAE |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost Regressor (Primary)** | **₹38.40** | **₹52.03** | **0.9981** | **₹41.26** | **₹43.88** |
| Random Forest Regressor | ₹38.33 | ₹52.19 | 0.9981 | ₹40.07 | ₹41.51 |
| Seasonal Historical Baseline | ₹43.81 | ₹60.18 | 0.9975 | ₹43.65 | ₹43.72 |

*Note: Models and evaluation reports are serialized under `ml/saved_models/` and `ml/evaluation/`.*

---

## 6. Project Directory Architecture

```text
crop_price_prediction_mini/
├── backend/
│   ├── app.py                      # Flask Application Factory & Server Entrypoint
│   ├── test_api.py                 # Automated API & ML Integration Test Suite
│   ├── database/
│   │   ├── db.py                   # MongoDB Client with persistent mongomock fallback
│   │   └── local_store.json        # Persistent JSON store for offline grading
│   ├── routes/
│   │   ├── admin_routes.py         # CSV Ingestion, Training trigger, User management
│   │   ├── auth_routes.py          # Registration, JWT Login, Profile
│   │   ├── farmer_routes.py        # Dashboard KPIs, Saved Crops, Price Alerts
│   │   ├── market_routes.py        # Live Ticker, Cross-Mandi Comparison
│   │   └── prediction_routes.py    # Predict API with SHAP & Decision Support
│   └── services/
│       ├── auth_service.py         # JWT tokens & RBAC decorators
│       ├── explanation_service.py  # SHAP TreeExplainer & Natural Language synthesis
│       ├── prediction_service.py   # Feature generation & forecast pipeline
│       └── recommendation_service.py # Smart Selling Decision Engine
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Navbar, Sidebar, WaterfallPlot
│   │   ├── context/                # AuthContext, LanguageContext (EN/KN)
│   │   ├── pages/
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── FarmerDashboard.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── MarketComparisonPage.jsx
│   │   │   ├── PredictionHistoryPage.jsx
│   │   │   ├── PredictionPage.jsx
│   │   │   └── PredictionResultPage.jsx
│   │   ├── services/api.js         # Axios interceptor instance
│   │   ├── App.jsx                 # Client routes
│   │   └── index.css               # Agricultural Theme Design System
│   └── package.json
│
├── ml/
│   ├── data/
│   │   ├── karnataka_mandi_prices.csv   # Standardized 46,720 AGMARKNET records
│   │   └── engineered_features.csv      # Complete engineered matrix
│   ├── evaluation/
│   │   └── model_evaluation_report.json # Overall, crop-wise, market-wise metrics
│   ├── saved_models/                    # Trained Joblib pipelines (7d, 15d, 30d)
│   └── training/
│       ├── data_pipeline.py             # Data ingestion, validation, and feature engineering
│       └── train_models.py              # Chronological model training & evaluation
│
├── documentation/
│   └── ARCHITECTURE.md             # Detailed System & Data Flow Specification
├── run_app.py                      # Unified Launcher Script (Backend + Frontend + Browser)
├── run_app.bat                     # 1-Click Windows Batch Launcher
└── README.md
```

---

## 7. How to Run the Application

### Option A: Unified 1-Click Launcher (Recommended)
Simply open PowerShell or Terminal in the root folder and run:

```powershell
python run_app.py
```
*(Or double-click `run_app.bat` in Windows Explorer)*

This automatically:
1. Boots the Flask REST API on `http://localhost:5000`
2. Boots the React Vite Frontend on `http://localhost:5173`
3. Opens the portal directly in your default web browser!

---

### Option B: Running Services Separately

**1. Start the Flask Backend:**
```powershell
$env:PYTHONPATH="."
python -m backend.app
```
*Health Check: `http://localhost:5000/api/health`*

**2. Start the React Frontend:**
```powershell
cd frontend
npm run dev
```
*Web Portal: `http://localhost:5173`*

---

## 8. Demonstration Credentials

For quick evaluation during project demonstration, 1-click login buttons are provided on the Sign In page:

- **Farmer Role:**
  - Email: `farmer@karnataka.gov`
  - Password: `Farmer@123`
- **Administrator Role:**
  - Email: `admin@cropprice.ai`
  - Password: `Admin@123`

---

## 9. Automated Testing

To run the automated end-to-end backend and ML test suite:

```powershell
python -m backend.test_api
```
Tests all 8 core workflows:
1. Server health check
2. Farmer authentication
3. Admin authentication
4. Real-time mandi price feed
5. Multi-horizon prediction with SHAP additivity reconciliation
6. Cross-mandi comparative analysis with freight deduction
7. Saved crop target price alerts
8. Admin overview & model performance telemetry
