#!/bin/sh
set -e

# Adversys-specific entrypoint (original Agent Zero uses supervisord via /exe/initialize.sh)
# This entrypoint ensures /a0 exists as a real directory for Delta data storage
# and activates the virtual environment before running the application

# Ensure /a0 data subdirectories exist (in case /a0 is mounted as a volume)
# If /a0 is mounted, the mount will override the directory, so we just ensure subdirectories exist
mkdir -p /a0/memory /a0/knowledge /a0/logs /a0/tmp /a0/usr

# Activate virtual environment and run command
. /opt/venv-a0/bin/activate
cd /app
exec "$@"
