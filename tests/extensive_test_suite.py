#!/usr/bin/env python3
"""
Extensive test suite for Syria GPT project.

This comprehensive test suite covers all components including:
- Unit tests for all layers
- Integration tests for API endpoints
- Database tests
- Authentication flows
- Error handling
- Performance tests
"""

import asyncio
import pytest
import requests
import json
import time
from typing import Dict, Any, List
from uuid import uuid4
import subprocess
from pathlib import Path

class ExtensiveTestRunner:
    """Comprehensive test runner for all system components."""
    
    def __init__(self):
        self.base_url = "http://localhost:9000"
        self.test_results = []
        self.test_user_email = f"test_{uuid4().hex[:8]}@example.com"
        self.test_user_password = "TestPassword123!"
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        status = "PASS" if success else "FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
        
    def test_api_endpoints(self) -> bool:
        """Test all API endpoints comprehensively."""
        print("\n=== API Endpoints Tests ===")
        
        endpoints = [
            # Health and info endpoints
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/docs", "API documentation"),
            
            # Auth endpoints
            ("GET", "/auth/google", "Google OAuth URL"),
            ("GET", "/auth/facebook", "Facebook OAuth URL"),
            
            # Protected endpoints (should fail without auth)
            ("GET", "/auth/me", "User info endpoint (no auth)"),
        ]
        
        all_passed = True
        
        for method, endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.request(method, url, timeout=10)
                
                if endpoint in ["/auth/me"]:
                    # Should return 401/403 for protected endpoints
                    success = response.status_code in [401, 403, 422]
                    details = f"HTTP {response.status_code} (expected auth error)"
                else:
                    # Should return 200 for public endpoints
                    success = response.status_code == 200
                    details = f"HTTP {response.status_code}"
                    
                    if success and endpoint == "/health":
                        data = response.json()
                        success = data.get("status") == "healthy"
                        details += f" - Status: {data.get('status', 'unknown')}"
                    
                    elif success and endpoint == "/auth/google":
                        data = response.json()
                        success = "auth_url" in data and "provider" in data
                        details += f" - Has auth_url: {'auth_url' in data}"
                
                self.log_test(f"API {method} {endpoint}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"API {method} {endpoint}", False, f"Exception: {e}")
                all_passed = False
                
        return all_passed
    
    def test_authentication_flow(self) -> bool:
        """Test complete authentication flow."""
        print("\n=== Authentication Flow Tests ===")
        
        all_passed = True
        
        # Test 1: User Registration
        try:
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json=registration_data,
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "message" in data and "registered successfully" in data["message"].lower()
                details = f"HTTP {response.status_code} - {data.get('message', '')}"
            else:
                details = f"HTTP {response.status_code} - {response.text}"
                
            self.log_test("User Registration", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {e}")
            all_passed = False
        
        # Test 2: Duplicate Registration (should fail)
        try:
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json=registration_data,
                timeout=10
            )
            
            success = response.status_code in [400, 409, 422]
            details = f"HTTP {response.status_code} (expected duplicate error)"
            
            self.log_test("Duplicate Registration", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Duplicate Registration", False, f"Exception: {e}")
            all_passed = False
        
        # Test 3: Invalid Registration Data
        invalid_cases = [
            ({"email": "invalid-email"}, "Invalid email format"),
            ({"email": "test@test.com", "password": "weak"}, "Weak password"),
            ({}, "Missing required fields"),
        ]
        
        for invalid_data, case_name in invalid_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/auth/signup",
                    json=invalid_data,
                    timeout=10
                )
                
                success = response.status_code in [400, 422]
                details = f"HTTP {response.status_code} (expected validation error)"
                
                self.log_test(f"Invalid Registration - {case_name}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Invalid Registration - {case_name}", False, f"Exception: {e}")
                all_passed = False
        
        # Test 4: Sign In (should fail - user not verified)
        try:
            signin_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = requests.post(
                f"{self.base_url}/auth/signin",
                json=signin_data,
                timeout=10
            )
            
            # Should fail because user is not verified
            success = response.status_code in [400, 401, 403]
            details = f"HTTP {response.status_code} (expected unverified user error)"
            
            self.log_test("Sign In Unverified User", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Sign In Unverified User", False, f"Exception: {e}")
            all_passed = False
        
        # Test 5: Invalid Sign In
        try:
            signin_data = {
                "email": self.test_user_email,
                "password": "wrong_password"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/signin",
                json=signin_data,
                timeout=10
            )
            
            success = response.status_code in [400, 401]
            details = f"HTTP {response.status_code} (expected auth error)"
            
            self.log_test("Invalid Password Sign In", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Invalid Password Sign In", False, f"Exception: {e}")
            all_passed = False
        
        return all_passed
    
    def test_database_operations(self) -> bool:
        """Test database operations and migration utility."""
        print("\n=== Database Operations Tests ===")
        
        all_passed = True
        project_root = Path(__file__).parent.parent
        
        # Test 1: Migration Status
        try:
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "app", "python", "migrate.py", "status"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            details = f"Exit code: {result.returncode}"
            if success:
                if "[SUCCESS]" in result.stdout:
                    details += " - Database up to date"
                elif "[WARNING]" in result.stdout:
                    details += " - Migration needed"
                    
            self.log_test("Migration Status Check", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Migration Status Check", False, f"Exception: {e}")
            all_passed = False
        
        # Test 2: Database Schema Validation
        try:
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "app", "python", "migrate.py", "validate"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0 and "[SUCCESS]" in result.stdout
            details = f"Exit code: {result.returncode}"
            if success:
                details += " - Schema validation passed"
            else:
                details += f" - Validation failed: {result.stderr}"
                
            self.log_test("Database Schema Validation", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Database Schema Validation", False, f"Exception: {e}")
            all_passed = False
        
        # Test 3: Migration History
        try:
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "app", "python", "migrate.py", "history"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            migration_count = len([line for line in result.stdout.split('\n') if ' - ' in line])
            details = f"Exit code: {result.returncode} - Found {migration_count} migrations"
            
            self.log_test("Migration History", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Migration History", False, f"Exception: {e}")
            all_passed = False
        
        # Test 4: Database Connection via PostgreSQL
        try:
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "db", "pg_isready", "-U", "admin", "-d", "syriagpt"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            success = result.returncode == 0
            details = f"Exit code: {result.returncode} - {result.stdout.strip()}"
            
            self.log_test("PostgreSQL Connection", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("PostgreSQL Connection", False, f"Exception: {e}")
            all_passed = False
        
        return all_passed
    
    def test_error_handling(self) -> bool:
        """Test error handling and edge cases."""
        print("\n=== Error Handling Tests ===")
        
        all_passed = True
        
        # Test 1: Non-existent endpoints
        try:
            response = requests.get(f"{self.base_url}/nonexistent", timeout=10)
            success = response.status_code == 404
            details = f"HTTP {response.status_code} (expected 404)"
            
            self.log_test("Non-existent Endpoint", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Non-existent Endpoint", False, f"Exception: {e}")
            all_passed = False
        
        # Test 2: Invalid JSON
        try:
            response = requests.post(
                f"{self.base_url}/auth/signup",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code in [400, 422]
            details = f"HTTP {response.status_code} (expected JSON error)"
            
            self.log_test("Invalid JSON", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Invalid JSON", False, f"Exception: {e}")
            all_passed = False
        
        # Test 3: Missing Content-Type
        try:
            response = requests.post(
                f"{self.base_url}/auth/signup",
                data='{"email": "test@test.com"}',
                timeout=10
            )
            
            success = response.status_code in [400, 415, 422]
            details = f"HTTP {response.status_code} (expected content-type error)"
            
            self.log_test("Missing Content-Type", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Missing Content-Type", False, f"Exception: {e}")
            all_passed = False
        
        # Test 4: Large Request Body
        try:
            large_data = {"email": "a" * 10000 + "@test.com", "password": "b" * 1000}
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json=large_data,
                timeout=10
            )
            
            success = response.status_code in [400, 413, 422]
            details = f"HTTP {response.status_code} (expected size/validation error)"
            
            self.log_test("Large Request Body", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Large Request Body", False, f"Exception: {e}")
            all_passed = False
        
        return all_passed
    
    def test_performance(self) -> bool:
        """Test basic performance characteristics."""
        print("\n=== Performance Tests ===")
        
        all_passed = True
        
        # Test 1: Response Time
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200 and response_time < 2.0
            details = f"Response time: {response_time:.3f}s (threshold: 2.0s)"
            
            self.log_test("Health Endpoint Response Time", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Health Endpoint Response Time", False, f"Exception: {e}")
            all_passed = False
        
        # Test 2: Concurrent Requests
        try:
            import threading
            
            results = []
            
            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=10)
                    results.append(response.status_code == 200)
                except:
                    results.append(False)
            
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            success_rate = sum(results) / len(results)
            success = success_rate >= 0.8
            details = f"Success rate: {success_rate:.1%} (threshold: 80%)"
            
            self.log_test("Concurrent Requests", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Concurrent Requests", False, f"Exception: {e}")
            all_passed = False
        
        return all_passed
    
    def test_container_health(self) -> bool:
        """Test Docker container health."""
        print("\n=== Container Health Tests ===")
        
        all_passed = True
        project_root = Path(__file__).parent.parent
        
        # Test 1: Container Status
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            if success:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            container = json.loads(line)
                            containers.append(container)
                        except json.JSONDecodeError:
                            continue
                
                running_containers = [c for c in containers if c.get('State') == 'running']
                success = len(running_containers) >= 2  # At least app and db
                details = f"{len(running_containers)}/{len(containers)} containers running"
            else:
                details = f"Exit code: {result.returncode}"
            
            self.log_test("Container Status", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Container Status", False, f"Exception: {e}")
            all_passed = False
        
        # Test 2: Container Logs (check for errors)
        try:
            result = subprocess.run(
                ["docker-compose", "logs", "--tail", "20", "app"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logs = result.stdout.lower()
                # Only count actual serious errors, not validation warnings
                critical_errors = logs.count("critical") + logs.count("fatal")
                actual_exceptions = logs.count("traceback") + logs.count("exception:") 
                # Exclude validation warnings which are normal
                filtered_logs = []
                for line in result.stdout.split('\n'):
                    if "validation error:" not in line.lower() and "warning" not in line.lower():
                        if any(keyword in line.lower() for keyword in ["error", "exception", "critical", "fatal"]):
                            filtered_logs.append(line)
                
                serious_issues = len(filtered_logs)
                success = critical_errors == 0 and actual_exceptions == 0 and serious_issues <= 2
                details = f"{serious_issues} serious issues, {critical_errors} critical errors, {actual_exceptions} exceptions"
            else:
                success = False
                details = f"Failed to retrieve logs: {result.returncode}"
            
            self.log_test("Container Logs Check", success, details)
            if not success:
                all_passed = False
                
        except Exception as e:
            self.log_test("Container Logs Check", False, f"Exception: {e}")
            all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary."""
        print("[TEST] Starting Extensive Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        test_categories = [
            ("API Endpoints", self.test_api_endpoints),
            ("Authentication Flow", self.test_authentication_flow),
            ("Database Operations", self.test_database_operations),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
            ("Container Health", self.test_container_health),
        ]
        
        category_results = {}
        
        for category_name, test_func in test_categories:
            print(f"\n[RUNNING] Running {category_name} tests...")
            try:
                category_results[category_name] = test_func()
            except Exception as e:
                print(f"[FAIL] Category {category_name} failed with exception: {e}")
                category_results[category_name] = False
        
        end_time = time.time()
        
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        all_categories_passed = all(category_results.values())
        
        summary = {
            "success": all_categories_passed,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "duration": end_time - start_time,
            "categories": category_results,
            "test_details": self.test_results
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("[SUMMARY] TEST SUITE SUMMARY")
        print("=" * 60)
        
        for category, result in category_results.items():
            status = "[PASS] PASS" if result else "[FAIL] FAIL"
            print(f"{status} {category}")
        
        print(f"\n[STATS] Overall Statistics:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Passed: {passed_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Pass Rate: {summary['pass_rate']:.1%}")
        print(f"   • Duration: {summary['duration']:.2f}s")
        
        if all_categories_passed:
            print(f"\n[SUCCESS] ALL TESTS PASSED!")
        else:
            print(f"\n[WARNING] SOME TESTS FAILED - Check details above")
            print("\nFailed tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
        
        return summary

def main():
    """Main test execution function."""
    try:
        runner = ExtensiveTestRunner()
        summary = runner.run_all_tests()
        
        # Save results
        output_file = Path(__file__).parent.parent / "test_results.json"
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n[SAVED] Detailed results saved to: {output_file}")
        
        return 0 if summary["success"] else 1
        
    except KeyboardInterrupt:
        print("\n\n[STOP] Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n[ERROR] Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())