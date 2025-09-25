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
    pass