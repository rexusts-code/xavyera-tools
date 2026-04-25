#!/bin/bash

# Xavyera Code - One-Click Installer
# This script sets up the entire environment automatically.

set -e

echo "🚀 Setting up Xavyera Code..."

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed. Please install it first."
    exit 1
fi

# 2. Create local directory if it doesn't exist
INSTALL_DIR="$HOME/Documents/ai"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "📦 Installing dependencies (this may take a minute)..."
mkdir -p .libs
pip3 install --target .libs rich click pydantic python-dotenv requests duckduckgo-search prompt_toolkit --break-system-packages || \
pip3 install --target .libs rich click pydantic python-dotenv requests duckduckgo-search prompt_toolkit

# 3. Create .env if missing
if [ ! -f .env ]; then
    echo "🔑 Configuring API Key..."
    read -p "Enter your Gemini API Key (get it at aistudio.google.com): " api_key < /dev/tty
    echo "GEMINI_API_KEY=$api_key" > .env
    echo "LUMINA_PROVIDER=gemini" >> .env
    echo "LUMINA_MODEL=gemini-1.5-flash" >> .env
fi

# 4. Create the xavyera command
echo "🛠️ Creating xavyera command..."
mkdir -p ~/.local/bin

cat <<EOF > ~/.local/bin/xavyera
#!/bin/bash
export PYTHONPATH="$INSTALL_DIR/.libs:\$PYTHONPATH"
python3 "$INSTALL_DIR/main.py" "\$@"
EOF

chmod +x ~/.local/bin/xavyera

# 5. Finalize
echo "----------------------------------------------------------"
echo "✅ Xavyera Code setup complete!"
echo "✨ You can now run the tool by typing: [bold]xavyera[/bold]"
echo "----------------------------------------------------------"

# Try to add ~/.local/bin to PATH for the current session if not there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "💡 Note: Please add ~/.local/bin to your PATH or run: alias xavyera='~/.local/bin/xavyera'"
fi
