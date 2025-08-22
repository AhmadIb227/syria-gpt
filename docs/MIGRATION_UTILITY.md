# Database Migration Utility

A comprehensive database migration utility for Syria GPT that simplifies common database operations using Alembic.

## Overview

The migration utility provides a user-friendly interface for managing database schema changes, data migrations, and database maintenance tasks. It wraps Alembic commands and provides additional helper functions for common database operations.

## Features

- ✅ Create and manage database migrations
- ✅ Upgrade/downgrade database schema
- ✅ View migration history and status
- ✅ Database initialization and reset
- ✅ Schema validation
- ✅ Database backup (SQLite)
- ✅ Helper functions for common migration tasks
- ✅ Command-line interface
- ✅ Python API

## Installation

The migration utility is part of the project and doesn't require separate installation. Make sure you have the required dependencies:

```bash
pip install alembic sqlalchemy
```

## Quick Start

### Command Line Usage

```bash
# Check current migration status
python utils/migration_utility.py status

# Create a new migration
python utils/migration_utility.py create -m "Add user preferences table"

# Upgrade to latest migration
python utils/migration_utility.py upgrade

# View migration history
python utils/migration_utility.py history --verbose

# Initialize database
python utils/migration_utility.py init

# Reset database (destructive!)
python utils/migration_utility.py reset --confirm
```

### Python API Usage

```python
from utils.migration_utility import MigrationUtility

# Initialize utility
migration_util = MigrationUtility()

# Check status
status = migration_util.check_migrations_status()
print(f"Current revision: {status['current_revision']}")

# Create migration
success = migration_util.create_migration("Add user settings")

# Upgrade database
success = migration_util.upgrade()

# Validate schema
is_valid = migration_util.validate_database_schema()
```

## Commands Reference

### create
Create a new database migration.

```bash
python utils/migration_utility.py create -m "Migration description"
```

Options:
- `-m, --message`: Migration description (required)
- `--sql`: Generate SQL scripts instead of Python

Example:
```bash
python utils/migration_utility.py create -m "Add email verification table"
```

### upgrade
Upgrade database to a specific revision or latest.

```bash
python utils/migration_utility.py upgrade [-r REVISION] [--sql]
```

Options:
- `-r, --revision`: Target revision (default: head)
- `--sql`: Generate SQL only, don't execute

Examples:
```bash
# Upgrade to latest
python utils/migration_utility.py upgrade

# Upgrade to specific revision
python utils/migration_utility.py upgrade -r abc123

# Generate upgrade SQL
python utils/migration_utility.py upgrade --sql
```

### downgrade
Downgrade database to a specific revision.

```bash
python utils/migration_utility.py downgrade -r REVISION [--sql]
```

Options:
- `-r, --revision`: Target revision (required)
- `--sql`: Generate SQL only, don't execute

Example:
```bash
python utils/migration_utility.py downgrade -r abc123
```

### history
Show migration history.

```bash
python utils/migration_utility.py history [--verbose]
```

Options:
- `--verbose`: Show detailed information

### current
Show current database revision.

```bash
python utils/migration_utility.py current
```

### heads
Show head revisions.

```bash
python utils/migration_utility.py heads
```

### status
Check migration status.

```bash
python utils/migration_utility.py status
```

### init
Initialize database with current schema.

```bash
python utils/migration_utility.py init
```

### drop
Drop all database tables.

```bash
python utils/migration_utility.py drop --confirm
```

**⚠️ Destructive operation! Requires --confirm flag.**

### reset
Reset database (drop and recreate).

```bash
python utils/migration_utility.py reset --confirm
```

**⚠️ Destructive operation! Requires --confirm flag.**

### validate
Validate current database schema.

```bash
python utils/migration_utility.py validate
```

### backup
Create database backup (SQLite only).

```bash
python utils/migration_utility.py backup [--backup-path PATH]
```

Options:
- `--backup-path`: Custom backup file path

## Migration Helper Functions

The utility includes helper functions for common migration tasks. Import them in your migration files:

```python
from utils.migration_helpers import *

def upgrade():
    # Add column if it doesn't exist
    add_column_if_not_exists('users', 'preferences', sa.JSON(), nullable=True)
    
    # Add index
    add_index_if_not_exists('users', ['email'], unique=True)
    
    # Add timestamp columns
    add_timestamp_columns('user_sessions')
    
    # Migrate data between tables
    migrate_data('old_users', 'users', {
        'user_id': 'id',
        'user_email': 'email',
        'user_name': 'name'
    })
```

### Available Helper Functions

#### Column Operations
- `add_column_if_not_exists(table, column, type, **kwargs)`: Add column if it doesn't exist
- `drop_column_if_exists(table, column)`: Drop column if it exists

#### Index Operations
- `add_index_if_not_exists(table, columns, name=None, unique=False)`: Add index if it doesn't exist
- `drop_index_if_exists(index_name, table=None)`: Drop index if it exists

#### Constraint Operations
- `add_foreign_key_if_not_exists(name, source_table, target_table, local_cols, remote_cols)`: Add FK constraint
- `drop_foreign_key_if_exists(name, table)`: Drop FK constraint if it exists

#### Data Operations
- `bulk_insert_data(table, data)`: Bulk insert data
- `migrate_data(source_table, target_table, column_mapping, where_clause="")`: Migrate data between tables
- `backup_table_data(table, backup_table=None)`: Create backup of table data
- `restore_table_data(backup_table, target_table, truncate=False)`: Restore data from backup

