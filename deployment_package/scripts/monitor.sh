#!/bin/bash
# MindMend System Monitoring Script
# =================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="/var/log/mindmend"
PID_FILE="/var/run/mindmend-monitor.pid"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Function to run monitoring cycle
run_monitoring() {
    cd "$APP_DIR"
    python3 monitoring.py >> "$LOG_DIR/monitoring.log" 2>&1
}

# Function to check system health
check_system_health() {
    log "Checking system health..."
    
    # Check disk space
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        warn "Disk usage is ${DISK_USAGE}%"
    fi
    
    # Check memory usage
    MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$MEM_USAGE" -gt 85 ]; then
        warn "Memory usage is ${MEM_USAGE}%"
    fi
    
    # Check CPU load
    CPU_LOAD=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | xargs)
    CPU_CORES=$(nproc)
    if (( $(echo "$CPU_LOAD > $CPU_CORES" | bc -l) )); then
        warn "CPU load is high: $CPU_LOAD (cores: $CPU_CORES)"
    fi
    
    # Check Docker containers
    if command -v docker &> /dev/null; then
        CONTAINERS_DOWN=$(docker-compose -f "$APP_DIR/docker-compose.yml" ps | grep -c "Exit\|Down" || echo "0")
        if [ "$CONTAINERS_DOWN" -gt 0 ]; then
            error "$CONTAINERS_DOWN Docker containers are down"
        fi
    fi
    
    log "System health check completed"
}

# Function to check application health
check_app_health() {
    log "Checking application health..."
    
    # Check main application endpoint
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log "Main application is responding"
    else
        error "Main application is not responding"
    fi
    
    # Check Ollama service
    if curl -f -s http://localhost:11434/api/tags > /dev/null; then
        log "Ollama service is responding"
    else
        warn "Ollama service is not responding"
    fi
    
    # Check PostgreSQL
    if docker exec mindmend_postgres pg_isready -U mindmend_user -d mindmend_production > /dev/null 2>&1; then
        log "PostgreSQL is responding"
    else
        error "PostgreSQL is not responding"
    fi
    
    # Check Redis
    if docker exec mindmend_redis redis-cli ping > /dev/null 2>&1; then
        log "Redis is responding"
    else
        error "Redis is not responding"
    fi
    
    log "Application health check completed"
}

# Function to generate health report
generate_health_report() {
    log "Generating health report..."
    
    REPORT_FILE="$LOG_DIR/health_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "system": {
    "disk_usage": "$(df -h / | awk 'NR==2 {print $5}')",
    "memory_usage": "$(free | awk 'NR==2{printf "%.0f%%", $3*100/$2}')",
    "cpu_load": "$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | xargs)",
    "uptime": "$(uptime | awk '{print $3, $4}' | sed 's/,//')"
  },
  "docker": {
    "containers_running": $(docker-compose -f "$APP_DIR/docker-compose.yml" ps | grep -c "Up" || echo "0"),
    "containers_down": $(docker-compose -f "$APP_DIR/docker-compose.yml" ps | grep -c "Exit\|Down" || echo "0")
  },
  "services": {
    "main_app": "$(curl -f -s http://localhost:8000/health && echo "healthy" || echo "unhealthy")",
    "ollama": "$(curl -f -s http://localhost:11434/api/tags && echo "healthy" || echo "unhealthy")",
    "postgres": "$(docker exec mindmend_postgres pg_isready -U mindmend_user -d mindmend_production > /dev/null 2>&1 && echo "healthy" || echo "unhealthy")",
    "redis": "$(docker exec mindmend_redis redis-cli ping > /dev/null 2>&1 && echo "healthy" || echo "unhealthy")"
  }
}
EOF
    
    log "Health report saved to: $REPORT_FILE"
}

# Function to cleanup old logs and reports
cleanup_old_files() {
    log "Cleaning up old files..."
    
    # Remove log files older than 30 days
    find "$LOG_DIR" -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    
    # Remove health reports older than 7 days
    find "$LOG_DIR" -name "health_report_*.json" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Remove old Docker images
    docker image prune -f > /dev/null 2>&1 || true
    
    log "Cleanup completed"
}

# Function to backup critical data
backup_data() {
    log "Creating backup..."
    
    BACKUP_DIR="/opt/mindmend/backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    
    mkdir -p "$BACKUP_DIR"
    
    # Database backup
    docker exec mindmend_postgres pg_dump -U mindmend_user mindmend_production | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz" || {
        error "Database backup failed"
        return 1
    }
    
    # Application files backup
    tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" -C /var/www/mindmend uploads 2>/dev/null || {
        warn "Application files backup failed or no files to backup"
    }
    
    # Remove backups older than 30 days
    find "$BACKUP_DIR" -name "*.gz" -type f -mtime +30 -delete 2>/dev/null || true
    
    log "Backup completed: $DATE"
}

# Function to start monitoring daemon
start_daemon() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log "Monitoring daemon is already running (PID: $(cat "$PID_FILE"))"
        return 0
    fi
    
    log "Starting monitoring daemon..."
    
    # Start daemon
    (
        while true; do
            run_monitoring
            check_system_health
            check_app_health
            
            # Run less frequent tasks
            if [ $(($(date +%M) % 15)) -eq 0 ]; then
                generate_health_report
            fi
            
            if [ $(($(date +%H) % 6)) -eq 0 ] && [ $(date +%M) -eq 0 ]; then
                cleanup_old_files
            fi
            
            if [ $(date +%H) -eq 2 ] && [ $(date +%M) -eq 0 ]; then
                backup_data
            fi
            
            sleep 60
        done
    ) &
    
    echo $! > "$PID_FILE"
    log "Monitoring daemon started (PID: $!)"
}

# Function to stop monitoring daemon
stop_daemon() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log "Stopping monitoring daemon (PID: $(cat "$PID_FILE"))..."
        kill "$(cat "$PID_FILE")"
        rm -f "$PID_FILE"
        log "Monitoring daemon stopped"
    else
        warn "Monitoring daemon is not running"
    fi
}

# Function to restart monitoring daemon
restart_daemon() {
    stop_daemon
    sleep 2
    start_daemon
}

# Function to show daemon status
status_daemon() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log "Monitoring daemon is running (PID: $(cat "$PID_FILE"))"
    else
        warn "Monitoring daemon is not running"
    fi
}

# Main command handler
case "${1:-start}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        restart_daemon
        ;;
    status)
        status_daemon
        ;;
    check)
        check_system_health
        check_app_health
        ;;
    report)
        generate_health_report
        ;;
    backup)
        backup_data
        ;;
    cleanup)
        cleanup_old_files
        ;;
    run)
        run_monitoring
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|check|report|backup|cleanup|run}"
        echo ""
        echo "Commands:"
        echo "  start    - Start monitoring daemon"
        echo "  stop     - Stop monitoring daemon" 
        echo "  restart  - Restart monitoring daemon"
        echo "  status   - Show daemon status"
        echo "  check    - Run health checks once"
        echo "  report   - Generate health report"
        echo "  backup   - Create backup"
        echo "  cleanup  - Clean up old files"
        echo "  run      - Run monitoring cycle once"
        exit 1
        ;;
esac