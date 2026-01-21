# Container Size Analysis V2 - Target: 15GB with Metasploit

## Current State
- **Current Size**: ~25GB
- **Target Size**: ~15GB
- **Required Savings**: ~10GB
- **Constraint**: Must keep Metasploit Framework (~2-3GB)

## Detailed Size Breakdown

### Major Components (Current ~25GB)

| Component | Size | Keep? | Action |
|-----------|------|-------|--------|
| **Metasploit Framework** | ~2-3GB | ✅ **YES** | Keep as-is |
| **Kali Linux Base** | ~2-3GB | ✅ YES | Keep (hard to change) |
| **Python Packages** | ~2-3GB | ✅ YES | Optimize (save ~500MB-1GB) |
| **Neo4j/BloodHound** | ~1.5-2GB | ❌ NO | **Remove** → Save ~1.5-2GB |
| **Wordlists** | ~1-2GB | ❌ NO | **Remove** → Save ~1-2GB |
| **ExploitDB** | ~500MB-1GB | ⚠️ OPTIONAL | **Skip update** → Save ~500MB-1GB |
| **Go Tools + Compiler** | ~500MB-1GB | ❌ NO | **Remove** → Save ~500MB-1GB |
| **Playwright Browsers** | ~500MB-1GB | ✅ YES | Keep (needed for A0) |
| **Other Security Tools** | ~2-3GB | ✅ YES | Keep (core functionality) |
| **Documentation/Locales** | ~500MB-1GB | ❌ NO | **Remove** → Save ~500MB-1GB |
| **Build Tools/Cache** | ~500MB-1GB | ❌ NO | **Remove** → Save ~500MB-1GB |

### Optimization Strategy

#### High-Impact Removals (Target: ~7-9GB savings)

1. **Remove Neo4j/BloodHound** (~1.5-2GB)
   - Not essential for core functionality
   - Can be installed separately if needed
   - **Action**: Skip installation via build arg

2. **Remove Wordlists Package** (~1-2GB)
   - Large collection, most not used
   - Can mount specific wordlists as volume if needed
   - **Action**: Skip installation via build arg

3. **Skip ExploitDB Update** (~500MB-1GB)
   - Database can be updated at runtime
   - Initial install is smaller
   - **Action**: Don't run `searchsploit -u` during build

4. **Remove Go Tools** (~500MB-1GB)
   - Includes Go compiler overhead
   - Tools can be installed as pre-compiled binaries
   - **Action**: Skip Go tools installation

5. **Remove Documentation/Locales** (~500MB-1GB)
   - Already in post_install.sh but verify it's working
   - **Action**: Ensure cleanup runs properly

6. **Remove Build Tools After Build** (~500MB-1GB)
   - gcc, g++, make, etc. not needed at runtime
   - **Action**: Add to post_install.sh cleanup

#### Medium-Impact Optimizations (Target: ~1-2GB savings)

7. **Optimize Python Packages** (~500MB-1GB)
   - Review if all ML packages are needed
   - Consider lighter alternatives
   - **Action**: Review requirements, use `--no-cache-dir` (already done)

8. **Additional Cleanup** (~500MB-1GB)
   - Remove pip cache
   - Remove npm cache
   - Remove temporary build files
   - **Action**: Enhance post_install.sh

## Recommended Build Configuration

### Build Command for ~15GB Target

```bash
docker build \
  --build-arg INSTALL_METASPLOIT=true \
  --build-arg INSTALL_NEO4J=false \
  --build-arg INSTALL_EXPLOITDB=true \
  --build-arg INSTALL_WORDLISTS=false \
  --build-arg INSTALL_GO_TOOLS=false \
  -f docker/run/Dockerfile \
  -t adversys-delta:15gb .
```

**Note**: ExploitDB is set to `true` but we'll skip the update step.

## Implementation Plan

### Step 1: Update install_additional.sh to Skip ExploitDB Update

Modify the script to skip `searchsploit -u` during build (can be run at runtime).

### Step 2: Enhance post_install.sh Cleanup

Add removal of:
- Build tools (gcc, g++, make, build-essential)
- Additional caches
- Verify documentation/locale removal is working

### Step 3: Use Optimized Install Script

Switch Dockerfile to use `install_additional_optimized.sh` with build args.

