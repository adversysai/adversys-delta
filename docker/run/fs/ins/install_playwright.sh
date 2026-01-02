#!/bin/bash
set -e

# activate venv
. "/ins/setup_venv.sh" "$@"

# install playwright if not installed (should be from requirements.txt)
uv pip install playwright

# set PW installation path to /a0/tmp/playwright
export PLAYWRIGHT_BROWSERS_PATH=/a0/tmp/playwright

# install chromium with dependencies
# Adversys Added this: Additional dependencies for Chrome stability in Docker/Podman containers
# Note: Package names match Kali Linux (Debian-based) package names
apt-get install -y \
    fonts-unifont \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxrandr2 \
    libasound2t64 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libxss1

# Install Playwright Chromium (headless shell only)
# Note: Kali Linux is not officially supported by Playwright, so it uses a fallback build (ubuntu20.04-x64)
# This is expected and works fine - the warning can be ignored
playwright install chromium --only-shell 2>&1 | grep -v "BEWARE: your OS is not officially supported" || true
