from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import time

attendance_bp = Blueprint("attendance", __name__)

# ------------------------- GET ATTENDANCE -------------------------
@attendance_bp.route('/api/attendance', methods=['GET'])
def get_attendance():
    supabase = current_app.config.get("SUPABASE")
    
    date = request.args.get('date')
    department = request.args.get('department')
    year = request.args.get('year')
    division = request.args.get('division')
    subject = request.args.get('subject')
    student_id = request.args.get('student_id')

    try:
        # Build filters for students query
        student_query = supabase.table("students").select("*")
        if department: 
            student_query = student_query.eq("department", department)
        if year: 
            student_query = student_query.eq("year", year)
        if division: 
            student_query = student_query.eq("division", division)
        if student_id: 
            student_query = student_query.eq("student_id", student_id)

        students_result = student_query.execute()
        students = students_result.data if students_result.data else []

        # Build filters for attendance query
        attendance_query = supabase.table("attendance_records").select("*")
        if date:
            # Filter by date (attendance records have created_at field)
            attendance_query = attendance_query.gte("created_at", f"{date}T00:00:00")
            attendance_query = attendance_query.lt("created_at", f"{date}T23:59:59")
        if student_id:
            attendance_query = attendance_query.eq("student_id", student_id)

        attendance_result = attendance_query.execute()
        attendance_records = attendance_result.data if attendance_result.data else []

        # Create a map of student_id -> attendance record
        attendance_map = {}
        for record in attendance_records:
            sid = record.get("student_id")
            if sid:
                attendance_map[sid] = record

        # Build attendance list combining students and their attendance
        attendance_list = []
        for student in students:
            sid = student.get("student_id")
            attendance_record = attendance_map.get(sid)
            
            if attendance_record:
                # Student has attendance record
                status = "present" if attendance_record.get("present") else "absent"
                marked_at = attendance_record.get("marked_at") or attendance_record.get("created_at")
            else:
                # Student doesn't have attendance record for this date
                status = "absent"
                marked_at = None

            attendance_list.append({
                "studentId": str(sid),
                "studentName": student.get("student_name"),
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "subject": subject or "N/A",
                "department": student.get("department"),
                "year": student.get("year"),
                "division": student.get("division"),
                "status": status,
                "markedAt": marked_at,
                "confidence": attendance_record.get("confidence", 0) if attendance_record else 0
            })

        # Calculate stats
        total_students = len(students)
        present_count = len([r for r in attendance_list if r.get("status") == "present"])
        absent_count = total_students - present_count
        attendance_rate = round((present_count / total_students * 100) if total_students > 0 else 0, 1)

        return jsonify({
            "success": True,
            "attendance": attendance_list,
            "stats": {
                "totalStudents": total_students,
                "presentToday": present_count,
                "absentToday": absent_count,
                "attendanceRate": attendance_rate
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------------- EXPORT TO EXCEL -------------------------
@attendance_bp.route('/api/attendance/export', methods=['GET'])
def export_attendance():
    supabase = current_app.config.get("SUPABASE")
    
    date = request.args.get('date')
    department = request.args.get('department')
    year = request.args.get('year')
    division = request.args.get('division')
    subject = request.args.get('subject')

    try:
        # Build filters for students query
        student_query = supabase.table("students").select("*")
        if department: 
            student_query = student_query.eq("department", department)
        if year: 
            student_query = student_query.eq("year", year)
        if division: 
            student_query = student_query.eq("division", division)

        students_result = student_query.execute()
        students = students_result.data if students_result.data else []

        # Build filters for attendance query
        attendance_query = supabase.table("attendance_records").select("*")
        if date:
            attendance_query = attendance_query.gte("created_at", f"{date}T00:00:00")
            attendance_query = attendance_query.lt("created_at", f"{date}T23:59:59")

        attendance_result = attendance_query.execute()
        attendance_records = attendance_result.data if attendance_result.data else []

        # Create a set of present student IDs
        present_students = set()
        for record in attendance_records:
            if record.get("present"):
                present_students.add(record.get("student_id"))

        # Build export data
        export_data = []
        for student in students:
            sid = student.get("student_id")
            status = "present" if sid in present_students else "absent"
            export_data.append({
                "studentId": str(sid),
                "name": student.get("student_name"),
                "subject": str(subject) if subject else "N/A",
                "date": str(date) if date else "N/A",
                "status": status
            })

        return jsonify({"success": True, "data": export_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500