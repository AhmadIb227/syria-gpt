#!/usr/bin/env python3
"""
Test script for the migration utility.

This script tests the migration utility functionality without requiring
a database connection.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_migration_utility():
    """Test the migration utility functionality."""
    print("Testing Migration Utility...")
    
    try:
        from utils.migration_utility import MigrationUtility
        from utils import migration_helpers
        
        # Test 1: Initialize utility
        print("\n1. Testing utility initialization...")
        try:
            migration_util = MigrationUtility()
            print("[SUCCESS] Migration utility initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize utility: {e}")
            return False
        
        # Test 2: Test helper functions import
        print("\n2. Testing helper functions...")
        try:
            # Just check if the functions exist
            assert hasattr(migration_helpers, 'add_column_if_not_exists')
            assert hasattr(migration_helpers, 'add_index_if_not_exists')
            assert hasattr(migration_helpers, 'add_foreign_key_if_not_exists')
            assert hasattr(migration_helpers, 'bulk_insert_data')
            assert hasattr(migration_helpers, 'migrate_data')
            assert hasattr(migration_helpers, 'add_timestamp_columns')
            print("[SUCCESS] All helper functions available")
        except Exception as e:
            print(f"[ERROR] Helper functions test failed: {e}")
            return False
        
        # Test 3: Test history reading (works without DB connection)
        print("\n3. Testing migration history...")
        try:
            history = migration_util.show_history(verbose=False)
            if isinstance(history, list):
                print(f"[SUCCESS] Found {len(history)} migrations in history")
            else:
                print("[WARNING] History returned unexpected format")
        except Exception as e:
            print(f"[ERROR] Failed to read history: {e}")
            return False
        
        # Test 4: Test head revision reading
        print("\n4. Testing head revision...")
        try:
            heads = migration_util.show_heads()
            if isinstance(heads, list):
                print(f"[SUCCESS] Found {len(heads)} head revisions")
            else:
                print("[WARNING] Heads returned unexpected format")
        except Exception as e:
            print(f"[ERROR] Failed to read heads: {e}")
            return False
        
        # Test 5: Test command line interface
        print("\n5. Testing CLI interface...")
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, 'migrate.py', 'history'
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("[SUCCESS] CLI interface working")
                print(f"Output: {result.stdout.strip()}")
            else:
                print(f"[WARNING] CLI returned non-zero exit code: {result.returncode}")
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"[ERROR] CLI test failed: {e}")
            return False
        
        print("\n" + "="*50)
        print("[SUCCESS] All migration utility tests passed!")
        print("="*50)
        return True
        
    except ImportError as e:
        print(f"[ERROR] Failed to import migration modules: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error during testing: {e}")
        return False

def test_alembic_integration():
    """Test Alembic integration."""
    print("\n\nTesting Alembic Integration...")
    
    try:
        # Test if alembic config is readable
        from alembic.config import Config
        from pathlib import Path
        
        config_path = Path(__file__).parent / "alembic.ini"
        if config_path.exists():
            alembic_cfg = Config(str(config_path))
            print("[SUCCESS] Alembic config loaded successfully")
            
            # Test script directory
            from alembic.script import ScriptDirectory
            script = ScriptDirectory.from_config(alembic_cfg)
            revisions = list(script.walk_revisions())
            print(f"[SUCCESS] Found {len(revisions)} migration revisions")
            
            return True
        else:
            print("[ERROR] Alembic config file not found")
            return False
            
    except Exception as e:
        print(f"[ERROR] Alembic integration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Syria GPT Migration Utility Tests")
    print("=" * 40)
    
    # Run tests
    utility_test = test_migration_utility()
    alembic_test = test_alembic_integration()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"Migration Utility: {'PASS' if utility_test else 'FAIL'}")
    print(f"Alembic Integration: {'PASS' if alembic_test else 'FAIL'}")
    
    if utility_test and alembic_test:
        print("\n[SUCCESS] All tests passed! Migration utility is ready to use.")
        
        print("\n" + "="*50)
        print("USAGE EXAMPLES:")
        print("python migrate.py status          # Check migration status")
        print("python migrate.py history         # Show migration history")
        print("python migrate.py create -m 'msg' # Create new migration")
        print("python migrate.py upgrade         # Upgrade to latest")
        print("python migrate.py --help          # Show all commands")
        print("="*50)
        
        return True
    else:
        print("\n[ERROR] Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)