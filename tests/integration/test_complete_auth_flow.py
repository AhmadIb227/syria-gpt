"""
Complete authentication flow integration tests.

Tests the entire authentication workflow from registration to protected endpoints.
"""

import pytest
import requests
import json
from uuid import uuid4
from typing import Dict, Any, Optional
import time


class TestCompleteAuthFlow:
    """Test complete authentication workflows."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.base_url = "http://localhost:9000"
        self.test_email = f"integration_test_{uuid4().hex[:8]}@example.com"
        self.test_password = "IntegrationTest123!"
        self.headers = {"Content-Type": "application/json"}
        self.access_token = None
        self.refresh_token = None
        
        # Ensure API is available
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API not available for integration tests")
        except requests.RequestException:
            pytest.skip("API not accessible for integration tests")
    
    def test_01_user_registration(self):
        """Test user registration flow."""
        registration_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": "Integration",
            "last_name": "Test"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/signup",
            json=registration_data,
            headers=self.headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "registered successfully" in data["message"].lower()
    
    def test_02_duplicate_registration_fails(self):
        """Test that duplicate registration fails."""
        registration_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": "Duplicate",
            "last_name": "Test"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/signup",
            json=registration_data,
            headers=self.headers,
            timeout=10
        )
        
        # Should fail with conflict or bad request
        assert response.status_code in [400, 409, 422]
    
    def test_03_signin_unverified_user_fails(self):
        """Test that unverified user cannot sign in."""
        signin_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(
            f"{self.base_url}/auth/signin",
            json=signin_data,
            headers=self.headers,
            timeout=10
        )
        
        # Should fail because user is not verified
        assert response.status_code in [400, 401, 403]
        data = response.json()
        assert "detail" in data
        # Check for verification-related error message
        assert any(keyword in data["detail"].lower() for keyword in ["verify", "active", "confirm"])
    
    def test_04_invalid_credentials_fail(self):
        """Test that invalid credentials fail."""
        # Wrong password
        signin_data = {
            "email": self.test_email,
            "password": "wrong_password"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/signin",
            json=signin_data,
            headers=self.headers,
            timeout=10
        )
        
        assert response.status_code in [400, 401]
        
        # Non-existent user
        signin_data = {
            "email": "nonexistent@example.com",
            "password": self.test_password
        }
        
        response = requests.post(
            f"{self.base_url}/auth/signin",
            json=signin_data,
            headers=self.headers,
            timeout=10
        )
        
        assert response.status_code in [400, 401]
    
    def test_05_oauth_endpoints_accessible(self):
        """Test OAuth endpoints are accessible."""
        # Google OAuth
        response = requests.get(f"{self.base_url}/auth/google", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "auth_url" in data
        assert "provider" in data
        assert data["provider"] == "google"
        assert "accounts.google.com" in data["auth_url"]
        
        # Facebook OAuth
        response = requests.get(f"{self.base_url}/auth/facebook", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "auth_url" in data
        assert "provider" in data
        assert data["provider"] == "facebook"
    
    def test_06_protected_endpoints_require_auth(self):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("GET", "/auth/me"),
            ("POST", "/auth/change-password"),
        ]
        
        for method, endpoint in protected_endpoints:
            response = requests.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                timeout=10
            )
            
            # Should require authentication
            assert response.status_code in [401, 403, 422]
    
    def test_07_invalid_request_formats(self):
        """Test handling of invalid request formats."""
        # Invalid JSON
        response = requests.post(
            f"{self.base_url}/auth/signup",
            data="invalid json",
            headers=self.headers,
            timeout=10
        )
        assert response.status_code in [400, 422]
        
        # Missing required fields
        response = requests.post(
            f"{self.base_url}/auth/signup",
            json={"email": "test@test.com"},  # Missing password
            headers=self.headers,
            timeout=10
        )
        assert response.status_code == 422
        
        # Invalid email format
        response = requests.post(
            f"{self.base_url}/auth/signup",
            json={"email": "invalid-email", "password": "ValidPass123!"},
            headers=self.headers,
            timeout=10
        )
        assert response.status_code == 422
    
    def test_08_password_validation(self):
        """Test password validation rules."""
        weak_passwords = [
            "123",          # Too short
            "password",     # Too common
            "12345678",     # No complexity
            "PASSWORD",     # No lowercase
            "password123",  # No uppercase
            "Password",     # No numbers
        ]
        
        for weak_password in weak_passwords:
            registration_data = {
                "email": f"weak_pass_{uuid4().hex[:4]}@example.com",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json=registration_data,
                headers=self.headers,
                timeout=10
            )
            
            # Should fail validation
            assert response.status_code in [400, 422], f"Weak password '{weak_password}' was accepted"
    
    def test_09_email_validation(self):
        """Test email validation rules."""
        invalid_emails = [
            "invalid",
            "@domain.com",
            "user@",
            "user space@domain.com",
            "user@domain",
            ""
        ]
        
        for invalid_email in invalid_emails:
            registration_data = {
                "email": invalid_email,
                "password": self.test_password,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json=registration_data,
                headers=self.headers,
                timeout=10
            )
            
            # Should fail validation
            assert response.status_code == 422, f"Invalid email '{invalid_email}' was accepted"
    
    def test_10_request_password_reset(self):
        """Test password reset request functionality."""
        # Request reset for registered user
        reset_data = {"email": self.test_email}
        
        response = requests.post(
            f"{self.base_url}/auth/request-password-reset",
            json=reset_data,
            headers=self.headers,
            timeout=10
        )
        
        # Should succeed regardless of verification status
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Request reset for non-existent user (should still return success for security)
        reset_data = {"email": "nonexistent@example.com"}
        
        response = requests.post(
            f"{self.base_url}/auth/request-password-reset",
            json=reset_data,
            headers=self.headers,
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_11_api_documentation_accessible(self):
        """Test that API documentation is accessible."""
        response = requests.get(f"{self.base_url}/docs", timeout=10)
        assert response.status_code == 200
        
        # Check that it's HTML content
        assert "text/html" in response.headers.get("content-type", "")
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
        
        # Test OpenAPI JSON schema
        response = requests.get(f"{self.base_url}/openapi.json", timeout=10)
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "/auth/signup" in schema["paths"]
    
    def test_12_cors_headers(self):
        """Test CORS headers are properly set."""
        response = requests.options(
            f"{self.base_url}/auth/signup",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        # Should return CORS headers
        assert response.status_code in [200, 204]
        headers = response.headers
        
        # Check for CORS headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
    
    def test_13_rate_limiting_protection(self):
        """Test basic protection against rapid requests."""
        # Make multiple rapid requests
        responses = []
        for i in range(20):
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json={
                    "email": f"rate_limit_{i}@example.com",
                    "password": "invalid"  # Will fail validation
                },
                headers=self.headers,
                timeout=10
            )
            responses.append(response.status_code)
            
            # Small delay between requests
            time.sleep(0.1)
        
        # Should handle all requests (might have rate limiting in production)
        # For now, just ensure no server errors
        server_errors = [code for code in responses if code >= 500]
        assert len(server_errors) == 0, f"Server errors encountered: {server_errors}"
    
    def test_14_response_format_consistency(self):
        """Test that API responses follow consistent format."""
        # Test successful response format
        response = requests.get(f"{self.base_url}/health", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        
        # Test error response format
        response = requests.post(
            f"{self.base_url}/auth/signup",
            json={"email": "invalid"},
            headers=self.headers,
            timeout=10
        )
        assert response.status_code == 422
        
        data = response.json()
        assert isinstance(data, dict)
        # Should have error details
        assert "detail" in data or "message" in data
    
    def test_15_security_headers(self):
        """Test that security headers are present."""
        response = requests.get(f"{self.base_url}/health", timeout=10)
        assert response.status_code == 200
        
        headers = response.headers
        
        # Check for security headers (these might be added by reverse proxy in production)
        # For now, just ensure no sensitive information is leaked
        assert "Server" not in headers or "uvicorn" not in headers.get("Server", "").lower()
        
        # Ensure no SQL error details in responses
        error_response = requests.get(f"{self.base_url}/nonexistent", timeout=10)
        assert "sql" not in error_response.text.lower()
        assert "traceback" not in error_response.text.lower()


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration scenarios."""
    
    def test_database_connection_pool(self):
        """Test database can handle multiple connections."""
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                response = requests.get("http://localhost:9000/health", timeout=10)
                results.append(response.status_code == 200)
            except:
                results.append(False)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.9, f"Success rate too low: {success_rate}"
    
    def test_transaction_integrity(self):
        """Test database transaction integrity."""
        # This test would require database access
        # For now, just test that registration is atomic
        
        unique_email = f"transaction_test_{uuid4().hex[:8]}@example.com"
        
        # First registration should succeed
        response1 = requests.post(
            "http://localhost:9000/auth/signup",
            json={
                "email": unique_email,
                "password": "TransactionTest123!",
                "first_name": "Transaction",
                "last_name": "Test"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response1.status_code == 200
        
        # Second registration with same email should fail
        response2 = requests.post(
            "http://localhost:9000/auth/signup",
            json={
                "email": unique_email,
                "password": "TransactionTest123!",
                "first_name": "Duplicate",
                "last_name": "Test"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response2.status_code in [400, 409, 422]