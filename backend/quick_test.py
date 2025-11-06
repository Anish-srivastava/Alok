import requests

print("🧪 Testing Authentication without bcrypt...")

# Test signup
print("Testing signup...")
signup_data = {
    "username": "test_user",
    "email": "test@example.com", 
    "password": "password123",
    "userType": "student"
}

try:
    response = requests.post("http://localhost:5000/api/signup", json=signup_data, timeout=10)
    print(f"Signup Status: {response.status_code}")
    print(f"Signup Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Signup works!")
        
        # Test signin
        print("\nTesting signin...")
        signin_data = {
            "email": "test@example.com",
            "password": "password123", 
            "userType": "student"
        }
        
        signin_response = requests.post("http://localhost:5000/api/signin", json=signin_data, timeout=10)
        print(f"Signin Status: {signin_response.status_code}")
        print(f"Signin Response: {signin_response.text}")
        
        if signin_response.status_code == 200:
            print("✅ Signin works!")
        else:
            print("❌ Signin failed")
    else:
        print("❌ Signup failed")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 Test completed!")