#!/bin/bash

# Stage 8: Database Backup Script
# PDF Industrial Pipeline - Automated Backup

set -euo pipefail

# ================================
# Configuration
# ================================
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="${POSTGRES_DB:-pdf_pipeline}"
DB_USER="${POSTGRES_USER:-pipeline_user}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

# Retention settings
DAILY_RETENTION=7    # Keep daily backups for 7 days
WEEKLY_RETENTION=4   # Keep weekly backups for 4 weeks
MONTHLY_RETENTION=12 # Keep monthly backups for 12 months

# ================================
# Functions
# ================================
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

create_backup() {
    local backup_file="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql"
    local compressed_file="${backup_file}.gz"
    
    log "Creating database backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Create database dump
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose --clean --no-owner --no-privileges > "$backup_file"; then
        
        # Compress the backup
        if gzip "$backup_file"; then
            log "Backup created successfully: $compressed_file"
            
            # Create symlinks for latest backup
            ln -sf "$(basename "$compressed_file")" "$BACKUP_DIR/latest_backup.sql.gz"
            
            # Create daily/weekly/monthly symlinks
            create_retention_links "$compressed_file"
            
            return 0
        else
            log "ERROR: Failed to compress backup"
            rm -f "$backup_file"
            return 1
        fi
    else
        log "ERROR: Failed to create database backup"
        return 1
    fi
}

create_retention_links() {
    local backup_file="$1"
    local basename_file=$(basename "$backup_file")
    
    # Daily backup link
    ln -sf "$basename_file" "$BACKUP_DIR/daily_backup_$(date +%A).sql.gz"
    
    # Weekly backup (every Sunday)
    if [[ $(date +%u) -eq 7 ]]; then
        ln -sf "$basename_file" "$BACKUP_DIR/weekly_backup_$(date +%V).sql.gz"
    fi
    
    # Monthly backup (first day of month)
    if [[ $(date +%d) -eq 01 ]]; then
        ln -sf "$basename_file" "$BACKUP_DIR/monthly_backup_$(date +%m).sql.gz"
    fi
}

cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    # Remove backups older than daily retention
    find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz" -type f -mtime +$DAILY_RETENTION -delete
    
    # Clean up broken symlinks
    find "$BACKUP_DIR" -type l ! -exec test -e {} \; -delete
    
    log "Cleanup completed"
}

verify_backup() {
    local backup_file="$BACKUP_DIR/latest_backup.sql.gz"
    
    if [[ -f "$backup_file" ]]; then
        local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
        
        if [[ $size -gt 1024 ]]; then  # At least 1KB
            log "Backup verification passed (size: ${size} bytes)"
            return 0
        else
            log "ERROR: Backup file is too small (size: ${size} bytes)"
            return 1
        fi
    else
        log "ERROR: Backup file not found"
        return 1
    fi
}

show_backup_info() {
    log "Backup process completed successfully!"
    
    echo ""
    echo "==================================="
    echo "📊 Backup Information"
    echo "==================================="
    echo "Database: $DB_NAME"
    echo "Timestamp: $TIMESTAMP"
    echo "Backup Directory: $BACKUP_DIR"
    echo ""
    
    if [[ -d "$BACKUP_DIR" ]]; then
        echo "📁 Available Backups:"
        ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "No backup files found"
        echo ""
        
        echo "🔗 Retention Links:"
        ls -la "$BACKUP_DIR" | grep "^l" || echo "No retention links found"
    fi
    
    echo "==================================="
}

# ================================
# Main Script
# ================================
main() {
    log "Starting backup process for database: $DB_NAME"
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
        log "Database not ready, waiting..."
        sleep 5
    done
    
    # Create backup
    if create_backup; then
        verify_backup
        cleanup_old_backups
        show_backup_info
    else
        log "ERROR: Backup process failed"
        exit 1
    fi
}

# Run main function
main "$@" 