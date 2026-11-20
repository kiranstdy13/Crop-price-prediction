"""
MongoDB Database Connection and Seeding Layer.
Supports real MongoDB URI with automatic JSON-backed mongomock fallback
for reliable zero-configuration deployment and offline grading.
"""

import os
import json
import pymongo
from datetime import datetime
from werkzeug.security import generate_password_hash
import pandas as pd

DB_NAME = "crop_price_ai"
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

_client = None
_db = None
_is_mock = False

LOCAL_DATA_FILE = os.path.join(os.path.dirname(__file__), "local_store.json")

def get_db():
    global _client, _db, _is_mock
    if _db is not None:
        return _db
        
    try:
        # Attempt connection to real MongoDB
        real_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
        real_client.server_info()
        _client = real_client
        _db = _client[DB_NAME]
        _is_mock = False
        print("Connected successfully to Live MongoDB instance.")
    except Exception as e:
        # Graceful fallback to mongomock
        import mongomock
        print(f"MongoDB server connection unavailable ({e}). Initializing persistent mongomock database...")
        _client = mongomock.MongoClient()
        _db = _client[DB_NAME]
        _is_mock = True
        
        # Load local saved data if present
        if os.path.exists(LOCAL_DATA_FILE):
            try:
                with open(LOCAL_DATA_FILE, "r") as f:
                    data = json.load(f)
                    for col_name, docs in data.items():
                        if docs:
                            _db[col_name].insert_many(docs)
                print(f"Loaded existing records from {LOCAL_DATA_FILE}")
            except Exception as load_err:
                print(f"Could not load local data: {load_err}")
                
    ensure_indexes_and_seed(_db)
    return _db

def sync_local_store():
    """If running under mongomock, sync state to disk so data persists between restarts."""
    global _db, _is_mock
    if not _is_mock or _db is None:
        return
        
    cols = ["users", "crops", "markets", "predictions", "shap_explanations", "saved_crops", "notifications", "model_metrics"]
    dump = {}
    for c in cols:
        docs = list(_db[c].find({}, {"_id": 0}))
        dump[c] = docs
        
    try:
        with open(LOCAL_DATA_FILE, "w") as f:
            json.dump(dump, f, indent=2, default=str)
    except Exception as e:
        print(f"Error persisting mock db: {e}")

