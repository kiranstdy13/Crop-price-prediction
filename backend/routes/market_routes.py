"""
Market and Crop Routes:
Provides supported crop lists, Karnataka markets, latest verified price tickers,
and comprehensive cross-mandi comparative analysis with transport cost factors.
"""

from flask import Blueprint, request, jsonify
import pandas as pd
from backend.database.db import get_db
from backend.services.prediction_service import generate_prediction_and_insights
from ml.training.data_pipeline import TRANSPORT_COST_ESTIMATE

market_bp = Blueprint("markets", __name__)

@market_bp.route("/crops", methods=["GET"])
def get_crops():
    db = get_db()
    crops = list(db.crops.find({}, {"_id": 0}))
    return jsonify({"crops": crops}), 200

@market_bp.route("/list", methods=["GET"])
def get_markets():
    db = get_db()
    markets = list(db.markets.find({}, {"_id": 0}))
    return jsonify({"markets": markets}), 200

@market_bp.route("/latest-prices", methods=["GET"])
def get_latest_prices():
    """
    Returns latest mandi modal prices, arrival volumes, and 7-day trend
    for supported crops across Karnataka APMCs.
    """
    db = get_db()
    crops = list(db.crops.find({}, {"_id": 0}))
    results = []
    
    for c in crops:
        comm = c["commodity"]
        # Fetch latest price for Bengaluru or first available
        latest = db.market_prices.find_one(
            {"commodity": comm, "market": "Bengaluru"},
            {"_id": 0},
            sort=[("date", -1)]
        )
        if not latest:
            latest = db.market_prices.find_one(
                {"commodity": comm},
                {"_id": 0},
                sort=[("date", -1)]
            )
            
        if latest:
            # 7-day prior price for trend
            cursor = db.market_prices.find(
                {"commodity": comm, "market": latest.get("market", "Bengaluru")},
                {"_id": 0}
            ).sort("date", -1).limit(7)
            hist = list(cursor)
            old_p = hist[-1]["modal_price"] if hist else latest["modal_price"]
            curr_p = latest["modal_price"]
            diff = curr_p - old_p
            pct = (diff / old_p * 100) if old_p > 0 else 0.0
            
            results.append({
                "commodity": comm,
                "category": c.get("category", "Produce"),
                "perishability": c.get("perishability", "Standard"),
                "market": latest.get("market", "Bengaluru"),
                "district": latest.get("district", "Bengaluru Urban"),
                "modal_price": float(curr_p),
                "minimum_price": float(latest.get("minimum_price", curr_p * 0.94)),
                "maximum_price": float(latest.get("maximum_price", curr_p * 1.07)),
                "market_arrivals": float(latest.get("market_arrivals", 100)),
                "date": str(latest.get("date", "")),
                "change_7d_pct": round(pct, 1),
                "trend": "up" if pct > 1 else ("down" if pct < -1 else "flat")
            })
            
    return jsonify({"prices": results, "state": "Karnataka", "source": "AGMARKNET & IMD"}), 200

@market_bp.route("/compare", methods=["GET"])
def compare_markets():
    """
    Cross-mandi price comparison across Karnataka APMCs.
    Accounts for mandi modal prices, predicted 7-day prices,
    transport costs from farm-gate, and net estimated proceeds.
    """
    commodity = request.args.get("commodity", "Tomato").strip()
    db = get_db()
    
    # Supported markets
    markets = ["Bengaluru", "Mysuru", "Hubballi", "Mandya"]
    comparison = []
    
    for m in markets:
        latest = db.market_prices.find_one(
            {"commodity": commodity, "market": m},
            {"_id": 0},
            sort=[("date", -1)]
        )
        if not latest:
            continue
            
        current_modal = float(latest["modal_price"])
        transport_cost = TRANSPORT_COST_ESTIMATE.get(m, 40.0)
        
        # Calculate fast 7-day predicted price
        try:
            pred_res = generate_prediction_and_insights(commodity, m, horizon_days=7)
            pred_price = pred_res["predicted_price"]
        except Exception:
            pred_price = current_modal * 1.02
            
        net_after_transport = round(current_modal - transport_cost, 2)
        
        comparison.append({
            "market": m,
            "district": latest.get("district", "Karnataka"),
            "current_modal_price": current_modal,
            "minimum_price": float(latest.get("minimum_price", current_modal * 0.94)),
            "maximum_price": float(latest.get("maximum_price", current_modal * 1.07)),
            "market_arrivals": float(latest.get("market_arrivals", 100)),
            "predicted_7d_price": pred_price,
            "transport_cost_per_quintal": transport_cost,
            "net_after_transport": net_after_transport,
            "date": str(latest.get("date", ""))
        })
        
    if not comparison:
        return jsonify({"error": f"No market data found for {commodity}."}), 404
        
    sorted_by_price = sorted(comparison, key=lambda x: x["current_modal_price"], reverse=True)
    sorted_by_net = sorted(comparison, key=lambda x: x["net_after_transport"], reverse=True)
    
    highest = sorted_by_price[0]
    lowest = sorted_by_price[-1]
    best_net = sorted_by_net[0]
    
    analysis_en = (
        f"For {commodity}, the highest current modal price is ₹{highest['current_modal_price']:,.0f}/quintal in {highest['market']}. "
        f"However, after factoring in transport expenses (~₹{best_net['transport_cost_per_quintal']}/quintal), "
        f"{best_net['market']} offers the highest net return at ₹{best_net['net_after_transport']:,.0f}/quintal. "
        "A higher mandi price does not automatically imply higher farmer profit without accounting for freight distance."
    )
    
    analysis_kn = (
        f"{commodity} ಬೆಳೆಗೆ ಗರಿಷ್ಠ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ {highest['market']} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ₹{highest['current_modal_price']:,.0f} ಆಗಿದೆ. "
        f"ಆದರೆ ಸಾರಿಗೆ ವೆಚ್ಚವನ್ನು ಪರಿಗಣಿಸಿದಾಗ, {best_net['market']} ಮಾರುಕಟ್ಟೆಯು ನಿವ್ವಳ ₹{best_net['net_after_transport']:,.0f} ಆದಾಯ ನೀಡುತ್ತದೆ."
    )
    
    return jsonify({
        "commodity": commodity,
        "markets": comparison,
        "highest_price_mandi": highest,
        "lowest_price_mandi": lowest,
        "best_net_mandi": best_net,
        "analysis_en": analysis_en,
        "analysis_kn": analysis_kn
    }), 200
