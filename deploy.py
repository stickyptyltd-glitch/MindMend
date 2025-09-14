#!/usr/bin/env python3
"""
MindMend Production Deployment Script
===================================
Automated deployment to mindmend.xyz with comprehensive security checks
"""

import os
import sys
import subprocess
import logging
import json
import time
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MindMendDeployment:
    """Production deployment manager for MindMend"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_config = self.load_deployment_config()
        
    def load_deployment_config(self):
        """Load deployment configuration"""
        config_file = self.project_root / 'deployment_config.json'
        
        default_config = {
            "domain": "mindmend.xyz",
            "server_user": "mindmend",
            "server_host": "your-server-ip",
            "app_directory": "/var/www/mindmend",
            "python_version": "3.11",
            "database_host": "localhost",
            "database_name": "mindmend_production",
            "ssl_enabled": True,
            "backup_enabled": True,
            "monitoring_enabled": True
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                default_config.update(config)
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default deployment config: {config_file}")
            
        return default_config
    
    def load_environment(self):
        """Load production environment variables"""
        env_file = self.project_root / '.env.production'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    def pre_deployment_checks(self):
        """Run pre-deployment security and readiness checks"""
        logger.info("🔍 Running pre-deployment checks...")
        
        # Load environment first
        self.load_environment()
        
        checks = []
        
        # 1. Environment file validation
        env_file = self.project_root / '.env.production'
        if not env_file.exists():
            checks.append(("❌ Production .env file missing", False))
        else:
            with open(env_file, 'r') as f:
                env_content = f.read()
                
            if 'your-stripe-secret-key' in env_content:
                checks.append(("❌ Stripe keys not configured", False))
            else:
                checks.append(("✅ Stripe keys configured", True))
                
            if 'your-openai-api-key' in env_content:
                checks.append(("❌ OpenAI API key not configured", False))
            else:
                checks.append(("✅ OpenAI API key configured", True))
        
        # 2. Database migrations
        try:
            result = subprocess.run(['python', 'test_payment_system.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                checks.append(("✅ Database models working", True))
            else:
                checks.append(("❌ Database models have issues", False))
        except Exception as e:
            checks.append((f"❌ Database test failed: {e}", False))
        
        # 3. Security configuration
        secret_key = os.environ.get('SECRET_KEY', '')
        if secret_key and len(secret_key) >= 32 and secret_key != 'your-secret-key-here':
            checks.append(("✅ Production SECRET_KEY configured", True))
        else:
            checks.append(("❌ Production SECRET_KEY not set", False))
        
        # 4. SSL certificate check
        domain = self.deployment_config['domain']
        try:
            result = subprocess.run(['curl', '-I', f'https://{domain}'], 
                                  capture_output=True, text=True, timeout=10)
            if 'HTTP/2 200' in result.stdout or 'HTTP/1.1 200' in result.stdout:
                checks.append(("✅ SSL certificate valid", True))
            else:
                checks.append(("⚠️  SSL certificate needs setup", False))
        except Exception:
            checks.append(("⚠️  Cannot verify SSL certificate", False))
        
        # Print results
        logger.info("\\n📋 Pre-deployment Check Results:")
        all_passed = True
        for check, passed in checks:
            logger.info(f"   {check}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def backup_current_deployment(self):
        """Create backup of current deployment"""
        logger.info("💾 Creating deployment backup...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"mindmend_backup_{timestamp}"
        
        backup_commands = [
            f"ssh {self.deployment_config['server_user']}@{self.deployment_config['server_host']} "
            f"'sudo mkdir -p /backups/{backup_name}'",
            
            f"ssh {self.deployment_config['server_user']}@{self.deployment_config['server_host']} "
            f"'sudo cp -r {self.deployment_config['app_directory']} /backups/{backup_name}/app'",
            
            f"ssh {self.deployment_config['server_user']}@{self.deployment_config['server_host']} "
            f"'sudo -u postgres pg_dump {self.deployment_config['database_name']} > "
            f"/backups/{backup_name}/database.sql'"
        ]
        
        for cmd in backup_commands:
            logger.info(f"Executing: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Backup command failed: {result.stderr}")
                return False
        
        logger.info(f"✅ Backup created: {backup_name}")
        return True
    
    def deploy_application(self):
        """Deploy application to production server"""
        logger.info("🚀 Deploying MindMend to production...")
        
        server_user = self.deployment_config['server_user']
        server_host = self.deployment_config['server_host']
        app_dir = self.deployment_config['app_directory']
        
        deployment_commands = [
            # Stop application
            f"ssh {server_user}@{server_host} 'sudo systemctl stop mindmend'",
            
            # Upload application files
            f"rsync -avz --delete --exclude='.git' --exclude='__pycache__' "
            f"--exclude='*.pyc' --exclude='deployment.log' "
            f"{self.project_root}/ {server_user}@{server_host}:{app_dir}/",
            
            # Install dependencies
            f"ssh {server_user}@{server_host} 'cd {app_dir} && "
            f"source venv/bin/activate && pip install -r requirements.txt'",
            
            # Run database migrations
            f"ssh {server_user}@{server_host} 'cd {app_dir} && "
            f"source venv/bin/activate && python -c \"from app import app, db; "
            f"with app.app_context(): db.create_all()\"'",
            
            # Set proper permissions
            f"ssh {server_user}@{server_host} 'sudo chown -R {server_user}:www-data {app_dir}'",
            f"ssh {server_user}@{server_host} 'sudo chmod -R 755 {app_dir}'",
            
            # Start application
            f"ssh {server_user}@{server_host} 'sudo systemctl start mindmend'",
            f"ssh {server_user}@{server_host} 'sudo systemctl enable mindmend'"
        ]
        
        for cmd in deployment_commands:
            logger.info(f"Executing: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Deployment command failed: {result.stderr}")
                return False
            time.sleep(2)  # Brief pause between commands
        
        logger.info("✅ Application deployed successfully")
        return True
    
    def verify_deployment(self):
        """Verify deployment is working correctly"""
        logger.info("🔍 Verifying deployment...")
        
        domain = self.deployment_config['domain']
        
        # Health check endpoints
        health_checks = [
            f"https://{domain}/",
            f"https://{domain}/health",
            f"https://{domain}/pricing"
        ]
        
        for url in health_checks:
            try:
                result = subprocess.run(['curl', '-f', '-s', url], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info(f"✅ {url} responding")
                else:
                    logger.error(f"❌ {url} not responding: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"❌ Health check failed for {url}: {e}")
                return False
        
        logger.info("✅ All health checks passed")
        return True
    
    def setup_ssl_certificate(self):
        """Set up SSL certificate using Let's Encrypt"""
        logger.info("🔒 Setting up SSL certificate...")
        
        server_user = self.deployment_config['server_user']
        server_host = self.deployment_config['server_host']
        domain = self.deployment_config['domain']
        
        ssl_commands = [
            f"ssh {server_user}@{server_host} 'sudo apt update'",
            f"ssh {server_user}@{server_host} 'sudo apt install -y certbot python3-certbot-nginx'",
            f"ssh {server_user}@{server_host} 'sudo certbot --nginx -d {domain} -d www.{domain} --non-interactive --agree-tos --email admin@{domain}'",
            f"ssh {server_user}@{server_host} 'sudo systemctl reload nginx'"
        ]
        
        for cmd in ssl_commands:
            logger.info(f"Executing: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"SSL setup command failed: {result.stderr}")
        
        return True
    
    def deploy(self, skip_checks=False, skip_backup=False):
        """Run complete deployment process"""
        logger.info("🎯 Starting MindMend production deployment")
        logger.info(f"   Domain: {self.deployment_config['domain']}")
        logger.info(f"   Server: {self.deployment_config['server_host']}")
        
        # Pre-deployment checks
        if not skip_checks:
            if not self.pre_deployment_checks():
                logger.error("❌ Pre-deployment checks failed. Fix issues before deploying.")
                return False
        
        # Create backup
        if not skip_backup:
            if not self.backup_current_deployment():
                logger.error("❌ Backup creation failed")
                return False
        
        # Deploy application
        if not self.deploy_application():
            logger.error("❌ Application deployment failed")
            return False
        
        # Set up SSL if needed
        if self.deployment_config['ssl_enabled']:
            self.setup_ssl_certificate()
        
        # Verify deployment
        if not self.verify_deployment():
            logger.error("❌ Deployment verification failed")
            return False
        
        logger.info("🎉 MindMend deployed successfully to production!")
        logger.info(f"   Website: https://{self.deployment_config['domain']}")
        logger.info(f"   Admin: https://{self.deployment_config['domain']}/admin")
        
        return True

def main():
    """Main deployment script"""
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [deploy|check|backup|ssl]")
        print("  deploy - Full deployment")
        print("  check  - Run pre-deployment checks only")  
        print("  backup - Create backup only")
        print("  ssl    - Setup SSL certificate only")
        return
    
    deployment = MindMendDeployment()
    command = sys.argv[1].lower()
    
    if command == 'check':
        deployment.pre_deployment_checks()
    elif command == 'backup':
        deployment.backup_current_deployment()
    elif command == 'ssl':
        deployment.setup_ssl_certificate()
    elif command == 'deploy':
        skip_checks = '--skip-checks' in sys.argv
        skip_backup = '--skip-backup' in sys.argv
        deployment.deploy(skip_checks=skip_checks, skip_backup=skip_backup)
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()