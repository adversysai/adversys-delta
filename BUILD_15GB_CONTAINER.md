# Building 15GB Container with Metasploit

## Quick Start

The Dockerfile has been updated to use optimized defaults that target ~15GB while keeping Metasploit.

### Default Build (Recommended - ~15GB)

```bash
docker build -f docker/run/Dockerfile -t adversys-delta:15gb .
```

**Default configuration:**
- ✅ Metasploit: **INSTALLED** (~2-3GB)
- ❌ Neo4j/BloodHound: **SKIPPED** (saves ~1.5-2GB)
- ✅ ExploitDB: **INSTALLED** but update skipped (saves ~500MB-1GB)
- ❌ Wordlists: **SKIPPED** (saves ~1-2GB)
- ❌ Go Tools: **SKIPPED** (saves ~500MB-1GB)
- ✅ Build tools: **REMOVED** after build (saves ~500MB-1GB)

### Custom Build (Override Defaults)

If you need different tools, override the build args:

```bash
# Keep everything (original ~25GB)
docker build \
  --build-arg INSTALL_METASPLOIT=true \
  --build-arg INSTALL_NEO4J=true \
  --build-arg INSTALL_EXPLOITDB=true \
  --build-arg INSTALL_WORDLISTS=true \
  --build-arg INSTALL_GO_TOOLS=true \
  -f docker/run/Dockerfile \
  -t adversys-delta:full .

# Minimal (no Metasploit, ~12GB)
docker build \
  --build-arg INSTALL_METASPLOIT=false \
  --build-arg INSTALL_NEO4J=false \
  --build-arg INSTALL_EXPLOITDB=false \
  --build-arg INSTALL_WORDLISTS=false \
  --build-arg INSTALL_GO_TOOLS=false \
  -f docker/run/Dockerfile \
  -t adversys-delta:minimal .

# Custom: Keep Metasploit + ExploitDB, skip others
docker build \
  --build-arg INSTALL_METASPLOIT=true \
  --build-arg INSTALL_NEO4J=false \
  --build-arg INSTALL_EXPLOITDB=true \
  --build-arg INSTALL_WORDLISTS=false \
  --build-arg INSTALL_GO_TOOLS=false \
  -f docker/run/Dockerfile \
  -t adversys-delta:custom .
```

## Verify Size

After building, check the size:

```bash
docker images adversys-delta:15gb
```

Or run detailed analysis inside the container:

```bash
docker run --rm adversys-delta:15gb bash /ins/analyze_size.sh
```

## What Changed

1. **Dockerfile** - Now uses `install_additional_optimized.sh` by default with optimized build args
2. **post_install.sh** - Enhanced to remove build tools after installation
3. **install_additional_optimized.sh** - Skips ExploitDB database update during build

## Runtime Notes

### ExploitDB Database Update

If you need an updated ExploitDB database, run this at runtime:

```bash
searchsploit -u
```

### Wordlists

If you need wordlists, you can:
1. Mount them as a volume: `docker run -v /path/to/wordlists:/usr/share/wordlists ...`
2. Install specific wordlists at runtime: `apt-get install wordlists-securelists`

### Go Tools

If you need Go tools, you can:
1. Install pre-compiled binaries
2. Install Go at runtime if needed
3. Use the tools from repos (many are available via apt)

## Expected Size Breakdown

| Component | Size | Status |
|-----------|------|--------|
| Metasploit Framework | ~2-3GB | ✅ Installed |
| Kali Linux Base | ~2-3GB | ✅ Installed |
| Python Packages | ~2-3GB | ✅ Installed |
| Other Security Tools | ~2-3GB | ✅ Installed |
| Playwright Browsers | ~500MB-1GB | ✅ Installed |
| **Total** | **~14-16GB** | ✅ Target achieved |

## Troubleshooting

### Container Still >15GB?

1. Check actual size: `docker images adversys-delta:15gb`
2. Run analysis: `docker run --rm adversys-delta:15gb bash /ins/analyze_size.sh`
3. Review what's taking space
4. Consider additional optimizations (see CONTAINER_SIZE_ANALYSIS_V2.md)

### Metasploit Not Working?

1. Verify it's installed: `docker run --rm adversys-delta:15gb which msfconsole`
2. Check size: `docker run --rm adversys-delta:15gb du -sh /usr/share/metasploit-framework`
3. Test: `docker run --rm adversys-delta:15gb msfconsole --version`

## Additional Resources

- `CONTAINER_SIZE_ANALYSIS_V2.md` - Detailed analysis and optimization strategies
- `CONTAINER_SIZE_OPTIMIZATION_GUIDE.md` - Original optimization guide
- `CONTAINER_SIZE_ANALYSIS.md` - Original size analysis
