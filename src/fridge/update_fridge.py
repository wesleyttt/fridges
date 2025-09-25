"""
Given a scan of a receipt, update the fridge with the items and quantities.
"""

import psycopg2
import os
import sys

# Add the src directory to the Python path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.dbconnect import get_db_connection
from cv.get_items import scan_receipt
from fridge.fridge_utils import get_fridge_by_id


def update_fridge(uid, items):
    """
    Add items from receipt to fridge database.
    items is a dict of {"item": {"quantity": , "unit_price": 1.99}}
    """
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()

        curr_fridge = get_fridge_by_id(uid)
        
        # Insert items into the items table
        for item in items:
            if item not in curr_fridge:
                curr_fridge[item] = items[item]
            else:
                curr_fridge[item]["quantity"] += items[item]["quantity"]
                curr_fridge[item]["unit_price"] = (curr_fridge[item]["unit_price"] * curr_fridge[item]["quantity"] + items[item]["unit_price"] * items[item]["quantity"]) / (curr_fridge[item]["quantity"] + items[item]["quantity"])

            # Overwrite the fridge column for the given uid with the updated fridge dict
            cursor.execute("""
                UPDATE fridges
                SET fridge = %s
                WHERE uid = %s
            """, (
                psycopg2.extras.Json(curr_fridge),
                str(uid)
            ))
        
        conn.commit()
        return True, f"Successfully added {len(items)} items to fridge {uid}"
        
    except psycopg2.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()


    