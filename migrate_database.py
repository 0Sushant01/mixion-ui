"""
Database Migration Script
Adds flow_rate column to existing bottles table if it doesn't exist
"""

import os
import sys
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


def migrate_database():
    """Add flow_rate column to bottles table if it doesn't exist"""
    
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        config.DATABASE_PATH
    )
    
    print("=" * 60)
    print("DATABASE MIGRATION")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    
    if not os.path.exists(db_path):
        print("\n⚠ Database file doesn't exist yet.")
        print("Run 'python app.py' first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if flow_rate column exists
        cursor.execute("PRAGMA table_info(bottles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'flow_rate' in columns:
            print("\n✓ flow_rate column already exists. No migration needed.")
        else:
            print("\n→ Adding flow_rate column to bottles table...")
            
            # Add the column with default value
            cursor.execute("""
                ALTER TABLE bottles 
                ADD COLUMN flow_rate REAL NOT NULL DEFAULT 10.0
            """)
            
            conn.commit()
            print("✓ flow_rate column added successfully!")
            print("  Default value: 10.0 ml/sec")
            
            # Display current bottles
            cursor.execute("SELECT id, name, position, flow_rate, enabled FROM bottles")
            bottles = cursor.fetchall()
            
            if bottles:
                print(f"\n📋 Current bottles ({len(bottles)}):")
                for bottle in bottles:
                    bottle_id, name, position, flow_rate, enabled = bottle
                    status = "✓" if enabled else "✗"
                    print(f"  {status} ID={bottle_id}: {name} (position={position}, flow_rate={flow_rate} ml/sec)")
                
                print("\n💡 You can update flow rates using the admin panel or SQL:")
                print("   UPDATE bottles SET flow_rate = 12.0 WHERE id = 1;")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
