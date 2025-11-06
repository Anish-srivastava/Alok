import requests
import json
import time

def test_simple_signup():
    """Test simple signup with direct Supabase"""
    print("Testing direct signup...")
    
    url = "http://localhost:5000/api/signup"
    data = {
        "username": "test_student",
        "email": "student@test.com", 
        "password": "password123",
        "userType": "student"
    }
    
    print(f"Sending request to: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Signup successful!")
            return True
        else:
            print("❌ Signup failed")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing signup endpoint directly...")
    test_simple_signup()