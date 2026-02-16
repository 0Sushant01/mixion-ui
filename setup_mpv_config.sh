#!/bin/bash
# Cleanup legacy MPV configuration
# Mixion now uses runtime MPV configuration instead of persistent files

echo "Cleaning up legacy MPV configuration..."
echo ""

# Remove old persistent configuration if it exists
MPV_CONFIG_DIR="$HOME/.config/mpv"
INPUT_CONF="$MPV_CONFIG_DIR/input.conf"

if [ -f "$INPUT_CONF" ]; then
    echo "⚠️  Found legacy configuration: $INPUT_CONF"
    echo "   Removing to prevent conflicts..."
    rm -f "$INPUT_CONF"
    echo "✓ Removed $INPUT_CONF"
else
    echo "✓ No legacy configuration found"
fi

echo ""
echo "────────────────────────────────────────────────────"
echo "MPV Configuration Status: RUNTIME ONLY"
echo "────────────────────────────────────────────────────"
echo ""
echo "Mixion uses runtime MPV arguments for splash screen:"
echo "  --input-conf=/dev/null"
echo "  --input-cmdlist=MOUSE_BTN0 quit"
echo ""
echo "This means:"
echo "  ✓ Touch-to-exit works ONLY during splash"
echo "  ✓ No system files modified"
echo "  ✓ Other MPV usage unaffected"
echo "  ✓ Safe for maintenance videos"
echo ""
echo "You can now run: python app.py"
echo "────────────────────────────────────────────────────"