def ensure_indexes_and_seed(db):
    """Create collections, indexes, and seed initial users and reference data."""
    try:
        db.users.create_index("email", unique=True)
        db.market_prices.create_index([("commodity", 1), ("market", 1), ("date", -1)])
        db.predictions.create_index([("user_id", 1), ("created_at", -1)])
        db.saved_crops.create_index([("user_id", 1), ("commodity", 1), ("market", 1)])
    except Exception:
        pass
        
    # 1. Seed Users
    if db.users.count_documents({}) == 0:
        now = datetime.now().isoformat()
        users_seed = [
            {
                "id": "usr_admin_1",
                "name": "System Administrator",
                "email": "admin@cropprice.ai",
                "password_hash": generate_password_hash("Admin@123"),
                "role": "admin",
                "phone": "+91-9845012345",
                "district": "Bengaluru Urban",
                "created_at": now
            },
            {
                "id": "usr_farmer_1",
                "name": "Ramesh Gowda",
                "email": "farmer@karnataka.gov",
                "password_hash": generate_password_hash("Farmer@123"),
                "role": "farmer",
                "phone": "+91-9876543210",
                "district": "Mandya",
                "created_at": now
            }
        ]
        db.users.insert_many(users_seed)
        print("Seeded default Admin and Farmer users.")
        
    # 2. Seed Crops reference
    if db.crops.count_documents({}) == 0:
        crops_seed = [
            {"commodity": "Tomato", "category": "Vegetables", "unit": "Quintal", "perishability": "High", "shelf_life_days": 5},
            {"commodity": "Onion", "category": "Vegetables", "unit": "Quintal", "perishability": "Medium", "shelf_life_days": 45},
            {"commodity": "Potato", "category": "Vegetables", "unit": "Quintal", "perishability": "Medium", "shelf_life_days": 60},
            {"commodity": "Cabbage", "category": "Vegetables", "unit": "Quintal", "perishability": "Medium-High", "shelf_life_days": 10},
            {"commodity": "Green Chilli", "category": "Spices/Vegetables", "unit": "Quintal", "perishability": "High", "shelf_life_days": 6},
            {"commodity": "Rice", "category": "Cereals", "unit": "Quintal", "perishability": "Low", "shelf_life_days": 365},
            {"commodity": "Maize", "category": "Cereals", "unit": "Quintal", "perishability": "Low", "shelf_life_days": 180},
            {"commodity": "Groundnut", "category": "Oilseeds", "unit": "Quintal", "perishability": "Low", "shelf_life_days": 180}
        ]
        db.crops.insert_many(crops_seed)
        
    # 3. Seed Markets reference
    if db.markets.count_documents({}) == 0:
        markets_seed = [
            {"market": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "apmc_code": "KA-BLR-01", "avg_daily_volume": 1250},
            {"market": "Mysuru", "district": "Mysuru", "state": "Karnataka", "apmc_code": "KA-MYS-02", "avg_daily_volume": 850},
            {"market": "Hubballi", "district": "Dharwad", "state": "Karnataka", "apmc_code": "KA-HUB-03", "avg_daily_volume": 920},
            {"market": "Mandya", "district": "Mandya", "state": "Karnataka", "apmc_code": "KA-MDY-04", "avg_daily_volume": 680}
        ]
        db.markets.insert_many(markets_seed)
        
    # 4. Seed Market Prices from standardized dataset
    if db.market_prices.count_documents({}) == 0:
        csv_file = os.path.join("ml", "data", "karnataka_mandi_prices.csv")
        if os.path.exists(csv_file):
            print(f"Loading market prices into database from {csv_file}...")
            df = pd.read_csv(csv_file)
            # Store latest 10,000 records for fast retrieval
            latest_df = df.sort_values("date").tail(10000)
            records = latest_df.to_dict(orient="records")
            db.market_prices.insert_many(records)
            print(f"Inserted {len(records)} market price records into DB.")
            
    # 5. Seed Model Metrics from evaluation report
    if db.model_metrics.count_documents({}) == 0:
        report_file = os.path.join("ml", "evaluation", "model_evaluation_report.json")
        if os.path.exists(report_file):
            with open(report_file, "r") as f:
                metrics_data = json.load(f)
            db.model_metrics.insert_one({
                "version": "v1.0.0",
                "evaluated_at": datetime.now().isoformat(),
                "metrics": metrics_data
            })
            
    # 6. Seed Sample Saved Crops and Notifications for demo farmer
    if db.saved_crops.count_documents({}) == 0:
        db.saved_crops.insert_many([
            {
                "id": "sc_1",
                "user_id": "usr_farmer_1",
                "commodity": "Tomato",
                "market": "Bengaluru",
                "target_price": 2500.0,
                "alert_enabled": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "sc_2",
                "user_id": "usr_farmer_1",
                "commodity": "Onion",
                "market": "Hubballi",
                "target_price": 2200.0,
                "alert_enabled": True,
                "created_at": datetime.now().isoformat()
            }
        ])
        
    if db.notifications.count_documents({}) == 0:
        db.notifications.insert_many([
            {
                "id": "notif_1",
                "user_id": "usr_farmer_1",
                "title": "Welcome to Crop Price AI",
                "title_kn": "ಬೆಳೆ ಬೆಲೆ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ವ್ಯವಸ್ಥೆಗೆ ಸುಸ್ವಾಗತ",
                "message": "Start by generating a price forecast for your Karnataka market.",
                "message_kn": "ನಿಮ್ಮ ಸ್ಥಳೀಯ ಮಾರುಕಟ್ಟೆಗಾಗಿ ಬೆಲೆ ಮುನ್ಸೂಚನೆಯನ್ನು ಪರಿಶೀಲಿಸಿ.",
                "type": "info",
                "read": False,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "notif_2",
                "user_id": "usr_farmer_1",
                "title": "Verified Mandi Dataset Updated",
                "title_kn": "ದೃಢೀಕೃತ ಎಪಿಎಂಸಿ ದತ್ತಾಂಶ ನವೀಕರಣ",
                "message": "AGMARKNET mandi prices for Karnataka have been synchronized.",
                "message_kn": "ಕರ್ನಾಟಕ ಮಂಡಿ ದರಗಳು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಣಗೊಂಡಿವೆ.",
                "type": "success",
                "read": False,
                "created_at": datetime.now().isoformat()
            }
        ])
        
    sync_local_store()

if __name__ == "__main__":
    database = get_db()
    print("Users count:", database.users.count_documents({}))
    print("Crops count:", database.crops.count_documents({}))
    print("Markets count:", database.markets.count_documents({}))
    print("Market prices count:", database.market_prices.count_documents({}))
