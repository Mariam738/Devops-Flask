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

# 4. Determine which backup file to restore
# If a file path is passed as an argument, use it. Otherwise, find the latest .sql file in ./backups/
if [ $# -eq 1 ]; then
    RESTORE_FILE="$1"
else
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/*.sql 2>/dev/null)" ]; then
        echo "Error: No backup files found in $BACKUP_DIR and none specified." >&2
        echo "Usage: $0 [path/to/backup.sql]" >&2
        exit 1
    fi
    RESTORE_FILE=$(ls -t "$BACKUP_DIR"/*.sql | head -n 1)
fi

if [ ! -f "$RESTORE_FILE" ]; then
    echo "Error: Backup file '$RESTORE_FILE' does not exist." >&2
    exit 1
fi

echo "-> Restoring database '$DB_NAME' from backup file: $RESTORE_FILE"

# 5. Drop and recreate the database to clear out any default rows created by the fresh container/volume
docker exec -e PGPASSWORD="$DB_PASSWORD" "$CONTAINER_NAME" psql -U "$DB_USER" -d "postgres" -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"
docker exec -e PGPASSWORD="$DB_PASSWORD" "$CONTAINER_NAME" psql -U "$DB_USER" -d "postgres" -c "CREATE DATABASE \"$DB_NAME\";"

# 6. Execute psql inside the container and pipe the backup file into it
docker exec -i -e PGPASSWORD="$DB_PASSWORD" "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$RESTORE_FILE"

echo "-> Backup successfully restored"

exit 0
