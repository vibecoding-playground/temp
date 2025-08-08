"""
MeetingMind - Metrics and Monitoring
Provides custom metrics for Prometheus monitoring

Author: Claude  
Date: 2025-01-08
"""

import time
import psutil
from typing import Dict, Any
from datetime import datetime, timezone

class MetricsCollector:
    """Collects and provides custom metrics for monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            "meetings_created": 0,
            "meetings_active": 0,
            "meetings_completed": 0,
            "websocket_connections": 0,
            "gemini_api_calls": 0,
            "gemini_api_errors": 0,
            "text_analyses_performed": 0,
            "action_items_generated": 0,
            "insights_generated": 0,
            "meeting_summaries_generated": 0,
            "summary_exports": 0
        }
        
    def increment(self, metric_name: str, value: int = 1):
        """Increment a counter metric"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def set_gauge(self, metric_name: str, value: int):
        """Set a gauge metric value"""
        self.metrics[metric_name] = value
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used / (1024 * 1024),
            "memory_available_mb": psutil.virtual_memory().available / (1024 * 1024),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - self.start_time,
        }
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        return {
            **self.metrics,
            "uptime_seconds": time.time() - self.start_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_prometheus_format(self) -> str:
        """Get metrics in Prometheus format"""
        lines = []
        
        # System metrics
        system_metrics = self.get_system_metrics()
        lines.append(f"# HELP meetingmind_cpu_percent CPU usage percentage")
        lines.append(f"# TYPE meetingmind_cpu_percent gauge")
        lines.append(f"meetingmind_cpu_percent {system_metrics['cpu_percent']}")
        
        lines.append(f"# HELP meetingmind_memory_percent Memory usage percentage")
        lines.append(f"# TYPE meetingmind_memory_percent gauge")
        lines.append(f"meetingmind_memory_percent {system_metrics['memory_percent']}")
        
        lines.append(f"# HELP meetingmind_uptime_seconds Application uptime in seconds")
        lines.append(f"# TYPE meetingmind_uptime_seconds counter")
        lines.append(f"meetingmind_uptime_seconds {system_metrics['uptime_seconds']}")
        
        # Application metrics
        app_metrics = self.get_application_metrics()
        
        # Counters
        counter_metrics = [
            "meetings_created", "meetings_completed", "gemini_api_calls",
            "gemini_api_errors", "text_analyses_performed", 
            "action_items_generated", "insights_generated",
            "meeting_summaries_generated", "summary_exports"
        ]
        
        for metric in counter_metrics:
            lines.append(f"# HELP meetingmind_{metric} Total number of {metric.replace('_', ' ')}")
            lines.append(f"# TYPE meetingmind_{metric} counter")
            lines.append(f"meetingmind_{metric} {app_metrics[metric]}")
        
        # Gauges
        gauge_metrics = ["meetings_active", "websocket_connections"]
        
        for metric in gauge_metrics:
            lines.append(f"# HELP meetingmind_{metric} Current number of {metric.replace('_', ' ')}")
            lines.append(f"# TYPE meetingmind_{metric} gauge")  
            lines.append(f"meetingmind_{metric} {app_metrics[metric]}")
        
        return "\n".join(lines) + "\n"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics()
        
        # Determine health status based on metrics
        health_status = "healthy"
        issues = []
        
        if system_metrics["cpu_percent"] > 90:
            health_status = "warning"
            issues.append("High CPU usage")
        
        if system_metrics["memory_percent"] > 85:
            health_status = "warning"  
            issues.append("High memory usage")
        
        if system_metrics["disk_usage_percent"] > 90:
            health_status = "critical"
            issues.append("High disk usage")
        
        # Calculate error rate
        total_api_calls = app_metrics["gemini_api_calls"]
        api_errors = app_metrics["gemini_api_errors"]
        error_rate = (api_errors / total_api_calls * 100) if total_api_calls > 0 else 0
        
        if error_rate > 10:  # More than 10% error rate
            health_status = "warning"
            issues.append(f"High API error rate: {error_rate:.1f}%")
        
        return {
            "status": health_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": system_metrics["uptime_seconds"],
            "issues": issues,
            "metrics": {
                "system": system_metrics,
                "application": app_metrics
            },
            "api_error_rate": error_rate,
            "total_meetings": app_metrics["meetings_created"],
            "active_connections": app_metrics["websocket_connections"]
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()