"""
Farmer Profile, Saved Crops, Target Alerts, and Notification Routes
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.database.db import get_db, sync_local_store
from backend.services.auth_service import jwt_required

farmer_bp = Blueprint("farmer", __name__)

@farmer_bp.route("/dashboard", methods=["GET"])
@jwt_required
def get_dashboard_summary():
    user = request.user
    user_id = user["id"]
    db = get_db()
    
    # 1. Total supported crops and markets count
    total_crops = db.crops.count_documents({})
    total_markets = db.markets.count_documents({})
    
    # 2. Farmer predictions count & recent predictions
    pred_cursor = db.predictions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(5)
    recent_predictions = list(pred_cursor)
    
    total_predictions = db.predictions.count_documents({"user_id": user_id})
    
    # 3. Saved crops count
    saved_crops = list(db.saved_crops.find({"user_id": user_id}, {"_id": 0}))
    
    # 4. Unread notifications count
    unread_notifications = db.notifications.count_documents({"user_id": user_id, "read": False})
    
    # 5. Top market tickers for Karnataka
    crops_list = ["Tomato", "Onion", "Potato", "Green Chilli"]
    tickers = []
    for c in crops_list:
        p = db.market_prices.find_one({"commodity": c}, {"_id": 0}, sort=[("date", -1)])
        if p:
            tickers.append({
                "commodity": c,
                "market": p.get("market", "Bengaluru"),
                "modal_price": p.get("modal_price", 0),
                "date": str(p.get("date", ""))
            })
            
    return jsonify({
        "user": user,
        "metrics": {
            "total_supported_crops": total_crops,
            "total_supported_markets": total_markets,
            "farmer_predictions_count": total_predictions,
            "saved_crops_count": len(saved_crops),
            "unread_notifications": unread_notifications
        },
        "recent_predictions": recent_predictions,
        "saved_crops": saved_crops,
        "market_tickers": tickers
    }), 200

@farmer_bp.route("/saved-crops", methods=["GET"])
@jwt_required
def get_saved_crops():
    user_id = request.user["id"]
    db = get_db()
    items = list(db.saved_crops.find({"user_id": user_id}, {"_id": 0}))
    
    # Enrich with latest price
    for item in items:
        latest = db.market_prices.find_one(
            {"commodity": item["commodity"], "market": item["market"]},
            {"_id": 0},
            sort=[("date", -1)]
        )
        if latest:
            item["current_price"] = latest.get("modal_price", 0)
            target = item.get("target_price", 0)
            item["target_met"] = (latest.get("modal_price", 0) >= target) if target > 0 else False
            item["date"] = str(latest.get("date", ""))
            
    return jsonify({"saved_crops": items}), 200

@farmer_bp.route("/saved-crops", methods=["POST"])
@jwt_required
def add_saved_crop():
    user_id = request.user["id"]
    data = request.get_json() or {}
    commodity = data.get("commodity", "").strip()
    market = data.get("market", "").strip()
    target_price = float(data.get("target_price", 0))
    alert_enabled = bool(data.get("alert_enabled", True))
    
    if not commodity or not market:
        return jsonify({"error": "Crop and market are required."}), 400
        
    db = get_db()
    existing = db.saved_crops.find_one({
        "user_id": user_id,
        "commodity": commodity,
        "market": market
    })
    
    if existing:
        db.saved_crops.update_one(
            {"id": existing["id"]},
            {"$set": {"target_price": target_price, "alert_enabled": alert_enabled}}
        )
        sync_local_store()
        return jsonify({"message": "Saved crop preference updated."}), 200
        
    sc_id = f"sc_{uuid.uuid4().hex[:10]}"
    doc = {
        "id": sc_id,
        "user_id": user_id,
        "commodity": commodity,
        "market": market,
        "target_price": target_price,
        "alert_enabled": alert_enabled,
        "created_at": datetime.now().isoformat()
    }
    db.saved_crops.insert_one(doc)
    doc.pop("_id", None)
    sync_local_store()
    
    return jsonify({"message": "Crop saved successfully.", "saved_crop": doc}), 201

@farmer_bp.route("/saved-crops/<crop_id>", methods=["DELETE"])
@jwt_required
def delete_saved_crop(crop_id):
    user_id = request.user["id"]
    db = get_db()
    res = db.saved_crops.delete_one({"id": crop_id, "user_id": user_id})
    sync_local_store()
    if res.deleted_count == 0:
        return jsonify({"error": "Saved crop not found."}), 404
    return jsonify({"message": "Crop removed from saved list."}), 200

@farmer_bp.route("/notifications", methods=["GET"])
@jwt_required
def get_notifications():
    user_id = request.user["id"]
    db = get_db()
    notifs = list(db.notifications.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(20))
    return jsonify({"notifications": notifs}), 200

@farmer_bp.route("/notifications/<notif_id>/read", methods=["PUT"])
@jwt_required
def mark_notification_read(notif_id):
    user_id = request.user["id"]
    db = get_db()
    db.notifications.update_one(
        {"id": notif_id, "user_id": user_id},
        {"$set": {"read": True}}
    )
    sync_local_store()
    return jsonify({"message": "Notification marked as read."}), 200
