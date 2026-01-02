# Convenience wrapper: Multi-stage build that combines base + run stages
# This allows building everything in one command, but you can also build separately:
#   1. docker build -f docker/base/Dockerfile -t adversys-delta-base:latest .
#   2. docker build -f docker/run/Dockerfile -t adversys-delta:latest .
#
# Stage 1: Build the base image (mirrors docker/base/Dockerfile)
FROM docker.io/kalilinux/kali-rolling AS base

# Set locale to en_US.UTF-8 and timezone to UTC
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales tzdata
RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime
RUN echo "UTC" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV TZ=UTC

# Copy base filesystem files (from docker/base/fs/)
COPY docker/base/fs/ /

# Install base packages (split for better cache management)
RUN bash /ins/install_base_packages1.sh
RUN bash /ins/install_base_packages2.sh
RUN bash /ins/install_base_packages3.sh
RUN bash /ins/install_base_packages4.sh

# Install python after packages to ensure version overriding
RUN bash /ins/install_python.sh

# Install searxng (optional, but part of official base)
# SearXNG is used by Agent Zero's search tools for privacy-respecting web searches
RUN bash /ins/install_searxng.sh

# Configure ssh (optional, but part of official base)
RUN bash /ins/configure_ssh.sh

# After install cleanup
RUN bash /ins/after_install.sh

# Stage 2: Install Agent Zero on top of base (matches docker/run/Dockerfile structure)
FROM base AS agent-zero

# Branch argument (defaults to "local" for local development)
# Can be overridden: docker build --build-arg BRANCH=main .
ARG BRANCH=local
ENV BRANCH=$BRANCH

# Copy application code to /git/agent-zero (where install scripts expect it for "local" branch)
# This matches the original Agent Zero pattern where code is built into the image at /git/agent-zero
COPY . /git/agent-zero

# Copy docker/run filesystem files (installation scripts, etc.)
COPY docker/run/fs/ /

# Pre-installation steps (updates apt, fixes cron permissions, sets up SSH)
RUN bash /ins/pre_install.sh $BRANCH

# Install Agent Zero using official installation script
# This handles: venv setup, requirements.txt, requirements2.txt, playwright, and preload
RUN bash /ins/install_A0.sh $BRANCH

# Pre-install spaCy model for Kokoro TTS to avoid permission errors at runtime
# The kokoro library may try to install en-core-web-sm automatically, so we pre-install it
# Ensure venv is writable (should be root-owned, but verify)
RUN chmod -R u+w /opt/venv-a0 2>/dev/null || true && \
    . /opt/venv-a0/bin/activate && \
    python -m pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl || \
    echo "Warning: Failed to pre-install spaCy model, will attempt at runtime"

# Install additional software (currently empty, but part of official flow)
RUN bash /ins/install_additional.sh $BRANCH

# Cache buster: cleanup repo and re-install A0 without caching
# This ensures clean installs and speeds up builds by purging caches
ARG CACHE_DATE=none
RUN echo "cache buster $CACHE_DATE" && bash /ins/install_A02.sh $BRANCH

# Post-installation cleanup
RUN bash /ins/post_install.sh $BRANCH

# Make executable scripts executable (original Agent Zero pattern)
RUN chmod +x /exe/initialize.sh /exe/run_A0.sh /exe/run_searxng.sh /exe/run_tunnel_api.sh 2>/dev/null || true

# Capture Git information during build (if available)
ARG GIT_COMMIT
ARG GIT_BRANCH
ARG GIT_TAG
ARG BUILD_DATE

ENV GIT_COMMIT=${GIT_COMMIT:-unknown}
ENV GIT_BRANCH=${GIT_BRANCH:-unknown}
ENV GIT_TAG=${GIT_TAG:-unknown}
ENV BUILD_DATE=${BUILD_DATE:-unknown}
ENV VERSION=${GIT_TAG:-dev}

# Adversys Added this: Ensure Playwright browsers are installed during build
# The install_playwright.sh script is already called by install_A0.sh, but we verify
# it completed successfully and ensure browsers are in the expected location
# This prevents runtime downloads when the container starts
RUN . /opt/venv-a0/bin/activate && \
    export PLAYWRIGHT_BROWSERS_PATH=/a0/tmp/playwright && \
    if [ ! -d "/a0/tmp/playwright" ] || [ -z "$(ls -A /a0/tmp/playwright 2>/dev/null)" ]; then \
        echo "Playwright browsers not found, running install script..." && \
        bash /ins/install_playwright.sh "$BRANCH"; \
    else \
        echo "Playwright browsers already installed at /a0/tmp/playwright"; \
    fi && \
    # Ensure Playwright binaries have execute permissions (important when /a0 is mounted as volume)
    find /a0/tmp/playwright -type f -name "headless_shell" -o -name "chrome" -o -name "chromium" | xargs chmod +x 2>/dev/null || true

# Expose ports (original Agent Zero pattern: 22 for SSH, 80 for UI, 9000-9009 for tunnel API)
# We use 8002 for UI instead of 80, but keep other ports for compatibility
EXPOSE 22 80 8002 9000-9009

# Set default environment variables
ENV WEB_UI_PORT=8002
ENV WEB_UI_HOST=0.0.0.0
ENV PLAYWRIGHT_BROWSERS_PATH=/a0/tmp/playwright

# Initialize runtime and switch to supervisord (original Agent Zero pattern)
# initialize.sh copies /per/* to /, sets up environment, and starts supervisord
# BRANCH is set as ENV from ARG, so it's available at runtime
# Use exec form to match original Agent Zero pattern: ["/exe/initialize.sh", "$BRANCH"]
# The script will detect literal "$BRANCH" and read from ENV variable instead
CMD ["/exe/initialize.sh", "$BRANCH"]
