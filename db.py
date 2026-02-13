#!/usr/bin/env python3
"""
Mixion Database Manager

Standalone administration tool for managing bottles, drinks, recipes, and limits.
This is the operator/developer interface - NOT the customer kiosk UI.

Usage:
    python db.py
"""

from src.admin.admin_app import AdminApp
from src.core.database import init_database


def main():
    print("Mixion Database Manager")
    print("-" * 40)
    
    # Initialize database (auto-migrate if needed)
    database = init_database()
    
    # Launch admin UI
    app = AdminApp(database)
    app.run()


if __name__ == "__main__":
    main()
