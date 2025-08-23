#!/usr/bin/env python3
"""
Comprehensive Stability Test Suite
Tests all major API endpoints multiple times to ensure stability.
"""

import requests
import json
import random
import string
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading


class StabilityTester:
    def __init__(self):
        self.base_url = "http://localhost:9000"
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.lock = threading.Lock()
        
    def log_result(self, test_name, success, error_msg=None):
        with self.lock:
            if success:
                self.results['passed'] += 1
            else:
                self.results['failed'] += 1
                self.results['errors'].append(f"{test_name}: {error_msg}")
    
    def generate_unique_user(self):
        """Generate unique user data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        unique_phone = f"+963{random.randint(100000000, 999999999)}"
        
        return {
            "email": f"stability_{timestamp}_{random_id}@test.com",
            "password": "StabilityTest123!",
            "first_name": "Stability",
            "last_name": f"Test{random_id}",
            "phone_number": unique_phone
        }
    
    def test_health_endpoint(self, iteration):
        """Test health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            success = response.status_code == 200
            self.log_result(f"Health-{iteration}", success, 
                          None if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result(f"Health-{iteration}", False, str(e))
    
    def test_root_endpoint(self, iteration):
        """Test root endpoint."""
        try:
            response = requests.get(self.base_url, timeout=5)
            success = response.status_code == 200
            self.log_result(f"Root-{iteration}", success,
                          None if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result(f"Root-{iteration}", False, str(e))
    
    def test_user_registration(self, iteration):
        """Test user registration with unique data."""
        try:
            user_data = self.generate_unique_user()
            response = requests.post(f"{self.base_url}/auth/signup", 
                                   json=user_data, timeout=10)
            success = response.status_code == 200
            self.log_result(f"Registration-{iteration}", success,
                          None if success else f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result(f"Registration-{iteration}", False, str(e))
    
    def test_oauth_endpoints(self, iteration):
        """Test OAuth endpoints."""
        try:
            # Test Google OAuth
            response = requests.get(f"{self.base_url}/auth/google", timeout=5)
            success = response.status_code == 200
            self.log_result(f"GoogleOAuth-{iteration}", success,
                          None if success else f"Status: {response.status_code}")
            
            # Test Facebook OAuth  
            response = requests.get(f"{self.base_url}/auth/facebook", timeout=5)
            success = response.status_code == 200
            self.log_result(f"FacebookOAuth-{iteration}", success,
                          None if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result(f"OAuth-{iteration}", False, str(e))
    
    def test_invalid_signin(self, iteration):
        """Test signin with invalid credentials."""
        try:
            response = requests.post(f"{self.base_url}/auth/signin",
                                   json={"email": f"invalid{iteration}@test.com", 
                                        "password": "wrongpassword"}, timeout=5)
            success = response.status_code == 401
            self.log_result(f"InvalidSignin-{iteration}", success,
                          None if success else f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result(f"InvalidSignin-{iteration}", False, str(e))
    
    def run_iteration_tests(self, iteration):
        """Run all tests for one iteration."""
        print(f"  🔄 Running iteration {iteration}...")
        
        # Run tests in sequence for this iteration
        self.test_health_endpoint(iteration)
        self.test_root_endpoint(iteration)  
        self.test_user_registration(iteration)
        self.test_oauth_endpoints(iteration)
        self.test_invalid_signin(iteration)
        
        return True
    
    def run_stability_test(self, iterations=10, parallel=False):
        """Run comprehensive stability tests."""
        print(f"🚀 Starting Stability Test Suite")
        print(f"   • Iterations: {iterations}")
        print(f"   • Mode: {'Parallel' if parallel else 'Sequential'}")
        print(f"   • Target: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        if parallel:
            # Run iterations in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.run_iteration_tests, i+1) 
                          for i in range(iterations)]
                for future in futures:
                    future.result()
        else:
            # Run iterations sequentially  
            for i in range(iterations):
                self.run_iteration_tests(i+1)
                time.sleep(0.1)  # Small delay between iterations
        
        end_time = time.time()
        
        # Report results
        print("\n" + "=" * 60)
        print("📊 STABILITY TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Duration: {end_time - start_time:.2f} seconds")
        
        if self.results['errors']:
            print(f"\n🚨 ERRORS ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("🎉 STABILITY TEST PASSED! (≥95% success rate)")
            return True
        else:
            print("⚠️  STABILITY TEST CONCERNS (< 95% success rate)")
            return False


def main():
    """Run stability tests."""
    tester = StabilityTester()
    
    print("Testing PostgreSQL + Docker stability with Syria GPT API")
    print("Testing basic endpoint stability...")
    
    # Run sequential tests first
    success = tester.run_stability_test(iterations=5, parallel=False)
    
    if success:
        print("\n🔄 Running parallel stress test...")
        # Reset results for parallel test
        tester.results = {'passed': 0, 'failed': 0, 'errors': []}
        tester.run_stability_test(iterations=3, parallel=True)
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        exit(1)