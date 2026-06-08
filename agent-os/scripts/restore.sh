#!/bin/bash
# restore.sh - Restore backup with explicit confirmation
set -e

# Use AGENT_ROOT or default to /data/agent-os
ROOT_DIR="${AGENT_ROOT:-/data/agent-os}"

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/backup.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "WARNING: This will overwrite files in the current workspace at ${ROOT_DIR}!"
read -p "Type 'proceed' to confirm restore of ${BACKUP_FILE}: " confirmation

if [ "${confirmation}" != "proceed" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Restoring backup..."
tar -xzf "${BACKUP_FILE}" -C "${ROOT_DIR}"

echo "Restore complete."
