#!/bin/bash
# MindMend Deployment Status Checker
# =================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

fail() {
    echo -e "${RED}❌ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo "🔍 MindMend Deployment Status Check"
echo "=================================="

# Check if running as mindmend user
if [[ $USER != "mindmend" ]]; then
    warn "Should be run as 'mindmend' user for full checks"
fi

# Check if in correct directory
if [[ ! -f "docker-compose.yml" ]]; then
    fail "Not in MindMend directory or docker-compose.yml missing"
    exit 1
fi

echo ""
echo "📋 System Requirements Check"
echo "----------------------------"

# Check Docker
if command -v docker &> /dev/null; then
    pass "Docker installed"
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    info "Version: $DOCKER_VERSION"
else
    fail "Docker not installed"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    pass "Docker Compose installed"
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    info "Version: $COMPOSE_VERSION"
else
    fail "Docker Compose not installed"
fi

# Check system resources
MEMORY_TOTAL=$(free -m | awk 'NR==2{printf "%d", $2}')
DISK_AVAILABLE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
CPU_CORES=$(nproc)

if [[ $MEMORY_TOTAL -ge 8000 ]]; then
    pass "Memory: ${MEMORY_TOTAL}MB (sufficient)"
else
    warn "Memory: ${MEMORY_TOTAL}MB (recommended: 8GB+)"
fi

if [[ $DISK_AVAILABLE -ge 50 ]]; then
    pass "Disk space: ${DISK_AVAILABLE}GB available"
else
    fail "Disk space: ${DISK_AVAILABLE}GB (need at least 50GB)"
fi

pass "CPU cores: $CPU_CORES"

echo ""
echo "📁 Configuration Files Check"
echo "----------------------------"

# Check environment file
if [[ -f ".env.production" ]]; then
    pass "Environment file exists"
    
    # Check critical variables
    if grep -q "OPENAI_API_KEY=sk-your-openai-api-key-here" .env.production; then
        fail "OpenAI API key not updated (still has placeholder)"
    else
        pass "OpenAI API key configured"
    fi
    
    if grep -q "MAIL_PASSWORD=your-gmail-app-password-here" .env.production; then
        warn "Email password not configured (alerts won't work)"
    else
        pass "Email configured"
    fi
    
else
    fail "Environment file (.env.production) missing"
fi

# Check Docker files
if [[ -f "Dockerfile" ]]; then
    pass "Dockerfile exists"
else
    fail "Dockerfile missing"
fi

if [[ -f "docker-compose.yml" ]]; then
    pass "Docker Compose file exists"
else
    fail "Docker Compose file missing"
fi

echo ""
echo "🐳 Docker Services Status"
echo "-------------------------"

# Check if containers are running
if docker-compose ps &> /dev/null; then
    CONTAINERS_UP=$(docker-compose ps | grep "Up" | wc -l)
    CONTAINERS_TOTAL=$(docker-compose ps | grep -E "(Up|Exit|Restarting)" | wc -l)
    
    if [[ $CONTAINERS_UP -eq $CONTAINERS_TOTAL ]] && [[ $CONTAINERS_UP -gt 0 ]]; then
        pass "All Docker containers running ($CONTAINERS_UP/$CONTAINERS_TOTAL)"
    elif [[ $CONTAINERS_UP -gt 0 ]]; then
        warn "Some containers running ($CONTAINERS_UP/$CONTAINERS_TOTAL)"
        docker-compose ps | grep -v "Up" | grep -E "(Exit|Restarting)"
    else
        fail "No containers running"
        echo "Run: docker-compose up -d"
    fi
else
    fail "Docker Compose not running or configured"
fi

echo ""
echo "🌐 Service Health Checks"
echo "------------------------"

# Check main application
if curl -f -s http://localhost:8000/health > /dev/null; then
    pass "Main application responding"
else
    fail "Main application not responding on http://localhost:8000/health"
fi

# Check Ollama
if curl -f -s http://localhost:11434/api/tags > /dev/null; then
    pass "Ollama service responding"
    MODEL_COUNT=$(curl -s http://localhost:11434/api/tags | grep -o '"name"' | wc -l)
    if [[ $MODEL_COUNT -gt 0 ]]; then
        pass "AI models installed ($MODEL_COUNT models)"
    else
        warn "No AI models found - they may still be downloading"
    fi
else
    fail "Ollama service not responding on http://localhost:11434"
fi

# Check PostgreSQL
if docker exec mindmend_postgres pg_isready -U mindmend_user -d mindmend_production > /dev/null 2>&1; then
    pass "PostgreSQL database responding"
else
    fail "PostgreSQL database not responding"
fi

# Check Redis
if docker exec mindmend_redis redis-cli ping > /dev/null 2>&1; then
    pass "Redis cache responding"
else
    fail "Redis cache not responding"
fi

# Check Nginx
if docker exec mindmend_nginx nginx -t > /dev/null 2>&1; then
    pass "Nginx configuration valid"
else
    fail "Nginx configuration invalid"
fi

echo ""
echo "🔒 Security & SSL Status"
echo "------------------------"

# Check SSL certificates
if [[ -f "/opt/mindmend/ssl/mindmend.xyz.crt" ]]; then
    pass "SSL certificate exists"
    
    # Check certificate expiry
    CERT_DAYS=$(openssl x509 -in /opt/mindmend/ssl/mindmend.xyz.crt -noout -enddate | cut -d= -f2 | xargs -I {} date -d "{}" +%s)
    CURRENT_DAYS=$(date +%s)
    DAYS_LEFT=$(( ($CERT_DAYS - $CURRENT_DAYS) / 86400 ))
    
    if [[ $DAYS_LEFT -gt 30 ]]; then
        pass "SSL certificate valid for $DAYS_LEFT days"
    elif [[ $DAYS_LEFT -gt 0 ]]; then
        warn "SSL certificate expires in $DAYS_LEFT days"
    else
        fail "SSL certificate expired"
    fi
else
    fail "SSL certificate not found"
fi

# Check firewall
if sudo ufw status | grep -q "Status: active"; then
    pass "Firewall active"
else
    warn "Firewall not active"
fi

# Check fail2ban
if systemctl is-active --quiet fail2ban; then
    pass "Fail2ban active"
else
    warn "Fail2ban not active"
fi

echo ""
echo "📊 System Performance"
echo "--------------------"

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
if (( $(echo "$CPU_USAGE < 80" | bc -l) )); then
    pass "CPU usage: ${CPU_USAGE}%"
else
    warn "High CPU usage: ${CPU_USAGE}%"
fi

# Memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$MEMORY_USAGE < 85" | bc -l) )); then
    pass "Memory usage: ${MEMORY_USAGE}%"
else
    warn "High memory usage: ${MEMORY_USAGE}%"
fi

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [[ $DISK_USAGE -lt 85 ]]; then
    pass "Disk usage: ${DISK_USAGE}%"
else
    warn "High disk usage: ${DISK_USAGE}%"
fi

echo ""
echo "🔗 External Connectivity"
echo "------------------------"

# Check DNS resolution
if nslookup mindmend.xyz > /dev/null 2>&1; then
    pass "DNS resolution working for mindmend.xyz"
else
    fail "DNS resolution failed for mindmend.xyz"
fi

if nslookup admin.mindmend.xyz > /dev/null 2>&1; then
    pass "DNS resolution working for admin.mindmend.xyz"
else
    fail "DNS resolution failed for admin.mindmend.xyz"
fi

# Check external HTTPS (if accessible)
EXTERNAL_IP=$(curl -s https://ipinfo.io/ip 2>/dev/null || echo "unknown")
info "Server external IP: $EXTERNAL_IP"

echo ""
echo "📋 Deployment Summary"
echo "--------------------"

# Count issues
ISSUES=0

# Critical checks
if ! command -v docker &> /dev/null; then ((ISSUES++)); fi
if ! command -v docker-compose &> /dev/null; then ((ISSUES++)); fi
if [[ ! -f ".env.production" ]]; then ((ISSUES++)); fi
if ! docker-compose ps | grep -q "Up"; then ((ISSUES++)); fi

if [[ $ISSUES -eq 0 ]]; then
    echo ""
    pass "✨ MindMend deployment looks healthy!"
    echo ""
    info "🌐 Your platform should be accessible at:"
    info "   Main site: https://mindmend.xyz"
    info "   Admin panel: https://admin.mindmend.xyz"
    echo ""
    info "🔑 Admin credentials (change after first login):"
    info "   Username: mindmend_admin"
    info "   Password: MindMend2024!SecureAdmin"
    echo ""
    info "📝 Next steps:"
    info "   1. Test the main website"
    info "   2. Log into admin panel and change password"
    info "   3. Set up 2FA for admin account"
    info "   4. Configure proper SSL certificates"
    info "   5. Update API keys if not done already"
else
    echo ""
    fail "❗ Found $ISSUES critical issues that need attention"
    echo ""
    info "📚 For troubleshooting help:"
    info "   - Check logs: docker-compose logs"
    info "   - Review: deployment_guide_production.md" 
    info "   - Quick deploy: QUICK_DEPLOY.md"
fi

echo ""