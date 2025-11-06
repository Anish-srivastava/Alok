import requests
import json

BASE_URL = "http://localhost:5000"

def test_simple_endpoints():
    print("🧪 Testing Simple Authentication Endpoints...")
    
    # Test simple signup
    print("\n1. Testing simple signup...")
    signup_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "password123",
        "userType": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/simple-signup", json=signup_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Simple signup works!")
            
            # Test simple signin
            print("\n2. Testing simple signin...")
            signin_data = {
                "email": "test@example.com",
                "password": "password123",
                "userType": "student"
            }
            
            signin_response = requests.post(f"{BASE_URL}/api/simple-signin", json=signin_data, timeout=10)
            print(f"Status: {signin_response.status_code}")
            print(f"Response: {signin_response.text}")
            
            if signin_response.status_code == 200:
                print("✅ Simple signin works!")
            else:
                print("❌ Simple signin failed")
        else:
            print("❌ Simple signup failed")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Request error: {e}")

def test_regular_endpoints():
    print("\n🧪 Testing Regular Authentication Endpoints...")
    
    # Test regular signup
    print("\n1. Testing regular signup...")
    signup_data = {
        "username": "regular_user",
        "email": "regular@example.com",
        "password": "password123",
        "userType": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/signup", json=signup_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Regular signup works!")
        else:
            print("❌ Regular signup failed")
            
    except requests.exceptions.Timeout:
        print("❌ Regular signup timed out")
    except Exception as e:
        print(f"❌ Regular signup error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Authentication Tests...")
    
    # Test health first
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print("❌ Backend health check failed")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        exit(1)
    
    # Test simple endpoints first
    test_simple_endpoints()
    
    # Test regular endpoints 
    test_regular_endpoints()
    
    print("\n🎯 Tests completed!")