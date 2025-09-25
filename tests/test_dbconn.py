import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from db.db_config import db_config

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
            SELECT id, uid, name 
            FROM users ORDER BY id ASC
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

    users = list_users()

    print(f"\n✅ Found {len(users)} user(s) in the database")
    for user in users:
        print(f"  - {user['uid']} ({user['name']})")