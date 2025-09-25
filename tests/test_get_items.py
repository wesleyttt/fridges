import sys
import json
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cv.get_items import scan_receipt


def test_scan_receipt():
    items = scan_receipt("tests/test_data/traderjoes1.jpg")
    print(items)


if __name__ == "__main__":
    test_scan_receipt()