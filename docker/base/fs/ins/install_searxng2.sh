#!/bin/bash
set -e

echo "====================SEARXNG2 START===================="


# clone SearXNG repo
git clone "https://github.com/searxng/searxng" \
                   "/usr/local/searxng/searxng-src"

echo "====================SEARXNG2 VENV===================="

# create virtualenv:
python3.13 -m venv "/usr/local/searxng/searx-pyenv"

# make it default
echo ". /usr/local/searxng/searx-pyenv/bin/activate" \
                   >>  "/usr/local/searxng/.profile"

# activate venv
source "/usr/local/searxng/searx-pyenv/bin/activate"

echo "====================SEARXNG2 INST===================="

# update pip's boilerplate
pip install --no-cache-dir -U pip setuptools wheel pyyaml lxml

# jump to SearXNG's working tree
cd "/usr/local/searxng/searxng-src"

# Install msgspec first (required by SearXNG's build process)
# SearXNG's pyproject.toml/setup.py imports msgspec during metadata generation
# Since we use --no-build-isolation, we must install it manually
pip install --no-cache-dir msgspec

# Install SearXNG into virtualenv (editable mode)
# --no-build-isolation is used to avoid installing build deps in isolated environment
# but we've already installed msgspec above
pip install --no-cache-dir --use-pep517 --no-build-isolation -e .

# cleanup cache
pip cache purge

echo "====================SEARXNG2 END===================="