#### Table Operations
- `rename_table_if_exists(old_name, new_name)`: Rename table if it exists

#### PostgreSQL Specific
- `create_enum_type(enum_name, values, schema=None)`: Create ENUM type
- `drop_enum_type(enum_name, schema=None)`: Drop ENUM type
- `update_sequence_value(sequence_name, new_value, schema=None)`: Update sequence value

#### Convenience Functions
- `add_timestamp_columns(table)`: Add created_at and updated_at columns
- `add_uuid_primary_key(table, column='id')`: Add UUID primary key
- `add_soft_delete_column(table, column='deleted_at')`: Add soft delete column
- `add_version_column(table, column='version')`: Add version column for optimistic locking

#### Utility Functions
- `execute_sql_file(file_path)`: Execute SQL commands from file

## Migration Best Practices

### 1. Always Test Migrations
- Test migrations on a copy of production data
- Test both upgrade and downgrade paths
- Validate data integrity after migration

### 2. Use Helper Functions
- Use helper functions to avoid duplication
- Check existence before creating/dropping objects
- Handle edge cases gracefully

### 3. Data Migrations
- Keep data migrations separate from schema migrations when possible
- Use transactions for data consistency
- Consider performance impact of large data migrations

### 4. Naming Conventions
- Use descriptive migration messages
- Follow consistent naming for indexes and constraints
- Include date or sequence in migration file names

### 5. Backup Strategy
- Always backup before running migrations in production
- Test restore procedures
- Keep multiple backup copies

## Example Migration Files

### Schema Migration
```python
"""Add user preferences table

Revision ID: abc123
Revises: def456
Create Date: 2024-01-15 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from utils.migration_helpers import *

def upgrade():
    # Create table
    op.create_table('user_preferences',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Add foreign key
    add_foreign_key_if_not_exists(
        'fk_user_preferences_user_id',
        'user_preferences', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Add index
    add_index_if_not_exists('user_preferences', ['user_id'], unique=True)

def downgrade():
    op.drop_table('user_preferences')
```

### Data Migration
```python
"""Migrate user settings to preferences table

Revision ID: ghi789
Revises: abc123
Create Date: 2024-01-15 11:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from utils.migration_helpers import *

def upgrade():
    # Backup existing data
    backup_table_data('user_settings')
    
    # Migrate data
    connection = op.get_bind()
    
    # Complex data transformation
    result = connection.execute(sa.text("""
        SELECT user_id, 
               json_build_object(
                   'theme', theme,
                   'language', language,
                   'notifications', notification_enabled
               ) as preferences
        FROM user_settings
    """))
    
    # Insert transformed data
    for row in result:
        connection.execute(sa.text("""
            INSERT INTO user_preferences (user_id, preferences)
            VALUES (:user_id, :preferences)
        """), {
            'user_id': row.user_id,
            'preferences': row.preferences
        })

def downgrade():
    # Restore from backup if needed
    restore_table_data('user_settings_backup', 'user_settings', truncate_target=True)
```

## Troubleshooting

### Common Issues

#### Migration Fails with "Target database is not up to date"
```bash
# Check current status
python utils/migration_utility.py status

# Upgrade to latest
python utils/migration_utility.py upgrade
```

#### Cannot Create Migration - No Changes Detected
- Ensure models are properly imported in `config/model.py`
- Check that model changes are saved
- Try creating migration manually with specific changes

#### Database Connection Issues
- Verify database URL in settings
- Check database server is running
- Ensure proper permissions

#### Foreign Key Constraint Errors
- Check that referenced tables exist
- Verify column types match
- Use helper functions to check existence

### Recovery Procedures

#### Restore from Backup
```python
from utils.migration_utility import MigrationUtility

migration_util = MigrationUtility()

# Reset database
migration_util.reset_database(confirm=True)

# Restore from backup
# (implement restoration logic based on your backup strategy)
```

#### Mark Migration as Applied (Skip)
```bash
# Mark specific migration as applied without running it
alembic stamp abc123
```

#### Resolve Migration Conflicts
```bash
# View current state
python utils/migration_utility.py current
python utils/migration_utility.py heads

# If multiple heads exist, merge them
alembic merge -m "Merge migrations" head1 head2
```

## Advanced Usage

### Custom Migration Templates

You can create custom migration templates by modifying the Alembic configuration or using the `--template` option.

### Environment-Specific Migrations

Use different Alembic configurations for different environments:

```bash
# Development
python utils/migration_utility.py upgrade

# Production (with different config)
ALEMBIC_CONFIG=alembic.prod.ini python utils/migration_utility.py upgrade
```

### Integration with CI/CD

```yaml
# Example GitHub Actions workflow
name: Database Migration
on: [push]
jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run migrations
        run: python utils/migration_utility.py upgrade --sql
      - name: Validate schema
        run: python utils/migration_utility.py validate
```

## Security Considerations

- Never commit database credentials to version control
- Use environment variables for sensitive configuration
- Restrict database permissions for migration user
- Audit migration scripts before applying in production
- Keep migration logs for compliance

## Performance Considerations

- Test migrations with production-sized data
- Consider impact of long-running migrations
- Use maintenance windows for major schema changes
- Monitor database performance during migrations
- Consider online migration strategies for zero-downtime deployments

## Contributing

When adding new helper functions:

1. Add comprehensive docstrings
2. Include error handling
3. Test with different database engines
4. Update this documentation
5. Add unit tests

## Support

For issues with the migration utility:

1. Check the troubleshooting section
2. Review migration logs
3. Test with a database copy first
4. Create an issue with reproduction steps