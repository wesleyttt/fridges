"""
Fridge represented as 
{
    items: [{item: , quantity:}, ...]
}
"""

import psycopg2
import os
import sys

# Add the current directory to the Python path for relative imports
sys.path.append(os.path.dirname(__file__))
from db.dbconnect import get_db_connection

def get_fridge_by_id(uid):
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM fridges WHERE uid = %s", (uid))
        res = cursor.fetchone()
        
        if res:
            return dict(res)["fridge"]
        else:
            return None
            
    except psycopg2.Error as e:
        print(f"❌ Error querying fridge: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

print(get_fridge_by_id("1"))
