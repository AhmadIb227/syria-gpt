#!/usr/bin/env python3
"""Development scripts for Syria GPT."""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent


def run_command(command: str, description: str = None):
    """Run a shell command."""
    if description:
        print(f"🔄 {description}...")
    
    result = subprocess.run(
        command,
        shell=True,
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        print(result.stderr)
        sys.exit(1)
    
    if description:
        print(f"✅ {description} completed")
    
    if result.stdout:
        print(result.stdout)


def format_code():
    """Format code with black."""
    run_command("python -m black .", "Formatting code")


def lint_code():
    """Lint code with flake8."""
    run_command("python -m flake8 --max-line-length=88 --extend-ignore=E203,W503", "Linting code")


def type_check():
    """Type check with mypy."""
    run_command("python -m mypy . --ignore-missing-imports", "Type checking")


def run_tests():
    """Run tests with pytest."""
    run_command("python -m pytest tests/ -v --cov=.", "Running tests")


def check_all():
    """Run all checks."""
    format_code()
    lint_code()
    type_check()
    run_tests()


def start_dev():
    """Start development server."""
    run_command("python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000", "Starting development server")


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("""
Available commands:
    format    - Format code with black
    lint      - Lint code with flake8  
    typecheck - Type check with mypy
    test      - Run tests with pytest
    check     - Run all checks
    dev       - Start development server
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        "format": format_code,
        "lint": lint_code,
        "typecheck": type_check,
        "test": run_tests,
        "check": check_all,
        "dev": start_dev,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()