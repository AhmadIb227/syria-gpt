"""
Migration helper functions for common database operations.

These functions provide convenient methods for performing common database
operations during migrations, such as adding indexes, constraints, and
data transformations.
"""

from typing import List, Dict, Any, Optional
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.engine import Connection


def add_index_if_not_exists(table_name: str, column_names: List[str], 
                           index_name: Optional[str] = None, unique: bool = False):
    """
    Add an index if it doesn't already exist.
    
    Args:
        table_name: Name of the table
        column_names: List of column names for the index
        index_name: Custom index name (optional)
        unique: Whether the index should be unique
    """
    if not index_name:
        suffix = "_unique_idx" if unique else "_idx"
        index_name = f"{table_name}_{'_'.join(column_names)}{suffix}"
    
    # Check if index exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    
    if index_name not in existing_indexes:
        op.create_index(index_name, table_name, column_names, unique=unique)
        print(f"Created index: {index_name}")
    else:
        print(f"Index already exists: {index_name}")


def drop_index_if_exists(index_name: str, table_name: Optional[str] = None):
    """
    Drop an index if it exists.
    
    Args:
        index_name: Name of the index to drop
        table_name: Name of the table (optional, for some databases)
    """
    connection = op.get_bind()
    
    try:
        if table_name:
            inspector = sa.inspect(connection)
            existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
            
            if index_name in existing_indexes:
                op.drop_index(index_name, table_name)
                print(f"Dropped index: {index_name}")
            else:
                print(f"Index does not exist: {index_name}")
        else:
            # Try to drop without table name (works for some databases)
            op.drop_index(index_name)
            print(f"Dropped index: {index_name}")
            
    except Exception as e:
        print(f"Could not drop index {index_name}: {e}")


def add_column_if_not_exists(table_name: str, column_name: str, column_type,
                            default=None, nullable: bool = True, 
                            server_default=None):
    """
    Add a column if it doesn't already exist.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to add
        column_type: SQLAlchemy column type
        default: Python default value
        nullable: Whether column can be null
        server_default: Server-side default value
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    
    if column_name not in columns:
        column_kwargs = {
            'nullable': nullable
        }
        if default is not None:
            column_kwargs['default'] = default
        if server_default is not None:
            column_kwargs['server_default'] = server_default
            
        op.add_column(table_name, sa.Column(column_name, column_type, **column_kwargs))
        print(f"Added column: {table_name}.{column_name}")
    else:
        print(f"Column already exists: {table_name}.{column_name}")


def drop_column_if_exists(table_name: str, column_name: str):
    """
    Drop a column if it exists.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to drop
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    
    if column_name in columns:
        op.drop_column(table_name, column_name)
        print(f"Dropped column: {table_name}.{column_name}")
    else:
        print(f"Column does not exist: {table_name}.{column_name}")


def rename_table_if_exists(old_name: str, new_name: str):
    """
    Rename a table if it exists.
    
    Args:
        old_name: Current table name
        new_name: New table name
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    table_names = inspector.get_table_names()
    
    if old_name in table_names:
        if new_name not in table_names:
            op.rename_table(old_name, new_name)
            print(f"Renamed table: {old_name} -> {new_name}")
        else:
            print(f"Target table name already exists: {new_name}")
    else:
        print(f"Source table does not exist: {old_name}")


def add_foreign_key_if_not_exists(constraint_name: str, source_table: str,
                                 referent_table: str, local_cols: List[str],
                                 remote_cols: List[str], 
                                 ondelete: Optional[str] = None,
                                 onupdate: Optional[str] = None):
    """
    Add a foreign key constraint if it doesn't exist.
    
    Args:
        constraint_name: Name of the constraint
        source_table: Source table name
        referent_table: Referenced table name
        local_cols: Local column names
        remote_cols: Referenced column names
        ondelete: ON DELETE action
        onupdate: ON UPDATE action
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_fks = inspector.get_foreign_keys(source_table)
    existing_names = [fk['name'] for fk in existing_fks]
    
    if constraint_name not in existing_names:
        op.create_foreign_key(
            constraint_name, source_table, referent_table,
            local_cols, remote_cols, ondelete=ondelete, onupdate=onupdate
        )
        print(f"Created foreign key: {constraint_name}")
    else:
        print(f"Foreign key already exists: {constraint_name}")


