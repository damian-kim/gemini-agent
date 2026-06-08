#!/bin/bash
set -e

# Use AGENT_ROOT or default to /data/agent-os
ROOT_DIR="${AGENT_ROOT:-/data/agent-os}"
BACKUP_DIR="${ROOT_DIR}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/agent-os-backup-${TIMESTAMP}.tar.gz"

echo "Starting Gemini Agent OS backup from ${ROOT_DIR}..."
mkdir -p "${BACKUP_DIR}"

# Archive code, config, and data layers (excluding docker caches, python caches, logs, and backups)
tar --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='runtime/logs/*' \
    --exclude='backups' \
    -czf "${BACKUP_FILE}" \
    -C "${ROOT_DIR}" .

echo "Backup created successfully at: ${BACKUP_FILE}"
