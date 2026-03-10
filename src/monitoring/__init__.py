"""
Monitoring module for YouTube automation.

Includes performance monitoring and error tracking.
"""

from .error_monitor import (
    AlertManager,
    ErrorCategory,
    ErrorEvent,
    ErrorMonitor,
    ErrorSeverity,
    get_alert_manager,
    get_error_monitor,
    monitor_errors,
    monitor_errors_async,
    quick_record_error,
)
from .performance_monitor import PerformanceAlert, PerformanceMonitor

__all__ = [
    # Performance monitoring
    "PerformanceAlert",
    "PerformanceMonitor",
    # Error monitoring
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorEvent",
    "ErrorMonitor",
    "AlertManager",
    "get_error_monitor",
    "get_alert_manager",
    "monitor_errors",
    "monitor_errors_async",
    "quick_record_error",
]
