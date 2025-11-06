#!/usr/bin/env python3
"""Test script for face recognition demo endpoint"""

import requests
import base64
import json

# Create a simple test image (base64 encoded 1x1 pixel PNG)
# This is just to test the API endpoint - won't match any face
test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

# Test the demo recognition endpoint
print("=== TESTING DEMO RECOGNITION ENDPOINT ===")

try:
    response = requests.post(
        "http://localhost:5000/api/demo/recognize",
        json={"image": f"data:image/png;base64,{test_image_b64}"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API endpoint is working!")
        print(f"Processing time: {result.get('processing_time', 'N/A')}s")
        print(f"Faces detected: {len(result.get('faces', []))}")
    else:
        print("❌ API endpoint error")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nNow the face recognition demo should work properly!")
print("Go to http://localhost:3001/student/demo-session and test with your camera.")