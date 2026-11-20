# System Architecture & Technical Specification

## 1. High-Level Architectural Diagram

```mermaid
flowchart TD
    subgraph Data_Layer ["Data & Ingestion Pipeline"]
        A1["AGMARKNET Historical Mandi Records (Karnataka APMCs)"]
        A2["IMD Weather Observations (Rainfall, Temp, Humidity)"]
        A3["Admin CSV Ingestion & Validation Gateway"]
        A1 --> B["Data Preprocessing & Schema Validation"]
        A2 --> B
        A3 --> B
        B --> C["Time-Series Feature Engineering (Lags, MAs, Volatility, Arrivals)"]
        C --> D["Engineered Dataset (ml/data/engineered_features.csv)"]
    end

    subgraph ML_Layer ["Machine Learning & XAI Subsystem"]
        D --> E["Chronological Holdout Split (Train: <2024-07, Val: 2024-H2, Test: 2025)"]
        E --> F1["XGBoost Regressors (Direct 7d, 15d, 30d Horizons)"]
        E --> F2["Random Forest Regressors (Benchmark)"]
        E --> F3["Seasonal Baseline Multipliers"]
        F1 --> G["SHAP TreeExplainer Attribution Engine"]
        F1 --> H["Joblib Model Serialization (ml/saved_models/)"]
    end

    subgraph Backend_Layer ["Flask REST Backend (Port 5000)"]
        H --> I["Prediction Service & Feature Generator"]
        G --> J["SHAP Explanation Service (Waterfall + NL Summaries)"]
        I --> K["Decision Support & Smart Selling Recommendation Engine"]
        K --> L["Flask Blueprints (/auth, /predictions, /markets, /farmer, /admin)"]
        L <--> M["MongoDB / Persistent Local Store (local_store.json)"]
    end

    subgraph Frontend_Layer ["React 19 Frontend (Port 5173)"]
        L <--> N["Axios API Client (src/services/api.js)"]
        N --> O["Auth & Language Contexts (EN / KN)"]
        O --> P1["Farmer Dashboard (Live Karnataka Tickers & KPIs)"]
        O --> P2["Prediction & Results (Recharts Trend + SHAP Waterfall)"]
        O --> P3["Market Comparison (Bengaluru, Mysuru, Hubballi, Mandya)"]
        O --> P4["Saved Crops Watchlist & Target Price Alerts"]
        O --> P5["Admin Operations (CSV Upload & Model Telemetry)"]
    end
```

---

## 2. SHAP Explainability & Additivity Axiom

For any tree-based prediction $\hat{y} = f(x)$, the SHAP attribution guarantees:

$$\hat{y} = \phi_0 + \sum_{i=1}^{M} \phi_i(x)$$

Where:
- $\phi_0 = \mathbb{E}[f(x)]$: The expected baseline price across Karnataka APMC mandis (approx. ₹2,514.70/quintal).
- $\phi_i(x)$: The marginal contribution of feature $i$ in ₹/quintal.
- Reconciled difference $|\hat{y} - (\phi_0 + \sum \phi_i)| < 0.001$, verified dynamically on every prediction.

---

## 3. Decision-Support Engine Formulation

The recommendation engine computes the estimated net economic gain:

$$\Delta P_{net} = (P_{pred} - P_{curr}) - (H \times C_{storage}) - (P_{curr} \times R_{spoilage}) - C_{transport}$$

Where:
- $P_{curr}$: Current mandi modal price.
- $P_{pred}$: Horizon-predicted future price ($H \in \{7, 15, 30\}$ days).
- $C_{storage}$: Daily crop holding expense (INR / quintal / day).
- $R_{spoilage}$: Expected loss percentage based on ambient crop shelf life (e.g. 12% per week for Tomato without cold storage).
- $C_{transport}$: Freight cost per quintal from farm-gate to destination APMC.

### Recommendation Policies:
1. **Consider Selling Now:** If $\Delta P_{net} \le 0$, or if farmer urgency is "High", or if horizon $H >$ ambient shelf life for perishable crops without cold storage.
2. **Consider Waiting:** If $\Delta P_{net} > 0$ and net percentage gain $\ge 4.0\%$, with shelf life $\ge H$.
3. **Monitor Market Conditions:** If net price delta is marginal (between $-2\%$ and $+4\%$).
