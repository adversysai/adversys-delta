#!/bin/bash
set -e

# Exit immediately if a command exits with a non-zero status.
# set -e

# branch from parameter
if [ -z "$1" ]; then
    echo "Error: Branch parameter is empty. Please provide a valid branch name."
    exit 1
fi
BRANCH="$1"

if [ "$BRANCH" = "local" ]; then
    # Adversys Added this: For local branch, copy from staging location
    # The code was copied to /tmp/agent-zero-source in the Dockerfile
    # This matches the original pattern where install_A0.sh handles getting the code
    if [ -d "/tmp/agent-zero-source" ] && [ "$(ls -A /tmp/agent-zero-source 2>/dev/null)" ]; then
        echo "Copying local dev files from /tmp/agent-zero-source to /git/agent-zero"
        mkdir -p /git/agent-zero
        cp -r /tmp/agent-zero-source/* /git/agent-zero/
        cp -r /tmp/agent-zero-source/.[!.]* /git/agent-zero/ 2>/dev/null || true
    else
        echo "ERROR: Local branch specified but no source code found in /tmp/agent-zero-source"
        echo "       Make sure the Dockerfile copies the code before running install_A0.sh"
        exit 1
    fi
else
    # For other branches, clone from GitHub (original behavior)
    # Use GITHUB_REPO_URL from environment (set via Dockerfile ARG/ENV)
    GITHUB_REPO_URL="${GITHUB_REPO_URL:-https://github.com/adversysai/adversys-delta}"
    echo "Cloning repository from branch $BRANCH..."
    echo "Repository URL: $GITHUB_REPO_URL"
    git clone -b "$BRANCH" "$GITHUB_REPO_URL" "/git/agent-zero" || {
        echo "CRITICAL ERROR: Failed to clone repository. Branch: $BRANCH, URL: $GITHUB_REPO_URL"
        exit 1
    }
fi

. "/ins/setup_venv.sh" "$@"

# moved to base image
# # Ensure the virtual environment and pip setup
# pip install --upgrade pip ipython requests
# # Install some packages in specific variants
# pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining A0 python packages
uv pip install -r /git/agent-zero/requirements.txt
# override for packages that have unnecessarily strict dependencies
uv pip install -r /git/agent-zero/requirements2.txt

# install playwright
bash /ins/install_playwright.sh "$@"

# Preload A0
# Note: --dockerized is a boolean flag (store_true), so no =true needed
python /git/agent-zero/preload.py --dockerized
