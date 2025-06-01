"""
Logging setup and utilities for TokenTrackTUI Neural Nexus.

Provides structured logging with proper configuration for both file
and console output, including integration with Textual's logging system.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json

from textual.logging import TextualHandler


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if configured
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in {
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                    'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                    'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                    'thread', 'threadName', 'processName', 'process', 'message'
                }:
                    log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ConsoleFormatter(logging.Formatter):
    """Human-readable formatter for console output."""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%H:%M:%S'
        )


class SecurityFilter(logging.Filter):
    """Filter to prevent logging of sensitive information."""
    
    SENSITIVE_FIELDS = {
        'password', 'token', 'key', 'secret', 'credential', 'auth',
        'api_key', 'access_token', 'refresh_token', 'bearer'
    }
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out log records that might contain sensitive data."""
        message = record.getMessage().lower()
        
        # Check if any sensitive field names appear in the message
        for sensitive in self.SENSITIVE_FIELDS:
            if sensitive in message:
                # Replace with sanitized version
                record.msg = "[REDACTED - Sensitive information filtered]"
                record.args = ()
                break
        
        return True


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    enable_textual_logging: bool = True,
    structured_file_logs: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up comprehensive logging for TokenTrackTUI.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default location
        enable_file_logging: Whether to log to file
        enable_console_logging: Whether to log to console
        enable_textual_logging: Whether to enable Textual's logging handler
        structured_file_logs: Whether to use JSON format for file logs
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    """
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root logger level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Security filter to prevent credential leakage
    security_filter = SecurityFilter()
    
    # Console logging
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(ConsoleFormatter())
        console_handler.addFilter(security_filter)
        root_logger.addHandler(console_handler)
    
    # File logging
    if enable_file_logging:
        if log_file is None:
            # Default log file location
            log_dir = Path.home() / '.local' / 'share' / 'tokentracktui' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'tokentracktui.log'
        
        # Use rotating file handler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        
        # Use structured or simple formatting
        if structured_file_logs:
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
        
        file_handler.addFilter(security_filter)
        root_logger.addHandler(file_handler)
    
    # Textual logging integration
    if enable_textual_logging:
        try:
            textual_handler = TextualHandler()
            textual_handler.setLevel(numeric_level)
            textual_handler.addFilter(security_filter)
            root_logger.addHandler(textual_handler)
        except Exception as e:
            # Fallback if Textual logging isn't available
            logging.warning(f"Failed to setup Textual logging: {e}")
    
    # Configure specific loggers
    _configure_specific_loggers(numeric_level)
    
    # Log the setup completion
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {level}, File: {log_file}")


def _configure_specific_loggers(level: int) -> None:
    """Configure logging levels for specific modules."""
    
    # Set appropriate levels for third-party libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # TokenTrackTUI loggers
    logging.getLogger('tokentracktui').setLevel(level)
    
    # Textual loggers
    logging.getLogger('textual').setLevel(logging.WARNING)
    logging.getLogger('rich').setLevel(logging.WARNING)


def get_logger(name: str, extra_context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Get a logger with optional extra context.
    
    Args:
        name: Logger name (usually __name__)
        extra_context: Additional context to include in log messages
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if extra_context:
        logger = logging.LoggerAdapter(logger, extra_context)
    
    return logger


def log_performance(func_name: str, duration: float, **kwargs) -> None:
    """Log performance metrics."""
    logger = get_logger('tokentracktui.performance')
    logger.info(
        f"Performance: {func_name} completed in {duration:.3f}s",
        extra={
            'performance_metric': True,
            'function': func_name,
            'duration_seconds': duration,
            **kwargs
        }
    )


def log_api_call(
    provider: str,
    endpoint: str,
    method: str = "GET",
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    **kwargs
) -> None:
    """Log API call information (without sensitive data)."""
    logger = get_logger('tokentracktui.api')
    
    message = f"API Call: {method} {endpoint}"
    if status_code:
        message += f" -> {status_code}"
    if duration:
        message += f" ({duration:.3f}s)"
    
    logger.info(
        message,
        extra={
            'api_call': True,
            'provider': provider,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration_seconds': duration,
            **kwargs
        }
    ) 