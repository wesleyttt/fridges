#!/usr/bin/env python3
"""
Test runner for the fridges application.

This script properly sets up the Python path and runs all tests.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_test(test_file: str) -> bool:
    """Run a single test file."""
    print(f"🧪 Running {test_file}...")
    print("=" * 50)
    
    try:
        # Import and run the test
        if test_file == "test_update_fridge":
            from tests.test_update_fridge import test_update_fridge_with_direct_data
            test_update_fridge_with_direct_data()
        elif test_file == "test_get_items":
            from tests.test_get_items import test_scan_receipt
            test_scan_receipt()
        elif test_file == "test_dbconn":
            from tests.test_dbconn import list_tables, list_users
            tables = list_tables()
            users = list_users()
            print(f"Found {len(tables)} tables and {len(users)} users")
        else:
            print(f"Unknown test: {test_file}")
            return False
        
        print(f"✅ {test_file} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ {test_file} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Running Fridges Test Suite")
    print("=" * 50)
    
    tests = [
        "test_dbconn",
        "test_get_items", 
        "test_update_fridge"
    ]
    
    results = []
    
    for test in tests:
        success = run_test(test)
        results.append((test, success))
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
