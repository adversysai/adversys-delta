#!/bin/bash
set -e

# Environment variables to control optional heavy tools
# Set these to "false" to skip installation and reduce container size
# Example: docker build --build-arg INSTALL_METASPLOIT=false --build-arg INSTALL_NEO4J=false ...
INSTALL_METASPLOIT=${INSTALL_METASPLOIT:-true}
INSTALL_NEO4J=${INSTALL_NEO4J:-true}
INSTALL_EXPLOITDB=${INSTALL_EXPLOITDB:-true}
INSTALL_WORDLISTS=${INSTALL_WORDLISTS:-true}
INSTALL_GO_TOOLS=${INSTALL_GO_TOOLS:-true}

echo "====================INSTALLING ADDITIONAL SECURITY TOOLS===================="
echo "Configuration:"
echo "  INSTALL_METASPLOIT=${INSTALL_METASPLOIT}"
echo "  INSTALL_NEO4J=${INSTALL_NEO4J}"
echo "  INSTALL_EXPLOITDB=${INSTALL_EXPLOITDB}"
echo "  INSTALL_WORDLISTS=${INSTALL_WORDLISTS}"
echo "  INSTALL_GO_TOOLS=${INSTALL_GO_TOOLS}"
echo ""

# Update package list
apt-get update

# Install ldap-utils for LDAP enumeration and testing
echo "Installing ldap-utils..."
apt-get install -y --no-install-recommends ldap-utils

# Install Metasploit Framework (OPTIONAL - ~2-3GB)
if [ "${INSTALL_METASPLOIT}" = "true" ]; then
    echo "Installing Metasploit Framework..."
    apt-get install -y --no-install-recommends metasploit-framework
else
    echo "Skipping Metasploit Framework (INSTALL_METASPLOIT=false)"
fi

# Install exploitdb (includes searchsploit) (OPTIONAL - ~500MB-1GB)
if [ "${INSTALL_EXPLOITDB}" = "true" ]; then
    echo "Installing exploitdb (searchsploit)..."
    apt-get install -y --no-install-recommends exploitdb
    # Skip database update during build to save space (~500MB-1GB)
    # Database can be updated at runtime with: searchsploit -u
    echo "Skipping exploitdb database update during build (run 'searchsploit -u' at runtime if needed)"
else
    echo "Skipping exploitdb (INSTALL_EXPLOITDB=false)"
fi

# Install masscan - Fast port scanner
echo "Installing masscan..."
apt-get install -y --no-install-recommends masscan

# Install Responder and Impacket
echo "Installing Responder and Impacket..."
apt-get install -y --no-install-recommends responder impacket-scripts python3-impacket

# Install CrackMapExec - Network pentesting tool
echo "Installing CrackMapExec..."
apt-get install -y --no-install-recommends crackmapexec

# Install BloodHound.py - Active Directory reconnaissance
echo "Installing BloodHound.py..."
apt-get install -y --no-install-recommends bloodhound.py

# Install password cracking tools
echo "Installing password cracking tools..."
apt-get install -y --no-install-recommends hashcat hashcat-utils john

# Install CEWL - Custom wordlist generator
echo "Installing cewl..."
apt-get install -y --no-install-recommends cewl

# Install ffuf - Fast web fuzzer
echo "Installing ffuf..."
apt-get install -y --no-install-recommends ffuf

# Install nosqlmap - NoSQL injection tool
echo "Installing nosqlmap..."
apt-get install -y --no-install-recommends nosqlmap || echo "Warning: nosqlmap not available in repos"

# Install XSStrike - XSS detection suite
echo "Installing xssstrike..."
apt-get install -y --no-install-recommends xsstrike || echo "Warning: xsstrike not available in repos"

# Install Kismet - Wireless network detector
echo "Installing kismet..."
apt-get install -y --no-install-recommends kismet

# Install Reaver - WPS cracking tool
echo "Installing reaver..."
apt-get install -y --no-install-recommends reaver

# Install Pixiewps - WPS Pixie Dust attack tool
echo "Installing pixiewps..."
apt-get install -y --no-install-recommends pixiewps

# Install Aircrack-ng suite (includes aircrack-ng, aireplay-ng, etc.)
echo "Installing aircrack-ng..."
apt-get install -y --no-install-recommends aircrack-ng

# Install Crunch - Wordlist generator
echo "Installing crunch..."
apt-get install -y --no-install-recommends crunch

