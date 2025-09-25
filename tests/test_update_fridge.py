"""
Test script for updating fridge with receipt items
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.fridge.update_fridge import update_fridge
from src.cv.get_items import scan_receipt
from src.fridge.fridge_utils import get_fridge_by_id

def test_update_fridge_with_direct_data():
    """Test updating fridge with direct items data."""
    print("=== Test 1: Direct Items Data ===")
    
    # Load test data from JSON file
    with open("tests/test_data/traderjoes1.json", "r") as f:
        test_items = json.load(f)
    
    print(f"Loaded {len(test_items)} items from JSON file")
    
    fridge_id = 1
    
    # Update fridge
    success, message = update_fridge(fridge_id, test_items)
    
    print(f"Success: {success}")
    print(f"Message: {message}")
    
    if success:
        # Check the updated fridge
        updated_fridge = get_fridge_by_id(fridge_id)
        print(f"Updated fridge: {json.dumps(updated_fridge, indent=2)}")
    
    print()


if __name__ == "__main__":
    print("Testing Fridge Update Functionality")
    print("=" * 50)
    
    try:
        test_update_fridge_with_direct_data()
        
        print("All tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
