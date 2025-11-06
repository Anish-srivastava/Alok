# teacher/attendance_records.py - OPTIMIZED VERSION

import io
import base64
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from PIL import Image
from scipy.spatial.distance import cosine
from deepface import DeepFace
import logging
import time

logger = logging.getLogger(__name__)

# Attendance Blueprint with URL prefix
attendance_session_bp = Blueprint(
    "attendance_session",
    __name__,
    url_prefix="/api/attendance"
)

# ----------------- OPTIMIZED Helper Functions ----------------- #

def read_image_from_base64_optimized(image_b64: str, target_size=(640, 480)):
    """Convert base64 image to RGB numpy array with optimization"""
    if image_b64.startswith("data:"):
        image_b64 = image_b64.split(",", 1)[1]
    
    image_bytes = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Resize large images to reduce processing time
    if img.width > target_size[0] or img.height > target_size[1]:
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    return np.array(img)

def detect_faces_optimized(rgb_image, detector):
    """Detect faces using preloaded MTCNN detector"""
    # Skip detection if image is too small
    if rgb_image.shape[0] < 50 or rgb_image.shape[1] < 50:
        return []
    
    detections = detector.detect_faces(rgb_image)
    faces = []
    
    for d in detections:
        if d["confidence"] > 0.85:  # Slightly lower threshold for better detection
            x, y, w, h = d["box"]
            x, y = max(0, x), max(0, y)
            if w > 40 and h > 40:  # Lower minimum size for better detection
                face_rgb = rgb_image[y:y+h, x:x+w]
                faces.append({
                    "box": (x, y, w, h), 
                    "face": face_rgb, 
                    "confidence": d["confidence"]
                })
    
    return faces

def extract_embedding_optimized(face_rgb):
    """Extract embedding using preloaded DeepFace model"""
    try:
        if face_rgb.shape[0] < 40 or face_rgb.shape[1] < 40:
            return None
            
        # Resize face to standard size
        face_pil = Image.fromarray(face_rgb.astype("uint8")).resize((160, 160))
        face_array = np.array(face_pil)
        
        # Use DeepFace with optimized parameters
        rep = DeepFace.represent(
            face_array, 
            model_name="Facenet512", 
            detector_backend="skip",
            enforce_detection=False  # Skip additional detection for speed
        )
        return np.array(rep[0]["embedding"], dtype=np.float32)  # Use float32 for speed
        
    except Exception as e:
        logger.error(f"Embedding extraction error: {e}")
        return None

def get_attendance_collection():
    """Get the attendance collection from app config"""
    return current_app.config.get("SUPABASE")

# Enhanced embedding cache for attendance sessions
class AttendanceEmbeddingCache:
    def __init__(self):
        self.cached_embeddings = {}
        self.last_update = {}
        self.cache_duration = 600  # 10 minutes for attendance sessions
    
    def get_session_embeddings(self, students_col, session_filter):
        """Get cached embeddings for specific session filters"""
        cache_key = str(sorted(session_filter.items()))
        current_time = time.time()
        
        if (cache_key not in self.cached_embeddings or 
            current_time - self.last_update.get(cache_key, 0) > self.cache_duration):
            
            logger.info(f"Refreshing attendance embedding cache for {session_filter}")
            
            # Fetch students matching the session filter
            students = list(students_col.find(session_filter))
            
            # Process embeddings - handle both old and new embedding formats
            session_embeddings = []
            for student in students:
                # Handle multiple embedding formats
                embeddings = student.get('embeddings') or student.get('embedding')
                if embeddings:
                    if isinstance(embeddings, list) and len(embeddings) > 0:
                        # Multiple embeddings - average them
                        if isinstance(embeddings[0], list):
                            avg_embedding = np.mean(embeddings, axis=0).astype(np.float32)
                        else:
                            avg_embedding = np.array(embeddings, dtype=np.float32)
                    else:
                        # Single embedding
                        avg_embedding = np.array(embeddings, dtype=np.float32)
                    
                    session_embeddings.append({
                        'embedding': avg_embedding,
                        'studentId': student.get('studentId'),
                        'studentName': student.get('studentName'),
                        'department': student.get('department'),
                        'year': student.get('year'),
                        'division': student.get('division')
                    })
            
            self.cached_embeddings[cache_key] = session_embeddings
            self.last_update[cache_key] = current_time
            logger.info(f"Cached {len(session_embeddings)} student embeddings for session")
        
        return self.cached_embeddings[cache_key]

