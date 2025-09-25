import sys
import json
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from cv.get_items import scan_receipt


def test_scan_receipt():
    items = scan_receipt("tests/test_data/traderjoes1.jpg")
    print(items)
    print(items[0])


if __name__ == "__main__":
    test_scan_receipt()