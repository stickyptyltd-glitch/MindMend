"""
MindMend Monitoring and Logging System
=====================================
Comprehensive monitoring, logging, and alerting for production deployment
"""

import os
import json
import time
import psutil
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass
from enum import Enum
import requests
import docker
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mindmend/monitoring.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict
    process_count: int
    timestamp: datetime

@dataclass
class ApplicationMetrics:
    active_sessions: int
    response_time_avg: float
    error_rate: float
    ai_model_usage: Dict
    database_connections: int
    timestamp: datetime

class MindMendMonitoring:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.metrics_history = []
        self.alert_config = {
            "cpu_threshold": 85,
            "memory_threshold": 90,
            "disk_threshold": 95,
            "error_rate_threshold": 5,
            "response_time_threshold": 30,
            "check_interval": 60
        }
        
        self.email_config = {
            "smtp_server": os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.environ.get("MAIL_PORT", 587)),
            "email": os.environ.get("MAIL_USERNAME"),
            "password": os.environ.get("MAIL_PASSWORD"),
            "alert_recipients": os.environ.get("ALERT_RECIPIENTS", "").split(",")
        }
        
        self.last_alerts = {}
        self.alert_cooldown = 300  # 5 minutes cooldown between similar alerts
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                process_count=process_count,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific metrics"""
        try:
            # Get active sessions (placeholder - implement with your session store)
            active_sessions = self._get_active_sessions()
            
            # Get response time from recent logs (placeholder)
            response_time_avg = self._calculate_avg_response_time()
            
            # Get error rate from logs
            error_rate = self._calculate_error_rate()
            
            # Get AI model usage
            ai_model_usage = self._get_ai_model_usage()
            
            # Get database connections
            db_connections = self._get_database_connections()
            
            return ApplicationMetrics(
                active_sessions=active_sessions,
                response_time_avg=response_time_avg,
                error_rate=error_rate,
                ai_model_usage=ai_model_usage,
                database_connections=db_connections,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return None
    
    def check_docker_health(self) -> Dict:
        """Check health of Docker containers"""
        container_status = {}
        
        try:
            containers = self.docker_client.containers.list(all=True)
            
            for container in containers:
                if "mindmend" in container.name:
                    container_status[container.name] = {
                        "status": container.status,
                        "health": getattr(container.attrs["State"], "Health", {}).get("Status", "unknown"),
                        "restart_count": container.attrs["RestartCount"],
                        "started_at": container.attrs["State"]["StartedAt"],
                        "cpu_usage": self._get_container_cpu_usage(container),
                        "memory_usage": self._get_container_memory_usage(container)
                    }
        except Exception as e:
            logger.error(f"Error checking Docker health: {e}")
        
        return container_status
    
    def check_service_endpoints(self) -> Dict:
        """Check if service endpoints are responding"""
        endpoints = {
            "main_app": "http://localhost:8000/health",
            "ollama": "http://localhost:11434/api/tags",
            "postgres": None,  # Will check via connection
            "redis": None      # Will check via connection
        }
        
        status = {}
        
        for service, url in endpoints.items():
            if url:
                try:
                    response = requests.get(url, timeout=10)
                    status[service] = {
                        "status": "healthy" if response.status_code == 200 else "unhealthy",
                        "response_time": response.elapsed.total_seconds(),
                        "status_code": response.status_code
                    }
                except Exception as e:
                    status[service] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            else:
                # For database and Redis, implement connection checks
                status[service] = self._check_database_connection(service)
        
        return status
    
    def analyze_logs(self, log_file: str, time_window: int = 3600) -> Dict:
        """Analyze application logs for errors and patterns"""
        if not os.path.exists(log_file):
            return {"error": "Log file not found"}
        
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        error_count = 0
        warning_count = 0
        total_requests = 0
        error_patterns = {}
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    # Parse log line timestamp and level
                    if "ERROR" in line:
                        error_count += 1
                        # Extract error patterns
                        if ":" in line:
                            error_type = line.split(":")[-1].strip()[:50]
                            error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                    elif "WARNING" in line:
                        warning_count += 1
                    elif any(method in line for method in ["GET", "POST", "PUT", "DELETE"]):
                        total_requests += 1
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {"error": str(e)}
        
        return {
            "error_count": error_count,
            "warning_count": warning_count,
            "total_requests": total_requests,
            "error_rate": (error_count / max(total_requests, 1)) * 100,
            "top_errors": sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def send_alert(self, level: AlertLevel, title: str, message: str, metrics: Dict = None):
        """Send alert via email"""
        alert_key = f"{level.value}_{title}"
        current_time = time.time()
        
        # Check cooldown
        if alert_key in self.last_alerts:
            if current_time - self.last_alerts[alert_key] < self.alert_cooldown:
                return  # Skip this alert due to cooldown
        
        self.last_alerts[alert_key] = current_time
        
        if not self.email_config["email"] or not self.email_config["alert_recipients"]:
            logger.warning("Email configuration not set, cannot send alerts")
            return
        
        try:
            # Create email
            msg = MimeMultipart()
            msg['From'] = self.email_config["email"]
            msg['To'] = ", ".join(self.email_config["alert_recipients"])
            msg['Subject'] = f"[MindMend {level.value.upper()}] {title}"
            
            # Email body
            body = f"""
MindMend Production Alert

Level: {level.value.upper()}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Title: {title}

Message:
{message}

"""
            
            if metrics:
                body += "\nSystem Metrics:\n"
                body += json.dumps(metrics, indent=2, default=str)
            
            body += f"""

Dashboard: https://admin.mindmend.xyz
Server: {os.uname().nodename}