### Step 4: Verify Metasploit is Kept

Ensure Metasploit installation is not affected by optimizations.

## Expected Results

| Configuration | Estimated Size | Savings |
|--------------|----------------|---------|
| Current | ~25GB | - |
| After removals | ~15-17GB | ~8-10GB |
| After cleanup | ~14-16GB | ~9-11GB |
| **Target** | **~15GB** | **~10GB** |

## Size Verification

After building, run:
```bash
docker run --rm adversys-delta:15gb bash /ins/analyze_size.sh
```

Or check size directly:
```bash
docker images adversys-delta:15gb
```

## Files to Modify

1. ✅ `docker/run/Dockerfile` - Switch to optimized script
2. ✅ `docker/run/fs/ins/install_additional_optimized.sh` - Already exists, verify it works
3. ✅ `docker/run/fs/ins/post_install.sh` - Enhance cleanup
4. ✅ `docker/run/fs/ins/install_additional.sh` - Skip ExploitDB update

## Detailed Component Analysis

### Metasploit Framework (KEEP - ~2-3GB)
- **Location**: `/usr/share/metasploit-framework`
- **Dependencies**: Ruby, PostgreSQL client libraries
- **Why Keep**: Core exploitation framework, explicitly required
- **Optimization**: None (required)

### Neo4j/BloodHound (REMOVE - ~1.5-2GB)
- **Location**: `/usr/share/neo4j`, `/var/lib/neo4j`
- **Dependencies**: Java runtime
- **Why Remove**: Not essential, can be separate container
- **Savings**: ~1.5-2GB

### Wordlists (REMOVE - ~1-2GB)
- **Location**: `/usr/share/wordlists`
- **Why Remove**: Large collection, most unused
- **Alternative**: Mount specific wordlists as volume
- **Savings**: ~1-2GB

### ExploitDB (KEEP BUT SKIP UPDATE - ~500MB-1GB)
- **Location**: `/usr/share/exploitdb`
- **Why Keep**: Useful tool
- **Optimization**: Install package but skip `searchsploit -u` during build
- **Savings**: ~500MB-1GB (by skipping update)

### Go Tools (REMOVE - ~500MB-1GB)
- **Location**: `/root/go`, `/usr/local/go`
- **Why Remove**: Compiler overhead, tools can be pre-compiled
- **Alternative**: Use pre-compiled binaries if needed
- **Savings**: ~500MB-1GB

### Python Packages (OPTIMIZE - ~2-3GB)
- **Location**: `/opt/venv-a0`
- **Large packages**: 
  - `sentence-transformers` (~500MB)
  - `unstructured[all-docs]` (~500MB)
  - `faiss-cpu` (~200MB)
  - `playwright` (~200MB with browsers)
- **Why Keep**: Core functionality
- **Optimization**: Review if all are needed, ensure `--no-cache-dir` is used
- **Savings**: ~500MB-1GB (limited)

### Build Tools (REMOVE - ~500MB-1GB)
- **Location**: Various
- **Why Remove**: Not needed at runtime
- **Savings**: ~500MB-1GB

## Risk Assessment

### Low Risk Removals
- ✅ Neo4j/BloodHound - Can be separate container
- ✅ Wordlists - Can mount as volume
- ✅ Go Tools - Can use pre-compiled binaries
- ✅ Build Tools - Not needed at runtime

### Medium Risk
- ⚠️ ExploitDB update skip - Database may be outdated, but can update at runtime

### High Risk (DO NOT REMOVE)
- ❌ Metasploit - Explicitly required
- ❌ Python packages - Core functionality
- ❌ Playwright - Needed for A0

## Next Steps

1. **Test optimized build** with recommended build args
2. **Measure actual size** after build
3. **Verify functionality** - Ensure Metasploit works
4. **Iterate** - If still >15GB, consider additional optimizations
5. **Document** - Update build instructions

## Additional Optimization Ideas (If Still >15GB)

1. **Multi-stage builds** - Build Go tools separately, copy only binaries
2. **Lighter base image** - Consider Debian slim + install only needed Kali tools
3. **Volume mounts** - Move large data files (wordlists, exploit DB) to volumes
4. **Layer optimization** - Combine RUN commands to reduce layers
5. **Remove unused Kali tools** - Audit which Kali packages are actually used
