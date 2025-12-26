#!/bin/sh
set -e

# Ensure the Agent Zero data directories exist (Adversys-standard paths)
mkdir -p /var/lib/adversys/agent-zero/{memory,knowledge,logs,tmp,usr}

# CUSTOM ADDITION: Apply branding patch at runtime to handle volume mounts
# This ensures branding is applied even when source code is mounted as a volume
# The script modifies files in-place, so it works with both built-in and mounted files
# Only apply if files are writable (not read-only volume mount)
if [ -d /app ] && [ -w /app/webui/components/welcome/welcome-screen.html ] 2>/dev/null; then
    # Check if branding script exists
    if [ -f /app/scripts/apply-branding.sh ]; then
        # Check if already branded (quick check on welcome screen)
        if ! grep -q "Welcome to Delta" /app/webui/components/welcome/welcome-screen.html 2>/dev/null; then
            echo "Applying branding patch at runtime (volume mount detected)..."
            chmod +x /app/scripts/apply-branding.sh 2>/dev/null || true
            /app/scripts/apply-branding.sh /app 2>/dev/null || true
            echo "Branding patch applied."
        fi
    elif [ -f /git/agent-zero/scripts/apply-branding.sh ] && [ -w /app ]; then
        # Use built-in script if available and /app is writable
        if ! grep -q "Welcome to Delta" /app/webui/components/welcome/welcome-screen.html 2>/dev/null; then
            echo "Applying branding patch at runtime (using built-in script)..."
            chmod +x /git/agent-zero/scripts/apply-branding.sh 2>/dev/null || true
            /git/agent-zero/scripts/apply-branding.sh /app 2>/dev/null || true
            echo "Branding patch applied."
        fi
    fi
fi

# Activate the virtual environment from the base image
. /opt/venv-a0/bin/activate

# Ensure venv is writable (safety check - should already be root-owned, but fix if needed)
# This handles cases where volumes or previous builds might have wrong permissions
chmod -R u+w /opt/venv-a0 2>/dev/null || true

# Run as root (original Agent Zero pattern - simpler and avoids permission issues)
cd /app
exec "$@"
