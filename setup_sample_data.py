"""
Sample Data Population Script
Run this to add sample drinks and recipes to your database
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import init_database


def populate_sample_data():
    """Populate database with sample drinks and recipes"""
    
    db = init_database()
    print("=" * 60)
    print("POPULATING SAMPLE DATA")
    print("=" * 60)
    
    # Clear existing test data (optional)
    print("\n1. Clearing existing drinks and recipes...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recipes")
        cursor.execute("DELETE FROM drinks")
    print("   ✓ Cleared")
    
    # Update existing bottles with realistic flow rates
    print("\n2. Updating bottles with flow rates...")
    bottles = db.get_all_bottles()
    
    if bottles:
        for i, bottle in enumerate(bottles):
            new_name = f"Bottle {chr(65 + i)}"  # A, B, C, etc.
            flow_rate = 10.0  # 10 ml/sec is realistic
            db.update_bottle(bottle['id'], new_name, bottle['position'], flow_rate, 1)
            print(f"   ✓ {new_name}: position={bottle['position']}, flow_rate={flow_rate} ml/sec")
    else:
        # Add sample bottles if none exist
        print("   No bottles found, adding defaults...")
        for i in range(6):
            bottle_id = db.add_bottle(f"Bottle {chr(65 + i)}", i + 1, 10.0)
            print(f"   ✓ Added Bottle {chr(65 + i)}: position={i + 1}, flow_rate=10.0 ml/sec")
    
    # Refresh bottles list
    bottles = db.get_all_bottles()
    
    # Add sample drinks
    print("\n3. Adding sample drinks...")
    
    drinks_data = [
        ("Mojito", 500),
        ("Margarita", 550),
        ("Cosmopolitan", 600),
        ("Mai Tai", 650),
        ("Piña Colada", 600),
    ]
    
    drink_ids = []
    for name, price in drinks_data:
        drink_id = db.add_drink(name, price, active=1)
        drink_ids.append(drink_id)
        print(f"   ✓ Added '{name}' (${price/100:.2f})")
    
    # Add recipes (using first 3 bottles for simplicity)
    print("\n4. Adding recipes...")
    
    if len(bottles) >= 3:
        # Mojito: 50ml + 30ml + 70ml = 150ml
        db.set_recipe(drink_ids[0], bottles[0]['id'], 50)
        db.set_recipe(drink_ids[0], bottles[1]['id'], 30)
        db.set_recipe(drink_ids[0], bottles[2]['id'], 70)
        print(f"   ✓ Mojito: {bottles[0]['name']}(50ml) + {bottles[1]['name']}(30ml) + {bottles[2]['name']}(70ml)")
        
        # Margarita: 60ml + 40ml + 50ml = 150ml
        db.set_recipe(drink_ids[1], bottles[0]['id'], 60)
        db.set_recipe(drink_ids[1], bottles[1]['id'], 40)
        db.set_recipe(drink_ids[1], bottles[2]['id'], 50)
        print(f"   ✓ Margarita: {bottles[0]['name']}(60ml) + {bottles[1]['name']}(40ml) + {bottles[2]['name']}(50ml)")
        
        # Cosmopolitan: 45ml + 45ml + 60ml = 150ml
        db.set_recipe(drink_ids[2], bottles[0]['id'], 45)
        db.set_recipe(drink_ids[2], bottles[1]['id'], 45)
        db.set_recipe(drink_ids[2], bottles[2]['id'], 60)
        print(f"   ✓ Cosmopolitan: {bottles[0]['name']}(45ml) + {bottles[1]['name']}(45ml) + {bottles[2]['name']}(60ml)")
        
        if len(bottles) >= 4:
            # Mai Tai: 50ml + 40ml + 30ml + 30ml = 150ml
            db.set_recipe(drink_ids[3], bottles[0]['id'], 50)
            db.set_recipe(drink_ids[3], bottles[1]['id'], 40)
            db.set_recipe(drink_ids[3], bottles[2]['id'], 30)
            db.set_recipe(drink_ids[3], bottles[3]['id'], 30)
            print(f"   ✓ Mai Tai: {bottles[0]['name']}(50ml) + {bottles[1]['name']}(40ml) + {bottles[2]['name']}(30ml) + {bottles[3]['name']}(30ml)")
        
        if len(bottles) >= 5:
            # Piña Colada: 50ml + 50ml + 50ml = 150ml
            db.set_recipe(drink_ids[4], bottles[1]['id'], 50)
            db.set_recipe(drink_ids[4], bottles[3]['id'], 50)
            db.set_recipe(drink_ids[4], bottles[4]['id'], 50)
            print(f"   ✓ Piña Colada: {bottles[1]['name']}(50ml) + {bottles[3]['name']}(50ml) + {bottles[4]['name']}(50ml)")
    
    # Set custom limits for all bottles
    print("\n5. Configuring custom mix limits...")
    for bottle in bottles:
        db.update_limit(bottle['id'], 0, 150)
        print(f"   ✓ {bottle['name']}: 0-150 ml")
    
    print("\n" + "=" * 60)
    print("SAMPLE DATA POPULATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nSummary:")
    print(f"  • Bottles: {len(bottles)}")
    print(f"  • Drinks: {len(drink_ids)}")
    print(f"  • Ready to test!")
    print("\nYou can now run: python app.py")
    print("=" * 60)


def test_pour_calculation():
    """Test the pour duration calculations"""
    print("\n" + "=" * 60)
    print("TESTING POUR CALCULATIONS")
    print("=" * 60)
    
    db = init_database()
    drinks = db.get_active_drinks()
    
    if not drinks:
        print("No drinks found. Run populate_sample_data() first.")
        return
    
    for drink in drinks:
        print(f"\n{drink['name']}:")
        recipes = db.get_recipes_for_drink(drink['id'])
        total_ml = 0
        max_time = 0
        
        for recipe in recipes:
            duration = recipe['amount_ml'] / recipe['flow_rate']
            total_ml += recipe['amount_ml']
            max_time = max(max_time, duration)
            
            print(f"  • {recipe['bottle_name']}: {recipe['amount_ml']}ml ÷ {recipe['flow_rate']}ml/s = {duration:.1f}s (relay {recipe['position']})")
        
        print(f"  → Total volume: {total_ml}ml")
        print(f"  → Pour time: ~{max_time:.1f}s (parallel dispensing)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    populate_sample_data()
    test_pour_calculation()
