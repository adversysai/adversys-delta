#!/bin/bash
set -e

# install playwright - moved to install A0
# bash /ins/install_playwright.sh "$@"

# searxng - moved to base image
# bash /ins/install_searxng.sh "$@"

echo "====================INSTALLING ADDITIONAL SECURITY TOOLS===================="

# Update package list
apt-get update

# Install ldap-utils for LDAP enumeration and testing
echo "Installing ldap-utils..."
apt-get install -y --no-install-recommends ldap-utils

# Install Metasploit Framework
echo "Installing Metasploit Framework..."
apt-get install -y --no-install-recommends metasploit-framework

# Install exploitdb (includes searchsploit)
echo "Installing exploitdb (searchsploit)..."
apt-get install -y --no-install-recommends exploitdb

# Update exploitdb database
echo "Updating exploitdb database..."
searchsploit -u || echo "Warning: searchsploit update failed, continuing anyway..."

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

# Install wordlists package
echo "Installing wordlists..."
apt-get install -y --no-install-recommends wordlists

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

# Install BloodHound components
echo "Installing bloodhound and neo4j..."
apt-get install -y --no-install-recommends bloodhound neo4j

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

# Install Go-based tools if not in repos
echo "Installing Go-based security tools..."

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

# findomain - Subdomain finder
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

# Ensure Go bin directory is in PATH for installed tools
echo 'export PATH=$PATH:/root/go/bin:/usr/local/go/bin' >> /root/.bashrc

echo "====================ADDITIONAL SECURITY TOOLS INSTALLATION COMPLETE===================="