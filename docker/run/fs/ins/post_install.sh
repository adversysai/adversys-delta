#!/bin/bash
set -e

echo "====================POST INSTALL CLEANUP START===================="

# Cleanup package lists and apt cache
rm -rf /var/lib/apt/lists/*
apt-get clean

# Remove documentation to save space (~500MB-1GB)
echo "Removing documentation..."
rm -rf /usr/share/doc /usr/share/man /usr/share/info

# Remove unnecessary locale files (keep only en_US)
echo "Removing unnecessary locales..."
find /usr/share/locale -mindepth 1 -maxdepth 1 ! -name 'en*' -exec rm -rf {} + 2>/dev/null || true

# Clean Python cache
echo "Cleaning Python cache..."
find /usr -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find /usr -type f -name "*.pyc" -delete 2>/dev/null || true
find /usr -type f -name "*.pyo" -delete 2>/dev/null || true
rm -rf /root/.cache/pip 2>/dev/null || true

# Clean Go cache (if Go was installed)
echo "Cleaning Go cache..."
if command -v go &> /dev/null; then
    go clean -cache -modcache -testcache 2>/dev/null || true
    rm -rf /root/go/pkg 2>/dev/null || true
fi

# Clean npm cache
echo "Cleaning npm cache..."
if command -v npm &> /dev/null; then
    npm cache clean --force 2>/dev/null || true
fi

# Remove temporary files
echo "Removing temporary files..."
rm -rf /tmp/* /var/tmp/* 2>/dev/null || true

# Remove build tools if not needed at runtime (saves ~500MB-1GB)
echo "Removing build tools..."
apt-get remove -y --purge build-essential gcc g++ make 2>/dev/null || true
apt-get autoremove -y 2>/dev/null || true

# Clean up any downloaded files in /tmp
echo "Cleaning downloaded files..."
find /tmp -type f -name "*.zip" -delete 2>/dev/null || true
find /tmp -type f -name "*.tar.gz" -delete 2>/dev/null || true
find /tmp -type f -name "*.deb" -delete 2>/dev/null || true

# Remove git history if not needed (saves space if /git/agent-zero is kept)
# Uncomment if you don't need git history in the container
# echo "Removing git history..."
# find /git -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true

echo "====================POST INSTALL CLEANUP END===================="