"""
Agricultural Price Prediction Service.
Integrates feature generation from verified market records,
horizon-specific XGBoost execution, SHAP explanations, and decision support.
"""

import os
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from backend.database.db import get_db, sync_local_store
from backend.services.explanation_service import explain_prediction
from backend.services.recommendation_service import generate_selling_recommendation
from ml.training.data_pipeline import determine_season

def get_latest_market_series(commodity: str, market: str, limit=60) -> pd.DataFrame:
    """Fetch latest historical records from DB or CSV fallback."""
    db = get_db()
    cursor = db.market_prices.find(
        {"commodity": commodity, "market": market},
        {"_id": 0}
    ).sort("date", -1).limit(limit)
    
    records = list(cursor)
    if not records:
        # Check if crop exists in case of capitalization or fallback to CSV
        csv_path = os.path.join("ml", "data", "karnataka_mandi_prices.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            sub = df[(df["commodity"] == commodity) & (df["market"] == market)].sort_values("date")
            if not sub.empty:
                records = sub.tail(limit).to_dict(orient="records")
                
    if not records:
        raise ValueError(f"No historical mandi records found for {commodity} in {market} market.")
        
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df

def generate_prediction_and_insights(
    commodity: str,
    market: str,
    horizon_days: int = 7,
    user_id: str = "guest",
    assumptions: dict = None
) -> dict:
    if horizon_days not in [7, 15, 30]:
        horizon_days = 7
        
    assumptions = assumptions or {}
    
    # 1. Retrieve latest verified historical data
    hist_df = get_latest_market_series(commodity, market, limit=60)
    latest_row = hist_df.iloc[-1]
    current_price = float(latest_row["modal_price"])
    current_date = pd.to_datetime(latest_row["date"])
    forecast_date = current_date + pd.Timedelta(days=horizon_days)
    
    # 2. Extract price lag values
    price_lag_1 = current_price
    price_lag_7 = float(hist_df.iloc[-7]["modal_price"]) if len(hist_df) >= 7 else price_lag_1
    price_lag_15 = float(hist_df.iloc[-15]["modal_price"]) if len(hist_df) >= 15 else price_lag_7
    price_lag_30 = float(hist_df.iloc[-30]["modal_price"]) if len(hist_df) >= 30 else price_lag_15
    
    # Moving averages
    price_ma_7 = float(hist_df.tail(7)["modal_price"].mean())
    price_ma_15 = float(hist_df.tail(15)["modal_price"].mean())
    price_ma_30 = float(hist_df.tail(30)["modal_price"].mean())
    price_volatility_7 = float(hist_df.tail(7)["modal_price"].std()) if len(hist_df) >= 7 else 0.0
    if np.isnan(price_volatility_7):
        price_volatility_7 = 0.0
        
    # Arrivals & Weather: use verified historical unless user supplied custom assumption
    arrivals = float(assumptions.get("market_arrivals", latest_row.get("market_arrivals", 110.0)))
    arrivals_lag_1 = float(hist_df.iloc[-2]["market_arrivals"]) if len(hist_df) >= 2 else arrivals
    arrivals_ma_7 = float(hist_df.tail(7)["market_arrivals"].mean()) if "market_arrivals" in hist_df.columns else arrivals
    arrivals_change_7d = round(((arrivals - arrivals_ma_7) / (arrivals_ma_7 + 1e-5)), 4)
    
    rainfall = float(assumptions.get("rainfall", latest_row.get("rainfall", 2.0)))
    temperature = float(assumptions.get("temperature", latest_row.get("temperature", 28.0)))
    humidity = float(assumptions.get("humidity", latest_row.get("humidity", 65.0)))
    
    forecast_month = int(forecast_date.month)
    forecast_season = determine_season(forecast_month)
    
    feature_dict = {
        "commodity": commodity,
        "market": market,
        "season": forecast_season,
        "month": forecast_month,
        "price_lag_1": price_lag_1,
        "price_lag_7": price_lag_7,
        "price_lag_15": price_lag_15,
        "price_lag_30": price_lag_30,
        "price_ma_7": price_ma_7,
        "price_ma_15": price_ma_15,
        "price_ma_30": price_ma_30,
        "price_volatility_7": round(price_volatility_7, 2),
        "market_arrivals": round(arrivals, 2),
        "arrivals_lag_1": round(arrivals_lag_1, 2),
        "arrivals_ma_7": round(arrivals_ma_7, 2),
        "arrivals_change_7d": arrivals_change_7d,
        "rainfall": round(rainfall, 2),
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2)
    }
    
    # 3. Compute XGBoost prediction and exact SHAP explanation
    explanation = explain_prediction(feature_dict, horizon=horizon_days)
    predicted_price = explanation["predicted_price"]
    
    # 4. Compute metrics and direction
    price_diff = round(predicted_price - current_price, 2)
    pct_change = round((price_diff / current_price * 100), 2) if current_price > 0 else 0.0
    
    if pct_change >= 2.0:
        direction = "increasing"
        direction_label = "Price Expected to Rise"
        direction_label_kn = "ಬೆಲೆ ಏರಿಕೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ"
    elif pct_change <= -2.0:
        direction = "decreasing"
        direction_label = "Price Expected to Fall"
        direction_label_kn = "ಬೆಲೆ ಇಳಿಕೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ"
    else:
        direction = "stable"
        direction_label = "Price Expected to Remain Stable"
        direction_label_kn = "ಬೆಲೆ ಸ್ಥಿರವಾಗಿರುವ ಸಾಧ್ಯತೆಯಿದೆ"
        
    # 5. Smart Selling Recommendation
    urgency = assumptions.get("farmer_urgency", "Normal")
    has_cold_storage = assumptions.get("has_cold_storage", False)
    recommendation = generate_selling_recommendation(
        crop=commodity,
        market=market,
        current_price=current_price,
        predicted_price=predicted_price,
        horizon_days=horizon_days,
        farmer_urgency=urgency,
        has_cold_storage=has_cold_storage
    )
    
    # 6. Build Historical + Forecast Time Series for Recharts
    recent_trend = hist_df.tail(30).copy()
    chart_series = []
    for _, r in recent_trend.iterrows():
        d_str = pd.to_datetime(r["date"]).strftime("%Y-%m-%d")
        chart_series.append({
            "date": d_str,
            "display_date": pd.to_datetime(r["date"]).strftime("%d %b"),
            "historical_price": float(r["modal_price"]),
            "predicted_price": None,
            "type": "historical"
        })
        
    # Add forecast point
    fc_date_str = forecast_date.strftime("%Y-%m-%d")
    chart_series.append({
        "date": fc_date_str,
        "display_date": forecast_date.strftime("%d %b"),
        "historical_price": None,
        "predicted_price": float(predicted_price),
        "type": "forecast"
    })
    
    prediction_id = f"pred_{uuid.uuid4().hex[:12]}"
    created_at = datetime.now().isoformat()
    
    pred_document = {
        "id": prediction_id,
        "user_id": user_id,
        "commodity": commodity,
        "market": market,
        "state": "Karnataka",
        "district": latest_row.get("district", "Karnataka Mandi"),
        "horizon_days": horizon_days,
        "current_modal_price": current_price,
        "predicted_price": predicted_price,
        "price_change": price_diff,
        "pct_change": pct_change,
        "price_direction": direction,
        "direction_label": direction_label,
        "direction_label_kn": direction_label_kn,
        "model_name": f"XGBoost Regressor (Horizon {horizon_days}d v1.0)",
        "forecast_date": fc_date_str,
        "forecast_display_date": forecast_date.strftime("%d %B %Y"),
        "current_date": current_date.strftime("%Y-%m-%d"),
        "features_used": feature_dict,
        "explanation": {
            "base_value": explanation["base_value"],
            "top_contributors": explanation["top_contributors"],
            "positive_factors": explanation["positive_factors"],
            "negative_factors": explanation["negative_factors"],
            "waterfall_data": explanation["waterfall_data"],
            "natural_language_en": explanation["natural_language_en"],
            "natural_language_kn": explanation["natural_language_kn"],
            "reconciliation_diff": explanation["reconciliation_diff"]
        },
        "recommendation": recommendation,
        "chart_data": chart_series,
        "created_at": created_at
    }
    
    # Store in MongoDB
    db = get_db()
    db.predictions.insert_one(pred_document)
    
    # Check if this prediction triggers any farmer saved-crop target alerts
    check_and_trigger_alerts(commodity, market, predicted_price)
    sync_local_store()
    
    return pred_document

