"""
Authentication Routes: Register, Login, Me
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.database.db import get_db, sync_local_store
from backend.services.auth_service import hash_password, verify_password, create_access_token, jwt_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    district = data.get("district", "Karnataka Mandi").strip()
    role = data.get("role", "farmer").strip()
    
    if role not in ["farmer", "admin"]:
        role = "farmer"
        
    if not email or not password or not name:
        return jsonify({"error": "Name, email, and password are required."}), 400
        
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400
        
    db = get_db()
    existing = db.users.find_one({"email": email})
    if existing:
        return jsonify({"error": "A user with this email address already exists."}), 409
        
    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    user_doc = {
        "id": user_id,
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "phone": phone,
        "district": district,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    
    db.users.insert_one(user_doc)
    sync_local_store()
    
    # Generate token
    token = create_access_token(user_doc)
    user_resp = {k: v for k, v in user_doc.items() if k != "password_hash"}
    
    return jsonify({
        "message": "User registered successfully.",
        "token": token,
        "user": user_resp
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
        
    db = get_db()
    user = db.users.find_one({"email": email})
    if not user or not verify_password(password, user.get("password_hash", "")):
        return jsonify({"error": "Invalid email or password."}), 401
        
    token = create_access_token(user)
    user_resp = {k: v for k, v in user.items() if k != "password_hash" and k != "_id"}
    
    return jsonify({
        "message": "Login successful.",
        "token": token,
        "user": user_resp
    }), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_me():
    return jsonify({"user": request.user}), 200
