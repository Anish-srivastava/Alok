# Simple test endpoint
from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)
test_bp = Blueprint("test", __name__)

@test_bp.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    logger.info("🧪 Test endpoint called")
    
    if request.method == 'GET':
        return jsonify({"success": True, "message": "GET request works", "method": "GET"})
    
    if request.method == 'POST':
        data = request.get_json()
        logger.info(f"🧪 POST data received: {data}")
        return jsonify({"success": True, "message": "POST request works", "data": data, "method": "POST"})

@test_bp.route('/api/test-supabase', methods=['GET'])
def test_supabase():
    logger.info("🧪 Testing Supabase connection")
    
    supabase = current_app.config.get("SUPABASE")
    
    try:
        result = supabase.table('auth_users').select("id").limit(1).execute()
        return jsonify({"success": True, "message": "Supabase connection works", "result": str(result)})
    except Exception as e:
        logger.error(f"🧪 Supabase error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500