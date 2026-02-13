import os
import sqlite3
from contextlib import contextmanager


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_directory()

    def _ensure_directory(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_database(self):
        with self.get_connection() as conn:
            self._create_tables(conn)
            self._insert_defaults(conn)
        print(f"Database initialized: {self.db_path}")

    def _create_tables(self, conn):
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bottles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position INTEGER NOT NULL UNIQUE,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                drink_id INTEGER NOT NULL,
                bottle_id INTEGER NOT NULL,
                amount_ml INTEGER NOT NULL,
                PRIMARY KEY (drink_id, bottle_id),
                FOREIGN KEY (drink_id) REFERENCES drinks(id) ON DELETE CASCADE,
                FOREIGN KEY (bottle_id) REFERENCES bottles(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_limits (
                bottle_id INTEGER PRIMARY KEY,
                min_ml INTEGER NOT NULL DEFAULT 0,
                max_ml INTEGER NOT NULL DEFAULT 150,
                FOREIGN KEY (bottle_id) REFERENCES bottles(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_drinks_active 
            ON drinks(active)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bottles_position 
            ON bottles(position)
        """)

    def _insert_defaults(self, conn):
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM bottles")
        bottle_count = cursor.fetchone()["count"]

        if bottle_count == 0:
            default_bottles = [
                ("Bottle A", 1),
                ("Bottle B", 2),
                ("Bottle C", 3),
            ]
            cursor.executemany(
                "INSERT INTO bottles (name, position) VALUES (?, ?)",
                default_bottles
            )
            print("Inserted default bottles")

        cursor.execute("SELECT COUNT(*) as count FROM custom_limits")
        limits_count = cursor.fetchone()["count"]

        if limits_count == 0:
            cursor.execute("SELECT id FROM bottles")
            bottle_ids = [row["id"] for row in cursor.fetchall()]

            default_limits = [(bottle_id, 0, 150) for bottle_id in bottle_ids]
            cursor.executemany(
                "INSERT INTO custom_limits (bottle_id, min_ml, max_ml) VALUES (?, ?, ?)",
                default_limits
            )
            print("Inserted default custom limits")

    # Bottle operations
    def get_all_bottles(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bottles ORDER BY position")
            return [dict(row) for row in cursor.fetchall()]

    def get_enabled_bottles(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bottles WHERE enabled = 1 ORDER BY position")
            return [dict(row) for row in cursor.fetchall()]

    def add_bottle(self, name, position):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bottles (name, position, enabled) VALUES (?, ?, 1)",
                (name, position)
            )
            return cursor.lastrowid

    def update_bottle(self, bottle_id, name, position, enabled):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE bottles SET name = ?, position = ?, enabled = ? WHERE id = ?",
                (name, position, enabled, bottle_id)
            )

    def delete_bottle(self, bottle_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bottles WHERE id = ?", (bottle_id,))

    # Drink operations
    def get_all_drinks(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM drinks ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def get_active_drinks(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM drinks WHERE active = 1 ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def add_drink(self, name, price, active=1):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO drinks (name, price, active) VALUES (?, ?, ?)",
                (name, price, active)
            )
            return cursor.lastrowid

    def update_drink(self, drink_id, name, price, active):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE drinks SET name = ?, price = ?, active = ? WHERE id = ?",
                (name, price, active, drink_id)
            )

    def delete_drink(self, drink_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM drinks WHERE id = ?", (drink_id,))

    # Recipe operations
    def get_recipes_for_drink(self, drink_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, b.name as bottle_name, b.position
                FROM recipes r
                JOIN bottles b ON r.bottle_id = b.id
                WHERE r.drink_id = ?
                ORDER BY b.position
            """, (drink_id,))
            return [dict(row) for row in cursor.fetchall()]

    def set_recipe(self, drink_id, bottle_id, amount_ml):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if amount_ml > 0:
                cursor.execute("""
                    INSERT OR REPLACE INTO recipes (drink_id, bottle_id, amount_ml)
                    VALUES (?, ?, ?)
                """, (drink_id, bottle_id, amount_ml))
            else:
                cursor.execute(
                    "DELETE FROM recipes WHERE drink_id = ? AND bottle_id = ?",
                    (drink_id, bottle_id)
                )

    def delete_all_recipes_for_drink(self, drink_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recipes WHERE drink_id = ?", (drink_id,))

    # Custom limits operations
    def get_all_limits(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cl.*, b.name as bottle_name, b.position
                FROM custom_limits cl
                JOIN bottles b ON cl.bottle_id = b.id
                ORDER BY b.position
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_limits_map(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT bottle_id, min_ml, max_ml FROM custom_limits")
            rows = cursor.fetchall()
            return {row["bottle_id"]: {"min_ml": row["min_ml"], "max_ml": row["max_ml"]} for row in rows}

    def update_limit(self, bottle_id, min_ml, max_ml):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO custom_limits (bottle_id, min_ml, max_ml)
                VALUES (?, ?, ?)
            """, (bottle_id, min_ml, max_ml))


def init_database(db_path=None):
    if db_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "database", "mixion.db")
    
    db = Database(db_path)
    db.init_database()
    return db
