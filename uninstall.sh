#!/bin/bash

# Xavyera Code - Uninstaller
# This script removes Xavyera Code and all its data from your system.

echo "⚠️  Uninstalling Xavyera Code..."

# 1. Remove the global command
if [ -f ~/.local/bin/xavyera ]; then
    rm ~/.local/bin/xavyera
    echo "🗑️  Removed xavyera CLI command."
fi

# 2. Remove usage tracking data
if [ -f ~/.xavyera_usage.json ]; then
    rm ~/.xavyera_usage.json
    echo "🗑️  Removed usage tracking data."
fi

# 3. Ask to remove the project files
read -p "Do you want to remove all project files in /home/xavyera/Documents/ai? (y/n): " remove_files
if [ "$remove_files" = "y" ]; then
    rm -rf /home/xavyera/Documents/ai
    echo "🗑️  Project files removed."
else
    echo "📂 Project files kept at /home/xavyera/Documents/ai."
fi

echo "✅ Xavyera Code has been uninstalled."
