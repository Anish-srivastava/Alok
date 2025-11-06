#!/usr/bin/env python3

import requests
import json

def test_signin():
    """Test the signin endpoint"""
    url = "http://localhost:5000/api/signin"
    
    # Test data - using the user we just created
    data = {
        "email": "Anshusrivastava2412@gmail.com",
        "password": "Anish@2412"
    }
    
    try:
        print("🔐 Testing signin endpoint...")
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, json=data)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Signin successful!")
            print(f"📝 Response data: {json.dumps(response_data, indent=2)}")
        else:
            print("❌ Signin failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the backend running?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health():
    """Test the health endpoint"""
    url = "http://localhost:5000/health"
    
    try:
        print("🩺 Testing health endpoint...")
        response = requests.get(url)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Backend is healthy!")
        else:
            print("❌ Backend health check failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend is not running!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    # First check if backend is running
    test_health()
    print()
    
    # Then test signin
    test_signin()