# Multi-stage build following official Agent Zero pattern
# Stage 1: Build the base image (mirrors docker/base/Dockerfile)
# Note: Docker doesn't support referencing another Dockerfile in FROM,
# so we replicate the base build steps here. This matches docker/base/Dockerfile exactly.
#
# MODIFIED: Added branding patch step to rebrand Agent Zero to Delta during build
# See scripts/apply-branding.sh for details
FROM docker.io/kalilinux/kali-rolling AS base

# Set locale to en_US.UTF-8 and timezone to UTC
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales tzdata
RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata
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
# SearXNG is used by Agent Zero's search tools, but installation has dependency issues with Python 3.13
# We'll skip it for now - Agent Zero can fall back to DuckDuckGo or other search engines
# If needed later, we can fix the installation or use a pre-built SearXNG image
# RUN bash /ins/install_searxng.sh

# Configure ssh (optional, but part of official base)
RUN bash /ins/configure_ssh.sh

# After install cleanup
RUN bash /ins/after_install.sh

# Stage 2: Install Agent Zero on top of base
FROM base AS agent-zero

# Set BRANCH to "local" to use local files instead of cloning from GitHub
ARG BRANCH=local
ENV BRANCH=$BRANCH

# Copy application code to /git/agent-zero (where install scripts expect it for "local" branch)
# Also create symlinks: /app for our docker-compose volume mount, /a0 for official scripts
COPY . /git/agent-zero

# Remove /app if it exists as a directory, then create symlink
# /app is used as the working directory and should point to /git/agent-zero
# /a0 will be created as a real directory later for data storage (not source code)
RUN rm -rf /app && \
    ln -sf /git/agent-zero /app

WORKDIR /app

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

# Post-installation cleanup
RUN bash /ins/post_install.sh $BRANCH

# Copy entrypoint and set permissions
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    test -f /entrypoint.sh && \
    head -1 /entrypoint.sh | grep -q '^#!/bin/sh'

# Configure Git safe directory to allow access to mounted repository
RUN git config --global --add safe.directory /app && \
    git config --global --add safe.directory /git/agent-zero

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

# Create directories for Agent Zero data
# Using root user (original Agent Zero pattern) for simplicity
# Create /a0 as a real directory (not symlink) for data storage
RUN mkdir -p /var/lib/adversys/agent-zero/{memory,knowledge,logs,tmp,usr} && \
    mkdir -p /a0/{memory,knowledge,logs,tmp,usr} && \
    mkdir -p /app/tmp/{playwright,downloads}

# Expose port 8002 (Adversys service port pattern)
EXPOSE 8002

# Set default environment variables
ENV WEB_UI_PORT=8002
ENV WEB_UI_HOST=0.0.0.0
ENV PLAYWRIGHT_BROWSERS_PATH=/app/tmp/playwright

# Run the application through the entrypoint (handles permissions)
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "run_ui.py", "--port=8002", "--host=0.0.0.0"]
