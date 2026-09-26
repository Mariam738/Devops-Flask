#!/usr/bin/env bash
set -euo pipefail

# 1. Path to your environment file
ENV_FILE="config/app.env"

# 2. Load environment variables if config/app.env exists
if [ -f "$ENV_FILE" ]; then
    echo "-> Loading environment variables from $ENV_FILE..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Warning: $ENV_FILE not found. Using default environment variables." >&2
fi

# 3. Configuration variables (pulls from env file, or falls back to sensible defaults)
CONTAINER_NAME="postgres"  
DB_USER="${POSTGRES_USER}"         
DB_NAME="${POSTGRES_DB}"             
DB_PASSWORD="${POSTGRES_PASSWORD}"
BACKUP_DIR="./backups"

# Ensure database password exists
if [ -z "$DB_PASSWORD" ]; then
    echo "Error: POSTGRES_PASSWORD is not set in $ENV_FILE or environment." >&2
    exit 1
fi

# 4. Create backup directory on your host machine
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

echo "-> Starting PostgreSQL backup from container '$CONTAINER_NAME'..."

docker exec -e PGPASSWORD="$DB_PASSWORD" -i "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

echo "-> Backup successfully saved to: $(realpath "$BACKUP_FILE")"

exit 0