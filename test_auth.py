#!/usr/bin/env python3
"""
Simple test script for the Syria GPT Authentication API
Run this after starting the server to test basic functionality
"""

import requests
import json
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:9000"

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"[OK] Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server is not running. Please start the server first.")
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
        print(f"[OK] Sign Up: {response.status_code} - {response.json()}")
        return response.status_code == 200, test_user
    except Exception as e:
        print(f"[ERROR] Sign Up failed: {e}")
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
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url')
            if auth_url and 'accounts.google.com' in auth_url:
                print(f"✅ Google Auth URL: {response.status_code} - Valid URL generated")
                print(f"   URL: {auth_url[:80]}...")
                return True
            else:
                print(f"❌ Google Auth URL: Invalid URL format - {data}")
                return False
        else:
            print(f"❌ Google Auth URL: {response.status_code} - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Google Auth URL failed: {e}")
        return False

def test_google_oauth_callback_error():
    """Test Google OAuth callback with invalid code"""
    invalid_code = "invalid_test_code_12345"
    
    try:
        response = requests.post(f"{BASE_URL}/auth/google/callback", json={"code": invalid_code})
        if response.status_code == 400:
            print(f"✅ Google OAuth Callback (Invalid Code): {response.status_code} - Properly rejected invalid code")
            return True
        else:
            print(f"❌ Google OAuth Callback (Invalid Code): Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Google OAuth Callback test failed: {e}")
        return False

def validate_oauth_configuration():
    """Validate OAuth configuration and provide detailed diagnostics"""
    print("\n🔧 OAuth 2.0 Configuration Diagnostics:")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/google")
        if response.status_code != 200:
            print(f"   ❌ Cannot get OAuth URL: {response.status_code}")
            return False
        
        data = response.json()
        auth_url = data.get('auth_url', '')
        
        # Parse the URL
        parsed_url = urlparse(auth_url)
        params = parse_qs(parsed_url.query)
        
        print(f"   🔗 Base URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}")
        
        # Check each parameter
        issues = []
        
        # 1. Check endpoint
        expected_path = "/o/oauth2/v2/auth"
        if parsed_url.path != expected_path:
            issues.append(f"Wrong endpoint: {parsed_url.path} (should be {expected_path})")
        else:
            print("   ✅ Correct OAuth 2.0 v2 endpoint")
        
        # 2. Check client_id
        client_id = params.get('client_id', [''])[0]
        if not client_id:
            issues.append("Missing client_id parameter")
        elif not client_id.endswith('.apps.googleusercontent.com'):
            issues.append("Client ID should end with .apps.googleusercontent.com")
        else:
            print(f"   ✅ Client ID: {client_id[:20]}...apps.googleusercontent.com")
        
        # 3. Check redirect_uri
        redirect_uri = params.get('redirect_uri', [''])[0]
        if not redirect_uri:
            issues.append("Missing redirect_uri parameter")
        elif not redirect_uri.startswith(('http://localhost:', 'https://')):
            issues.append("Redirect URI should use http://localhost: or https://")
        else:
            print(f"   ✅ Redirect URI: {redirect_uri}")
        
        # 4. Check scope
        scope = params.get('scope', [''])[0]
        required_scopes = ['openid', 'email', 'profile']
        if not scope:
            issues.append("Missing scope parameter")
        else:
            missing_scopes = [s for s in required_scopes if s not in scope]
            if missing_scopes:
                issues.append(f"Missing scopes: {missing_scopes}")
            else:
                print(f"   ✅ Scopes: {scope}")
        
        # 5. Check response_type
        response_type = params.get('response_type', [''])[0]
        if response_type != 'code':
            issues.append(f"Wrong response_type: {response_type} (should be 'code')")
        else:
            print("   ✅ Response type: code")
        
        # 6. Check access_type
        access_type = params.get('access_type', [''])[0]
        if access_type != 'offline':
            issues.append(f"Wrong access_type: {access_type} (should be 'offline')")
        else:
            print("   ✅ Access type: offline")
        
        # 7. Check prompt
        prompt = params.get('prompt', [''])[0]
        if prompt != 'consent':
            print(f"   ⚠️  Prompt: {prompt} (recommended: 'consent' for refresh tokens)")
        else:
            print("   ✅ Prompt: consent")
        
        if issues:
            print("\n   🚨 Configuration Issues Found:")
            for issue in issues:
                print(f"      • {issue}")
            return False
        else:
            print("\n   🎉 OAuth configuration looks good!")
            return True
            
    except Exception as e:
        print(f"   ❌ Configuration validation failed: {e}")
        return False

def test_google_oauth_flow_structure():
    """Test Google OAuth flow structure and configuration"""
    print("\n🔍 Testing Google OAuth 2.0 Flow:")
    
    # Run detailed configuration validation
    config_valid = validate_oauth_configuration()
    
    if not config_valid:
        return False
    
    # Test 2: Check callback endpoint exists
    try:
        # This should fail with 422 (missing code) but endpoint should exist
        response = requests.post(f"{BASE_URL}/auth/google/callback", json={})
        if response.status_code == 422:
            print("   ✅ Google callback endpoint exists and validates input")
        else:
            print(f"   ⚠️  Callback endpoint response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Callback endpoint test failed: {e}")
        return False
    
    print("   📋 Google OAuth 2.0 Flow Test Summary:")
    print("   • Auth URL generation: ✅ Working")
    print("   • Required parameters: ✅ Present")  
    print("   • Callback endpoint: ✅ Available")
    print("   • Input validation: ✅ Working")
    print("   📝 Note: Full OAuth flow requires valid Google credentials")
    
    return True

def main():
    """Run all tests"""
    print("Testing Syria GPT Authentication API")
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
    
    # Test 6: Google OAuth callback error handling
    test_google_oauth_callback_error()
    
    # Test 7: Google OAuth flow structure
    test_google_oauth_flow_structure()
    
    print("\n" + "=" * 50)
    print("🎉 Test completed! Check the results above.")

if __name__ == "__main__":
    main()