# Container Size Optimization Guide

## Quick Summary

Your delta container is **25GB** primarily due to:
- Metasploit Framework (~2-3GB)
- Neo4j/BloodHound (~1-2GB)
- ExploitDB database (~500MB-1GB)
- Wordlists (~1-2GB)
- Go tools and compiler (~500MB-1GB)
- Python packages (~2-3GB)
- Kali Linux base (~2-3GB)
- Many other security tools

## Immediate Actions (No Code Changes)

### 1. Analyze Current Container Size
Run this inside your container to see what's taking up space:
```bash
docker run --rm -it adversys-delta:latest bash /ins/analyze_size.sh
```

Or copy the script and run it:
```bash
docker exec <container-id> bash /ins/analyze_size.sh
```

### 2. Test the Improved Cleanup
The `post_install.sh` has been updated with comprehensive cleanup. Rebuild to see the impact:
```bash
docker build -t adversys-delta:latest .
```

Expected reduction: **~2-3GB** (from 25GB to ~22GB)

## Short-term Optimizations (Easy Code Changes)

### Option A: Use Optimized Install Script (Recommended)

1. **Replace the install script** (or modify Dockerfile to use optimized version):
   ```bash
   # In docker/run/Dockerfile, change:
   RUN bash /ins/install_additional.sh $BRANCH
   # To:
   RUN bash /ins/install_additional_optimized.sh $BRANCH
   ```

2. **Build with optional tools disabled**:
   ```bash
   docker build \
     --build-arg INSTALL_METASPLOIT=false \
     --build-arg INSTALL_NEO4J=false \
     --build-arg INSTALL_EXPLOITDB=false \
     --build-arg INSTALL_WORDLISTS=false \
     --build-arg INSTALL_GO_TOOLS=false \
     -t adversys-delta:minimal .
   ```

   Expected size: **~12-15GB** (saves ~10GB)

3. **Or build with only some tools disabled**:
   ```bash
   docker build \
     --build-arg INSTALL_METASPLOIT=false \
     --build-arg INSTALL_NEO4J=false \
     -t adversys-delta:optimized .
   ```

   Expected size: **~18-20GB** (saves ~5-7GB)

### Option B: Modify Existing Script

Edit `docker/run/fs/ins/install_additional.sh` and comment out or make conditional:
- Lines 19-21: Metasploit Framework
- Lines 23-29: ExploitDB (or skip the update)
- Line 89: Wordlists
- Lines 192: Neo4j/BloodHound
- Lines 228-264: Go tools

## Long-term Optimizations

### 1. Use Lighter Base Image
Consider switching from `kalilinux/kali-rolling` to `debian:bookworm-slim` and install only needed Kali tools.

### 2. Multi-stage Builds
Build Go tools in a separate stage and copy only binaries.

### 3. Separate Containers
Move heavy tools (Metasploit, Neo4j) to separate containers that can be started on-demand.

### 4. Volume Mounts
Mount wordlists, exploit databases, and Playwright browsers as volumes instead of including in image.

## Size Comparison

| Configuration | Estimated Size | Tools Included |
|--------------|----------------|----------------|
| Current | ~25GB | All tools |
| With cleanup only | ~22GB | All tools |
| Without Metasploit/Neo4j | ~18-20GB | Most tools |
| Minimal (no heavy tools) | ~12-15GB | Core tools only |
| Optimized base + cleanup | ~8-12GB | Core tools only |

## Files Modified/Created

1. ✅ `CONTAINER_SIZE_ANALYSIS.md` - Detailed analysis
2. ✅ `docker/run/fs/ins/post_install.sh` - Enhanced cleanup
3. ✅ `docker/run/fs/ins/analyze_size.sh` - Size analysis script
4. ✅ `docker/run/fs/ins/install_additional_optimized.sh` - Optional tools version

## Next Steps

1. **Test the cleanup**: Rebuild with updated `post_install.sh`
2. **Analyze size**: Run `analyze_size.sh` to see actual breakdown
3. **Decide on tools**: Determine which heavy tools are actually needed
4. **Implement optimization**: Use optimized script or modify existing one
5. **Monitor**: Track container size after each optimization

## Example Build Commands

### Full build (current):
```bash
docker build -t adversys-delta:full .
```

### Optimized build (skip heavy tools):
```bash
docker build \
  --build-arg INSTALL_METASPLOIT=false \
  --build-arg INSTALL_NEO4J=false \
  --build-arg INSTALL_EXPLOITDB=false \
  -f docker/run/Dockerfile \
  -t adversys-delta:optimized .
```

### Minimal build (core tools only):
```bash
docker build \
  --build-arg INSTALL_METASPLOIT=false \
  --build-arg INSTALL_NEO4J=false \
  --build-arg INSTALL_EXPLOITDB=false \
  --build-arg INSTALL_WORDLISTS=false \
  --build-arg INSTALL_GO_TOOLS=false \
  -f docker/run/Dockerfile \
  -t adversys-delta:minimal .
```
