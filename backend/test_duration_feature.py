#!/usr/bin/env python3
"""Test attendance session creation after table is created"""

import requests
import json
from datetime import datetime

print("=== TESTING ATTENDANCE SESSION WITH DURATION ===")

# Test data for session creation
session_data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "subject": "Test Subject with Duration",
    "department": "Computer Science", 
    "year": "2nd Year",
    "division": "A",
    "duration": 5  # 5 minutes for quick testing
}

print(f"Creating session with {session_data['duration']} minute duration...")

try:
    response = requests.post(
        "http://localhost:5000/api/attendance/create_session",
        json=session_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS! Session created with duration feature!")
        print(f"📝 Session ID: {result.get('session_id')}")
        print(f"👥 Students Count: {result.get('students_count')}")
        print(f"⏱️  Duration: {result.get('duration_minutes')} minutes")
        print(f"⏰ Expires At: {result.get('expires_at')}")
        print()
        print("🎉 The duration feature is working!")
        print("- Go to the frontend and create a session")
        print("- You'll see the duration selector (5, 10, 20, 30 min)")
        print("- A countdown timer will appear in the header")
        print("- Session will auto-expire when time runs out")
        
    else:
        print("❌ FAILED! Session creation error:")
        print(f"Response: {response.text}")
        if response.status_code == 500:
            print("\n💡 This means the attendance_sessions table still doesn't exist.")
            print("Please create it first using the SQL in SUPABASE_INSTRUCTIONS.txt")
        
except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR: Backend server is not running")
    print("Start the backend with: python app.py")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n=== WHAT TO TEST NEXT ===")
print("1. Create the table in Supabase (if you haven't)")
print("2. Run this script to verify backend works")
print("3. Test in frontend: http://localhost:3001/teacher/start-session")
print("4. Create a 5-minute session to see auto-expiration quickly")