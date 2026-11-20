"""
Admin Management Routes:
System overview, user management, CSV dataset upload & validation,
model training management, and model performance metrics.
"""

import os
import io
import json
import pandas as pd
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from backend.database.db import get_db, sync_local_store
from backend.services.auth_service import admin_required
from ml.training.data_pipeline import validate_dataset, build_feature_engineered_dataset
from ml.training.train_models import train_all_models

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/overview", methods=["GET"])
@admin_required
def get_admin_overview():
    db = get_db()
    total_users = db.users.count_documents({})
    total_farmers = db.users.count_documents({"role": "farmer"})
    total_admins = db.users.count_documents({"role": "admin"})
    total_crops = db.crops.count_documents({})
    total_markets = db.markets.count_documents({})
    total_predictions = db.predictions.count_documents({})
    total_price_records = db.market_prices.count_documents({})
    
    # Model evaluation metrics
    metrics_doc = db.model_metrics.find_one({}, {"_id": 0}, sort=[("evaluated_at", -1)])
    
    return jsonify({
        "stats": {
            "total_users": total_users,
            "total_farmers": total_farmers,
            "total_admins": total_admins,
            "total_crops": total_crops,
            "total_markets": total_markets,
            "total_predictions": total_predictions,
            "total_price_records": total_price_records
        },
        "model_version": "v1.0.0",
        "last_trained": metrics_doc.get("evaluated_at", "2026-11-19") if metrics_doc else "2026-11-19",
        "dataset_source": "AGMARKNET & IMD (Karnataka APMCs)"
    }), 200

@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users_list():
    db = get_db()
    users = list(db.users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1))
    return jsonify({"users": users}), 200

@admin_bp.route("/model-metrics", methods=["GET"])
@admin_required
def get_model_metrics():
    db = get_db()
    metrics_doc = db.model_metrics.find_one({}, {"_id": 0}, sort=[("evaluated_at", -1)])
    if not metrics_doc:
        report_file = os.path.join("ml", "evaluation", "model_evaluation_report.json")
        if os.path.exists(report_file):
            with open(report_file, "r") as f:
                metrics_data = json.load(f)
            return jsonify({"metrics": metrics_data, "version": "v1.0.0"}), 200
        return jsonify({"error": "No model metrics available."}), 404
        
    return jsonify(metrics_doc), 200

@admin_bp.route("/upload-dataset", methods=["POST"])
@admin_required
def upload_dataset():
    """
    Accepts CSV upload, validates required schema, data types, value boundaries,
    and ingests verified records into the system.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded in form-data."}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400
        
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported."}), 400
        
    try:
        content = file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(content))
        
        # Normalize column names
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Validate dataset
        is_valid, validation_errors = validate_dataset(df)
        if not is_valid:
            return jsonify({
                "status": "VALIDATION_FAILED",
                "errors": validation_errors
            }), 422
            
        # Ingest into database
        db = get_db()
        records = df.to_dict(orient="records")
        db.market_prices.insert_many(records)
        
        # Save uploaded file
        save_dir = os.path.join("ml", "data")
        save_path = os.path.join(save_dir, f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(save_path, index=False)
        sync_local_store()
        
        return jsonify({
            "status": "SUCCESS",
            "message": f"Dataset validated and ingested successfully. Added {len(records)} verified records.",
            "records_ingested": len(records),
            "columns": list(df.columns)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to process CSV file: {str(e)}"}), 500

@admin_bp.route("/trigger-training", methods=["POST"])
@admin_required
def trigger_training():
    """
    Triggers chronological retraining of Random Forest, XGBoost, and Baseline models
    using updated features.
    """
    try:
        results = train_all_models()
        db = get_db()
        db.model_metrics.insert_one({
            "version": f"v1.{datetime.now().strftime('%m%d')}",
            "evaluated_at": datetime.now().isoformat(),
            "metrics": results
        })
        sync_local_store()
        return jsonify({
            "message": "Model retraining completed successfully.",
            "results": results
        }), 200
    except Exception as e:
        return jsonify({"error": f"Model training failed: {str(e)}"}), 500
