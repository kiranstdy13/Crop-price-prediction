# AI-Based Crop Price Prediction – Mini Project

A compact Streamlit application demonstrating:
- Multi-crop / multi-market price estimation
- XGBoost regression
- SHAP feature contribution explanations
- Historical trend visualization
- Basic decision-support messaging

## Important data limitation
The included `data/demo_crop_prices.csv` is **simulated demonstration data**, not official AGMARKNET data. Do not report its predictions or evaluation metrics as real market results. Replace it with verified historical mandi data before academic submission.

## Setup (Windows PowerShell)

```powershell
cd crop_price_prediction_mini
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## CSV schema

The app expects `data/demo_crop_prices.csv` with columns:

`date,crop,market,modal_price,arrivals,rainfall_mm,temperature_c,humidity`

The app derives `price_lag_1`, `price_avg_7`, and `month` from the data and prediction inputs.

## Replace the demo data
1. Download verified daily modal prices and arrivals from AGMARKNET or data.gov.in.
2. Standardize prices to INR/quintal and arrivals to quintals.
3. Join weather observations by date and a defensible market/location mapping.
4. Keep one row per date-crop-market combination.
5. Save the prepared file using the schema above.
6. Retrain and evaluate chronologically. For research-grade results, build forecast targets and features strictly as-of each forecast origin, and evaluate on later unseen dates.

## Current mini-project limitations
- The 7/15/30-day selection changes the forecast month and the displayed forecast date; it is a teaching baseline, not a validated multi-horizon time-series model.
- Future arrivals and weather are user-entered assumptions.
- The app uses a simple chronological holdout and should be extended to rolling-origin backtesting.
- A global model is trained on all bundled crop-market records. Report per-crop/per-market errors when using real data.
- SHAP explains model associations, not causal effects.

## Suggested next improvements
- Train separate direct forecast targets for 7, 15 and 30 days.
- Add walk-forward validation and prediction intervals.
- Add Kannada language support and a proper farmer/admin login.
- Move model training to a separate script and save versioned model artifacts.