def drop_foreign_key_if_exists(constraint_name: str, table_name: str):
    """
    Drop a foreign key constraint if it exists.
    
    Args:
        constraint_name: Name of the constraint
        table_name: Name of the table
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_fks = inspector.get_foreign_keys(table_name)
    existing_names = [fk['name'] for fk in existing_fks]
    
    if constraint_name in existing_names:
        op.drop_constraint(constraint_name, table_name, type_='foreignkey')
        print(f"Dropped foreign key: {constraint_name}")
    else:
        print(f"Foreign key does not exist: {constraint_name}")


def bulk_insert_data(table_name: str, data: List[Dict[str, Any]]):
    """
    Bulk insert data into a table.
    
    Args:
        table_name: Name of the table
        data: List of dictionaries containing row data
    """
    if not data:
        print(f"No data to insert into {table_name}")
        return
    
    connection = op.get_bind()
    
    # Create a table object for the insert
    metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload_with=connection)
    
    # Perform bulk insert
    connection.execute(table.insert(), data)
    print(f"Inserted {len(data)} rows into {table_name}")


def execute_sql_file(file_path: str):
    """
    Execute SQL commands from a file.
    
    Args:
        file_path: Path to SQL file
    """
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()
            
        connection = op.get_bind()
        
        # Split SQL commands (basic splitting by semicolon)
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for command in commands:
            connection.execute(text(command))
            
        print(f"Executed SQL file: {file_path}")
        
    except Exception as e:
        print(f"Failed to execute SQL file {file_path}: {e}")
        raise


def create_enum_type(enum_name: str, values: List[str], schema: Optional[str] = None):
    """
    Create an ENUM type (PostgreSQL specific).
    
    Args:
        enum_name: Name of the enum type
        values: List of enum values
        schema: Schema name (optional)
    """
    connection = op.get_bind()
    
    # Check if we're using PostgreSQL
    if connection.dialect.name == 'postgresql':
        try:
            # Create ENUM type
            enum_type = sa.Enum(*values, name=enum_name, schema=schema)
            enum_type.create(connection, checkfirst=True)
            print(f"Created ENUM type: {enum_name}")
        except Exception as e:
            print(f"Failed to create ENUM type {enum_name}: {e}")
    else:
        print(f"ENUM types not supported for {connection.dialect.name}")


def drop_enum_type(enum_name: str, schema: Optional[str] = None):
    """
    Drop an ENUM type (PostgreSQL specific).
    
    Args:
        enum_name: Name of the enum type
        schema: Schema name (optional)
    """
    connection = op.get_bind()
    
    if connection.dialect.name == 'postgresql':
        try:
            enum_type = sa.Enum(name=enum_name, schema=schema)
            enum_type.drop(connection, checkfirst=True)
            print(f"Dropped ENUM type: {enum_name}")
        except Exception as e:
            print(f"Failed to drop ENUM type {enum_name}: {e}")
    else:
        print(f"ENUM types not supported for {connection.dialect.name}")


def update_sequence_value(sequence_name: str, new_value: int, schema: Optional[str] = None):
    """
    Update a sequence's current value (PostgreSQL specific).
    
    Args:
        sequence_name: Name of the sequence
        new_value: New value for the sequence
        schema: Schema name (optional)
    """
    connection = op.get_bind()
    
    if connection.dialect.name == 'postgresql':
        schema_prefix = f"{schema}." if schema else ""
        sql = f"SELECT setval('{schema_prefix}{sequence_name}', {new_value})"
        connection.execute(text(sql))
        print(f"Updated sequence {sequence_name} to {new_value}")
    else:
        print(f"Sequences not supported for {connection.dialect.name}")


def migrate_data(source_table: str, target_table: str, 
                column_mapping: Dict[str, str], where_clause: str = ""):
    """
    Migrate data from one table to another with column mapping.
    
    Args:
        source_table: Source table name
        target_table: Target table name
        column_mapping: Dict mapping source columns to target columns
        where_clause: Optional WHERE clause for source data
    """
    connection = op.get_bind()
    
    # Build the SELECT part
    select_cols = []
    insert_cols = []
    
    for source_col, target_col in column_mapping.items():
        select_cols.append(source_col)
        insert_cols.append(target_col)
    
    select_part = ", ".join(select_cols)
    insert_part = ", ".join(insert_cols)
    
    # Build the migration query
    where_part = f" WHERE {where_clause}" if where_clause else ""
    sql = f"""
    INSERT INTO {target_table} ({insert_part})
    SELECT {select_part}
    FROM {source_table}{where_part}
    """
    
    result = connection.execute(text(sql))
    rows_affected = result.rowcount if hasattr(result, 'rowcount') else 0
    print(f"Migrated {rows_affected} rows from {source_table} to {target_table}")


def backup_table_data(table_name: str, backup_table_name: Optional[str] = None):
    """
    Create a backup of table data.
    
    Args:
        table_name: Name of the table to backup
        backup_table_name: Name for backup table (defaults to {table_name}_backup)
    """
    if not backup_table_name:
        backup_table_name = f"{table_name}_backup"
    
    connection = op.get_bind()
    
    # Create backup table with same structure
    sql = f"""
    CREATE TABLE {backup_table_name} AS 
    SELECT * FROM {table_name}
    """
    
    connection.execute(text(sql))
    print(f"Created backup table: {backup_table_name}")


def restore_table_data(backup_table_name: str, target_table_name: str, 
                      truncate_target: bool = False):
    """
    Restore data from backup table.
    
    Args:
        backup_table_name: Name of backup table
        target_table_name: Name of target table
        truncate_target: Whether to truncate target table first
    """
    connection = op.get_bind()
    
    if truncate_target:
        connection.execute(text(f"TRUNCATE TABLE {target_table_name}"))
        print(f"Truncated table: {target_table_name}")
    
    sql = f"""
    INSERT INTO {target_table_name}
    SELECT * FROM {backup_table_name}
    """
    
    result = connection.execute(text(sql))
    rows_affected = result.rowcount if hasattr(result, 'rowcount') else 0
    print(f"Restored {rows_affected} rows to {target_table_name}")


# Convenience functions for common patterns
def add_timestamp_columns(table_name: str):
    """Add created_at and updated_at timestamp columns."""
    add_column_if_not_exists(
        table_name, 'created_at', sa.DateTime(),
        server_default=sa.func.now(), nullable=False
    )
    add_column_if_not_exists(
        table_name, 'updated_at', sa.DateTime(),
        server_default=sa.func.now(), nullable=False
    )


def add_uuid_primary_key(table_name: str, column_name: str = 'id'):
    """Add a UUID primary key column."""
    add_column_if_not_exists(
        table_name, column_name, sa.UUID(),
        server_default=sa.text('gen_random_uuid()'), nullable=False
    )


def add_soft_delete_column(table_name: str, column_name: str = 'deleted_at'):
    """Add a soft delete timestamp column."""
    add_column_if_not_exists(
        table_name, column_name, sa.DateTime(), nullable=True
    )


def add_version_column(table_name: str, column_name: str = 'version'):
    """Add a version column for optimistic locking."""
    add_column_if_not_exists(
        table_name, column_name, sa.Integer(),
        server_default='1', nullable=False
    )