def check_and_trigger_alerts(commodity: str, market: str, price: float):
    db = get_db()
    try:
        saved = list(db.saved_crops.find({
            "commodity": commodity,
            "market": market,
            "alert_enabled": True
        }))
        for sc in saved:
            target = float(sc.get("target_price", 0))
            if target > 0 and price >= target:
                notif_id = f"notif_{uuid.uuid4().hex[:10]}"
                db.notifications.insert_one({
                    "id": notif_id,
                    "user_id": sc["user_id"],
                    "title": f"Target Price Reached: {commodity}",
                    "title_kn": f"ಗುರಿ ಬೆಲೆ ತಲುಪಿದೆ: {commodity}",
                    "message": f"Predicted price for {commodity} in {market} is ₹{price:,.0f}/quintal, exceeding your target of ₹{target:,.0f}.",
                    "message_kn": f"{market} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {commodity} ಬೆಲೆ ₹{price:,.0f} ತಲುಪಿದ್ದು, ನಿಮ್ಮ ಗುರಿ ₹{target:,.0f} ಗಿಂತ ಹೆಚ್ಚಾಗಿದೆ.",
                    "type": "target_alert",
                    "read": False,
                    "created_at": datetime.now().isoformat()
                })
    except Exception as e:
        print(f"Alert check exception: {e}")
