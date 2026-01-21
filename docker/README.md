# Docker Build Instructions

This folder contains the Docker build configurations for Adversys Delta. The build is split into two stages: **base** and **run**.

## Directory Structure

```
docker/
├── base/                    # Base image (Kali Linux + dependencies)
│   ├── Dockerfile
│   └── fs/                  # Files copied to container filesystem
│       ├── etc/             # Configuration files (searxng)
│       └── ins/             # Installation scripts
│
├── run/                     # Runtime image (application + tools)
│   ├── Dockerfile
│   └── fs/                  # Files copied to container filesystem
│       ├── etc/             # Config files (nginx, supervisor, searxng)
│       ├── exe/             # Executable/startup scripts
│       ├── ins/             # Installation scripts
│       └── per/             # Persistent user files (.bashrc, .profile)
│
└── README.md
```

## Build Context

**Important:** All docker builds must be run from the **project root directory** (`adversys-delta`), not from inside the `docker/` folder. This is because the Dockerfiles reference paths relative to the project root.

## Building the Images

### Step 1: Build the Base Image

The base image contains Kali Linux with essential packages, Python, and SearXNG.

```powershell
# From the project root (adversys-delta)
docker build -f docker/base/Dockerfile -t adversys-delta-base:latest .
```

### Step 2: Build the Run Image

The run image extends the base image with the application code and additional tools.

```powershell
# From the project root (adversys-delta)
docker build -f docker/run/Dockerfile -t adversys-delta:latest .
```

## Build Arguments

The run image supports several build arguments to customize the installation:

| Argument               | Default                                          | Description                                                   |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------- |
| `BRANCH`             | `local`                                        | Branch to use (`local` for local dev, or a git branch name) |
| `ENVIRONMENT`        | `development`                                  | Environment type (`development` or `production`)          |
| `GITHUB_REPO_URL`    | `https://github.com/adversysai/adversys-delta` | Repository URL for cloning                                    |
| `INSTALL_METASPLOIT` | `true`                                         | Install Metasploit Framework                                  |
| `INSTALL_NEO4J`      | `false`                                        | Install Neo4j database                                        |
| `INSTALL_EXPLOITDB`  | `true`                                         | Install ExploitDB                                             |
| `INSTALL_WORDLISTS`  | `false`                                        | Install wordlists                                             |
| `INSTALL_GO_TOOLS`   | `false`                                        | Install Go-based tools                                        |
| `CACHE_DATE`         | `none`                                         | Cache buster for forcing rebuilds                             |

### Example: Production Build with Custom Options

```powershell
docker build -f docker/run/Dockerfile `
  --build-arg BRANCH=main `
  --build-arg GITHUB_REPO_URL='https://github.com/adversysai/adversys-delta' `
  --build-arg ENVIRONMENT=production `
  --build-arg INSTALL_METASPLOIT=true `
  --build-arg INSTALL_NEO4J=true `
  --build-arg INSTALL_EXPLOITDB=true `
  --build-arg INSTALL_WORDLISTS=true `
  --build-arg INSTALL_GO_TOOLS=true `
  -t adversys-delta:production .
```

### Example: Minimal Build (Smaller Image Size)

```powershell
docker build -f docker/run/Dockerfile `
  --build-arg INSTALL_METASPLOIT=false `
  --build-arg INSTALL_EXPLOITDB=false `
  -t adversys-delta:minimal .
```

## Exposed Ports

The run image exposes the following ports:

| Port      | Service              |
| --------- | -------------------- |
| 22        | SSH                  |
| 80        | HTTP (nginx)         |
| 9000-9009 | Application services |

## Common Issues

### "path not found" Error

If you see an error like:

```
ERROR: failed to compute cache key: "/docker/base/fs": not found
```

This means you're running the build from the wrong directory. Make sure you're in the **project root** (`adversys-delta`), not inside `docker/` or `docker/base/`.

**Wrong:**

```powershell
cd docker/base
docker build .
```

**Correct:**

```powershell
cd C:\path\to\adversys-delta
docker build -f docker/base/Dockerfile .
```

## Filesystem Layout

### Base Image (`/ins/` scripts)

- `install_base_packages1-4.sh` - Install system packages (split for caching)
- `install_python.sh` - Install Python
- `install_searxng.sh` - Install SearXNG search engine
- `configure_ssh.sh` - Configure SSH server
- `after_install.sh` - Post-installation cleanup

### Run Image (`/ins/` scripts)

- `pre_install.sh` - Pre-installation setup
- `install_A0.sh` - Install main application
- `install_additional_optimized.sh` - Install optional tools (Metasploit, etc.)
- `install_A02.sh` - Secondary installation (no cache)
- `post_install.sh` - Post-installation cleanup

### Run Image (`/exe/` scripts)

- `initialize.sh` - Container entrypoint
- `run_A0.sh` - Start the main application
- `run_searxng.sh` - Start SearXNG
- `run_tunnel_api.sh` - Start tunnel API
- `supervisor_event_listener.py` - Supervisor event handling
