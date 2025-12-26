#!/bin/bash
# ============================================================================
# CUSTOM ADDITION: Branding Patch Script
# ============================================================================
# This script is a custom addition to rebrand Agent Zero to Delta.
# It replaces "Agent Zero", "agent0", "A0" with "Delta" in user-facing text
# during the Docker build process, allowing us to maintain upstream Agent Zero
# code while applying our own branding.
#
# This script is automatically executed in Dockerfile and DockerfileLocal
# before the installation steps run.
#
# See scripts/README.md for full documentation.
# ============================================================================

# Don't exit on error - we want to continue even if some replacements fail
set +e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Applying branding patch: Agent Zero/agent0/A0 -> Delta${NC}"

# Define the base directory (should be /git/agent-zero or /app in container)
BASE_DIR="${1:-/git/agent-zero}"

if [ ! -d "$BASE_DIR" ]; then
    echo -e "${YELLOW}Warning: Base directory $BASE_DIR not found, trying /app${NC}"
    BASE_DIR="/app"
fi

if [ ! -d "$BASE_DIR" ]; then
    echo -e "${YELLOW}Warning: Base directory $BASE_DIR not found, using current directory${NC}"
    BASE_DIR="."
fi

echo "Using base directory: $BASE_DIR"

# Function to replace text in a file
replace_in_file() {
    local file="$1"
    local pattern="$2"
    local replacement="$3"
    
    if [ -f "$file" ]; then
        # Use sed with in-place editing
        sed -i "s|${pattern}|${replacement}|g" "$file"
    fi
}

# Replace in HTML files (titles, headings, alt text)
echo "Processing HTML files..."
find "$BASE_DIR/webui" -type f \( -name "*.html" \) -exec sed -i \
    -e 's/Agent Zero/Delta/g' \
    -e 's/agent0/Delta/g' \
    -e 's/A0 Chat/Delta Chat/g' \
    -e 's/A0 MCP/Delta MCP/g' \
    -e 's/A0 A2A/Delta A2A/g' \
    -e 's/agent-zero\.ai/delta.ai/g' \
    -e 's/agent0ai\/agent-zero/deltaai\/delta/g' \
    {} +

# Replace in JavaScript files (user-facing strings, comments, not variable names)
echo "Processing JavaScript files..."
find "$BASE_DIR/webui" -type f \( -name "*.js" \) -exec sed -i \
    -e 's/"Agent Zero"/"Delta"/g' \
    -e 's/'\''Agent Zero'\''/'\''Delta'\''/g' \
    -e 's/`Agent Zero`/`Delta`/g' \
    -e 's/Agent Zero/Delta/g' \
    -e 's/"agent0"/"Delta"/g' \
    -e 's/'\''agent0'\''/'\''Delta'\''/g' \
    -e 's/agent0/Delta/g' \
    -e 's/\* A0 Chat UI/\* Delta Chat UI/g' \
    -e 's/A0 Chat UI/Delta Chat UI/g' \
    -e 's/agent-zero\.ai/delta.ai/g' \
    -e 's/agent0ai\/agent-zero/deltaai\/delta/g' \
    {} +

# Replace in JSON files (manifest, etc.)
echo "Processing JSON files..."
find "$BASE_DIR/webui" -type f \( -name "*.json" \) -exec sed -i \
    -e 's/"Agent Zero"/"Delta"/g' \
    -e 's/"agent-zero"/"delta"/g' \
    -e 's/"agent0"/"delta"/g' \
    -e 's/Agent Zero/Delta/g' \
    -e 's/agent-zero/delta/g' \
    -e 's/agent0/delta/g' \
    {} +

# Replace in Python files (user-facing messages, docstrings, comments)
# Be careful not to break technical references
echo "Processing Python files..."
find "$BASE_DIR" -type f \( -name "*.py" \) ! -path "*/vendor/*" ! -path "*/__pycache__/*" -exec sed -i \
    -e 's/Agent Zero/Delta/g' \
    -e 's/agent0/Delta/g' \
    -e 's/A0 Chat/Delta Chat/g' \
    -e 's/agent-zero\.ai/delta.ai/g' \
    {} +

# Replace in Markdown files (documentation, README)
# Skip vendor and knowledge base files to avoid breaking technical docs
echo "Processing Markdown files..."
find "$BASE_DIR" -type f \( -name "*.md" \) ! -path "*/vendor/*" ! -path "*/knowledge/*" -exec sed -i \
    -e 's/Agent Zero/Delta/g' \
    -e 's/agent0/Delta/g' \
    -e 's/A0 Chat/Delta Chat/g' \
    -e 's/agent-zero\.ai/delta.ai/g' \
    -e 's/agent0ai\/agent-zero/deltaai\/delta/g' \
    {} +

# Specific file replacements
echo "Processing specific files..."

# index.html
if [ -f "$BASE_DIR/webui/index.html" ]; then
    replace_in_file "$BASE_DIR/webui/index.html" "Agent Zero" "Delta"
fi

# login.html
if [ -f "$BASE_DIR/webui/login.html" ]; then
    replace_in_file "$BASE_DIR/webui/login.html" "Agent Zero" "Delta"
fi

# manifest.json
if [ -f "$BASE_DIR/webui/js/manifest.json" ]; then
    replace_in_file "$BASE_DIR/webui/js/manifest.json" "Agent Zero" "Delta"
    replace_in_file "$BASE_DIR/webui/js/manifest.json" "agent-zero" "delta"
    replace_in_file "$BASE_DIR/webui/js/manifest.json" "agent0" "delta"
fi

# welcome-screen.html
if [ -f "$BASE_DIR/webui/components/welcome/welcome-screen.html" ]; then
    replace_in_file "$BASE_DIR/webui/components/welcome/welcome-screen.html" "Agent Zero" "Delta"
fi

# welcome-store.js
if [ -f "$BASE_DIR/webui/components/welcome/welcome-store.js" ]; then
    replace_in_file "$BASE_DIR/webui/components/welcome/welcome-store.js" "agent-zero.ai" "delta.ai"
    replace_in_file "$BASE_DIR/webui/components/welcome/welcome-store.js" "agent0ai/agent-zero" "deltaai/delta"
    replace_in_file "$BASE_DIR/webui/components/welcome/welcome-store.js" "agent0" "delta"
fi

# index.js - replace A0 references in comments
if [ -f "$BASE_DIR/webui/index.js" ]; then
    replace_in_file "$BASE_DIR/webui/index.js" "* A0 Chat UI" "* Delta Chat UI"
    replace_in_file "$BASE_DIR/webui/index.js" "A0 Chat UI" "Delta Chat UI"
fi

echo -e "${GREEN}Branding patch applied successfully!${NC}"

