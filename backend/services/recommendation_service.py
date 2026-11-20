"""
Smart Selling Recommendation and Agricultural Decision Support Engine.
Balances predicted price trends against holding costs, spoilage risks,
crop perishability, transportation expenses, and farmer cash-flow urgency.
"""

PERISHABILITY_RULES = {
    "Tomato": {
        "tier": "Highly Perishable",
        "shelf_life_days": 5,
        "daily_storage_cost": 8.0,
        "spoilage_rate_per_week": 0.12,
        "cold_storage_recommended": True
    },
    "Green Chilli": {
        "tier": "Highly Perishable",
        "shelf_life_days": 6,
        "daily_storage_cost": 7.0,
        "spoilage_rate_per_week": 0.10,
        "cold_storage_recommended": True
    },
    "Cabbage": {
        "tier": "Medium-High Perishable",
        "shelf_life_days": 10,
        "daily_storage_cost": 5.0,
        "spoilage_rate_per_week": 0.06,
        "cold_storage_recommended": True
    },
    "Onion": {
        "tier": "Semi-Perishable",
        "shelf_life_days": 45,
        "daily_storage_cost": 2.5,
        "spoilage_rate_per_week": 0.02,
        "cold_storage_recommended": False
    },
    "Potato": {
        "tier": "Semi-Perishable",
        "shelf_life_days": 60,
        "daily_storage_cost": 2.0,
        "spoilage_rate_per_week": 0.015,
        "cold_storage_recommended": False
    },
    "Maize": {
        "tier": "Non-Perishable Grains",
        "shelf_life_days": 180,
        "daily_storage_cost": 1.2,
        "spoilage_rate_per_week": 0.005,
        "cold_storage_recommended": False
    },
    "Rice": {
        "tier": "Non-Perishable Grains",
        "shelf_life_days": 365,
        "daily_storage_cost": 1.0,
        "spoilage_rate_per_week": 0.003,
        "cold_storage_recommended": False
    },
    "Groundnut": {
        "tier": "Non-Perishable Oilseed",
        "shelf_life_days": 180,
        "daily_storage_cost": 1.5,
        "spoilage_rate_per_week": 0.005,
        "cold_storage_recommended": False
    }
}

DEFAULT_TRANSPORT_COST = 40.0  # INR per quintal average

