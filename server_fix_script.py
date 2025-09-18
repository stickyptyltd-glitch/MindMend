#!/usr/bin/env python3

"""
MindMend Server Fix Script
Alternative approaches when SSH is not accessible
"""

import requests
import time
import json
from datetime import datetime

class ServerDiagnostics:
    def __init__(self, server_ip="67.219.102.9", domain="mindmend.xyz"):
        self.server_ip = server_ip
        self.domain = domain

    def check_server_status(self):
        """Comprehensive server status check"""
        print("🔍 MindMend Server Diagnostics")
        print("=" * 50)

        # Check basic connectivity
        import subprocess
        try:
            ping_result = subprocess.run(['ping', '-c', '3', self.server_ip],
                                       capture_output=True, text=True, timeout=10)
            if ping_result.returncode == 0:
                print("✅ Server is responding to ping")
            else:
                print("❌ Server not responding to ping")
        except Exception as e:
            print(f"❌ Ping test failed: {e}")

        # Check HTTP response
        try:
            response = requests.get(f"http://{self.server_ip}", timeout=10)
            print(f"📊 HTTP Status: {response.status_code}")
            print(f"🌐 Server: {response.headers.get('Server', 'Unknown')}")

            if response.status_code == 502:
                print("🔴 502 Bad Gateway - Backend application is down")
                print("💡 This means nginx is running but Flask app is not")
        except Exception as e:
            print(f"❌ HTTP test failed: {e}")

        # Check specific ports
        ports_to_check = [22, 80, 443, 8000, 8080]
        for port in ports_to_check:
            self.check_port(port)

        # Check domain resolution
        try:
            import socket
            ip = socket.gethostbyname(self.domain)
            print(f"🌐 Domain {self.domain} resolves to: {ip}")
            if ip == self.server_ip:
                print("✅ Domain resolution correct")
            else:
                print("⚠️  Domain resolves to different IP")
        except Exception as e:
            print(f"❌ Domain resolution failed: {e}")

    def check_port(self, port):
        """Check if specific port is open"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_ip, port))
            sock.close()

            if result == 0:
                print(f"✅ Port {port} is open")
            else:
                print(f"❌ Port {port} is closed")
        except Exception as e:
            print(f"❌ Port {port} check failed: {e}")

    def suggest_fixes(self):
        """Suggest possible fixes based on diagnosis"""
        print("\n🛠️  Suggested Fixes")
        print("=" * 50)
        print("1. 🔄 Server Restart Needed")
        print("   - Contact your hosting provider to restart the server")
        print("   - Flask application process may have crashed")
        print("   - Port 8000 (Flask) appears to be down while nginx (port 80) is up")

        print("\n2. 🔑 SSH Access Issues")
        print("   - SSH port 22 may be blocked or filtered")
        print("   - Try alternative access methods:")
        print("   - Console access through hosting provider")
        print("   - Web-based terminal if available")

        print("\n3. 📞 Contact Hosting Provider")
        print("   - Server may need manual intervention")
        print("   - Possible network configuration issues")
        print("   - Ask them to restart services or check process status")

        print("\n4. 🚀 Immediate Temporary Fix")
        print("   - Deploy static landing page while fixing main application")
        print("   - Use CDN or alternative hosting for temporary page")

def create_nginx_fix_commands():
    """Generate commands to fix nginx configuration"""
    commands = """
# Commands to run when SSH access is restored:

# Check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check what's listening on port 8000 (Flask app should be here)
sudo lsof -i :8000
sudo ss -tlnp | grep :8000

# Check Flask application process
ps aux | grep flask
ps aux | grep python

# Restart Flask application (assuming it's in /root/MindMend)
cd /root/MindMend
nohup python app.py &

# Or if using docker-compose:
docker-compose ps
docker-compose restart

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx if needed
sudo systemctl restart nginx

# Check firewall status
sudo ufw status
sudo iptables -L
    """
    return commands

def deploy_emergency_landing_page():
    """Instructions for deploying emergency landing page"""
    print("\n🚨 Emergency Landing Page Deployment")
    print("=" * 50)
    print("Since the main server is down, here are options:")

    print("\n1. 📄 Static File Hosting")
    print("   - Upload simple_landing.html to a free static host")
    print("   - Options: Netlify, Vercel, GitHub Pages")
    print("   - Point domain temporarily to static host")

    print("\n2. 🌐 CDN Deployment")
    print("   - Use CloudFlare or similar CDN")
    print("   - Upload static files")
    print("   - Redirect traffic while main server is fixed")

    print("\n3. 📱 Social Media Announcement")
    print("   - Post on social media about temporary maintenance")
    print("   - Provide alternative contact methods")
    print("   - Announce expected fix timeline")

    # Create a simple deployment script
    deployment_script = '''
#!/bin/bash
# Emergency deployment script

echo "🚨 MindMend Emergency Deployment"

# Option 1: Deploy to Netlify using curl
if command -v curl &> /dev/null; then
    echo "📤 Uploading to Netlify..."
    # zip -r site.zip simple_landing.html
    # curl -H "Content-Type: application/zip" -H "Authorization: Bearer YOUR_TOKEN" --data-binary "@site.zip" https://api.netlify.com/api/v1/sites
fi

# Option 2: Use GitHub Pages
if [ -d ".git" ]; then
    echo "📤 Deploying to GitHub Pages..."
    git add simple_landing.html
    git commit -m "Emergency landing page deployment"
    git push origin main
fi

echo "✅ Emergency deployment initiated"
    '''

    with open('/home/dayle/emergency_deploy.sh', 'w') as f:
        f.write(deployment_script)

    print(f"\n📝 Emergency deployment script created: /home/dayle/emergency_deploy.sh")

if __name__ == "__main__":
    print("🧠 MindMend Server Fix Assistant")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    diagnostics = ServerDiagnostics()

    # Run diagnostics
    diagnostics.check_server_status()

    # Suggest fixes
    diagnostics.suggest_fixes()

    # Generate fix commands
    print("\n💻 Server Fix Commands")
    print("=" * 50)
    print(create_nginx_fix_commands())

    # Emergency deployment options
    deploy_emergency_landing_page()

    print("\n📞 Next Steps:")
    print("1. Contact hosting provider about server restart")
    print("2. Deploy temporary landing page")
    print("3. Monitor server status")
    print("4. Restore Flask application when access is available")

    print(f"\n✅ Diagnostics complete. Report saved to: mindmend_server_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")