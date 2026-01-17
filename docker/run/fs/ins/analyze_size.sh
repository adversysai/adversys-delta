#!/bin/bash
# Script to analyze container size and identify large directories/files
# Usage: Run inside the container: bash /ins/analyze_size.sh

echo "====================CONTAINER SIZE ANALYSIS===================="
echo ""

echo "=== Total Container Size ==="
du -sh / 2>/dev/null | head -1
echo ""

echo "=== Top 20 Largest Directories ==="
du -h --max-depth=1 / 2>/dev/null | sort -rh | head -20
echo ""

echo "=== Large Files (>100MB) ==="
find / -type f -size +100M -exec du -h {} + 2>/dev/null | sort -rh | head -20
echo ""

echo "=== Package Sizes ==="
dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -rn | head -20
echo ""

echo "=== Python Package Sizes ==="
if [ -d "/opt/venv-a0" ]; then
    echo "Virtual environment size:"
    du -sh /opt/venv-a0
    echo ""
    echo "Largest Python packages:"
    du -sh /opt/venv-a0/lib/python*/site-packages/* 2>/dev/null | sort -rh | head -20
fi
echo ""

echo "=== Go Tools Size ==="
if [ -d "/root/go" ]; then
    du -sh /root/go
    du -sh /root/go/bin/* 2>/dev/null | sort -rh | head -10
fi
echo ""

echo "=== Metasploit Size ==="
if [ -d "/usr/share/metasploit-framework" ]; then
    du -sh /usr/share/metasploit-framework
fi
echo ""

echo "=== Neo4j Size ==="
if [ -d "/usr/share/neo4j" ] || [ -d "/var/lib/neo4j" ]; then
    du -sh /usr/share/neo4j /var/lib/neo4j 2>/dev/null
fi
echo ""

echo "=== ExploitDB Size ==="
if [ -d "/usr/share/exploitdb" ]; then
    du -sh /usr/share/exploitdb
fi
echo ""

echo "=== Wordlists Size ==="
if [ -d "/usr/share/wordlists" ]; then
    du -sh /usr/share/wordlists
    du -sh /usr/share/wordlists/* 2>/dev/null | sort -rh | head -10
fi
echo ""

echo "=== Playwright Browsers Size ==="
if [ -d "/a0/tmp/playwright" ]; then
    du -sh /a0/tmp/playwright
fi
echo ""

echo "====================ANALYSIS COMPLETE===================="