# Install wordlists package (OPTIONAL - ~1-2GB)
if [ "${INSTALL_WORDLISTS}" = "true" ]; then
    echo "Installing wordlists..."
    apt-get install -y --no-install-recommends wordlists
else
    echo "Skipping wordlists (INSTALL_WORDLISTS=false)"
fi

# Install PowerSploit (PowerShell post-exploitation framework)
echo "Installing powersploit..."
apt-get install -y --no-install-recommends powersploit

# Install Empire - Post-exploitation framework
echo "Installing powershell-empire..."
apt-get install -y --no-install-recommends powershell-empire

# Install LaZagne - Credential recovery tool
echo "Installing lazagne..."
apt-get install -y --no-install-recommends lazagne || echo "Warning: lazagne not available in repos"

# Install Pacu - AWS exploitation framework
echo "Installing pacu..."
apt-get install -y --no-install-recommends pacu || echo "Warning: pacu not available in repos"

# Install ScoutSuite - Multi-cloud security auditing tool
echo "Installing scoutsuite..."
apt-get install -y --no-install-recommends scoutsuite || echo "Warning: scoutsuite not available in repos"

# Network scanning and enumeration tools
echo "Installing network scanning tools..."
apt-get install -y --no-install-recommends nmap ncat netcat-traditional

# Install Hydra - Password brute forcing
echo "Installing hydra..."
apt-get install -y --no-install-recommends hydra

# Web enumeration and fuzzing tools
echo "Installing web enumeration tools..."
apt-get install -y --no-install-recommends gobuster dirb nikto whatweb wfuzz

# Install Nuclei - Vulnerability scanner
echo "Installing nuclei..."
apt-get install -y --no-install-recommends nuclei

# SQL injection tools
echo "Installing sqlmap..."
apt-get install -y --no-install-recommends sqlmap

# SMB enumeration tools
echo "Installing SMB tools..."
apt-get install -y --no-install-recommends smbclient smbmap enum4linux enum4linux-ng

# Install evil-winrm - WinRM exploitation
echo "Installing evil-winrm..."
apt-get install -y --no-install-recommends evil-winrm

# Subdomain discovery tools
echo "Installing subdomain discovery tools..."
apt-get install -y --no-install-recommends subfinder amass

# DNS enumeration tools
echo "Installing DNS tools..."
apt-get install -y --no-install-recommends dnsrecon dnsenum fierce bind9-dnsutils

# OSINT tools
echo "Installing OSINT tools..."
apt-get install -y --no-install-recommends theharvester || echo "Warning: theharvester not available"
apt-get install -y --no-install-recommends spiderfoot || echo "Warning: spiderfoot not available"

# SSL/TLS testing
echo "Installing SSL/TLS testing tools..."
apt-get install -y --no-install-recommends testssl.sh sslscan || echo "Warning: some SSL tools not available"
apt-get install -y --no-install-recommends sslyze || echo "Warning: sslyze not available"

# WordPress scanning
echo "Installing wpscan..."
apt-get install -y --no-install-recommends wpscan

# Additional web tools
echo "Installing additional web tools..."
apt-get install -y --no-install-recommends commix wafw00f || echo "Warning: some web tools not available"
apt-get install -y --no-install-recommends arjun || echo "Warning: arjun not available in repos"

# Kerberos tools
echo "Installing Kerberos tools..."
apt-get install -y --no-install-recommends krb5-user

# Web crawling and link discovery
echo "Installing web crawling tools..."
apt-get install -y --no-install-recommends wget curl lynx w3m

# Additional reconnaissance tools
echo "Installing additional recon tools..."
apt-get install -y --no-install-recommends whois dnsutils host nmap-common

# Install feroxbuster - Fast content discovery
echo "Installing feroxbuster..."
apt-get install -y --no-install-recommends feroxbuster

# Install chisel - Tunneling tool
echo "Installing chisel..."
apt-get install -y --no-install-recommends chisel

# Install socat - Multipurpose relay
echo "Installing socat..."
apt-get install -y --no-install-recommends socat

# Install BloodHound components (OPTIONAL - includes Neo4j, ~1-2GB)
if [ "${INSTALL_NEO4J}" = "true" ]; then
    echo "Installing bloodhound and neo4j..."
    apt-get install -y --no-install-recommends bloodhound neo4j
else
    echo "Skipping Neo4j/BloodHound (INSTALL_NEO4J=false)"
fi