def generate_selling_recommendation(
    crop: str,
    market: str,
    current_price: float,
    predicted_price: float,
    horizon_days: int,
    farmer_urgency: str = "Normal", # "High" (immediate cash needed) or "Normal"
    has_cold_storage: bool = False
) -> dict:
    """
    Synthesizes economic analysis and generates explainable selling recommendation.
    """
    crop_info = PERISHABILITY_RULES.get(crop, {
        "tier": "Standard Produce",
        "shelf_life_days": 14,
        "daily_storage_cost": 4.0,
        "spoilage_rate_per_week": 0.05,
        "cold_storage_recommended": False
    })
    
    price_diff = predicted_price - current_price
    pct_change = (price_diff / current_price * 100) if current_price > 0 else 0.0
    
    # Financial breakdown
    total_storage_cost = crop_info["daily_storage_cost"] * horizon_days
    weeks = horizon_days / 7.0
    spoilage_rate = crop_info["spoilage_rate_per_week"] * weeks
    if has_cold_storage and crop_info["cold_storage_recommended"]:
        spoilage_rate = spoilage_rate * 0.35  # Cold storage reduces spoilage
        
    expected_spoilage_loss = current_price * spoilage_rate
    estimated_net_diff = price_diff - total_storage_cost - expected_spoilage_loss
    net_pct_change = (estimated_net_diff / current_price * 100) if current_price > 0 else 0.0
    
    # Logic Decision Tree
    action = "Monitor market conditions"
    action_kn = "ಮಾರುಕಟ್ಟೆ ಪರಿಸ್ಥಿತಿಯನ್ನು ಗಮನಿಸಿ"
    urgency_tag = "neutral"
    key_reasons = []
    key_reasons_kn = []
    
    # Rule 1: High cash urgency
    if farmer_urgency.lower() == "high":
        action = "Consider selling now"
        action_kn = "ಈಗಲೇ ಮಾರಾಟ ಮಾಡಲು ಪರಿಗಣಿಸಿ"
        urgency_tag = "sell_now"
        key_reasons.append("Farmer has high immediate cash requirements; holding incurs liquidity risk.")
        key_reasons_kn.append("ತಕ್ಷಣದ ಹಣಕಾಸಿನ ಅಗತ್ಯತೆ ಇರುವುದರಿಂದ ಈಗಲೇ ಮಾರಾಟ ಮಾಡುವುದು ಸೂಕ್ತ.")
        
    # Rule 2: Exceeding perishability / shelf life
    elif horizon_days > crop_info["shelf_life_days"] and not has_cold_storage and crop_info["tier"] in ["Highly Perishable", "Medium-High Perishable"]:
        action = "Consider selling now"
        action_kn = "ಈಗಲೇ ಮಾರಾಟ ಮಾಡಲು ಪರಿಗಣಿಸಿ"
        urgency_tag = "sell_now"
        key_reasons.append(
            f"{crop} is {crop_info['tier'].lower()} with an ambient shelf life of only ~{crop_info['shelf_life_days']} days. "
            f"Waiting {horizon_days} days without cold storage risks substantial post-harvest spoilage (~{spoilage_rate*100:.1f}%)."
        )
        key_reasons_kn.append(
            f"{crop} ಕೊಳೆಯುವ ಬೆಳೆಯಾಗಿದ್ದು, ಶೀತಲ ಸಂಗ್ರಹಾಗಾರವಿಲ್ಲದೆ {horizon_days} ದಿನ ಇರಿಸಿದರೆ ಹಾನಿಯಾಗುವ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು."
        )
        
    # Rule 3: Significant positive net benefit
    elif estimated_net_diff > 0 and net_pct_change >= 4.0:
        action = "Consider waiting"
        action_kn = "ಬೆಲೆ ಹೆಚ್ಚಳಕ್ಕಾಗಿ ಕಾಯಲು ಪರಿಗಣಿಸಿ"
        urgency_tag = "wait"
        key_reasons.append(
            f"Model predicts a gross price rise of ₹{price_diff:,.0f}/quintal (+{pct_change:.1f}%). "
            f"Even after deducting estimated storage costs (₹{total_storage_cost:,.0f}) and spoilage risk (₹{expected_spoilage_loss:,.0f}), "
            f"the estimated net advantage is +₹{estimated_net_diff:,.0f}/quintal (+{net_pct_change:.1f}%)."
        )
        key_reasons_kn.append(
            f"ಅಂದಾಜು ಬೆಲೆ ಹೆಚ್ಚಳ ₹{price_diff:,.0f} (+{pct_change:.1f}%). ಸಂಗ್ರಹಣಾ ವೆಚ್ಚ ಕಳೆದು ನಿವ್ವಳ ಲಾಭ ನಿರೀಕ್ಷಿತವಾಗಿದೆ."
        )
        
    # Rule 4: Predicted price drop or negative net difference
    elif estimated_net_diff < 0 and net_pct_change <= -2.0:
        action = "Consider selling now"
        action_kn = "ಈಗಲೇ ಮಾರಾಟ ಮಾಡಲು ಪರಿಗಣಿಸಿ"
        urgency_tag = "sell_now"
        key_reasons.append(
            f"Expected price trend is negative or does not cover holding costs (Net: -₹{abs(estimated_net_diff):,.0f}/quintal). "
            "Selling at current mandi rates minimizes holding expense."
        )
        key_reasons_kn.append(
            f"ಬೆಲೆ ಇಳಿಕೆಯಾಗುವ ನಿರೀಕ್ಷೆಯಿದೆ ಅಥವಾ ಸಂಗ್ರಹ ವೆಚ್ಚ ಭರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ಈಗಲೇ ಮಾರಾಟ ಮಾಡುವುದು ಸುರಕ್ಷಿತ."
        )
        
    # Rule 5: Marginal price movement
    else:
        action = "Monitor market conditions"
        action_kn = "ಮಾರುಕಟ್ಟೆ ಪರಿಸ್ಥಿತಿಯನ್ನು ಗಮನಿಸಿ"
        urgency_tag = "monitor"
        key_reasons.append(
            f"Expected net price change is marginal (+{net_pct_change:.1f}%). "
            "Market volatility could offset gains. Monitor local mandi arrivals over the next 2-3 days before committing."
        )
        key_reasons_kn.append(
            "ಬೆಲೆಯ ಬದಲಾವಣೆ ಅಲ್ಪ ಪ್ರಮಾಣದಲ್ಲಿದೆ. ಮುಂದಿನ 2-3 ದಿನಗಳ ಮಾರುಕಟ್ಟೆ ಆವಕವನ್ನು ಗಮನಿಸಿ ತೀರ್ಮಾನಿಸಿ."
        )

    disclaimer_en = (
        "Agricultural Decision Support Notice: Recommendations are generated through statistical decision trees "
        "and machine learning forecasts. They do not constitute guaranteed financial returns. Farmers should factor in "
        "local mandi commissions, labor, and transport before finalizing transactions."
    )
    disclaimer_kn = (
        "ಕೃಷಿ ನಿರ್ಧಾರ ಬೆಂಬಲ ಸೂಚನೆ: ಈ ಶಿಫಾರಸುಗಳು ಸಂಖ್ಯಾಶಾಸ್ತ್ರೀಯ ಮುನ್ಸೂಚನೆಗಳನ್ನು ಆಧರಿಸಿವೆ. "
        "ಯಾವುದೇ ಭವಿಷ್ಯದ ಲಾಭದ ಗ್ಯಾರಂಟಿ ಇಲ್ಲ. ಸ್ಥಳೀಯ ಮಾರುಕಟ್ಟೆ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ಖಚಿತಪಡಿಸಿಕೊಂಡು ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳಿ."
    )

    return {
        "action": action,
        "action_kn": action_kn,
        "urgency_tag": urgency_tag,
        "crop": crop,
        "market": market,
        "horizon_days": horizon_days,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "gross_price_change": round(price_diff, 2),
        "gross_pct_change": round(pct_change, 2),
        "holding_costs": {
            "daily_storage_rate": crop_info["daily_storage_cost"],
            "total_storage_cost": round(total_storage_cost, 2),
            "estimated_spoilage_loss": round(expected_spoilage_loss, 2),
            "estimated_transport_cost": DEFAULT_TRANSPORT_COST
        },
        "estimated_net_difference": round(estimated_net_diff, 2),
        "net_pct_change": round(net_pct_change, 2),
        "crop_perishability_tier": crop_info["tier"],
        "shelf_life_days": crop_info["shelf_life_days"],
        "key_reasons": key_reasons,
        "key_reasons_kn": key_reasons_kn,
        "disclaimer_en": disclaimer_en,
        "disclaimer_kn": disclaimer_kn
    }

if __name__ == "__main__":
    rec = generate_selling_recommendation(
        crop="Tomato",
        market="Bengaluru",
        current_price=2000.0,
        predicted_price=2300.0,
        horizon_days=15,
        farmer_urgency="Normal",
        has_cold_storage=False
    )
    print("Action:", rec["action"])
    print("Reasons:", rec["key_reasons"])
    print("Net Difference:", rec["estimated_net_difference"])
