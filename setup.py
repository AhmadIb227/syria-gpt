#!/usr/bin/env python3
"""
Comprehensive setup script for Syria GPT project.

This script handles complete environment setup, dependency installation,
database initialization, and system validation.
"""

import os
import sys
import subprocess
import shutil
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SetupManager:
    """Manages the complete setup process for Syria GPT."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def log_status(self, message: str, level: str = "info"):
        """Log status with appropriate level."""
        if level == "error":
            logger.error(f"[ERROR] {message}")
            self.errors.append(message)
        elif level == "warning":
            logger.warning(f"[WARNING] {message}")
            self.warnings.append(message)
        else:
            logger.info(f"[INFO] {message}")
    
    def run_command(self, command: List[str], description: str, 
                   cwd: Optional[Path] = None, timeout: int = 300) -> bool:
        """Run a command and handle errors."""
        try:
            self.log_status(f"Running: {description}")
            self.log_status(f"Command: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                self.log_status(f"SUCCESS: {description}")
                if result.stdout.strip():
                    logger.debug(f"Output: {result.stdout.strip()}")
                return True
            else:
                self.log_status(f"FAILED: {description} (exit code: {result.returncode})", "error")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr}")
                if result.stdout:
                    logger.error(f"Standard output: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_status(f"TIMEOUT: {description} (exceeded {timeout}s)", "error")
            return False
        except Exception as e:
            self.log_status(f"EXCEPTION: {description} - {e}", "error")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        self.log_status("Checking system prerequisites...")
        
        prerequisites = [
            ("python", "Python 3.8+"),
            ("docker", "Docker"),
            ("docker-compose", "Docker Compose"),
            ("git", "Git")
        ]
        
        all_good = True
        for command, name in prerequisites:
            if shutil.which(command):
                self.log_status(f"{name}: Found")
            else:
                self.log_status(f"{name}: NOT FOUND", "error")
                all_good = False
        
        # Check Python version
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                self.log_status(f"Python version: {version.major}.{version.minor}.{version.micro}")
            else:
                self.log_status(f"Python version too old: {version.major}.{version.minor}.{version.micro}", "error")
                all_good = False
        except Exception as e:
            self.log_status(f"Failed to check Python version: {e}", "error")
            all_good = False
        
        return all_good
    
    def setup_environment(self) -> bool:
        """Setup Python environment and install dependencies."""
        self.log_status("Setting up Python environment...")
        
        # Check if we're in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.log_status("Virtual environment detected")
        else:
            self.log_status("No virtual environment detected - consider using one", "warning")
        
        # Upgrade pip
        if not self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                               "Upgrading pip"):
            return False
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            if not self.run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                                   "Installing Python dependencies"):
                return False
        else:
            self.log_status("Requirements file not found", "error")
            return False
        
        # Verify installation
        if not self.run_command([sys.executable, "-m", "pip", "check"], 
                               "Checking dependency compatibility"):
            self.log_status("Some dependency conflicts exist", "warning")
        
        return True
    
    def setup_environment_file(self) -> bool:
        """Setup environment configuration file."""
        self.log_status("Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            self.log_status("Environment file already exists")
            return True
        
        if env_example.exists():
            try:
                shutil.copy(env_example, env_file)
                self.log_status("Environment file created from example")
                return True
            except Exception as e:
                self.log_status(f"Failed to copy environment file: {e}", "error")
                return False
        else:
            # Create basic .env file
            basic_env = '''# Syria GPT Environment Configuration
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+psycopg2://admin:admin123@db:5432/syriagpt
SECRET_KEY=your-super-secret-key-minimum-32-characters-long-for-testing
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
EMAIL_VERIFICATION_EXPIRE_HOURS=24
PASSWORD_RESET_EXPIRE_HOURS=1
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@syriagpt.com
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:9000/auth/google/callback
FRONTEND_URL=http://localhost:3000
'''
            try:
                with open(env_file, 'w') as f:
                    f.write(basic_env)
                self.log_status("Basic environment file created")
                return True
            except Exception as e:
                self.log_status(f"Failed to create environment file: {e}", "error")
                return False
    
    def setup_docker(self) -> bool:
        """Setup Docker containers."""
        self.log_status("Setting up Docker containers...")
        
        # Stop any existing containers
        self.run_command(["docker-compose", "down"], "Stopping existing containers")
        
        # Build containers
        if not self.run_command(["docker-compose", "build"], "Building Docker containers", timeout=600):
            return False
        
        # Start containers
        if not self.run_command(["docker-compose", "up", "-d"], "Starting Docker containers"):
            return False
        
        # Wait for containers to be ready
        self.log_status("Waiting for containers to start...")
        time.sleep(10)
        
        # Check container status
        if not self.run_command(["docker-compose", "ps"], "Checking container status"):
            return False
        
        return True
    
    def setup_database(self) -> bool:
        """Setup and initialize database."""
        self.log_status("Setting up database...")
        
        # Wait for database to be ready
        max_attempts = 30
        for attempt in range(max_attempts):
            if self.run_command(
                ["docker-compose", "exec", "-T", "db", "pg_isready", "-U", "admin", "-d", "syriagpt"],
                f"Checking database readiness (attempt {attempt + 1}/{max_attempts})"
            ):
                break
            time.sleep(2)
        else:
            self.log_status("Database failed to become ready", "error")
            return False
        
        # Run migrations
        if not self.run_command(
            ["docker-compose", "exec", "-T", "app", "python", "migrate.py", "upgrade"],
            "Running database migrations"
        ):
            return False
        
        # Validate database schema
        if not self.run_command(
            ["docker-compose", "exec", "-T", "app", "python", "migrate.py", "validate"],
            "Validating database schema"
        ):
            return False
        
        return True
    
    def run_tests(self) -> bool:
        """Run test suite."""
        self.log_status("Running test suite...")
        
        # Run unit tests
        if not self.run_command([sys.executable, "-m", "pytest", "tests/unit/", "-v"], 
                               "Running unit tests"):
            self.log_status("Some unit tests failed", "warning")
        
        # Test migration utility
        if not self.run_command([sys.executable, "test_migration_utility.py"], 
                               "Testing migration utility"):
            self.log_status("Migration utility tests failed", "warning")
        
        return True
    
    def validate_setup(self) -> bool:
        """Validate the complete setup."""
        self.log_status("Validating setup...")
        
        # Run health check
        if not self.run_command([sys.executable, "health_check.py"], 
                               "Running health check"):
            self.log_status("Health check failed", "warning")
        
        # Test API endpoints
        try:
            import requests
            
            # Wait for API to be ready
            time.sleep(5)
            
            endpoints = [
                ("http://localhost:9000/health", "Health endpoint"),
                ("http://localhost:9000/", "Root endpoint"),
                ("http://localhost:9000/docs", "Documentation endpoint"),
                ("http://localhost:9000/auth/google", "Google OAuth endpoint")
            ]
            
            for url, name in endpoints:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        self.log_status(f"{name}: OK (HTTP {response.status_code})")
                    else:
                        self.log_status(f"{name}: Warning (HTTP {response.status_code})", "warning")
                except Exception as e:
                    self.log_status(f"{name}: Failed - {e}", "error")
                    
        except ImportError:
            self.log_status("Requests library not available for endpoint testing", "warning")
        
        return True
    
    def cleanup_on_failure(self):
        """Cleanup resources on setup failure."""
        self.log_status("Cleaning up due to setup failure...")
        self.run_command(["docker-compose", "down"], "Stopping containers")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate setup summary."""
        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "endpoints": {
                "api": "http://localhost:9000",
                "docs": "http://localhost:9000/docs",
                "health": "http://localhost:9000/health",
                "pgadmin": "http://localhost:5050"
            } if len(self.errors) == 0 else {}
        }
    
    def run_setup(self) -> bool:
        """Run the complete setup process."""
        self.log_status("Starting Syria GPT setup process...")
        self.log_status("=" * 60)
        
        steps = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Environment Setup", self.setup_environment),
            ("Environment File", self.setup_environment_file),
            ("Docker Setup", self.setup_docker),
            ("Database Setup", self.setup_database),
            ("Test Execution", self.run_tests),
            ("Setup Validation", self.validate_setup)
        ]
        
        for step_name, step_func in steps:
            self.log_status(f"\n🔄 STEP: {step_name}")
            self.log_status("-" * 40)
            
            try:
                if not step_func():
                    self.log_status(f"Step failed: {step_name}", "error")
                    if step_name in ["Docker Setup", "Database Setup"]:
                        self.cleanup_on_failure()
                    return False
                else:
                    self.log_status(f"Step completed: {step_name}")
            except Exception as e:
                self.log_status(f"Step exception: {step_name} - {e}", "error")
                return False
        
        # Generate and display summary
        summary = self.generate_summary()
        
        self.log_status("\n" + "=" * 60)
        self.log_status("SETUP SUMMARY")
        self.log_status("=" * 60)
        
        if summary["success"]:
            self.log_status("🎉 Setup completed successfully!")
            self.log_status("\n📡 Available endpoints:")
            for name, url in summary["endpoints"].items():
                self.log_status(f"   • {name.upper()}: {url}")
                
            self.log_status("\n🚀 Next steps:")
            self.log_status("   1. Visit http://localhost:9000/docs for API documentation")
            self.log_status("   2. Use http://localhost:5050 for PgAdmin database management")
            self.log_status("   3. Check logs with: docker-compose logs -f app")
            self.log_status("   4. Run health check: python health_check.py")
            
        else:
            self.log_status("❌ Setup failed with errors:")
            for error in summary["errors"]:
                self.log_status(f"   • {error}")
        
        if summary["warnings"]:
            self.log_status("\n⚠️ Warnings:")
            for warning in summary["warnings"]:
                self.log_status(f"   • {warning}")
        
        # Save summary to file
        try:
            with open(self.project_root / "setup_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            self.log_status("\n📋 Setup summary saved to: setup_summary.json")
        except Exception as e:
            self.log_status(f"Failed to save summary: {e}", "warning")
        
        return summary["success"]

def main():
    """Main setup function."""
    print("Syria GPT Setup Script")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Usage: python setup.py [options]

Options:
  --help    Show this help message
  
This script will:
  1. Check system prerequisites
  2. Install Python dependencies
  3. Setup environment configuration
  4. Build and start Docker containers
  5. Initialize database with migrations
  6. Run tests
  7. Validate the complete setup

Requirements:
  - Python 3.8+
  - Docker and Docker Compose
  - Git
        """)
        return 0
    
    setup_manager = SetupManager()
    
    try:
        success = setup_manager.run_setup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
        setup_manager.cleanup_on_failure()
        return 130
    except Exception as e:
        print(f"\n\n💥 Setup failed with unexpected error: {e}")
        setup_manager.cleanup_on_failure()
        return 1

if __name__ == "__main__":
    sys.exit(main())