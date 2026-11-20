"""
Automated Backend API and Model Integration Test Suite
"""

import json
from backend.app import create_app

def run_tests():
    app = create_app()
    client = app.test_client()
    
    print("=== TEST 1: Health Endpoint ===")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("Health response:", res.get_json())
    
    print("\n=== TEST 2: User Login (Farmer) ===")
    res = client.post("/api/auth/login", json={
        "email": "farmer@karnataka.gov",
        "password": "Farmer@123"
    })
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    farmer_data = res.get_json()
    farmer_token = farmer_data["token"]
    print("Farmer login OK. User:", farmer_data["user"]["name"])
    
    print("\n=== TEST 3: User Login (Admin) ===")
    res = client.post("/api/auth/login", json={
        "email": "admin@cropprice.ai",
        "password": "Admin@123"
    })
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    admin_data = res.get_json()
    admin_token = admin_data["token"]
    print("Admin login OK. User:", admin_data["user"]["name"])
    
    print("\n=== TEST 4: Get Latest Mandi Prices ===")
    res = client.get("/api/markets/latest-prices")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    prices = res.get_json()["prices"]
    print(f"Retrieved latest prices for {len(prices)} crops across Karnataka.")
    print("Sample crop price:", prices[0])
    
    print("\n=== TEST 5: Crop Price Prediction with SHAP & Decision Support ===")
    pred_payload = {
        "commodity": "Tomato",
        "market": "Bengaluru",
        "horizon_days": 7,
        "assumptions": {
            "farmer_urgency": "Normal",
            "has_cold_storage": False
        }
    }
    res = client.post("/api/predictions/predict",
        headers={"Authorization": f"Bearer {farmer_token}"},
        json=pred_payload
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.get_data(as_text=True)}"
    pred_res = res.get_json()
    print("Crop:", pred_res["commodity"], "Market:", pred_res["market"])
    print("Current Price: ₹", pred_res["current_modal_price"])
    print("Predicted Price: ₹", pred_res["predicted_price"])
    print("Direction:", pred_res["direction_label"])
    print("Base Value (SHAP): ₹", pred_res["explanation"]["base_value"])
    print("Top Positive Factors:", len(pred_res["explanation"]["positive_factors"]))
    print("Top Negative Factors:", len(pred_res["explanation"]["negative_factors"]))
    print("Reconciliation Diff:", pred_res["explanation"]["reconciliation_diff"])
    print("Selling Recommendation:", pred_res["recommendation"]["action"])
    print("English Rationale:", pred_res["recommendation"]["key_reasons"])
    
    print("\n=== TEST 6: Market Comparison ===")
    res = client.get("/api/markets/compare?commodity=Onion")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    comp_data = res.get_json()
    print("Comparison markets count:", len(comp_data["markets"]))
    print("Highest mandi price:", comp_data["highest_price_mandi"]["market"], "₹", comp_data["highest_price_mandi"]["current_modal_price"])
    print("Best net return mandi:", comp_data["best_net_mandi"]["market"], "₹", comp_data["best_net_mandi"]["net_after_transport"])
    print("Analysis:", comp_data["analysis_en"])
    
    print("\n=== TEST 7: Farmer Saved Crops & Target Price Alerts ===")
    res = client.post("/api/farmer/saved-crops",
        headers={"Authorization": f"Bearer {farmer_token}"},
        json={"commodity": "Potato", "market": "Mysuru", "target_price": 2400.0, "alert_enabled": True}
    )
    assert res.status_code in [200, 201], f"Expected 200/201, got {res.status_code}"
    
    res = client.get("/api/farmer/saved-crops", headers={"Authorization": f"Bearer {farmer_token}"})
    assert res.status_code == 200
    saved = res.get_json()["saved_crops"]
    print(f"Farmer has {len(saved)} saved crop alerts.")
    
    print("\n=== TEST 8: Admin Overview & Model Metrics ===")
    res = client.get("/api/admin/overview", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    print("Admin overview stats:", res.get_json()["stats"])
    
    res = client.get("/api/admin/model-metrics", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    print("Model metrics loaded successfully for horizons:", list(res.get_json()["metrics"].keys()))
    
    print("\n>>> ALL 8 BACKEND AND ML INTEGRATION TESTS PASSED PERFECTLY! <<<")

if __name__ == "__main__":
    run_tests()
