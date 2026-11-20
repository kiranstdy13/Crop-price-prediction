"""
Flask Application Entrypoint for AI Crop Price Prediction Platform.
MCA Final Year Project - Explainable Decision Support System for Farmers.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

from backend.routes.auth_routes import auth_bp
from backend.routes.prediction_routes import prediction_bp
from backend.routes.market_routes import market_bp
from backend.routes.farmer_routes import farmer_bp
from backend.routes.admin_routes import admin_bp
from backend.database.db import get_db

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(prediction_bp, url_prefix="/api/predictions")
    app.register_blueprint(market_bp, url_prefix="/api/markets")
    app.register_blueprint(farmer_bp, url_prefix="/api/farmer")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "HEALTHY",
            "project": "AI-Based Crop Price Prediction and Explainable Decision Support System",
            "state": "Karnataka",
            "supported_crops": ["Tomato", "Onion", "Potato", "Cabbage", "Green Chilli", "Rice", "Maize", "Groundnut"],
            "supported_markets": ["Bengaluru", "Mysuru", "Hubballi", "Mandya"],
            "version": "2.0.0"
        }), 200
        
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404
        
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500
        
    return app

app = create_app()

if __name__ == "__main__":
    # Ensure DB is connected and seeded
    get_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Crop Price AI Backend Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