# Global cache instance for attendance
attendance_cache = AttendanceEmbeddingCache()

def find_best_match_optimized_attendance(query_embedding, students_col, session_doc, threshold=0.6):
    """Optimized student matching for attendance with session-specific filtering"""
    # Build filter for students in this session's class
    student_filter = {"embeddings": {"$exists": True, "$ne": None}}
    
    # Add session-specific filters
    if session_doc.get("department"):
        student_filter["department"] = session_doc.get("department")
    if session_doc.get("year"):
        student_filter["year"] = session_doc.get("year")
    if session_doc.get("division"):
        student_filter["division"] = session_doc.get("division")
    
    # Get cached embeddings for this session
    cached_embeddings = attendance_cache.get_session_embeddings(students_col, student_filter)
    
    if not cached_embeddings:
        return None, float('inf')
    
    best_match = None
    min_distance = float('inf')
    
    # Vectorized comparison for speed
    for student_data in cached_embeddings:
        stored_embedding = student_data['embedding']
        distance = cosine(query_embedding, stored_embedding)
        
        if distance < min_distance:
            min_distance = distance
            best_match = student_data
    
    return best_match if min_distance < threshold else None, min_distance

# ----------------- OPTIMIZED Routes ----------------- #

@attendance_session_bp.route("/create_session", methods=["POST"])
def create_session():
    """Create a new attendance session"""
    data = request.json
    supabase = current_app.config.get("SUPABASE")
    # Read duration (minutes) if provided (default 10 minutes)
    try:
        duration_minutes = int(data.get("duration", 10))
        if duration_minutes <= 0:
            duration_minutes = 10
    except Exception:
        duration_minutes = 10

    # Build base session document
    session_doc = {
        "date": data.get("date"),
        "subject": data.get("subject"),
        "department": data.get("department"),
        "year": data.get("year"),
        "division": data.get("division"),
        "created_at": datetime.now().isoformat(),
        "duration_minutes": duration_minutes,
        # session expires after duration_minutes from creation
        "expires_at": (datetime.now() + timedelta(minutes=duration_minutes)).isoformat(),
        "finalized": False,
        "ended_at": None,
        "students": []
    }

    # Prepopulate session with all students in that class
    student_filter = {}
    if data.get("department"): student_filter["department"] = data.get("department")
    if data.get("year"): student_filter["year"] = data.get("year")
    if data.get("division"): student_filter["division"] = data.get("division")

    try:
        # Use Supabase to get students
        if student_filter:
            query = supabase.table('students').select('student_id, student_name, department, year, division')
            for key, value in student_filter.items():
                query = query.eq(key, value)
            response = query.execute()
            students = response.data
        else:
            students = []
            
        for s in students:
            sid = s.get("student_id")
            name = s.get("student_name")
            session_doc["students"].append({
                "student_id": sid,
                "student_name": name,
                "present": False,
                "marked_at": None
            })
        
        logger.info(f"Created session with {len(students)} students preloaded")
        
    except Exception as e:
        logger.error(f"Error preloading students: {e}")
        # Continue with empty students list

    try:
        # Insert session into Supabase attendance_sessions table
        response = supabase.table('attendance_sessions').insert(session_doc).execute()
        session_id = response.data[0]['id']
        
        # return expires_at as ISO string for frontend timers
        return jsonify({
            "session_id": str(session_id),
            "students_count": len(session_doc["students"]),
            "duration_minutes": duration_minutes,
            "expires_at": session_doc["expires_at"]
        })
    except Exception as e:
        logger.error(f"Error creating session in Supabase: {e}")
        return jsonify({"error": "Failed to create session"}), 500

