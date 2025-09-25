import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Add the current directory to the Python path for relative imports
sys.path.append(os.path.dirname(__file__))
from db_config import db_config  

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

