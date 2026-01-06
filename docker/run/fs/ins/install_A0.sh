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
    # For local branch, code should already be copied to /git/agent-zero by the Dockerfile
    if [ -d "/git/agent-zero" ] && [ "$(ls -A /git/agent-zero 2>/dev/null)" ]; then
        echo "Using local dev files from /git/agent-zero"
    else
        echo "ERROR: Local branch specified but no source code found in /git/agent-zero"
        echo "       Make sure the Dockerfile copies the code before running install_A0.sh"
        exit 1
    fi
else
    # For other branches, clone from GitHub (original behavior)
    # Use GITHUB_REPO_URL from environment (set via Dockerfile ARG/ENV)
    GITHUB_REPO_URL="${GITHUB_REPO_URL:-https://github.com/adversysai/adversys-delta}"
    echo "Cloning repository from branch $BRANCH..."
    echo "Repository URL: $GITHUB_REPO_URL"
    
    # Remove existing directory if it exists (Dockerfile may have copied code there)
    if [ -d "/git/agent-zero" ]; then
        echo "Removing existing /git/agent-zero directory before cloning..."
        rm -rf /git/agent-zero
    fi
    
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
