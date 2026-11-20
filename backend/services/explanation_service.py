"""
Explainable AI (SHAP) Service
Provides exact SHAP values, feature importance, waterfall data,
and dynamic natural language explanations for agricultural price forecasts.
"""

import os
import joblib
import numpy as np
import pandas as pd
import shap

FEATURE_HUMAN_NAMES = {
    "num__price_lag_1": "Latest daily price recorded",
    "num__price_lag_7": "Price recorded 7 days ago",
    "num__price_lag_15": "Price recorded 15 days ago",
    "num__price_lag_30": "Price recorded 30 days ago",
    "num__price_ma_7": "7-day moving average price",
    "num__price_ma_15": "15-day moving average price",
    "num__price_ma_30": "30-day moving average price",
    "num__price_volatility_7": "7-day price volatility",
    "num__market_arrivals": "Market arrivals today (quintals)",
    "num__arrivals_lag_1": "Previous day market arrivals",
    "num__arrivals_ma_7": "7-day average market arrivals",
    "num__arrivals_change_7d": "7-day change in market supply",
    "num__rainfall": "Rainfall recorded (mm)",
    "num__temperature": "Ambient temperature (°C)",
    "num__humidity": "Relative humidity (%)",
    "num__month": "Seasonal calendar month",
    "cat__commodity_Tomato": "Tomato commodity baseline",
    "cat__commodity_Onion": "Onion commodity baseline",
    "cat__commodity_Potato": "Potato commodity baseline",
    "cat__commodity_Cabbage": "Cabbage commodity baseline",
    "cat__commodity_Green Chilli": "Green Chilli commodity baseline",
    "cat__commodity_Rice": "Rice commodity baseline",
    "cat__commodity_Maize": "Maize commodity baseline",
    "cat__commodity_Groundnut": "Groundnut commodity baseline",
    "cat__market_Bengaluru": "Bengaluru APMC market factor",
    "cat__market_Mysuru": "Mysuru Bandipalya market factor",
    "cat__market_Hubballi": "Hubballi Amargol market factor",
    "cat__market_Mandya": "Mandya APMC market factor",
    "cat__season_Kharif": "Kharif season cycle",
    "cat__season_Rabi": "Rabi season cycle",
    "cat__season_Summer": "Summer season cycle"
}

FEATURE_HUMAN_NAMES_KN = {
    "num__price_lag_1": "ಇತ್ತೀಚಿನ ದೈನಂದಿನ ಬೆಲೆ",
    "num__price_lag_7": "7 ದಿನಗಳ ಹಿಂದಿನ ಬೆಲೆ",
    "num__price_lag_15": "15 ದಿನಗಳ ಹಿಂದಿನ ಬೆಲೆ",
    "num__price_lag_30": "30 ದಿನಗಳ ಹಿಂದಿನ ಬೆಲೆ",
    "num__price_ma_7": "7 ದಿನಗಳ ಸರಾಸರಿ ಬೆಲೆ",
    "num__price_ma_15": "15 ದಿನಗಳ ಸರಾಸರಿ ಬೆಲೆ",
    "num__price_ma_30": "30 ದಿನಗಳ ಸರಾಸರಿ ಬೆಲೆ",
    "num__price_volatility_7": "7 ದಿನಗಳ ಬೆಲೆ ಏರಿಳಿತ",
    "num__market_arrivals": "ಮಾರುಕಟ್ಟೆ ಆವಕ ಪ್ರಮಾಣ (ಕ್ವಿಂಟಾಲ್)",
    "num__arrivals_lag_1": "ಹಿಂದಿನ ದಿನದ ಆವಕ",
    "num__arrivals_ma_7": "7 ದಿನಗಳ ಸರಾಸರಿ ಆವಕ",
    "num__arrivals_change_7d": "ಆವಕ ಪೂರೈಕೆಯ 7 ದಿನಗಳ ಬದಲಾವಣೆ",
    "num__rainfall": "ಮಳೆ ಪ್ರಮಾಣ (ಮಿ.ಮೀ)",
    "num__temperature": "ತಾಪಮಾನ (°C)",
    "num__humidity": "ಆರ್ದ್ರತೆ (%)",
    "num__month": "ಋತುಮಾನ ತಿಂಗಳು",
    "cat__commodity_Tomato": "ಟೊಮೆಟೊ ಬೆಳೆ ಮೂಲಬೆಲೆ",
    "cat__commodity_Onion": "ಈರುಳ್ಳಿ ಬೆಳೆ ಮೂಲಬೆಲೆ",
    "cat__commodity_Potato": "ಆಲೂಗಡ್ಡೆ ಬೆಳೆ ಮೂಲಬೆಲೆ",
    "cat__commodity_Cabbage": "ಎಲೆಕೋಸು ಬೆಳೆ ಮೂಲಬೆಲೆ",
    "cat__commodity_Green Chilli": "ಹಸಿರು ಮೆಣಸಿನಕಾಯಿ ಮೂಲಬೆಲೆ",
    "cat__commodity_Rice": "ಅಕ್ಕಿ ಬೆಳೆ ಮೂಲಬೆಲೆ",
    "cat__commodity_Maize": "ಮೆಕ್ಕೆಜೋಳ ಮೂಲಬೆಲೆ",
    "cat__commodity_Groundnut": "ಕಡಲೆಕಾಯಿ ಮೂಲಬೆಲೆ",
    "cat__market_Bengaluru": "ಬೆಂಗಳೂರು ಮಾರುಕಟ್ಟೆ ಅಂಶ",
    "cat__market_Mysuru": "ಮೈಸೂರು ಬಂಡಿಪಾಳ್ಯ ಮಾರುಕಟ್ಟೆ ಅಂಶ",
    "cat__market_Hubballi": "ಹುಬ್ಬಳ್ಳಿ ಅಮರಗೋಳ ಮಾರುಕಟ್ಟೆ ಅಂಶ",
    "cat__market_Mandya": "ಮಂಡ್ಯ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ ಅಂಶ",
    "cat__season_Kharif": "ಖಾರೀಫ್ ಋತುಮಾನ",
    "cat__season_Rabi": "ರಬಿ ಋತುಮಾನ",
    "cat__season_Summer": "ಬೇಸಿಗೆ ಋತುಮಾನ"
}

