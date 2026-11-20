"""
Model Training and Serialization Script
Trains Random Forest Regressor, XGBoost Regressor, and Seasonal Baseline Model
across multiple forecast horizons (7, 15, 30 days) with strict chronological splits.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

CAT_FEATURES = ["commodity", "market", "season"]
NUM_FEATURES = [
    "month",
    "price_lag_1", "price_lag_7", "price_lag_15", "price_lag_30",
    "price_ma_7", "price_ma_15", "price_ma_30", "price_volatility_7",
    "market_arrivals", "arrivals_lag_1", "arrivals_ma_7", "arrivals_change_7d",
    "rainfall", "temperature", "humidity"
]
ALL_FEATURES = CAT_FEATURES + NUM_FEATURES

class SeasonalBaselineModel:
    """
    Seasonal naive baseline: predicts based on recent moving average 
    and monthly historical seasonal index.
    """
    def __init__(self):
        self.crop_market_month_multipliers = {}
        self.global_mean = 2000.0
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        df = X.copy()
        df["target"] = y.values
        self.global_mean = float(y.mean())
        grouped = df.groupby(["commodity", "market", "month"])["target"].mean().to_dict()
        self.crop_market_month_multipliers = grouped
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = []
        for _, row in X.iterrows():
            key = (row["commodity"], row["market"], int(row["month"]))
            if key in self.crop_market_month_multipliers:
                pred = self.crop_market_month_multipliers[key]
            else:
                pred = row.get("price_ma_7", self.global_mean)
            preds.append(float(pred))
        return np.array(preds)

def get_preprocessor():
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
        ("num", "passthrough", NUM_FEATURES)
    ])

def train_all_models(data_path="ml/data/engineered_features.csv", output_dir="ml/saved_models"):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    
    # Chronological Split
    train_mask = df["date"] < "2024-07-01"
    val_mask = (df["date"] >= "2024-07-01") & (df["date"] < "2025-01-01")
    test_mask = df["date"] >= "2025-01-01"
    
    train_df = df[train_mask]
    val_df = df[val_mask]
    test_df = df[test_mask]
    
    print(f"Dataset split - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    horizons = [7, 15, 30]
    comparison_results = {}
    
    for h in horizons:
        target_col = f"target_{h}d"
        print(f"\n--- Training Models for Horizon: {h} Days ---")
        
        # Drop rows where target is NaN (at the end of series)
        tr = train_df.dropna(subset=[target_col])
        va = val_df.dropna(subset=[target_col])
        te = test_df.dropna(subset=[target_col])
        
        X_tr, y_tr = tr[ALL_FEATURES], tr[target_col]
        X_va, y_va = va[ALL_FEATURES], va[target_col]
        X_te, y_te = te[ALL_FEATURES], te[target_col]
        
        # 1. Seasonal Baseline
        baseline = SeasonalBaselineModel()
        baseline.fit(X_tr, y_tr)
        base_pred = baseline.predict(X_te)
        base_metrics = {
            "MAE": round(float(mean_absolute_error(y_te, base_pred)), 2),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_te, base_pred))), 2),
            "R2": round(float(r2_score(y_te, base_pred)), 4)
        }
        print(f"Seasonal Baseline ({h}d) -> MAE: ₹{base_metrics['MAE']}, RMSE: ₹{base_metrics['RMSE']}, R²: {base_metrics['R2']}")
        
        # 2. Random Forest Regressor
        rf_pipe = Pipeline([
            ("prep", get_preprocessor()),
            ("rf", RandomForestRegressor(
                n_estimators=100, max_depth=12, min_samples_split=5,
                random_state=42, n_jobs=-1
            ))
        ])
        rf_pipe.fit(X_tr, y_tr)
        rf_pred = rf_pipe.predict(X_te)
        rf_metrics = {
            "MAE": round(float(mean_absolute_error(y_te, rf_pred)), 2),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_te, rf_pred))), 2),
            "R2": round(float(r2_score(y_te, rf_pred)), 4)
        }
        print(f"Random Forest ({h}d)     -> MAE: ₹{rf_metrics['MAE']}, RMSE: ₹{rf_metrics['RMSE']}, R²: {rf_metrics['R2']}")
        
        # 3. XGBoost Regressor (Primary candidate)
        xgb_pipe = Pipeline([
            ("prep", get_preprocessor()),
            ("xgb", XGBRegressor(
                n_estimators=250, max_depth=5, learning_rate=0.04,
                subsample=0.85, colsample_bytree=0.85,
                objective="reg:squarederror", random_state=42, n_jobs=-1
            ))
        ])
        xgb_pipe.fit(X_tr, y_tr)
        xgb_pred = xgb_pipe.predict(X_te)
        xgb_metrics = {
            "MAE": round(float(mean_absolute_error(y_te, xgb_pred)), 2),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_te, xgb_pred))), 2),
            "R2": round(float(r2_score(y_te, xgb_pred)), 4)
        }
        print(f"XGBoost Regressor ({h}d) -> MAE: ₹{xgb_metrics['MAE']}, RMSE: ₹{xgb_metrics['RMSE']}, R²: {xgb_metrics['R2']}")
        
        # Per-crop and per-market breakdown for XGBoost on Test Set
        crop_metrics = {}
        for crop_name in te["commodity"].unique():
            idx = te["commodity"] == crop_name
            crop_metrics[crop_name] = {
                "MAE": round(float(mean_absolute_error(y_te[idx], xgb_pred[idx])), 2),
                "RMSE": round(float(np.sqrt(mean_squared_error(y_te[idx], xgb_pred[idx]))), 2),
                "R2": round(float(r2_score(y_te[idx], xgb_pred[idx])), 4)
            }
            
        market_metrics = {}
        for mkt_name in te["market"].unique():
            idx = te["market"] == mkt_name
            market_metrics[mkt_name] = {
                "MAE": round(float(mean_absolute_error(y_te[idx], xgb_pred[idx])), 2),
                "RMSE": round(float(np.sqrt(mean_squared_error(y_te[idx], xgb_pred[idx]))), 2),
                "R2": round(float(r2_score(y_te[idx], xgb_pred[idx])), 4)
            }
            
        comparison_results[f"{h}d"] = {
            "horizon_days": h,
            "test_sample_size": len(y_te),
            "baseline": base_metrics,
            "random_forest": rf_metrics,
            "xgboost": xgb_metrics,
            "crop_wise_xgboost": crop_metrics,
            "market_wise_xgboost": market_metrics
        }
        
        # Save models
        joblib.dump(xgb_pipe, os.path.join(output_dir, f"model_xgb_{h}d_v1.joblib"))
        joblib.dump(rf_pipe, os.path.join(output_dir, f"model_rf_{h}d_v1.joblib"))
        joblib.dump(baseline, os.path.join(output_dir, f"model_baseline_{h}d_v1.joblib"))
        
    # Save overall metadata & evaluation metrics
    meta = {
        "model_version": "v1.0.0",
        "trained_at": datetime.now().isoformat(),
        "state": "Karnataka",
        "supported_crops": sorted(df["commodity"].unique().tolist()),
        "supported_markets": sorted(df["market"].unique().tolist()),
        "horizons": horizons,
        "features": {
            "categorical": CAT_FEATURES,
            "numerical": NUM_FEATURES,
            "all": ALL_FEATURES
        },
        "evaluation": comparison_results
    }
    
    meta_path = os.path.join(output_dir, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
        
    eval_path = "ml/evaluation/model_evaluation_report.json"
    os.makedirs(os.path.dirname(eval_path), exist_ok=True)
    with open(eval_path, "w") as f:
        json.dump(comparison_results, f, indent=2)
        
    print(f"\nTraining complete. Saved artifacts to {output_dir}/ and {eval_path}")
    return comparison_results

if __name__ == "__main__":
    train_all_models()
