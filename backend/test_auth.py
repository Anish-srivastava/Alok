import requests

BASE_URL = "http://localhost:5000"

def test_student_signup():
    """Test student signup"""
    print("Testing student signup...")
    
    student_data = {
        "username": "test_student",
        "email": "student@test.com",
        "password": "password123",
        "userType": "student"
    }
    
    response = requests.post(f"{BASE_URL}/api/signup", json=student_data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_teacher_signup():
    """Test teacher signup"""
    print("\nTesting teacher signup...")
    
    teacher_data = {
        "username": "test_teacher",
        "email": "teacher@test.com",
        "password": "password123",
        "userType": "teacher",
        "employeeId": "EMP001",
        "department": "Computer Science"
    }
    
    response = requests.post(f"{BASE_URL}/api/signup", json=teacher_data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_student_signin():
    """Test student signin"""
    print("\nTesting student signin...")
    
    student_credentials = {
        "email": "student@test.com",
        "password": "password123",
        "userType": "student"
    }
    
    response = requests.post(f"{BASE_URL}/api/signin", json=student_credentials, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_teacher_signin():
    """Test teacher signin"""
    print("\nTesting teacher signin...")
    
    teacher_credentials = {
        "email": "teacher@test.com",
        "password": "password123",
        "userType": "teacher"
    }
    
    response = requests.post(f"{BASE_URL}/api/signin", json=teacher_credentials, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

if __name__ == "__main__":
    print("🧪 Starting Authentication Tests...")
    
    # Test health first
    if not test_health():
        print("❌ Health check failed. Make sure the backend is running.")
        exit(1)
    
    # Test signups
    student_signup_success = test_student_signup()
    teacher_signup_success = test_teacher_signup()
    
    # Test signins (only if signups were successful)
    if student_signup_success:
        test_student_signin()
    
    if teacher_signup_success:
        test_teacher_signin()
    
    print("\n✅ Authentication tests completed!")