# Database Manager User Guide

The Mixion Database Manager (`db.py`) is a standalone administration tool for configuring the drink machine system.

## Starting the Application

```bash
python db.py
```

The application will:
1. Auto-create the database if it doesn't exist
2. Apply any needed migrations
3. Open a windowed interface with four tabs

## Tabs Overview

### 1. Bottles Tab

Manage the physical bottles/containers in your machine.

**Actions:**
- **Add Bottle**: Create a new bottle entry
  - Name: Descriptive name (e.g., "Orange Juice")
  - Position: Physical slot number (1, 2, 3, etc.)
  - Enabled: Whether the bottle is active

- **Edit Selected**: Modify an existing bottle
- **Delete Selected**: Remove a bottle (will also delete associated recipes)

**Tips:**
- Position numbers should match physical hardware slots
- Disable bottles temporarily without deleting them
- Deleting a bottle removes it from all recipes

### 2. Drinks Tab

Define the drinks available in your menu.

**Actions:**
- **Add Drink**: Create a new menu item
  - Name: Display name for customers
  - Price: Cost in cents/rupees (integer)
  - Active: Whether the drink appears in the menu

- **Edit Selected**: Update drink details
- **Delete Selected**: Remove drink and all its recipes

**Tips:**
- Set Active=No to hide drinks without deleting them
- Price is stored as an integer (e.g., 150 for ₹1.50)
- Create the drink first, then define its recipe

### 3. Recipes Tab

Map which bottles are used for each drink and in what amounts.

**Workflow:**
1. Select a drink from the dropdown
2. Click "Load Recipe" to see current recipe
3. Enter amount (ml) for each bottle
4. Click "Save Recipe"

**Fields:**
- Enter `0` to exclude a bottle from the recipe
- Enter any positive integer for ml amount
- A drink can use 1, 2, or all 3 bottles

**Example:**
```
Drink: Tropical Mix
Bottle A (Orange): 100ml
Bottle B (Pineapple): 50ml
Bottle C (Soda): 0ml
```

**Tips:**
- You can modify recipes at any time
- "Clear Recipe" removes all ingredients for selected drink
- Recipes are validated before saving

### 4. Custom Limits Tab

Set safety limits for the custom pour feature.

**Purpose:**
When customers create custom drinks, these limits prevent waste and overpour.

**Configuration:**
- **Min (ml)**: Minimum pour amount allowed
- **Max (ml)**: Maximum pour amount allowed

**Example:**
```
Bottle A: Min=10ml, Max=200ml
```

**Tips:**
- Min must be less than or equal to Max
- Values cannot be negative
- Set realistic limits based on cup size
- Click "Save All Limits" to apply changes

## Data Safety

- All numeric fields are validated
- Negative values are rejected
- Database uses transactions (rollback on error)
- Foreign key constraints prevent orphaned data

## Common Workflows

### Adding a New Drink

1. Go to **Bottles** tab → Verify bottles are configured
2. Go to **Drinks** tab → Click "Add Drink"
3. Enter name and price → Save
4. Go to **Recipes** tab → Select new drink
5. Set ml amounts for each bottle → Save Recipe

### Changing Bottle Configuration

1. Go to **Bottles** tab
2. Select bottle → Click "Edit Selected"
3. Update name or position
4. Save changes
5. Recipes automatically use new bottle name

### Temporarily Disabling a Drink

1. Go to **Drinks** tab
2. Select drink → Click "Edit Selected"
3. Uncheck "Active"
4. Save

The drink remains in the database but won't appear in customer menu.

## Troubleshooting

**Problem: "Position already exists" error**
- Each bottle must have a unique position number
- Edit existing bottle or use different position

**Problem: Dialog doesn't close after save**
- Check for error messages
- Verify all required fields are filled
- Ensure numeric values are valid integers

**Problem: Recipe doesn't save**
- Make sure drink exists in Drinks tab
- Verify amounts are non-negative integers
- Check that bottles exist and are enabled

**Problem: Database locked**
- Close any other programs accessing mixion.db
- Make sure app.py is not running
- Restart the admin tool

## Database Location

The database file is located at:
```
database/mixion.db
```

### Backup

To backup your configuration:
```bash
cp database/mixion.db database/mixion.db.backup
```

### Reset

To start fresh:
```bash
rm database/mixion.db
python db.py
```

A new database with default bottles will be created.

## Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Confirm in dialogs
- **Esc**: Cancel dialogs (where supported)

## Support

For issues or questions:
1. Check console output for error messages
2. Verify Python version (3.9+ recommended)
3. Ensure dependencies are installed
4. Review database file permissions
