#!/bin/bash

# Stage 8: Production Deployment Script
# PDF Industrial Pipeline - Automated Deployment

set -euo pipefail

# ================================
# Configuration
# ================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="production"
COMPOSE_FILE="docker-compose.production.yml"
BACKUP_BEFORE_DEPLOY=true
RUN_HEALTH_CHECKS=true
TIMEOUT=300

# ================================
# Functions
# ================================
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy PDF Industrial Pipeline to production environment.

OPTIONS:
    -e, --environment ENV    Deployment environment (default: production)
    -f, --compose-file FILE  Docker Compose file (default: docker-compose.production.yml)
    -s, --skip-backup        Skip database backup before deployment
    -n, --no-health-checks   Skip health checks after deployment
    -t, --timeout SECONDS    Health check timeout (default: 300)
    -h, --help              Show this help message

EXAMPLES:
    $0                                    # Deploy to production
    $0 -e staging                         # Deploy to staging
    $0 -s -n                             # Deploy without backup and health checks
    $0 -f docker-compose.custom.yml      # Use custom compose file

EOF
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check if required files exist
    if [[ ! -f "$DOCKER_DIR/$COMPOSE_FILE" ]]; then
        error "Compose file not found: $DOCKER_DIR/$COMPOSE_FILE"
    fi
    
    if [[ ! -f "$DOCKER_DIR/production.env" ]]; then
        error "Environment file not found: $DOCKER_DIR/production.env"
    fi
    
    success "Prerequisites check passed"
}

backup_database() {
    if [[ "$BACKUP_BEFORE_DEPLOY" == "true" ]]; then
        log "Creating database backup..."
        
        cd "$DOCKER_DIR"
        
        # Create backup using the backup service
        if docker-compose -f "$COMPOSE_FILE" --profile backup run --rm backup; then
            success "Database backup completed"
        else
            warning "Database backup failed, continuing with deployment"
        fi
    else
        log "Skipping database backup"
    fi
}

pull_latest_images() {
    log "Pulling latest Docker images..."
    
    cd "$DOCKER_DIR"
    
    if docker-compose -f "$COMPOSE_FILE" pull; then
        success "Images pulled successfully"
    else
        error "Failed to pull Docker images"
    fi
}

deploy_services() {
    log "Deploying services..."
    
    cd "$DOCKER_DIR"
    
    # Deploy with zero-downtime strategy
    log "Starting new containers..."
    if docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans; then
        success "Services deployed successfully"
    else
        error "Failed to deploy services"
    fi
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
}

run_health_checks() {
    if [[ "$RUN_HEALTH_CHECKS" == "true" ]]; then
        log "Running health checks..."
        
        local start_time=$(date +%s)
        local end_time=$((start_time + TIMEOUT))
        
        while [[ $(date +%s) -lt $end_time ]]; do
            if curl -f -s http://localhost/health > /dev/null; then
                success "Health check passed"
                return 0
            fi
            
            log "Waiting for application to be ready..."
            sleep 10
        done
        
        error "Health check failed after ${TIMEOUT} seconds"
    else
        log "Skipping health checks"
    fi
}

cleanup_old_images() {
    log "Cleaning up old Docker images..."
    
    # Remove dangling images
    if docker image prune -f; then
        success "Old images cleaned up"
    else
        warning "Failed to clean up old images"
    fi
}

show_deployment_info() {
    log "Deployment completed successfully!"
    
    echo ""
    echo "==================================="
    echo "📊 Deployment Information"
    echo "==================================="
    echo "Environment: $ENVIRONMENT"
    echo "Compose File: $COMPOSE_FILE"
    echo "Deployment Time: $(date)"
    echo ""
    echo "🔗 Service URLs:"
    echo "  • Application: http://localhost"
    echo "  • API Docs: http://localhost/docs"
    echo "  • Grafana: http://localhost:3000"
    echo "  • Prometheus: http://localhost:9090"
    echo ""
    echo "📋 Useful Commands:"
    echo "  • View logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  • Check status: docker-compose -f $COMPOSE_FILE ps"
    echo "  • Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "==================================="
}

rollback() {
    warning "Rolling back deployment..."
    
    cd "$DOCKER_DIR"
    
    # Stop current containers
    docker-compose -f "$COMPOSE_FILE" down
    
    # You could implement more sophisticated rollback logic here
    # For example, restoring from backup, using previous image tags, etc.
    
    error "Deployment failed and rollback completed"
}

# ================================
# Main Script
# ================================
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -f|--compose-file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -s|--skip-backup)
                BACKUP_BEFORE_DEPLOY=false
                shift
                ;;
            -n|--no-health-checks)
                RUN_HEALTH_CHECKS=false
                shift
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    log "Starting deployment to $ENVIRONMENT environment..."
    
    # Set up error handling
    trap rollback ERR
    
    # Execute deployment steps
    check_prerequisites
    backup_database
    pull_latest_images
    deploy_services
    run_health_checks
    cleanup_old_images
    
    # Remove error trap on success
    trap - ERR
    
    show_deployment_info
}

# Run main function
main "$@" 