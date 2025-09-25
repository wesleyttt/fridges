import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import db_config
from datetime import datetime

def get_db_connection():
    """Create and return a database connection using secure config."""
    try:
        # Validate configuration first
        db_config.validate()
        
        # Get connection parameters
        conn_params = db_config.get_connection_params()
        
        # Create connection
        conn = psycopg2.connect(**conn_params)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None


def get_user_by_id(user_id):
    """Get user information by ID."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, name, email, created_at, updated_at 
            FROM users WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        return dict(user) if user else None
        
    except psycopg2.Error as e:
        print(f"❌ Error getting user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def list_tables():
    """List all tables in the database."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Query to get all table names
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print("📋 Available tables:")
            for table in tables:
                print(f"  - {table[0]}")
            return [table[0] for table in tables]
        else:
            print("📭 No tables found in the database")
            return []
        
    except psycopg2.Error as e:
        print(f"❌ Error listing tables: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def list_users():
    """List all users (without passwords)."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, name, email, created_at, updated_at 
            FROM users ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        return [dict(user) for user in users]
        
    except psycopg2.Error as e:
        print(f"❌ Error listing users: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🗄️  Database Table Listing")
    print("=" * 30)
    
    # List all tables in the database
    tables = list_tables()
    
    if tables:
        print(f"\n✅ Found {len(tables)} table(s) in the database")
    else:
        print("\n❌ No tables found or connection failed")