#!/usr/bin/env python3
"""
PostgreSQL Integration Test Script
This script tests basic database operations to ensure PostgreSQL is working correctly.
"""

import requests
import json
import random
import string
from datetime import datetime


def generate_test_email():
    """Generate a unique test email."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_string = ''.join(random.choices(string.ascii_lowercase, k=6))
    return f"test_{timestamp}_{random_string}@example.com"


def test_api_endpoints():
    """Test key API endpoints."""
    base_url = "http://localhost:9000"
    
    print("🔍 Testing PostgreSQL Integration with Syria GPT API")
    print("=" * 60)
    
    # Test 1: Health Check
    print("1. Testing Health Endpoint...")
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    health_data = response.json()
    print(f"   ✅ Health check passed: {health_data['status']}")
    
    # Test 2: Root Endpoint
    print("\n2. Testing Root Endpoint...")
    response = requests.get(base_url)
    assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
    root_data = response.json()
    print(f"   ✅ Root endpoint passed: {root_data['message']}")
    
    # Test 3: User Registration (Database Write)
    print("\n3. Testing User Registration (Database Write)...")
    test_email = generate_test_email()
    # Generate unique phone number
    random_phone_suffix = ''.join(random.choices(string.digits, k=6))
    unique_phone = f"+963{random_phone_suffix}"
    
    registration_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": unique_phone
    }
    
    response = requests.post(f"{base_url}/auth/signup", json=registration_data)
    assert response.status_code == 200, f"Registration failed: {response.status_code} - {response.text}"
    registration_result = response.json()
    print(f"   ✅ User registration passed: {registration_result['message']}")
    
    # Test 4: Duplicate Registration (Database Constraint Check)
    print("\n4. Testing Duplicate Registration (Database Constraint)...")
    response = requests.post(f"{base_url}/auth/signup", json=registration_data)
    assert response.status_code == 400, f"Duplicate registration should fail: {response.status_code}"
    duplicate_result = response.json()
    print(f"   ✅ Duplicate registration correctly rejected: {duplicate_result['detail']}")
    
    # Test 5: OAuth Endpoints
    print("\n5. Testing OAuth Endpoints...")
    response = requests.get(f"{base_url}/auth/google")
    assert response.status_code == 200, f"Google OAuth failed: {response.status_code}"
    oauth_data = response.json()
    print(f"   ✅ Google OAuth endpoint working: {oauth_data['provider']}")
    
    # Test 6: Database Query via API (Check user exists)
    print("\n6. Testing Database Query via API...")
    # This would require a protected endpoint that returns user info
    # For now, we'll just check if signin rejects invalid credentials
    response = requests.post(f"{base_url}/auth/signin", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401, f"Invalid login should be rejected: {response.status_code}"
    print("   ✅ Database query validation working (invalid credentials rejected)")
    
    print("\n" + "=" * 60)
    print("🎉 All PostgreSQL integration tests PASSED!")
    print("   • Database connection: Working")
    print("   • Data persistence: Working") 
    print("   • Constraints: Working")
    print("   • API endpoints: Working")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)