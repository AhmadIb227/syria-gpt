#!/usr/bin/env python3
"""
Comprehensive health check script for Syria GPT application.

This script validates all components of the application are working correctly.
"""

import sys
import requests
import json
from pathlib import Path
import subprocess
import time

def print_status(message, status="INFO"):
    """Print formatted status message."""
    symbols = {"INFO": "i", "SUCCESS": "[OK]", "ERROR": "[X]", "WARNING": "!"}
    symbol = symbols.get(status, "•")
    print(f"[{symbol}] {message}")

def check_api_health():
    """Check API health endpoints."""
    try:
        # Health check
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"API Health: {data['status']} - {data['service']} v{data['version']}", "SUCCESS")
        else:
            print_status(f"API Health check failed: HTTP {response.status_code}", "ERROR")
            return False
            
        # Root endpoint
        response = requests.get("http://localhost:9000/", timeout=5)
        if response.status_code == 200:
            print_status("Root endpoint accessible", "SUCCESS")
        else:
            print_status(f"Root endpoint failed: HTTP {response.status_code}", "WARNING")
            
        # Documentation
        response = requests.get("http://localhost:9000/docs", timeout=5)
        if response.status_code == 200:
            print_status("API documentation accessible", "SUCCESS")
        else:
            print_status("API documentation not accessible", "WARNING")
            
        return True
        
    except requests.RequestException as e:
        print_status(f"API connection failed: {e}", "ERROR")
        return False

def check_auth_endpoints():
    """Check authentication endpoints."""
    try:
        # Google OAuth
        response = requests.get("http://localhost:9000/auth/google", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "auth_url" in data and "provider" in data:
                print_status("Google OAuth endpoint working", "SUCCESS")
            else:
                print_status("Google OAuth endpoint response invalid", "WARNING")
        else:
            print_status(f"Google OAuth failed: HTTP {response.status_code}", "ERROR")
            
        # Registration test (expect validation error for incomplete data)
        response = requests.post("http://localhost:9000/auth/signup", 
                               json={"email": "invalid"}, timeout=5)
        if response.status_code in [400, 422]:  # Validation error expected
            print_status("Registration endpoint responding to validation", "SUCCESS")
        else:
            print_status(f"Registration endpoint unexpected response: HTTP {response.status_code}", "WARNING")
            
        return True
        
    except requests.RequestException as e:
        print_status(f"Auth endpoints check failed: {e}", "ERROR")
        return False

def check_containers():
    """Check Docker container status."""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"], 
            capture_output=True, text=True, cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container = json.loads(line)
                        containers.append(container)
                    except json.JSONDecodeError:
                        continue
                        
            for container in containers:
                name = container.get('Service', 'Unknown')
                state = container.get('State', 'Unknown')
                status = container.get('Status', 'Unknown')
                
                if state == 'running':
                    print_status(f"Container {name}: {state} ({status})", "SUCCESS")
                else:
                    print_status(f"Container {name}: {state} ({status})", "ERROR")
                    
            return len([c for c in containers if c.get('State') == 'running']) >= 2
        else:
            print_status("Failed to check container status", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Container check failed: {e}", "ERROR")
        return False

def check_database():
    """Check database connectivity."""
    try:
        # Test database connection through migration utility
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "app", "python", "migrate.py", "status"],
            capture_output=True, text=True, cwd=Path(__file__).parent, timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout
            if "[SUCCESS]" in output:
                print_status("Database connection and migrations: UP TO DATE", "SUCCESS")
                return True
            elif "[WARNING]" in output:
                print_status("Database connection: OK, migrations may be needed", "WARNING")
                return True
        
        print_status("Database connection or migrations failed", "ERROR")
        return False
        
    except subprocess.TimeoutExpired:
        print_status("Database check timed out", "ERROR")
        return False
    except Exception as e:
        print_status(f"Database check failed: {e}", "ERROR")
        return False

def check_logs():
    """Check for recent errors in logs."""
    try:
        result = subprocess.run(
            ["docker-compose", "logs", "--tail", "20", "app"],
            capture_output=True, text=True, cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            logs = result.stdout.lower()
            error_count = logs.count("error")
            exception_count = logs.count("exception") + logs.count("traceback")
            
            if error_count == 0 and exception_count == 0:
                print_status("No recent errors in application logs", "SUCCESS")
                return True
            elif error_count <= 2 and exception_count == 0:
                print_status(f"Minor errors in logs ({error_count} errors)", "WARNING")
                return True
            else:
                print_status(f"Multiple errors in logs ({error_count} errors, {exception_count} exceptions)", "ERROR")
                return False
        else:
            print_status("Could not retrieve logs", "WARNING")
            return True
            
    except Exception as e:
        print_status(f"Log check failed: {e}", "WARNING")
        return True

def main():
    """Run comprehensive health checks."""
    print("[HEALTH CHECK] Syria GPT Health Check")
    print("=" * 50)
    
    checks = [
        ("Container Status", check_containers),
        ("Database Connectivity", check_database),
        ("API Health", check_api_health),
        ("Authentication Endpoints", check_auth_endpoints),
        ("Application Logs", check_logs),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n[CHECK] {check_name}")
        print("-" * 30)
        
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(f"Check failed with exception: {e}", "ERROR")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("[SUMMARY] HEALTH CHECK SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "[OK]" if result else "[X]"
        print(f"[{symbol}] {check_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print_status("[SUCCESS] All systems operational!", "SUCCESS")
        print("\n[INFO] Available endpoints:")
        print("   • API: http://localhost:9000")
        print("   • Documentation: http://localhost:9000/docs")
        print("   • PgAdmin: http://localhost:5050")
        print("   • Health: http://localhost:9000/health")
        return 0
    else:
        print_status("[WARNING] Some issues detected. Check details above.", "WARNING")
        return 1

if __name__ == "__main__":
    sys.exit(main())