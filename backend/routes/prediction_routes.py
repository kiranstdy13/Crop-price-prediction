"""
Prediction Routes: Predict, History, Detail
"""

from flask import Blueprint, request, jsonify
from backend.services.prediction_service import generate_prediction_and_insights
from backend.services.auth_service import get_current_user, jwt_required
from backend.database.db import get_db

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/predict", methods=["POST"])
def predict():
    data = request.get_json() or {}
    commodity = data.get("commodity", "").strip()
    market = data.get("market", "").strip()
    horizon = int(data.get("horizon_days", 7))
    assumptions = data.get("assumptions", {})
    
    if not commodity or not market:
        return jsonify({"error": "Both commodity (crop) and market are required."}), 400
        
    user = get_current_user()
    user_id = user["id"] if user else "guest_farmer"
    
    try:
        result = generate_prediction_and_insights(
            commodity=commodity,
            market=market,
            horizon_days=horizon,
            user_id=user_id,
            assumptions=assumptions
        )
        # Remove mongo _id if present
        result.pop("_id", None)
        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@prediction_bp.route("/history", methods=["GET"])
@jwt_required
def history():
    user_id = request.user["id"]
    db = get_db()
    cursor = db.predictions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(25)
    
    return jsonify({"predictions": list(cursor)}), 200

@prediction_bp.route("/<pred_id>", methods=["GET"])
def get_prediction_detail(pred_id):
    db = get_db()
    doc = db.predictions.find_one({"id": pred_id}, {"_id": 0})
    if not doc:
        return jsonify({"error": "Prediction record not found."}), 404
    return jsonify(doc), 200
