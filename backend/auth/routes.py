from flask import Blueprint, request, jsonify, current_app
import time
import logging
import hashlib

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

def simple_hash(password):
    """Simple hash function for testing (NOT for production!)"""
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    logger.info("📝 Signup endpoint called")
    try:
        data = request.get_json()
        logger.info(f"📝 Received data: {data}")
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType', 'student')  # Default to student

        if not all([username, email, password]):
            logger.warning("📝 Missing required fields")
            return jsonify({"success": False, "error": "All fields required"}), 400

        supabase = current_app.config.get("SUPABASE")
        logger.info(f"📝 Supabase client: {supabase}")
        
        # Choose table based on user type
        if user_type == 'teacher':
            table_name = 'auth_teachers'
            # Add additional teacher-specific fields
            employee_id = data.get('employeeId')
            department = data.get('department', 'General')  # Default department
            
            if not employee_id:
                return jsonify({"success": False, "error": "Employee ID required for teachers"}), 400
        else:
            table_name = 'auth_users'
            # For students, employeeId is optional (could be student ID)
            employee_id = data.get('employeeId', '')  # Optional for students
        
        logger.info(f"📝 Using table: {table_name}")
        
        # Check if email already exists in the appropriate table
        logger.info(f"📝 Checking for existing email: {email}")
        existing_user = supabase.table(table_name).select("id").eq("email", email).execute()
        logger.info(f"📝 Existing user check result: {existing_user}")
        
        if existing_user.data:
            return jsonify({
                "success": False, 
                "error": f"Email already registered as {user_type}"
            }), 400

        # Use simple hash instead of bcrypt for testing
        hashed_pw = simple_hash(password)
        logger.info("📝 Password hashed successfully")

        # Prepare user document based on user type
        if user_type == 'teacher':
            # For teachers table - no user_type column
            user_doc = {
                "username": username,
                "email": email,
                "password": hashed_pw,
                "employee_id": employee_id,
                "department": department,
                "status": "active",
                "role": "teacher",
                "created_at": int(time.time())  # Convert to integer
            }
        else:
            # For students in auth_users table - has user_type column
            user_doc = {
                "username": username,
                "email": email,
                "password": hashed_pw,
                "user_type": user_type,
                "student_id": employee_id,  # Store as student_id for students
                "department": "General",  # Default department for students
                "status": "active",
                "role": "student",
                "created_at": int(time.time())  # Convert to integer
            }
        
        logger.info(f"📝 Inserting user: {user_doc}")
        result = supabase.table(table_name).insert(user_doc).execute()
        logger.info(f"📝 Insert result: {result}")
        
        if result.data:
            return jsonify({
                "success": True, 
                "message": f"{user_type.capitalize()} registered successfully"
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Registration failed"
            }), 500
            
    except Exception as e:
        logger.error(f"📝 Signup error: {str(e)}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@auth_bp.route('/api/signin', methods=['POST'])
def api_signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('userType', 'student')  # Default to student

    if not all([email, password]):
        return jsonify({"success": False, "error": "Email and password required"}), 400

    supabase = current_app.config.get("SUPABASE")
    
    # Choose table based on user type
    if user_type == 'teacher':
        table_name = 'auth_teachers'
        user_role = "teacher"
    else:
        table_name = 'auth_users'
        user_role = "student"
    
    # Find user in appropriate table
    user_result = supabase.table(table_name).select("*").eq("email", email).execute()
    
    if not user_result.data:
        return jsonify({
            "success": False, 
            "error": f"No {user_type} account found with this email"
        }), 401
    
    user = user_result.data[0]
    
    # Check password with simple hash
    if user['password'] != simple_hash(password):
        return jsonify({
            "success": False, 
            "error": "Invalid password"
        }), 401
    
    # Check if account is active
    if user.get('status') == 'inactive':
        return jsonify({
            "success": False, 
            "error": "Account is deactivated. Contact administrator."
        }), 401

    # Prepare response based on user type
    user_info = {
        "id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "userType": user_type,
        "role": user_role
    }
    
    # Add type-specific information
    if user_type == 'teacher':
        user_info.update({
            "employeeId": user.get('employee_id'),
            "department": user.get('department'),
            "name": user['username']  # Use username as display name for teachers
        })
        
        # Check if teacher has student record too (optional)
        student_result = supabase.table('students').select("*").eq("email", email).execute()
        if student_result.data:
            student_record = student_result.data[0]
            user_info['hasStudentRecord'] = True
            user_info['studentId'] = student_record.get('student_id')
    else:
        # For students, try to get student record
        student_result = supabase.table('students').select("*").eq("email", email).execute()
        if student_result.data:
            student_record = student_result.data[0]
            user_info.update({
                "studentId": student_record.get('student_id'),
                "studentName": student_record.get('student_name'),
                "department": student_record.get('department'),
                "hasStudentRecord": True
            })

    return jsonify({
        "success": True, 
        "message": f"Signed in successfully as {user_type}",
        "user": user_info,
        "userType": user_type
    })

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    # You can add logout logic here if needed (e.g., invalidate tokens)
    return jsonify({"success": True, "message": "Logged out successfully"})

# Additional route to check user type and permissions
@auth_bp.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get current user's profile information"""
    user_email = request.headers.get('X-User-Email')
    user_type = request.headers.get('X-User-Type', 'student')
    
    if not user_email:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    supabase = current_app.config.get("SUPABASE")
    
    # Get user from appropriate table
    if user_type == 'teacher':
        table_name = 'auth_teachers'
    else:
        table_name = 'auth_users'
    
    user_result = supabase.table(table_name).select("*").eq("email", user_email).execute()
    
    if not user_result.data:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    user = user_result.data[0]
    # Remove password from response
    user.pop('password', None)
    
    return jsonify({
        "success": True,
        "user": user
    })

# Route to switch user type (if user has both teacher and student accounts)
@auth_bp.route('/api/switch-role', methods=['POST'])
def switch_user_role():
    """Allow users to switch between teacher and student roles if they have both"""
    data = request.get_json()
    user_email = data.get('email')
    target_type = data.get('targetType')  # 'teacher' or 'student'
    
    if not all([user_email, target_type]):
        return jsonify({"success": False, "error": "Email and target type required"}), 400
    
    supabase = current_app.config.get("SUPABASE")
    
    # Check if user exists in target table
    if target_type == 'teacher':
        table_name = 'auth_teachers'
    else:
        table_name = 'auth_users'
    
    target_user_result = supabase.table(table_name).select("*").eq("email", user_email).execute()
    
    if not target_user_result.data:
        return jsonify({
            "success": False, 
            "error": f"No {target_type} account found for this email"
        }), 404
    
    target_user = target_user_result.data[0]
    
    # Return user info for the target role
    user_info = {
        "id": target_user['id'],
        "username": target_user['username'],
        "email": target_user['email'],
        "userType": target_type
    }
    
    if target_type == 'teacher':
        user_info.update({
            "employeeId": target_user.get('employee_id'),
            "department": target_user.get('department')
        })
    
    return jsonify({
        "success": True,
        "message": f"Switched to {target_type} role",
        "user": user_info,
        "userType": target_type
    })
