"""
Example usage of the Mixion database layer.
This file demonstrates how to interact with the database.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import init_database


def example_read_bottles():
    db = init_database()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bottles WHERE enabled = 1 ORDER BY position")
        bottles = cursor.fetchall()
        
        print("\n=== BOTTLES ===")
        for bottle in bottles:
            print(f"Position {bottle['position']}: {bottle['name']} (ID: {bottle['id']})")


def example_add_drink():
    db = init_database()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Insert a drink
        cursor.execute(
            "INSERT INTO drinks (name, price, active) VALUES (?, ?, ?)",
            ("Tropical Mix", 150, 1)
        )
        drink_id = cursor.lastrowid
        
        # Add recipe (50ml from bottle 1, 100ml from bottle 2)
        cursor.executemany(
            "INSERT INTO recipes (drink_id, bottle_id, amount_ml) VALUES (?, ?, ?)",
            [
                (drink_id, 1, 50),
                (drink_id, 2, 100),
            ]
        )
        
        print(f"\n=== DRINK CREATED ===")
        print(f"Drink ID: {drink_id}")
        print(f"Name: Tropical Mix")
        print(f"Price: 150")


def example_read_drinks_with_recipes():
    db = init_database()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                d.id,
                d.name,
                d.price,
                b.name as bottle_name,
                r.amount_ml
            FROM drinks d
            JOIN recipes r ON d.id = r.drink_id
            JOIN bottles b ON r.bottle_id = b.id
            WHERE d.active = 1
            ORDER BY d.id, b.position
        """)
        
        results = cursor.fetchall()
        
        print("\n=== DRINKS WITH RECIPES ===")
        current_drink = None
        for row in results:
            if current_drink != row['id']:
                current_drink = row['id']
                print(f"\n{row['name']} (₹{row['price']})")
            print(f"  - {row['amount_ml']}ml from {row['bottle_name']}")


def example_get_custom_limits():
    db = init_database()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                b.name,
                cl.min_ml,
                cl.max_ml
            FROM custom_limits cl
            JOIN bottles b ON cl.bottle_id = b.id
            ORDER BY b.position
        """)
        
        limits = cursor.fetchall()
        
        print("\n=== CUSTOM POUR LIMITS ===")
        for limit in limits:
            print(f"{limit['name']}: {limit['min_ml']}ml - {limit['max_ml']}ml")


if __name__ == "__main__":
    print("Mixion Database Examples\n")
    
    example_read_bottles()
    example_add_drink()
    example_read_drinks_with_recipes()
    example_get_custom_limits()
    
    print("\n✓ All examples completed successfully")