# Install Covenant C2 dependencies (if available)
echo "Installing additional C2 tools..."
apt-get install -y --no-install-recommends sliver-client sliver-server || echo "Sliver not available in repos"

# Install additional impacket tools (ensure all are available)
echo "Verifying impacket tools..."
apt-get install -y --no-install-recommends python3-impacket impacket-scripts

# Install LDAP domain dumper
echo "Installing ldapdomaindump..."
apt-get install -y --no-install-recommends ldapdomaindump || python3 -m pip install --no-cache-dir ldapdomaindump || echo "Warning: ldapdomaindump installation failed"

# Install additional Python security tools via pip
echo "Installing Python security tools..."
python3 -m pip install --no-cache-dir \
    mitm6 \
    pypykatz \
    lsassy \
    certipy-ad \
    coercer \
    targetedKerberoast \
    krbrelayx \
    pwntools \
    pycryptodome \
    paramiko \
    pywinrm || echo "Warning: Some Python tools failed to install"

# Install Python tools that may not be in repos
echo "Installing additional Python tools via pip..."
python3 -m pip install --no-cache-dir laZagne || echo "Warning: laZagne pip install failed"
python3 -m pip install --no-cache-dir pacu || echo "Warning: pacu pip install failed"
python3 -m pip install --no-cache-dir ScoutSuite || echo "Warning: ScoutSuite pip install failed"

# Install Go-based tools if not in repos (OPTIONAL - requires Go compiler, ~500MB-1GB)
if [ "${INSTALL_GO_TOOLS}" = "true" ]; then
    echo "Installing Go-based security tools..."
    
    # Check if Go is installed, if not, install it
    if ! command -v go &> /dev/null; then
        echo "Go not found, installing Go..."
        apt-get install -y --no-install-recommends golang-go
    fi
    
    # Dalfox - XSS scanner
    if ! command -v dalfox &> /dev/null; then
        echo "Installing dalfox via go install..."
        go install github.com/hahwul/dalfox/v2@latest 2>/dev/null || echo "Failed to install dalfox"
    fi
    
    # Katana - Web crawler
    if ! command -v katana &> /dev/null; then
        echo "Installing katana via go install..."
        go install github.com/projectdiscovery/katana/cmd/katana@latest 2>/dev/null || echo "Failed to install katana"
    fi
    
    # GoSpider - Web spider
    if ! command -v gospider &> /dev/null; then
        echo "Installing gospider via go install..."
        go install github.com/jaeles-project/gospider@latest 2>/dev/null || echo "Failed to install gospider"
    fi
    
    # Hakrawler - Web crawler
    if ! command -v hakrawler &> /dev/null; then
        echo "Installing hakrawler via go install..."
        go install github.com/hakluke/hakrawler@latest 2>/dev/null || echo "Failed to install hakrawler"
    fi
    
    # dnsx - DNS toolkit
    if ! command -v dnsx &> /dev/null; then
        echo "Installing dnsx via go install..."
        go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>/dev/null || echo "Failed to install dnsx"
    fi
    
    # assetfinder - Subdomain finder
    if ! command -v assetfinder &> /dev/null; then
        echo "Installing assetfinder via go install..."
        go install github.com/tomnomnom/assetfinder@latest 2>/dev/null || echo "Failed to install assetfinder"
    fi
    
    # Clean Go cache after installation
    go clean -cache -modcache -testcache 2>/dev/null || true
else
    echo "Skipping Go tools (INSTALL_GO_TOOLS=false)"
fi

# findomain - Subdomain finder (doesn't require Go)
if ! command -v findomain &> /dev/null; then
    echo "Installing findomain..."
    wget -q https://github.com/findomain/findomain/releases/latest/download/findomain-linux-i386.zip -O /tmp/findomain.zip 2>/dev/null || true
    if [ -f /tmp/findomain.zip ]; then
        unzip -q /tmp/findomain.zip -d /tmp/ 2>/dev/null || true
        chmod +x /tmp/findomain 2>/dev/null || true
        mv /tmp/findomain /usr/local/bin/ 2>/dev/null || true
        rm /tmp/findomain.zip 2>/dev/null || true
    fi
fi

# Ensure Go bin directory is in PATH for installed tools (if Go was installed)
if command -v go &> /dev/null; then
    echo 'export PATH=$PATH:/root/go/bin:/usr/local/go/bin' >> /root/.bashrc
fi

echo "====================ADDITIONAL SECURITY TOOLS INSTALLATION COMPLETE===================="
