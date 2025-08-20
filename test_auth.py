#!/usr/bin/env python3
"""
Simple test script for the Syria GPT Authentication API
Run this after starting the server to test basic functionality
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:9000"

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return False

def test_signup():
    """Test user registration"""
    test_user = {
        "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=test_user)
        print(f"✅ Sign Up: {response.status_code} - {response.json()}")
        return response.status_code == 200, test_user
    except Exception as e:
        print(f"❌ Sign Up failed: {e}")
        return False, None

def test_signin(user_data):
    """Test user login"""
    if not user_data:
        return False, None
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signin", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            print(f"✅ Sign In: {response.status_code} - Got tokens")
            return True, tokens
        else:
            print(f"❌ Sign In: {response.status_code} - {response.json()}")
            return False, None
    except Exception as e:
        print(f"❌ Sign In failed: {e}")
        return False, None

def test_protected_route(tokens):
    """Test accessing protected route"""
    if not tokens:
        return False
    
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"✅ Protected Route (/auth/me): {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Protected Route failed: {e}")
        return False

def test_google_auth_url():
    """Test Google auth URL generation"""
    try:
        response = requests.get(f"{BASE_URL}/auth/google")
        print(f"✅ Google Auth URL: {response.status_code} - URL generated")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Google Auth URL failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Syria GPT Authentication API")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        sys.exit(1)
    
    # Test 2: Sign up
    signup_success, user_data = test_signup()
    
    # Test 3: Sign in (only if signup succeeded)
    signin_success, tokens = test_signin(user_data) if signup_success else (False, None)
    
    # Test 4: Protected route (only if signin succeeded)
    if signin_success:
        test_protected_route(tokens)
    
    # Test 5: Google auth URL
    test_google_auth_url()
    
    print("\n" + "=" * 50)
    print("🎉 Test completed! Check the results above.")
    print("Note: Email verification and password reset require SMTP configuration.")
    print("Note: Google OAuth requires proper Google Client ID/Secret configuration.")

if __name__ == "__main__":
    main()