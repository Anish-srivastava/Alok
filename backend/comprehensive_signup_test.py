#!/usr/bin/env python3
"""
Test both student and teacher signup after fixing the auth routes
"""

import requests
import json
import time

def test_signup(user_data, user_type):
    """Test signup for a specific user type"""
    print(f"\n🧪 Testing {user_type} signup...")
    print(f"Data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/signup",
            headers={"Content-Type": "application/json"},
            json=user_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200 and response_data.get('success'):
            print(f"✅ {user_type} signup SUCCESSFUL!")
            return True
        else:
            print(f"❌ {user_type} signup FAILED")
            if 'error' in response_data:
                print(f"Error details: {response_data['error']}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server")
        print("Make sure the backend is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("=" * 80)
    print("🧪 COMPREHENSIVE SIGNUP TEST")
    print("=" * 80)
    
    # Test student signup
    student_data = {
        "username": "teststudent123",
        "email": "student123@test.com",
        "password": "password123",
        "employeeId": "STU123",
        "userType": "student"
    }
    
    student_success = test_signup(student_data, "Student")
    
    time.sleep(1)  # Small delay between tests
    
    # Test teacher signup  
    teacher_data = {
        "username": "testteacher123",
        "email": "teacher123@test.com",
        "password": "password123",
        "employeeId": "EMP123",
        "userType": "teacher",
        "department": "Computer Science"
    }
    
    teacher_success = test_signup(teacher_data, "Teacher")
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS")
    print("=" * 80)
    print(f"Student signup: {'✅ PASS' if student_success else '❌ FAIL'}")
    print(f"Teacher signup: {'✅ PASS' if teacher_success else '❌ FAIL'}")
    
    if student_success and teacher_success:
        print("\n🎉 ALL TESTS PASSED! Signup is working correctly!")
        print("✅ You can now use the frontend: http://localhost:3000/signup")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
        if not teacher_success:
            print("\n🔧 If teacher signup failed with 'user_type' error, run this SQL in Supabase:")
            print("ALTER TABLE auth_teachers ADD COLUMN IF NOT EXISTS user_type TEXT;")
    
    print("\n" + "=" * 80)
    print("🧹 CLEANUP")
    print("=" * 80)
    print("Test accounts created (you may want to delete them from Supabase):")
    print("- student123@test.com")
    print("- teacher123@test.com")

if __name__ == "__main__":
    main()