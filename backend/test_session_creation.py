#!/usr/bin/env python3
"""Test attendance session creation after table creation"""

import requests
import json

# Test the create session endpoint
print("=== TESTING ATTENDANCE SESSION CREATION ===")

session_data = {
    "date": "2025-11-06",
    "subject": "Test Subject",
    "department": "Computer Science", 
    "year": "2nd Year",
    "division": "A",
    "duration": 10
}

try:
    response = requests.post(
        "http://localhost:5000/api/attendance/create_session",
        json=session_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Session created successfully!")
        print(f"Session ID: {result.get('session_id')}")
        print(f"Students count: {result.get('students_count')}")
        print(f"Duration: {result.get('duration_minutes')} minutes")
        print(f"Expires at: {result.get('expires_at')}")
    else:
        print("❌ Session creation failed")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nInstructions:")
print("1. Create the attendance_sessions table in Supabase first")
print("2. Make sure the backend server is running")
print("3. Then try creating an attendance session in the frontend")