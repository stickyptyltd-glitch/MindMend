#!/bin/bash
# MindMend Server Initial Setup Script
# ====================================

set -e

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
    exit 1
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root (use sudo)"
fi

log "Starting server setup for MindMend..."

# Update system
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install essential packages
log "Installing essential packages..."
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    htop \
    nano \
    cron \
    logrotate \
    fail2ban

# Install Docker
log "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install Docker Compose (standalone)
log "Installing Docker Compose..."
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create mindmend user
log "Creating mindmend user..."
if ! id "mindmend" &>/dev/null; then
    useradd -m -s /bin/bash -G docker mindmend
    echo "mindmend ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/mindmend
fi

# Configure Docker for mindmend user
usermod -aG docker mindmend

# Install NVIDIA Docker (for GPU support with Ollama)
log "Installing NVIDIA Docker support..."
if lspci | grep -i nvidia > /dev/null; then
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    apt-get update
    apt-get install -y nvidia-container-toolkit
    systemctl restart docker
    log "NVIDIA Docker support installed"
else
    warn "No NVIDIA GPU detected. Ollama will run on CPU."
fi

# Configure swap (if needed)
log "Configuring swap..."
if ! swapon --show | grep -q "/swapfile"; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
fi

# Configure log rotation
log "Setting up log rotation..."
cat > /etc/logrotate.d/mindmend << 'EOF'
/var/log/mindmend/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 mindmend mindmend
    postrotate
        docker-compose -f /home/mindmend/MindMend/docker-compose.yml restart app
    endscript
}
EOF

# Setup fail2ban for security
log "Configuring fail2ban..."
cat > /etc/fail2ban/jail.d/mindmend.conf << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/mindmend/access.log
maxretry = 6

[nginx-dos]
enabled = true
filter = nginx-dos
port = http,https
logpath = /var/log/mindmend/access.log
maxretry = 30
findtime = 60
bantime = 1800
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Configure basic firewall
log "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Setup system monitoring
log "Installing system monitoring..."
cat > /usr/local/bin/mindmend-monitor.sh << 'EOF'
#!/bin/bash
# MindMend System Monitor

LOG_FILE="/var/log/mindmend/system-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo "[$DATE] WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi

# Check Docker containers
CONTAINERS_DOWN=$(docker-compose -f /home/mindmend/MindMend/docker-compose.yml ps | grep -c "Exit\|Down" || echo "0")
if [ $CONTAINERS_DOWN -gt 0 ]; then
    echo "[$DATE] ERROR: $CONTAINERS_DOWN containers are down" >> $LOG_FILE
fi

# Check SSL certificate expiry
if openssl x509 -checkend 604800 -noout -in /opt/mindmend/ssl/mindmend.xyz.crt; then
    echo "[$DATE] SSL certificate expires within 7 days" >> $LOG_FILE
fi
EOF

chmod +x /usr/local/bin/mindmend-monitor.sh

# Setup cron job for monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/mindmend-monitor.sh") | crontab -

# Setup automatic security updates
log "Configuring automatic security updates..."
apt-get install -y unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

echo 'APT::Periodic::Update-Package-Lists "1";' > /etc/apt/apt.conf.d/20auto-upgrades
echo 'APT::Periodic::Unattended-Upgrade "1";' >> /etc/apt/apt.conf.d/20auto-upgrades

# Set system timezone
log "Setting timezone to Melbourne/Australia..."
timedatectl set-timezone Australia/Melbourne

# Configure system limits
log "Optimizing system limits..."
cat >> /etc/security/limits.conf << 'EOF'
mindmend soft nofile 65536
mindmend hard nofile 65536
mindmend soft nproc 4096
mindmend hard nproc 4096
EOF

# Enable and start Docker
systemctl enable docker
systemctl start docker

log "Server setup completed successfully!"
warn "Please set a password for the mindmend user: sudo passwd mindmend"
warn "Consider setting up SSH key authentication and disabling password authentication"
log "You can now log in as the mindmend user and run the deployment script"