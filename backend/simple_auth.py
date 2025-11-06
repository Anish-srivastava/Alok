# Simple signup test without bcrypt
from flask import Blueprint, request, jsonify, current_app
import time
import logging

logger = logging.getLogger(__name__)
simple_auth_bp = Blueprint("simple_auth", __name__)

@simple_auth_bp.route('/api/simple-signup', methods=['POST'])
def simple_signup():
    logger.info("🧪 Simple signup endpoint called")
    
    try:
        data = request.get_json()
        logger.info(f"🧪 Received data: {data}")
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType', 'student')

        if not all([username, email, password]):
            logger.warning("🧪 Missing required fields")
            return jsonify({"success": False, "error": "All fields required"}), 400

        supabase = current_app.config.get("SUPABASE")
        logger.info(f"🧪 Supabase client: {supabase}")
        
        # Choose table based on user type
        table_name = 'auth_users' if user_type == 'student' else 'auth_teachers'
        logger.info(f"🧪 Using table: {table_name}")
        
        # Check if email already exists
        logger.info(f"🧪 Checking for existing email: {email}")
        existing_user = supabase.table(table_name).select("id").eq("email", email).execute()
        logger.info(f"🧪 Existing user check result: {existing_user}")
        
        if existing_user.data:
            return jsonify({
                "success": False, 
                "error": f"Email already registered as {user_type}"
            }), 400

        # Store password as plain text for testing (NEVER do this in production!)
        user_doc = {
            "username": username,
            "email": email,
            "password": password,  # Plain text for testing
            "user_type": user_type,
            "status": "active",
            "created_at": int(time.time())  # Convert to integer
        }
        
        if user_type == 'teacher':
            user_doc.update({
                "employee_id": data.get('employeeId', 'EMP001'),
                "department": data.get('department', 'General'),
                "role": "teacher"
            })
        
        logger.info(f"🧪 Inserting user: {user_doc}")
        result = supabase.table(table_name).insert(user_doc).execute()
        logger.info(f"🧪 Insert result: {result}")
        
        if result.data:
            return jsonify({
                "success": True, 
                "message": f"{user_type.capitalize()} registered successfully (TEST VERSION)"
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Registration failed"
            }), 500
            
    except Exception as e:
        logger.error(f"🧪 Simple signup error: {str(e)}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@simple_auth_bp.route('/api/simple-signin', methods=['POST'])
def simple_signin():
    logger.info("🧪 Simple signin endpoint called")
    
    try:
        data = request.get_json()
        logger.info(f"🧪 Received data: {data}")
        
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType', 'student')

        if not all([email, password]):
            return jsonify({"success": False, "error": "Email and password required"}), 400

        supabase = current_app.config.get("SUPABASE")
        table_name = 'auth_users' if user_type == 'student' else 'auth_teachers'
        
        # Find user
        user_result = supabase.table(table_name).select("*").eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({
                "success": False, 
                "error": f"No {user_type} account found with this email"
            }), 401
        
        user = user_result.data[0]
        
        # Check password (plain text for testing)
        if user['password'] != password:
            return jsonify({
                "success": False, 
                "error": "Invalid password"
            }), 401

        # Prepare response
        user_info = {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "userType": user_type
        }

        return jsonify({
            "success": True, 
            "message": f"Signed in successfully as {user_type} (TEST VERSION)",
            "user": user_info,
            "userType": user_type
        })
            
    except Exception as e:
        logger.error(f"🧪 Simple signin error: {str(e)}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500