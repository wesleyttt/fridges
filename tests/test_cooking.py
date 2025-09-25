import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.cooking.make_recipes import make_recipes

def test_recipe_generation():
    # Path to sample items
    sample_items_path = project_root / "res" / "sample_items.txt"
    
    # Read sample items
    with open(sample_items_path, "r") as f:
        items_data = f.read().strip()

    items_data = json.loads(items_data)
    print(items_data)
    
    try:
        recipes = make_recipes("test_user", items_data)
        
        if recipes:
            print("\nSuccessfully generated recipes:")
            print(recipes)
        else:
            print("No recipes were generated.")
            
    except Exception as e:
        print(f"Error generating recipes: {e}")
        raise

if __name__ == "__main__":
    test_recipe_generation()