#!/usr/bin/env python3
"""
Database migration script for Render deployment.
Runs the initial database schema setup automatically.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def run_migration():
    """Run database migrations from SQL file."""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    print("🔄 Starting database migration...")
    print(f"📡 Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(database_url, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Read SQL migration file
        sql_file = os.path.join(os.path.dirname(__file__), 'data', 'mock_signups.sql')
        
        if not os.path.exists(sql_file):
            print(f"❌ ERROR: Migration file not found: {sql_file}")
            sys.exit(1)
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        print("📄 Migration file loaded")
        
        # Split SQL into individual statements (handle multi-line statements)
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            # Skip comments
            if line.strip().startswith('--') or not line.strip():
                continue
            
            current_statement.append(line)
            
            # If line ends with semicolon, it's the end of a statement
            if line.strip().endswith(';'):
                stmt = '\n'.join(current_statement)
                if stmt.strip():
                    statements.append(stmt)
                current_statement = []
        
        # Execute each statement
        print(f"🔧 Executing {len(statements)} SQL statements...")
        
        with engine.connect() as conn:
            for i, statement in enumerate(statements, 1):
                try:
                    # Skip SELECT statements (verification queries)
                    if statement.strip().upper().startswith('SELECT'):
                        print(f"  ⏭️  Skipping verification query {i}")
                        continue
                    
                    conn.execute(text(statement))
                    conn.commit()
                    
                    # Identify what kind of statement this is
                    stmt_type = statement.strip().split()[0].upper()
                    if stmt_type == 'CREATE' and 'TABLE' in statement.upper():
                        table_name = extract_table_name(statement)
                        print(f"  ✓ Created table: {table_name}")
                    elif stmt_type == 'INSERT':
                        print(f"  ✓ Inserted data")
                    elif stmt_type == 'CREATE' and 'INDEX' in statement.upper():
                        index_name = extract_index_name(statement)
                        print(f"  ✓ Created index: {index_name}")
                    else:
                        print(f"  ✓ Executed statement {i}")
                        
                except SQLAlchemyError as e:
                    error_msg = str(e)
                    
                    # Check if error is because table/index already exists
                    if 'already exists' in error_msg.lower():
                        print(f"  ⚠️  Skipping (already exists)")
                    # Check if trying to insert duplicate data
                    elif 'duplicate key' in error_msg.lower() or 'unique constraint' in error_msg.lower():
                        print(f"  ⚠️  Skipping (data already exists)")
                    else:
                        print(f"  ❌ Error executing statement {i}: {error_msg}")
                        raise
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = 'user_signups'
            """))
            table_exists = result.fetchone()[0] > 0
            
            if table_exists:
                # Get row count
                result = conn.execute(text("SELECT COUNT(*) FROM user_signups"))
                row_count = result.fetchone()[0]
                print(f"✅ Table 'user_signups' exists with {row_count} rows")
            else:
                print("❌ ERROR: Table 'user_signups' was not created")
                sys.exit(1)
        
        print("\n✅ Migration completed successfully!")
        
    except SQLAlchemyError as e:
        print(f"\n❌ Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


def extract_table_name(statement: str) -> str:
    """Extract table name from CREATE TABLE statement."""
    try:
        parts = statement.upper().split('TABLE')
        if len(parts) > 1:
            table_part = parts[1].strip().split()[0]
            # Remove IF NOT EXISTS
            if table_part == 'IF':
                return parts[1].strip().split()[3].replace('(', '')
            return table_part.replace('(', '')
    except:
        pass
    return "unknown"


def extract_index_name(statement: str) -> str:
    """Extract index name from CREATE INDEX statement."""
    try:
        parts = statement.upper().split('INDEX')
        if len(parts) > 1:
            index_part = parts[1].strip().split()[0]
            # Remove IF NOT EXISTS
            if index_part == 'IF':
                return parts[1].strip().split()[3]
            return index_part
    except:
        pass
    return "unknown"


if __name__ == "__main__":
    run_migration()

