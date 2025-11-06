#!/usr/bin/env python3
"""
Test signup after database fix
"""

import requests
import json

# Test data
test_user = {
    "username": "testuser",
    "email": "testuser@example.com", 
    "password": "password123",
    "employeeId": "STU001",
    "userType": "student"
}

test_teacher = {
    "username": "testteacher",
    "email": "testteacher@example.com",
    "password": "password123", 
    "employeeId": "EMP001",
    "userType": "teacher",
    "department": "Computer Science"
}

print("=== TESTING SIGNUP ENDPOINT ===")

# Test student signup
print("\n1. Testing student signup...")
try:
    response = requests.post(
        "http://127.0.0.1:5000/api/signup",
        headers={"Content-Type": "application/json"},
        json=test_user,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Student signup successful!")
    else:
        print("❌ Student signup failed")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend server")
    print("Make sure the Flask backend is running on http://127.0.0.1:5000")
    print("Run: python app.py in the backend directory")
except Exception as e:
    print(f"❌ Error: {e}")

# Test teacher signup
print("\n2. Testing teacher signup...")
try:
    response = requests.post(
        "http://127.0.0.1:5000/api/signup", 
        headers={"Content-Type": "application/json"},
        json=test_teacher,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Teacher signup successful!")
    else:
        print("❌ Teacher signup failed")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend server")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== CLEANUP ===")
print("If the tests were successful, you may want to delete the test accounts from Supabase.")
print("These test emails were used:")
print("- testuser@example.com (student)")
print("- testteacher@example.com (teacher)")