@attendance_session_bp.route("/end_session", methods=["POST"])
def end_session():
    """Finalize an attendance session with enhanced logging"""
    data = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    try:
        collection = get_attendance_collection()
        db = current_app.config.get("DB")
        students_col = db.students

        session_doc = collection.find_one({"_id": ObjectId(session_id)})
        if not session_doc:
            return jsonify({"error": "Session not found"}), 404

        # Build set of present student ids
        present_students = set(
            s.get("student_id") for s in session_doc.get("students", []) 
            if s.get("present")
        )

        # Get all students in that class
        student_filter = {}
        if session_doc.get("department"): student_filter["department"] = session_doc.get("department")
        if session_doc.get("year"): student_filter["year"] = session_doc.get("year")
        if session_doc.get("division"): student_filter["division"] = session_doc.get("division")

        all_students = list(students_col.find(student_filter)) if student_filter else []
        
        # Mark absent students
        absent_count = 0
        for s in all_students:
            sid = s.get("studentId") or s.get("student_id")
            sname = s.get("studentName") or s.get("student_name")
            
            if sid not in present_students:
                # Update existing entry or create new absent entry
                updated = collection.update_one(
                    {"_id": ObjectId(session_id), "students.student_id": sid},
                    {"$set": {"students.$.present": False, "students.$.marked_at": None}}
                )
                
                if updated.matched_count == 0:
                    # No existing entry, add new absent entry
                    collection.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$push": {
                            "students": {
                                "student_id": sid, 
                                "student_name": sname, 
                                "present": False, 
                                "marked_at": None
                            }
                        }}
                    )
                absent_count += 1

        # Mark session as finalized
        collection.update_one(
            {"_id": ObjectId(session_id)}, 
            {"$set": {"finalized": True, "ended_at": datetime.now()}}
        )

        logger.info(f"Session finalized: {len(present_students)} present, {absent_count} absent")

        return jsonify({
            "success": True,
            "statistics": {
                "present_count": len(present_students),
                "absent_count": absent_count,
                "total_students": len(all_students)
            }
        })

    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@attendance_session_bp.route("/real-mark", methods=["POST"])
