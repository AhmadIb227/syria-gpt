#!/usr/bin/env python3
"""
Database Migration Script for Syria GPT
======================================

This script handles database migrations using Alembic.
It provides commands for initializing, creating, and applying migrations.

Usage:
    python migrate.py init                    # Initialize migration repository
    python migrate.py create "description"   # Create new migration
    python migrate.py upgrade               # Apply all pending migrations
    python migrate.py downgrade             # Downgrade one migration
    python migrate.py current               # Show current migration
    python migrate.py history               # Show migration history
    python migrate.py check                 # Check for issues and validate
"""

import sys
import os
import subprocess
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from config.model import Base

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MigrationManager:
    """Handles database migrations and validation"""
    
    def __init__(self):
        self.database_url = settings.DATABASE_URL
        self.engine = None
        
    def _get_engine(self):
        """Create database engine if not exists"""
        if not self.engine:
            try:
                self.engine = create_engine(self.database_url, echo=False)
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                sys.exit(1)
        return self.engine
    
    def _run_alembic_command(self, command):
        """Run alembic command and handle errors"""
        try:
            result = subprocess.run(
                f"alembic {command}",
                shell=True,
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            if result.returncode != 0:
                logger.error(f"Alembic command failed: {result.stderr}")
                return False
            
            if result.stdout:
                print(result.stdout)
            return True
            
        except Exception as e:
            logger.error(f"Error running alembic command: {e}")
            return False
    
    def check_database_connection(self):
        """Test database connectivity"""
        logger.info("Testing database connection...")
        try:
            engine = self._get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False
    
    def validate_models(self):
        """Validate SQLAlchemy models"""
        logger.info("Validating SQLAlchemy models...")
        try:
            # Check if all models have proper table names
            for table_name, table in Base.metadata.tables.items():
                if not table_name:
                    logger.error(f"✗ Table missing name: {table}")
                    return False
                
                # Check if table has primary key
                if not table.primary_key:
                    logger.error(f"✗ Table '{table_name}' missing primary key")
                    return False
            
            logger.info("✓ All models validated successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Model validation failed: {e}")
            return False
    
    def check_migration_conflicts(self):
        """Check for potential migration conflicts"""
        logger.info("Checking for migration conflicts...")
        versions_dir = project_root / "alembic" / "versions"
        
        if not versions_dir.exists():
            logger.info("✓ No migrations exist yet")
            return True
        
        migration_files = list(versions_dir.glob("*.py"))
        if len(migration_files) == 0:
            logger.info("✓ No migration conflicts found")
            return True
        
        # Check for duplicate revision IDs (basic check)
        revisions = []
        for migration_file in migration_files:
            try:
                with open(migration_file, 'r') as f:
                    content = f.read()
                    # Extract revision ID
                    for line in content.split('\n'):
                        if line.strip().startswith('revision ='):
                            revision = line.split('=')[1].strip().strip('"\'')
                            if revision in revisions:
                                logger.error(f"✗ Duplicate revision ID found: {revision}")
                                return False
                            revisions.append(revision)
                            break
            except Exception as e:
                logger.warning(f"Could not parse migration file {migration_file}: {e}")
        
        logger.info("✓ No migration conflicts detected")
        return True
    
    def init(self):
        """Initialize migration repository"""
        logger.info("Initializing migration repository...")
        
        if (project_root / "alembic" / "versions").exists():
            logger.warning("Migration repository already exists")
            return True
        
        return self._run_alembic_command("init alembic")
    
    def create_migration(self, message):
        """Create new migration"""
        if not message:
            logger.error("Migration message is required")
            return False
        
        logger.info(f"Creating migration: {message}")
        return self._run_alembic_command(f'revision --autogenerate -m "{message}"')
    
    def upgrade(self, revision="head"):
        """Apply migrations"""
        logger.info(f"Upgrading to revision: {revision}")
        return self._run_alembic_command(f"upgrade {revision}")
    
    def downgrade(self, revision="-1"):
        """Downgrade migrations"""
        logger.info(f"Downgrading to revision: {revision}")
        return self._run_alembic_command(f"downgrade {revision}")
    
    def current(self):
        """Show current migration"""
        logger.info("Current migration:")
        return self._run_alembic_command("current")
    
    def history(self):
        """Show migration history"""
        logger.info("Migration history:")
        return self._run_alembic_command("history")
    
    def check(self):
        """Run comprehensive checks"""
        logger.info("Running comprehensive migration checks...")
        
        checks = [
            ("Database Connection", self.check_database_connection),
            ("Model Validation", self.validate_models),
            ("Migration Conflicts", self.check_migration_conflicts),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            logger.info(f"\n--- {check_name} ---")
            if not check_func():
                all_passed = False
        
        if all_passed:
            logger.info("\n✓ All checks passed! Database is ready for migrations.")
        else:
            logger.error("\n✗ Some checks failed. Please fix issues before proceeding.")
        
        return all_passed

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    manager = MigrationManager()
    command = sys.argv[1].lower()
    
    try:
        if command == "init":
            success = manager.init()
        elif command == "create":
            if len(sys.argv) < 3:
                logger.error("Migration message required")
                sys.exit(1)
            success = manager.create_migration(sys.argv[2])
        elif command == "upgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            success = manager.upgrade(revision)
        elif command == "downgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
            success = manager.downgrade(revision)
        elif command == "current":
            success = manager.current()
        elif command == "history":
            success = manager.history()
        elif command == "check":
            success = manager.check()
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()