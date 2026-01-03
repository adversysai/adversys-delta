#!/bin/bash

echo "Running initialization script..."

# branch from parameter or environment variable
# If argument is "$BRANCH" (literal string from exec form CMD), use ENV variable instead
# This matches the original Agent Zero pattern where CMD uses exec form: ["/exe/initialize.sh", "$BRANCH"]
# In exec form, Docker doesn't expand variables, so "$BRANCH" is passed as literal string
if [ "$1" = '$BRANCH' ]; then
    # Argument is literal "$BRANCH" string, use ENV variable (set from Dockerfile ARG/ENV)
    BRANCH="${BRANCH:-local}"
else
    # Argument is actual branch name, use it (or default to "local")
    BRANCH="${1:-local}"
fi

# Copy all contents from persistent /per to root directory (/) without overwriting
# /per may be:
#   1. Built into the image (from docker/run/fs/per/) - always available
#   2. Mounted from host (./services/data/delta/per) - overrides image's /per if mounted
# If mounted and empty, the mount hides the image's built-in /per files
# So we check if /per exists and has contents, then copy to /
if [ -d "/per" ]; then
    if [ "$(ls -A /per 2>/dev/null)" ]; then
        echo "Copying persistent storage from /per..."
        cp -r --no-preserve=ownership,mode /per/* / 2>/dev/null || true
        echo "Persistent storage copied from /per"
    else
        echo "Note: /per is mounted but empty (mount overrides image's built-in /per files)"
        echo "      To use built-in /per files, ensure host directory has contents or don't mount /per"
    fi
else
    echo "Note: /per directory not found (not mounted, using image's built-in /per if present)"
fi

# allow execution of /root/.bashrc and /root/.profile
chmod 444 /root/.bashrc 2>/dev/null || true
chmod 444 /root/.profile 2>/dev/null || true

# update package list to save time later
apt-get update > /dev/null 2>&1 &

# let supervisord handle the services
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