---
MindMend Monitoring System
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_config["email"], self.email_config["password"])
                server.send_message(msg)
            
            logger.info(f"Alert sent: {level.value} - {title}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def check_thresholds(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Check metrics against thresholds and trigger alerts"""
        if system_metrics:
            if system_metrics.cpu_percent > self.alert_config["cpu_threshold"]:
                self.send_alert(
                    AlertLevel.WARNING,
                    "High CPU Usage",
                    f"CPU usage is {system_metrics.cpu_percent}%, exceeding threshold of {self.alert_config['cpu_threshold']}%",
                    {"cpu_percent": system_metrics.cpu_percent}
                )
            
            if system_metrics.memory_percent > self.alert_config["memory_threshold"]:
                self.send_alert(
                    AlertLevel.ERROR,
                    "High Memory Usage",
                    f"Memory usage is {system_metrics.memory_percent}%, exceeding threshold of {self.alert_config['memory_threshold']}%",
                    {"memory_percent": system_metrics.memory_percent}
                )
            
            if system_metrics.disk_percent > self.alert_config["disk_threshold"]:
                self.send_alert(
                    AlertLevel.CRITICAL,
                    "Critical Disk Space",
                    f"Disk usage is {system_metrics.disk_percent}%, exceeding critical threshold of {self.alert_config['disk_threshold']}%",
                    {"disk_percent": system_metrics.disk_percent}
                )
        
        if app_metrics:
            if app_metrics.error_rate > self.alert_config["error_rate_threshold"]:
                self.send_alert(
                    AlertLevel.ERROR,
                    "High Error Rate",
                    f"Application error rate is {app_metrics.error_rate}%, exceeding threshold of {self.alert_config['error_rate_threshold']}%",
                    {"error_rate": app_metrics.error_rate}
                )
            
            if app_metrics.response_time_avg > self.alert_config["response_time_threshold"]:
                self.send_alert(
                    AlertLevel.WARNING,
                    "Slow Response Time",
                    f"Average response time is {app_metrics.response_time_avg}s, exceeding threshold of {self.alert_config['response_time_threshold']}s",
                    {"response_time_avg": app_metrics.response_time_avg}
                )
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        system_metrics = self.collect_system_metrics()
        app_metrics = self.collect_application_metrics()
        docker_health = self.check_docker_health()
        service_status = self.check_service_endpoints()
        log_analysis = self.analyze_logs("/var/log/mindmend/app.log")
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",  # Will be determined below
            "system_metrics": system_metrics.__dict__ if system_metrics else None,
            "application_metrics": app_metrics.__dict__ if app_metrics else None,
            "docker_health": docker_health,
            "service_status": service_status,
            "log_analysis": log_analysis
        }
        
        # Determine overall status
        issues = []
        if system_metrics:
            if system_metrics.cpu_percent > 90:
                issues.append("High CPU")
            if system_metrics.memory_percent > 95:
                issues.append("High Memory")
            if system_metrics.disk_percent > 98:
                issues.append("Critical Disk Space")
        
        if any(service["status"] == "unhealthy" for service in service_status.values()):
            issues.append("Service Issues")
        
        if log_analysis.get("error_rate", 0) > 10:
            issues.append("High Error Rate")
        
        if issues:
            report["overall_status"] = "unhealthy"
            report["issues"] = issues
        
        return report
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.info("Starting monitoring cycle")
        
        try:
            # Collect metrics
            system_metrics = self.collect_system_metrics()
            app_metrics = self.collect_application_metrics()
            
            # Store metrics
            if system_metrics and app_metrics:
                self.metrics_history.append({
                    "timestamp": datetime.utcnow(),
                    "system": system_metrics,
                    "application": app_metrics
                })
                
                # Keep only last 1440 entries (24 hours if run every minute)
                if len(self.metrics_history) > 1440:
                    self.metrics_history = self.metrics_history[-1440:]
            
            # Check thresholds
            self.check_thresholds(system_metrics, app_metrics)
            
            # Generate and save health report
            health_report = self.generate_health_report()
            self._save_health_report(health_report)
            
            logger.info("Monitoring cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            self.send_alert(
                AlertLevel.ERROR,
                "Monitoring System Error",
                f"Error in monitoring cycle: {str(e)}"
            )
    
    def _get_active_sessions(self) -> int:
        """Get count of active user sessions"""
        # Placeholder - implement with your session store
        return 0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from logs"""
        # Placeholder - implement log parsing
        return 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate from logs"""
        # Placeholder - implement log parsing
        return 0.0
    
    def _get_ai_model_usage(self) -> Dict:
        """Get AI model usage statistics"""
        # Placeholder - implement model usage tracking
        return {}
    
    def _get_database_connections(self) -> int:
        """Get active database connections"""
        # Placeholder - implement database connection counting
        return 0
    
    def _get_container_cpu_usage(self, container) -> float:
        """Get CPU usage for Docker container"""
        try:
            stats = container.stats(stream=False)
            return 0.0  # Placeholder calculation
        except:
            return 0.0
    
    def _get_container_memory_usage(self, container) -> Dict:
        """Get memory usage for Docker container"""
        try:
            stats = container.stats(stream=False)
            return {"usage": 0, "limit": 0}  # Placeholder
        except:
            return {"usage": 0, "limit": 0}
    
    def _check_database_connection(self, service: str) -> Dict:
        """Check database connection health"""
        # Placeholder - implement actual database health checks
        return {"status": "unknown"}
    
    def _save_health_report(self, report: Dict):
        """Save health report to file"""
        try:
            reports_dir = Path("/var/log/mindmend/health_reports")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"health_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving health report: {e}")

# Global monitoring instance
monitoring = MindMendMonitoring()

if __name__ == "__main__":
    # Run monitoring cycle
    monitoring.run_monitoring_cycle()