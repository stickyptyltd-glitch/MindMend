#!/bin/bash
# MindMend Production Deployment Script
# =====================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="mindmend"
DOMAIN="mindmend.xyz"
ADMIN_DOMAIN="admin.mindmend.xyz"
BACKUP_DIR="/opt/mindmend/backups"
LOG_FILE="/var/log/mindmend/deploy.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        error "Git is not installed. Please install Git first."
    fi
    
    # Check available disk space (minimum 10GB)
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $AVAILABLE_SPACE -lt 10 ]]; then
        error "Insufficient disk space. At least 10GB required, only ${AVAILABLE_SPACE}GB available."
    fi
    
    log "System requirements check passed"
}

# Setup directories
setup_directories() {
    log "Setting up directories..."
    
    sudo mkdir -p /var/log/mindmend
    sudo mkdir -p /var/www/mindmend/uploads
    sudo mkdir -p /opt/mindmend/ssl
    sudo mkdir -p /opt/mindmend/backups
    
    # Set proper permissions
    sudo chown -R $USER:$USER /var/log/mindmend
    sudo chown -R $USER:$USER /var/www/mindmend
    sudo chown -R $USER:$USER /opt/mindmend
    
    log "Directories setup completed"
}

# Generate SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    if [[ ! -f "/opt/mindmend/ssl/${DOMAIN}.crt" ]]; then
        info "Generating self-signed SSL certificate for development..."
        sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "/opt/mindmend/ssl/${DOMAIN}.key" \
            -out "/opt/mindmend/ssl/${DOMAIN}.crt" \
            -subj "/C=AU/ST=Victoria/L=Melbourne/O=Sticky Pty Ltd/CN=${DOMAIN}"
        
        # Generate admin domain certificate
        sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "/opt/mindmend/ssl/${ADMIN_DOMAIN}.key" \
            -out "/opt/mindmend/ssl/${ADMIN_DOMAIN}.crt" \
            -subj "/C=AU/ST=Victoria/L=Melbourne/O=Sticky Pty Ltd/CN=${ADMIN_DOMAIN}"
    fi
    
    warn "For production, replace self-signed certificates with proper SSL certificates from Let's Encrypt or your SSL provider"
    log "SSL setup completed"
}

# Setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    if [[ ! -f ".env.production" ]]; then
        error ".env.production file not found. Please create it with proper configuration."
    fi
    
    # Generate random passwords if not set
    if ! grep -q "POSTGRES_PASSWORD=" .env.production; then
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> .env.production
    fi
    
    if ! grep -q "REDIS_PASSWORD=" .env.production; then
        REDIS_PASSWORD=$(openssl rand -base64 32)
        echo "REDIS_PASSWORD=${REDIS_PASSWORD}" >> .env.production
    fi
    
    log "Environment variables setup completed"
}

# Build and start services
deploy_services() {
    log "Building and deploying services..."
    
    # Stop existing services
    docker-compose down || true
    
    # Build new images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    info "Waiting for services to start..."
    sleep 30
    
    # Check service health
    if ! docker-compose ps | grep -q "Up"; then
        error "Some services failed to start. Check logs with: docker-compose logs"
    fi
    
    log "Services deployed successfully"
}

# Install Ollama models
install_ai_models() {
    log "Installing AI models..."
    
    # Wait for Ollama to be ready
    info "Waiting for Ollama service..."
    until docker exec mindmend_ollama ollama list &>/dev/null; do
        sleep 5
    done
    
    # Install essential models
    info "Installing llama2 model..."
    docker exec mindmend_ollama ollama pull llama2:7b
    
    info "Installing codellama model..."
    docker exec mindmend_ollama ollama pull codellama:7b
    
    info "Installing mistral model for therapy..."
    docker exec mindmend_ollama ollama pull mistral:7b
    
    log "AI models installation completed"
}

# Setup backup system
setup_backup() {
    log "Setting up backup system..."
    
    # Create backup script
    cat > /tmp/backup_mindmend.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/mindmend/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker exec mindmend_postgres pg_dump -U mindmend_user mindmend_production | gzip > "${BACKUP_DIR}/db_backup_${DATE}.sql.gz"

# Application files backup
tar -czf "${BACKUP_DIR}/app_backup_${DATE}.tar.gz" -C /var/www/mindmend uploads

# Keep only last 30 days of backups
find "${BACKUP_DIR}" -name "*.gz" -type f -mtime +30 -delete

echo "Backup completed: ${DATE}"
EOF
    
    sudo mv /tmp/backup_mindmend.sh /opt/mindmend/backup_mindmend.sh
    sudo chmod +x /opt/mindmend/backup_mindmend.sh
    
    # Setup cron job for daily backups
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/mindmend/backup_mindmend.sh >> /var/log/mindmend/backup.log 2>&1") | crontab -
    
    log "Backup system setup completed"
}

# Configure firewall
setup_firewall() {
    log "Configuring firewall..."
    
    # Enable UFW if not already enabled
    if ! sudo ufw status | grep -q "Status: active"; then
        sudo ufw --force enable
    fi
    
    # Allow necessary ports
    sudo ufw allow 22/tcp   # SSH
    sudo ufw allow 80/tcp   # HTTP
    sudo ufw allow 443/tcp  # HTTPS
    
    # Deny all other incoming traffic by default
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    log "Firewall configuration completed"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Check if main application is responding
    if curl -f -s http://localhost/health > /dev/null; then
        log "Application health check passed"
    else
        error "Application health check failed"
    fi
    
    # Check database connection
    if docker exec mindmend_postgres pg_isready -U mindmend_user -d mindmend_production > /dev/null; then
        log "Database health check passed"
    else
        error "Database health check failed"
    fi
    
    log "All health checks passed"
}

# Main deployment process
main() {
    log "Starting MindMend deployment..."
    
    check_root
    check_requirements
    setup_directories
    setup_ssl
    setup_environment
    deploy_services
    install_ai_models
    setup_backup
    setup_firewall
    health_check
    
    log "Deployment completed successfully!"
    info "Application is now available at: https://${DOMAIN}"
    info "Admin panel is available at: https://${ADMIN_DOMAIN}"
    warn "Please update DNS records to point to this server"
    warn "Replace self-signed SSL certificates with proper certificates for production"
}

# Run main function
main "$@"