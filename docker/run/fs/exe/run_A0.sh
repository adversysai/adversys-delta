#!/bin/bash

. "/ins/setup_venv.sh" "$@"
. "/ins/copy_A0.sh" "$@"

# Ensure we're using the venv Python (activation should handle this, but be explicit)
# After activation, 'python' should point to /opt/venv-a0/bin/python
# Using full path is more reliable in supervisord context
PYTHON="${VIRTUAL_ENV:-/opt/venv-a0}/bin/python"

$PYTHON /a0/prepare.py --dockerized
# $PYTHON /a0/preload.py --dockerized # no need to run preload if it's done during container build

echo "Starting Delta..."
exec $PYTHON /a0/run_ui.py \
    --dockerized \
    --port=8002 \
    --host="0.0.0.0"
    # --code_exec_ssh_enabled=true \
    # --code_exec_ssh_addr="localhost" \
    # --code_exec_ssh_port=22 \
    # --code_exec_ssh_user="root" \
    # --code_exec_ssh_pass="toor"