_models_cache = {}

def get_model(horizon=7):
    global _models_cache
    if horizon not in _models_cache:
        model_path = os.path.join("ml", "saved_models", f"model_xgb_{horizon}d_v1.joblib")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Trained model not found at {model_path}")
        _models_cache[horizon] = joblib.load(model_path)
    return _models_cache[horizon]

def explain_prediction(features_dict: dict, horizon=7):
    """
    Computes exact SHAP values for an individual prediction row.
    Returns:
      - base_value (INR)
      - predicted_price (INR)
      - waterfall_data (array for Recharts waterfall plot)
      - positive_factors (list)
      - negative_factors (list)
      - natural_language_explanation_en (string)
      - natural_language_explanation_kn (string)
      - reconciliation_diff (float)
    """
    pipeline = get_model(horizon)
    prep = pipeline.named_steps["prep"]
    xgb = pipeline.named_steps["xgb"]
    
    # Order features correctly
    cat_cols = ["commodity", "market", "season"]
    num_cols = [
        "month",
        "price_lag_1", "price_lag_7", "price_lag_15", "price_lag_30",
        "price_ma_7", "price_ma_15", "price_ma_30", "price_volatility_7",
        "market_arrivals", "arrivals_lag_1", "arrivals_ma_7", "arrivals_change_7d",
        "rainfall", "temperature", "humidity"
    ]
    all_cols = cat_cols + num_cols
    
    input_df = pd.DataFrame([features_dict])[all_cols]
    transformed = prep.transform(input_df)
    feature_names = prep.get_feature_names_out()
    
    explainer = shap.TreeExplainer(xgb)
    shap_results = explainer(transformed)
    
    base_value = float(shap_results.base_values[0])
    shap_values = shap_results.values[0]
    predicted_price = float(xgb.predict(transformed)[0])
    
    # Mathematical reconciliation
    sum_contributions = float(np.sum(shap_values))
    reconciled_sum = base_value + sum_contributions
    reconciliation_diff = abs(predicted_price - reconciled_sum)
    
    items = []
    for idx, (name, val) in enumerate(zip(feature_names, shap_values)):
        val_float = float(val)
        human_name = FEATURE_HUMAN_NAMES.get(name, name.replace("num__", "").replace("cat__", ""))
        human_name_kn = FEATURE_HUMAN_NAMES_KN.get(name, human_name)
        items.append({
            "feature_id": name,
            "feature_name": human_name,
            "feature_name_kn": human_name_kn,
            "contribution": round(val_float, 2),
            "abs_contribution": round(abs(val_float), 2),
            "direction": "up" if val_float >= 0 else "down"
        })
        
    items_sorted = sorted(items, key=lambda x: x["abs_contribution"], reverse=True)
    
    positive_factors = [x for x in items_sorted if x["contribution"] > 0][:5]
    negative_factors = [x for x in items_sorted if x["contribution"] < 0][:5]
    top_contributors = items_sorted[:8]
    
    # Build Waterfall structure
    waterfall_data = []
    current_acc = round(base_value, 2)
    waterfall_data.append({
        "name": "State Baseline",
        "name_kn": "ರಾಜ್ಯ ಸರಾಸರಿ",
        "start": 0,
        "amount": round(base_value, 2),
        "total": round(base_value, 2),
        "type": "baseline"
    })
    
    for item in top_contributors:
        start_val = current_acc
        current_acc = round(current_acc + item["contribution"], 2)
        waterfall_data.append({
            "name": item["feature_name"],
            "name_kn": item["feature_name_kn"],
            "start": start_val,
            "amount": item["contribution"],
            "total": current_acc,
            "type": "positive" if item["contribution"] >= 0 else "negative"
        })
        
    waterfall_data.append({
        "name": "Final Predicted Price",
        "name_kn": "ಅಂತಿಮ ಅಂದಾಜು ಬೆಲೆ",
        "start": 0,
        "amount": round(predicted_price, 2),
        "total": round(predicted_price, 2),
        "type": "final"
    })
    
    # Generate Natural Language Explanations
    crop = features_dict.get("commodity", "Crop")
    market = features_dict.get("market", "Karnataka Mandi")
    
    pos_summary = ", ".join([f"{f['feature_name']} (+₹{f['contribution']:,.1f})" for f in positive_factors[:2]])
    neg_summary = ", ".join([f"{f['feature_name']} (-₹{abs(f['contribution']):,.1f})" for f in negative_factors[:2]])
    
    pos_summary_kn = ", ".join([f"{f['feature_name_kn']} (+₹{f['contribution']:,.1f})" for f in positive_factors[:2]])
    neg_summary_kn = ", ".join([f"{f['feature_name_kn']} (-₹{abs(f['contribution']):,.1f})" for f in negative_factors[:2]])
    
    nl_en = f"The XGBoost model forecasts a {horizon}-day price of ₹{predicted_price:,.0f}/quintal for {crop} at {market} Mandi. "
    if abs(predicted_price - base_value) < 50:
        nl_en += f"The forecast is close to the statewide baseline of ₹{base_value:,.0f}/quintal. "
    elif predicted_price > base_value:
        nl_en += f"This forecast is ₹{predicted_price - base_value:,.0f} higher than the state baseline of ₹{base_value:,.0f}/quintal. "
    else:
        nl_en += f"This forecast is ₹{base_value - predicted_price:,.0f} lower than the state baseline of ₹{base_value:,.0f}/quintal. "
        
    if positive_factors:
        nl_en += f"Main positive price drivers include: {pos_summary}. "
    if negative_factors:
        nl_en += f"Main downward pressures include: {neg_summary}. "
    nl_en += "Note: SHAP reflects empirical machine learning correlations and historical price dynamics rather than guaranteed market causation."
    
    nl_kn = f"{market} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {crop} ಬೆಳೆಗೆ {horizon} ದಿನಗಳ ನಂತರ ಅಂದಾಜು ಬೆಲೆ ಕ್ವಿಂಟಾಲ್‌ಗೆ ₹{predicted_price:,.0f} ಆಗಿದೆ. "
    if positive_factors:
        nl_kn += f"ಬೆಲೆ ಹೆಚ್ಚಳಕ್ಕೆ ಕಾರಣವಾದ ಅಂಶಗಳು: {pos_summary_kn}. "
    if negative_factors:
        nl_kn += f"ಬೆಲೆ ಇಳಿಕೆಗೆ ಕಾರಣವಾದ ಅಂಶಗಳು: {neg_summary_kn}. "
    nl_kn += "ಗಮನಿಸಿ: ಈ ವಿಶ್ಲೇಷಣೆಯು ಐತಿಹಾಸಿಕ ಮಾರುಕಟ್ಟೆ ದತ್ತಾಂಶ ಮತ್ತು ಯಂತ್ರ ಕಲಿಕೆ ಮಾದರಿಯನ್ನು ಆಧರಿಸಿದೆ."
    
    return {
        "base_value": round(base_value, 2),
        "predicted_price": round(predicted_price, 2),
        "reconciliation_diff": round(reconciliation_diff, 4),
        "top_contributors": top_contributors,
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "waterfall_data": waterfall_data,
        "natural_language_en": nl_en,
        "natural_language_kn": nl_kn
    }

if __name__ == "__main__":
    sample_features = {
        "commodity": "Tomato",
        "market": "Bengaluru",
        "season": "Rabi",
        "month": 11,
        "price_lag_1": 2200.0,
        "price_lag_7": 2150.0,
        "price_lag_15": 2080.0,
        "price_lag_30": 1950.0,
        "price_ma_7": 2180.0,
        "price_ma_15": 2120.0,
        "price_ma_30": 2040.0,
        "price_volatility_7": 35.0,
        "market_arrivals": 120.0,
        "arrivals_lag_1": 125.0,
        "arrivals_ma_7": 118.0,
        "arrivals_change_7d": 0.017,
        "rainfall": 2.5,
        "temperature": 27.0,
        "humidity": 65.0
    }
    exp = explain_prediction(sample_features, horizon=7)
    print("Base Value:", exp["base_value"])
    print("Predicted:", exp["predicted_price"])
    print("Reconciliation Diff:", exp["reconciliation_diff"])
    print("\nEnglish Explanation:\n", exp["natural_language_en"])
    print("\nKannada Explanation:\n", exp["natural_language_kn"])
