#!/usr/bin/env python3
"""
Standalone OAuth URL test without database dependency
"""
import sys
from urllib.parse import urlencode, urlparse, parse_qs

# Mock settings
class MockSettings:
    GOOGLE_CLIENT_ID = "134729060788-b5v8fhl32jdsf0db30g4vvoasle7t84o.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"
    GOOGLE_REDIRECT_URI = "http://localhost:9000/auth/google/callback"

def generate_oauth_url():
    """Generate Google OAuth URL exactly like our endpoint does"""
    settings = MockSettings()
    
    # Use the correct Google OAuth 2.0 authorization endpoint
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    # Define parameters exactly as in our code
    params = {
        "client_id": str(settings.GOOGLE_CLIENT_ID).strip(),
        "redirect_uri": str(settings.GOOGLE_REDIRECT_URI).strip(),
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": "oauth_security_state"
    }
    
    # Properly encode the parameters
    google_auth_url = f"{base_url}?{urlencode(params)}"
    return google_auth_url

def validate_oauth_url(url):
    """Validate the OAuth URL contains all required parameters"""
    print("OAuth URL Validation Report")
    print("=" * 50)
    print(f"URL: {url}")
    print()
    
    # Parse URL
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    print("URL Components:")
    print(f"  Base: {parsed.scheme}://{parsed.netloc}{parsed.path}")
    print(f"  Parameters: {len(params)} found")
    print()
    
    # Check required parameters
    required_params = {
        "client_id": "Google Client ID",
        "redirect_uri": "Callback URL", 
        "scope": "Permission scopes",
        "response_type": "OAuth flow type",
        "access_type": "Token type",
        "prompt": "Consent behavior",
        "state": "Security token"
    }
    
    issues = []
    
    print("Parameter Validation:")
    for param, description in required_params.items():
        if param in params and params[param][0]:
            value = params[param][0]
            if param == "client_id":
                print(f"  [OK] {param}: {value[:30]}...")
            elif param == "redirect_uri":
                print(f"  [OK] {param}: {value}")
            else:
                print(f"  [OK] {param}: {value}")
        else:
            issues.append(f"Missing {param} ({description})")
            print(f"  [FAIL] {param}: MISSING")
    
    # Specific validations
    print()
    print("Specific Validations:")
    
    # Check endpoint
    if parsed.path == "/o/oauth2/v2/auth":
        print("  [OK] Using correct OAuth 2.0 v2 endpoint")
    else:
        issues.append(f"Wrong endpoint: {parsed.path}")
        print(f"  [FAIL] Wrong endpoint: {parsed.path}")
    
    # Check response_type
    response_type = params.get("response_type", [""])[0]
    if response_type == "code":
        print("  [OK] response_type=code (correct for authorization code flow)")
    else:
        issues.append(f"Wrong response_type: {response_type}")
        print(f"  [FAIL] response_type should be 'code', got '{response_type}'")
    
    # Check client_id format
    client_id = params.get("client_id", [""])[0]
    if client_id.endswith(".apps.googleusercontent.com"):
        print("  [OK] Client ID format is correct")
    else:
        issues.append("Client ID format incorrect")
        print("  [FAIL] Client ID should end with .apps.googleusercontent.com")
    
    print()
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("ALL VALIDATIONS PASSED!")
        print("OAuth URL is correctly formatted.")
        return True

def main():
    """Main test function"""
    print("Google OAuth 2.0 URL Generator Test")
    print("=" * 50)
    
    try:
        # Generate URL
        oauth_url = generate_oauth_url()
        
        # Validate URL
        is_valid = validate_oauth_url(oauth_url)
        
        print()
        if is_valid:
            print("SUCCESS: OAuth URL is properly configured!")
            print()
            print("Copy this URL to test in browser:")
            print(oauth_url)
        else:
            print("FAILURE: OAuth URL has configuration issues!")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()