def mark_attendance_with_duplicate_prevention():
    """Attendance marking with enhanced duplicate prevention"""
    start_time = time.time()
    
    # Check if models are ready
    model_manager = current_app.config.get("MODEL_MANAGER")
    if not model_manager or not model_manager.is_ready():
        return jsonify({"error": "Face recognition models not initialized"}), 503
    
    detector = model_manager.get_detector()
    
    data = request.get_json()
    session_id = data.get("session_id")
    image_b64 = data.get("image")

    if not session_id or not image_b64:
        return jsonify({"error": "Missing session_id or image"}), 400

    try:
        # Use same image processing as demo
        rgb = read_image_from_base64_optimized(image_b64)
        faces = detect_faces_optimized(rgb, detector)

        if len(faces) == 0:
            return jsonify({"message": "No faces detected", "faces": []})

        # Validate session
        collection = get_attendance_collection()
        session_doc = collection.find_one({"_id": ObjectId(session_id)})
        if not session_doc:
            return jsonify({"error": "Session not found"}), 404

        # Check if session already finalized
        if session_doc.get("finalized"):
            return jsonify({"error": "Session already finalized"}), 400

        # Check if session has expired based on duration
        expires_at = session_doc.get("expires_at")
        if expires_at:
            # expires_at stored as datetime in MongoDB
            now = datetime.now()
            if now > expires_at:
                # finalize session and return expired message
                collection.update_one({"_id": ObjectId(session_id)}, {"$set": {"finalized": True, "ended_at": now}})
                logger.info(f"Session {session_id} expired at {expires_at}, auto-finalized")
                return jsonify({"error": "Session expired"}), 400

        # GET LIST OF ALREADY MARKED STUDENTS IN THIS SESSION
        already_present_students = set()
        for student_entry in session_doc.get("students", []):
            if student_entry.get("present") == True:
                already_present_students.add(student_entry.get("student_id"))
        
        logger.info(f"Session {session_id} already has {len(already_present_students)} students marked present")

        # Recognition logic (same as demo session)
        db = current_app.config.get("DB")
        students_col = db.students
        threshold = float(current_app.config.get("THRESHOLD", 0.6))
        
        # Search ALL students (same as demo session)
        students = list(students_col.find({"embeddings": {"$exists": True, "$ne": None}}))
        results = []

        for f in faces:
            emb = extract_embedding_optimized(f["face"])
            if emb is None:
                results.append({
                    "match": None, 
                    "distance": None, 
                    "box": f["box"],
                    "error": "Failed to extract embedding"
                })
                continue

            # EXACT SAME MATCHING LOGIC AS DEMO SESSION
            best, min_d = None, float("inf")
            for student in students:
                stored_embeddings = student.get("embeddings", [])
                if not stored_embeddings:
                    continue
                
                # Average multiple embeddings
                if isinstance(stored_embeddings, list) and len(stored_embeddings) > 0:
                    avg_embedding = np.mean(stored_embeddings, axis=0)
                else:
                    avg_embedding = np.array(stored_embeddings)
                
                d = cosine(emb, avg_embedding)
                if d < min_d:
                    min_d = d
                    best = student

            if min_d < threshold and best:
                student_id = best.get("studentId")
                student_name = best.get("studentName")

                # CHECK FOR DUPLICATE BEFORE MARKING
                if student_id in already_present_students:
                    # Student already marked present in this session
                    results.append({
                        "match": {"user_id": student_id, "name": student_name},
                        "distance": round(float(min_d), 4),
                        "confidence": round((1 - min_d) * 100, 1),
                        "box": f["box"],
                        "already_marked": True,
                        "status": "duplicate",
                        "message": f"{student_name} is already marked present in this session"
                    })
                    logger.info(f"Duplicate detection: {student_name} ({student_id}) already present")
                    continue

                # MARK ATTENDANCE (Student not yet marked)
                updated = collection.update_one(
                    {"_id": ObjectId(session_id), "students.student_id": student_id, "students.present": False},
                    {"$set": {"students.$.present": True, "students.$.marked_at": datetime.now()}}
                )

                if updated.matched_count > 0 and updated.modified_count > 0:
                    # Successfully marked present
                    already_present_students.add(student_id)  # Update our local set
                    results.append({
                        "match": {"user_id": student_id, "name": student_name},
                        "distance": round(float(min_d), 4),
                        "confidence": round((1 - min_d) * 100, 1),
                        "box": f["box"],
                        "already_marked": False,
                        "status": "marked_present",
                        "message": f"{student_name} marked present successfully"
                    })
                    logger.info(f"✅ Marked {student_name} ({student_id}) as present")
                
                else:
                    # Student entry doesn't exist, create new one
                    collection.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$push": {
                            "students": {
                                "student_id": student_id,
                                "student_name": student_name,
                                "present": True,
                                "marked_at": datetime.now()
                            }
                        }}
                    )
                    already_present_students.add(student_id)  # Update our local set
                    results.append({
                        "match": {"user_id": student_id, "name": student_name},
                        "distance": round(float(min_d), 4),
                        "confidence": round((1 - min_d) * 100, 1),
                        "box": f["box"],
                        "already_marked": False,
                        "status": "marked_present_new",
                        "message": f"{student_name} added to session and marked present"
                    })
                    logger.info(f"✅ Added {student_name} ({student_id}) to session as present")

            else:
                # No match found
                results.append({
                    "match": None, 
                    "distance": round(float(min_d), 4) if min_d != float('inf') else None,
                    "confidence": round((1 - min_d) * 100, 1) if min_d != float('inf') else None,
                    "box": f["box"],
                    "status": "no_match",
                    "message": "Face not recognized"
                })

        processing_time = time.time() - start_time
        
        # Return comprehensive response
        return jsonify({
            "message": "Recognition processed", 
            "faces": results, 
            "processing_time": round(processing_time, 3),
            "session_info": {
                "session_id": session_id,
                "total_present_now": len(already_present_students),
                "faces_detected": len(faces),
                "duplicates_prevented": sum(1 for r in results if r.get("status") == "duplicate")
            }
        })

    except Exception as e:
        logger.error(f"Attendance error: {e}")
        return jsonify({"error": str(e)}), 500

    """Finalize an attendance session with enhanced logging"""
    data = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    try:
        collection = get_attendance_collection()
        db = current_app.config.get("DB")
        students_col = db.students

        session_doc = collection.find_one({"_id": ObjectId(session_id)})
        if not session_doc:
            return jsonify({"error": "Session not found"}), 404

        # Build set of present student ids
        present_students = set(
            s.get("student_id") for s in session_doc.get("students", []) 
            if s.get("present")
        )

        # Get all students in that class
        student_filter = {}
        if session_doc.get("department"): student_filter["department"] = session_doc.get("department")
        if session_doc.get("year"): student_filter["year"] = session_doc.get("year")
        if session_doc.get("division"): student_filter["division"] = session_doc.get("division")

        all_students = list(students_col.find(student_filter)) if student_filter else []
        
        # Mark absent students
        absent_count = 0
        for s in all_students:
            sid = s.get("studentId") or s.get("student_id")
            sname = s.get("studentName") or s.get("student_name")
            
            if sid not in present_students:
                # Update existing entry or create new absent entry
                updated = collection.update_one(
                    {"_id": ObjectId(session_id), "students.student_id": sid},
                    {"$set": {"students.$.present": False, "students.$.marked_at": None}}
                )
                
                if updated.matched_count == 0:
                    # No existing entry, add new absent entry
                    collection.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$push": {
                            "students": {
                                "student_id": sid, 
                                "student_name": sname, 
                                "present": False, 
                                "marked_at": None
                            }
                        }}
                    )
                absent_count += 1

        # Mark session as finalized
        collection.update_one(
            {"_id": ObjectId(session_id)}, 
            {"$set": {"finalized": True, "ended_at": datetime.now()}}
        )

        logger.info(f"Session finalized: {len(present_students)} present, {absent_count} absent")

        return jsonify({
            "success": True,
            "statistics": {
                "present_count": len(present_students),
                "absent_count": absent_count,
                "total_students": len(all_students)
            }
        })

    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Get active sessions for students
