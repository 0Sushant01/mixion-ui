# Database Directory

This directory stores the SQLite database file for the Mixion application.

## Auto-Creation

The database file `mixion.db` is **automatically created** when you run `app.py` for the first time.

You do **not** need to:
- Run any setup scripts
- Execute migration commands
- Create the database manually

## What Gets Created

On first boot, the following are automatically set up:

### Tables
- `bottles` - Liquid bottle configuration
- `drinks` - Predefined drink menu items
- `recipes` - Ingredient mapping for drinks
- `custom_limits` - Safety limits for custom pours

### Default Data
- 3 bottles (Bottle A, B, C at positions 1, 2, 3)
- Custom pour limits (0-150ml per bottle)

## Location

Database file: `database/mixion.db`

This file is ignored by git to prevent committing local data.

## Resetting the Database

To start fresh, simply delete `mixion.db` and restart the app.

## Backup

To backup your drink recipes and configuration:

```bash
cp database/mixion.db database/mixion.db.backup
```
