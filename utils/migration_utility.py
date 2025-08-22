"""
Database Migration Utility

This utility provides a simplified interface for common database migration operations
using Alembic. It wraps Alembic commands and provides additional helper functions
for database management.

Author: Syria GPT
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from config.settings import settings
    from config.database import engine, SessionLocal
    from config.model import Base
except ImportError as e:
    print(f"Failed to import project modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

logger = logging.getLogger(__name__)


class MigrationUtility:
    """Database migration utility class."""
    
    def __init__(self, alembic_cfg_path: str = "alembic.ini"):
        """Initialize the migration utility."""
        self.project_root = Path(__file__).parent.parent
        self.alembic_cfg_path = self.project_root / alembic_cfg_path
        
        if not self.alembic_cfg_path.exists():
            raise FileNotFoundError(f"Alembic config file not found: {self.alembic_cfg_path}")
        
        self.alembic_cfg = Config(str(self.alembic_cfg_path))
        
        # Override database URL from environment if provided
        if hasattr(settings, 'DATABASE_URL'):
            self.alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    def get_current_revision(self) -> Optional[str]:
        """Get the current database revision."""
        try:
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
    
    def get_head_revision(self) -> Optional[str]:
        """Get the latest revision from migration files."""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            return script.get_current_head()
        except Exception as e:
            logger.error(f"Failed to get head revision: {e}")
            return None
    
    def create_migration(
        self, 
        message: str, 
        autogenerate: bool = True,
        sql: bool = False,
        head: str = "head",
        splice: bool = False,
        branch_label: Optional[str] = None,
        version_path: Optional[str] = None
    ) -> bool:
        """
        Create a new migration.
        
        Args:
            message: Migration description
            autogenerate: Auto-generate migration from model changes
            sql: Generate SQL scripts instead of Python
            head: Revision to base new migration on
            splice: Allow creation of migration on non-head revision
            branch_label: Label for new branch
            version_path: Path for version files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Creating migration: {message}")
            
            command.revision(
                self.alembic_cfg,
                message=message,
                autogenerate=autogenerate,
                sql=sql,
                head=head,
                splice=splice,
                branch_label=branch_label,
                version_path=version_path
            )
            
            print(f"[SUCCESS] Migration '{message}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            print(f"[ERROR] Failed to create migration: {e}")
            return False
    
    def upgrade(self, revision: str = "head", sql: bool = False, tag: Optional[str] = None) -> bool:
        """
        Upgrade database to a revision.
        
        Args:
            revision: Target revision (default: head)
            sql: Generate SQL only, don't execute
            tag: Tag to apply to upgraded revision
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current = self.get_current_revision()
            print(f"Upgrading from revision {current} to {revision}")
            
            command.upgrade(
                self.alembic_cfg,
                revision,
                sql=sql,
                tag=tag
            )
            
            new_revision = self.get_current_revision()
            print(f"[SUCCESS] Database upgraded to revision {new_revision}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upgrade database: {e}")
            print(f"[ERROR] Failed to upgrade database: {e}")
            return False
    
    def downgrade(self, revision: str, sql: bool = False, tag: Optional[str] = None) -> bool:
        """
        Downgrade database to a revision.
        
        Args:
            revision: Target revision
            sql: Generate SQL only, don't execute
            tag: Tag to apply to downgraded revision
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current = self.get_current_revision()
            print(f"Downgrading from revision {current} to {revision}")
            
            command.downgrade(
                self.alembic_cfg,
                revision,
                sql=sql,
                tag=tag
            )
            
            new_revision = self.get_current_revision()
            print(f"[SUCCESS] Database downgraded to revision {new_revision}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to downgrade database: {e}")
            print(f"[ERROR] Failed to downgrade database: {e}")
            return False
    
    def show_history(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Show migration history.
        
        Args:
            verbose: Show detailed information
            
        Returns:
            List of migration information
        """
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            revisions = []
            
            for revision in script.walk_revisions():
                rev_info = {
                    'revision': revision.revision,
                    'down_revision': revision.down_revision,
                    'branch_labels': revision.branch_labels,
                    'message': revision.doc,
                    'create_date': getattr(revision.module, 'create_date', 'Unknown')
                }
                revisions.append(rev_info)
                
                if verbose:
                    print(f"Revision: {revision.revision}")
                    print(f"  Down revision: {revision.down_revision}")
                    print(f"  Branch labels: {revision.branch_labels}")
                    print(f"  Message: {revision.doc}")
                    print(f"  Create date: {getattr(revision.module, 'create_date', 'Unknown')}")
                    print("-" * 50)
                else:
                    print(f"{revision.revision} - {revision.doc}")
            
            return revisions
            
        except Exception as e:
            logger.error(f"Failed to show history: {e}")
            print(f"[ERROR] Failed to show history: {e}")
            return []
    
    def show_current(self) -> Optional[str]:
        """Show current database revision."""
        current = self.get_current_revision()
        if current:
            print(f"Current revision: {current}")
        else:
            print("No current revision (database not initialized)")
        return current
    
    def show_heads(self) -> List[str]:
        """Show head revisions."""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            heads = script.get_heads()
            
            print("Head revisions:")
            for head in heads:
                print(f"  {head}")
                
            return heads
            
        except Exception as e:
            logger.error(f"Failed to show heads: {e}")
            print(f"[ERROR] Failed to show heads: {e}")
            return []
    
    def init_database(self) -> bool:
        """Initialize database with current schema."""
        try:
            print("Initializing database...")
            Base.metadata.create_all(bind=engine)
            print("[SUCCESS] Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            print(f"[ERROR] Failed to initialize database: {e}")
            return False
    
    def drop_database(self, confirm: bool = False) -> bool:
        """
        Drop all database tables.
        
        Args:
            confirm: Must be True to actually drop tables
            
        Returns:
            True if successful, False otherwise
        """
        if not confirm:
            print("[ERROR] Must pass confirm=True to drop database")
            return False
            
        try:
            print("[WARNING]  Dropping all database tables...")
            Base.metadata.drop_all(bind=engine)
            print("[SUCCESS] Database tables dropped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop database: {e}")
            print(f"[ERROR] Failed to drop database: {e}")
            return False
    
    def reset_database(self, confirm: bool = False) -> bool:
        """
        Reset database (drop and recreate).
        
        Args:
            confirm: Must be True to actually reset database
            
        Returns:
            True if successful, False otherwise
        """
        if not confirm:
            print("[ERROR] Must pass confirm=True to reset database")
            return False
            
        success = self.drop_database(confirm=True)
        if success:
            success = self.init_database()
            
        return success
    
    def validate_database_schema(self) -> bool:
        """Validate current database schema against models."""
        try:
            print("Validating database schema...")
            
            # This is a simplified validation - in production you might want
            # to compare actual table structure with model definitions
            with engine.connect() as conn:
                # Try to query each table defined in models
                for table in Base.metadata.tables.values():
                    try:
                        result = conn.execute(text(f"SELECT 1 FROM {table.name} LIMIT 1"))
                        result.close()
                    except Exception as e:
                        print(f"[ERROR] Table {table.name} validation failed: {e}")
                        return False
                        
            print("[SUCCESS] Database schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            print(f"[ERROR] Schema validation failed: {e}")
            return False
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a database backup (SQLite only for this implementation).
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_{timestamp}.db"
            
            # This is a simplified backup for SQLite
            # For PostgreSQL, you'd use pg_dump
            if "sqlite" in settings.DATABASE_URL.lower():
                import shutil
                db_path = settings.DATABASE_URL.replace("sqlite:///", "")
                shutil.copy2(db_path, backup_path)
                print(f"[SUCCESS] Database backed up to {backup_path}")
                return True
            else:
                print("[ERROR] Backup only implemented for SQLite databases")
                return False
                
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            print(f"[ERROR] Failed to backup database: {e}")
            return False
    
    def check_migrations_status(self) -> Dict[str, Any]:
        """Check the status of migrations."""
        try:
            current = self.get_current_revision()
            head = self.get_head_revision()
            
            status = {
                'current_revision': current,
                'head_revision': head,
                'is_up_to_date': current == head,
                'needs_upgrade': current != head and current is not None,
                'needs_initialization': current is None
            }
            
            if status['is_up_to_date']:
                print("[SUCCESS] Database is up to date")
            elif status['needs_initialization']:
                print("[WARNING]  Database needs initialization")
            elif status['needs_upgrade']:
                print(f"[WARNING]  Database needs upgrade from {current} to {head}")
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to check migration status: {e}")
            print(f"[ERROR] Failed to check migration status: {e}")
            return {'error': str(e)}


def main():
    """CLI interface for migration utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Utility")
    parser.add_argument("command", choices=[
        "create", "upgrade", "downgrade", "history", "current", "heads",
        "init", "drop", "reset", "validate", "backup", "status"
    ], help="Migration command")
    
    parser.add_argument("-m", "--message", help="Migration message")
    parser.add_argument("-r", "--revision", default="head", help="Target revision")
    parser.add_argument("--sql", action="store_true", help="Generate SQL only")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive operations")
    parser.add_argument("--backup-path", help="Backup file path")
    
    args = parser.parse_args()
    
    try:
        migration_util = MigrationUtility()
        
        if args.command == "create":
            if not args.message:
                print("[ERROR] Migration message is required for create command")
                sys.exit(1)
            success = migration_util.create_migration(args.message, sql=args.sql)
            
        elif args.command == "upgrade":
            success = migration_util.upgrade(args.revision, sql=args.sql)
            
        elif args.command == "downgrade":
            if args.revision == "head":
                print("[ERROR] Specific revision is required for downgrade")
                sys.exit(1)
            success = migration_util.downgrade(args.revision, sql=args.sql)
            
        elif args.command == "history":
            migration_util.show_history(verbose=args.verbose)
            success = True
            
        elif args.command == "current":
            migration_util.show_current()
            success = True
            
        elif args.command == "heads":
            migration_util.show_heads()
            success = True
            
        elif args.command == "init":
            success = migration_util.init_database()
            
        elif args.command == "drop":
            success = migration_util.drop_database(confirm=args.confirm)
            
        elif args.command == "reset":
            success = migration_util.reset_database(confirm=args.confirm)
            
        elif args.command == "validate":
            success = migration_util.validate_database_schema()
            
        elif args.command == "backup":
            success = migration_util.backup_database(args.backup_path)
            
        elif args.command == "status":
            migration_util.check_migrations_status()
            success = True
            
        else:
            print(f"[ERROR] Unknown command: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Migration utility failed: {e}")
        print(f"[ERROR] Migration utility failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()