@attendance_session_bp.route("/active_sessions", methods=["GET"])
def get_active_sessions():
    """Get all active attendance sessions that haven't expired"""
    supabase = current_app.config.get("SUPABASE")
    
    try:
        # Get current time
        current_time = datetime.now().isoformat()
        
        # Fetch active sessions that haven't expired and aren't finalized
        response = supabase.table('attendance_sessions').select('*').eq('finalized', False).gt('expires_at', current_time).execute()
        sessions = response.data
        
        # Format sessions for frontend
        active_sessions = []
        for session in sessions:
            active_sessions.append({
                "session_id": session['id'],
                "date": session['date'],
                "subject": session['subject'],
                "department": session['department'],
                "year": session['year'],
                "division": session['division'],
                "duration_minutes": session['duration_minutes'],
                "expires_at": session['expires_at'],
                "created_at": session['created_at']
            })
        
        return jsonify({
            "success": True,
            "active_sessions": active_sessions,
            "count": len(active_sessions)
        })
        
    except Exception as e:
        logger.error(f"Error fetching active sessions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Mark attendance for a student in a session
@attendance_session_bp.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    """Mark attendance for a student in an active session"""
    data = request.json
    supabase = current_app.config.get("SUPABASE")
    
    session_id = data.get("session_id")
    student_id = data.get("student_id")
    student_name = data.get("student_name")
    
    if not session_id or not student_id or not student_name:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    try:
        # Check if session exists and is active
        current_time = datetime.now().isoformat()
        session_response = supabase.table('attendance_sessions').select('*').eq('id', session_id).eq('finalized', False).gt('expires_at', current_time).execute()
        
        if not session_response.data:
            return jsonify({"success": False, "error": "Session not found or expired"}), 404
        
        session = session_response.data[0]
        
        # Check if student is already marked present
        existing_record = supabase.table('attendance_records').select('*').eq('session_id', session_id).eq('student_id', student_id).execute()
        
        if existing_record.data:
            return jsonify({"success": False, "error": "Attendance already marked for this student"}), 400
        
        # Create attendance record
        attendance_record = {
            "session_id": session_id,
            "student_id": student_id,
            "student_name": student_name,
            "present": True,
            "marked_at": datetime.now().isoformat()
        }
        
        # Insert attendance record
        supabase.table('attendance_records').insert(attendance_record).execute()
        
        # Update session's students array to mark as present
        students = session.get('students', [])
        for student in students:
            if student.get('student_id') == student_id:
                student['present'] = True
                student['marked_at'] = datetime.now().isoformat()
                break
        
        # Update session with modified students array
        supabase.table('attendance_sessions').update({"students": students}).eq('id', session_id).execute()
        
        return jsonify({
            "success": True,
            "message": "Attendance marked successfully",
            "student_id": student_id,
            "student_name": student_name,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Check if student has already marked attendance for active sessions
@attendance_session_bp.route("/check_attendance/<student_id>", methods=["GET"])
def check_student_attendance(student_id):
    """Check if student has marked attendance for any active sessions"""
    supabase = current_app.config.get("SUPABASE")
    
    try:
        # Get current time
        current_time = datetime.now().isoformat()
        
        # Check for attendance records in active sessions
        attendance_response = supabase.table('attendance_records').select('session_id').eq('student_id', student_id).execute()
        
        if attendance_response.data:
            # Get session IDs where student has marked attendance
            marked_session_ids = [record['session_id'] for record in attendance_response.data]
            
            # Check if any of these sessions are still active
            active_marked_sessions = []
            for session_id in marked_session_ids:
                session_response = supabase.table('attendance_sessions').select('*').eq('id', session_id).eq('finalized', False).gt('expires_at', current_time).execute()
                if session_response.data:
                    active_marked_sessions.append(session_response.data[0])
            
            return jsonify({
                "success": True,
                "has_marked_attendance": len(active_marked_sessions) > 0,
                "marked_sessions": active_marked_sessions
            })
        
        return jsonify({
            "success": True,
            "has_marked_attendance": False,
            "marked_sessions": []
        })
        
    except Exception as e:
        logger.error(f"Error checking student attendance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Get attendance records for a session (for teachers)
@attendance_session_bp.route("/session_attendance/<session_id>", methods=["GET"])
def get_session_attendance(session_id):
    """Get all attendance records for a specific session"""
    supabase = current_app.config.get("SUPABASE")
    
    try:
        # Get session details
        session_response = supabase.table('attendance_sessions').select('*').eq('id', session_id).execute()
        
        if not session_response.data:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        session = session_response.data[0]
        
        # Get attendance records for this session
        attendance_response = supabase.table('attendance_records').select('*').eq('session_id', session_id).execute()
        attendance_records = attendance_response.data
        
        # Count present and total students
        total_students = len(session.get('students', []))
        present_count = len(attendance_records)
        
        return jsonify({
            "success": True,
            "session": {
                "id": session['id'],
                "date": session['date'],
                "subject": session['subject'],
                "department": session['department'],
                "year": session['year'],
                "division": session['division'],
                "created_at": session['created_at'],
                "expires_at": session['expires_at'],
                "finalized": session['finalized']
            },
            "attendance_records": attendance_records,
            "statistics": {
                "total_students": total_students,
                "present_count": present_count,
                "absent_count": total_students - present_count,
                "attendance_percentage": round((present_count / total_students * 100) if total_students > 0 else 0, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching session attendance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Health check for attendance models
@attendance_session_bp.route("/models/status", methods=["GET"])
def attendance_model_status():
    """Check model status for attendance system"""
    model_manager = current_app.config.get("MODEL_MANAGER")
    
    if not model_manager:
        return jsonify({
            "success": False,
            "error": "Model manager not available"
        }), 500
    
    return jsonify({
        "success": True,
        "models_ready": model_manager.is_ready(),
        "health_check": model_manager.health_check(),
        "cache_info": {
            "embedding_cache_active": True,
            "cache_duration": "10 minutes"
        },
        "timestamp": time.time()
    })
