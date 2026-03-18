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
            self._migrate_schema(conn)
            self._insert_defaults(conn)
        print(f"Database initialized: {self.db_path}")

    def _create_tables(self, conn):
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bottles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position INTEGER NOT NULL UNIQUE,
                flow_rate REAL NOT NULL DEFAULT 600.0,
                current_volume_ml REAL NOT NULL DEFAULT 1000.0,
                capacity_ml REAL NOT NULL DEFAULT 1000.0,
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

        # --- Transaction Logging Tables ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drink_name TEXT NOT NULL,
                msg_id TEXT UNIQUE,
                status TEXT DEFAULT 'pending', -- pending, completed, failed, cancelled
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                bottle_id INTEGER NOT NULL,
                amount_ml INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (bottle_id) REFERENCES bottles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                event_type TEXT NOT NULL, -- TX, RX, ERR, INFO
                message TEXT,
                payload TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
            )
        """)

    def _migrate_schema(self, conn):
        """Auto-migrate database schema for new columns"""
        cursor = conn.cursor()
        
        # Check if flow_rate column exists in bottles table
        cursor.execute("PRAGMA table_info(bottles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'flow_rate' not in columns:
            print("  → Migrating: Adding flow_rate column to bottles table...")
            cursor.execute("""
                ALTER TABLE bottles 
                ADD COLUMN flow_rate REAL NOT NULL DEFAULT 600.0
            """)
            print("  ✓ Migration complete: flow_rate column added")

        if 'current_volume_ml' not in columns:
            print("  → Migrating: Adding current_volume_ml and capacity_ml columns to bottles table...")
            cursor.execute("""
                ALTER TABLE bottles 
                ADD COLUMN current_volume_ml REAL NOT NULL DEFAULT 1000.0
            """)
            cursor.execute("""
                ALTER TABLE bottles 
                ADD COLUMN capacity_ml REAL NOT NULL DEFAULT 1000.0
            """)
            print("  ✓ Migration complete: volume tracking columns added")

        # --- Ensure logging tables exist (for cases where DB existed before logging update) ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if not cursor.fetchone():
            print("  → Migrating: Creating transaction logging tables...")
            self._create_tables(conn)
            print("  ✓ Migration complete: Logging tables created")

    def _insert_defaults(self, conn):
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM bottles")
        bottle_count = cursor.fetchone()["count"]

        if bottle_count == 0:
            default_bottles = [
                ("Bottle A", 1, 600.0, 1000.0, 1000.0),
                ("Bottle B", 2, 600.0, 1000.0, 1000.0),
                ("Bottle C", 3, 600.0, 1000.0, 1000.0),
            ]
            cursor.executemany(
                "INSERT INTO bottles (name, position, flow_rate, current_volume_ml, capacity_ml) VALUES (?, ?, ?, ?, ?)",
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

    def get_bottle_by_id(self, bottle_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bottles WHERE id = ?", (bottle_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_bottle(self, name, position, flow_rate=600.0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bottles (name, position, flow_rate, enabled) VALUES (?, ?, ?, 1)",
                (name, position, flow_rate)
            )
            return cursor.lastrowid

    def update_bottle(self, bottle_id, name, position, flow_rate, enabled):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE bottles SET name = ?, position = ?, flow_rate = ?, enabled = ? WHERE id = ?",
                (name, position, flow_rate, enabled, bottle_id)
            )

    def delete_bottle(self, bottle_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bottles WHERE id = ?", (bottle_id,))

    # Volume operations
    def get_volume(self, bottle_id):
        bottle = self.get_bottle_by_id(bottle_id)
        return bottle["current_volume_ml"] if bottle else 0.0

    def get_capacity(self, bottle_id):
        bottle = self.get_bottle_by_id(bottle_id)
        return bottle["capacity_ml"] if bottle else 0.0

    def set_volume(self, bottle_id, value):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE bottles SET current_volume_ml = ? WHERE id = ?",
                (value, bottle_id)
            )

    def update_volume(self, bottle_id, delta):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE bottles SET current_volume_ml = current_volume_ml + ? WHERE id = ?",
                (delta, bottle_id)
            )

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
                SELECT r.*, b.name as bottle_name, b.position, b.flow_rate
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

    # --- Transaction Logging Operations ---
    def start_transaction(self, drink_name, msg_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transactions (drink_name, msg_id, status) VALUES (?, ?, 'pending')",
                (drink_name, msg_id)
            )
            return cursor.lastrowid

    def update_transaction_status(self, transaction_id, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transactions SET status = ?, end_time = CURRENT_TIMESTAMP WHERE id = ?",
                (status, transaction_id)
            )

    def add_transaction_item(self, transaction_id, bottle_id, amount_ml, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transaction_items (transaction_id, bottle_id, amount_ml, status)
                VALUES (?, ?, ?, ?)
            """, (transaction_id, bottle_id, amount_ml, status))

    def add_transaction_log(self, transaction_id, event_type, message, payload=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transaction_logs (transaction_id, event_type, message, payload)
                VALUES (?, ?, ?, ?)
            """, (transaction_id, event_type, message, payload))


def init_database(db_path=None):
    if db_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "database", "mixion.db")
    
    db = Database(db_path)
    db.init_database()
    return db
