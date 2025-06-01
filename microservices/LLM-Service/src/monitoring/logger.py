import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'child_id'):
            log_entry['child_id'] = record.child_id
        if hasattr(record, 'analysis_type'):
            log_entry['analysis_type'] = record.analysis_type
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup structured logging configuration"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return root_logger

class StructuredLogger:
    """Wrapper for structured logging with context"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self._log(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self._log(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self._log(logging.ERROR, message, **kwargs)
        
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self._log(logging.DEBUG, message, **kwargs)
        
    def _log(self, level: int, message: str, **kwargs):
        """Internal log method with context injection"""
        # Create a log record
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "",  # pathname
            0,   # lineno
            message,
            (),  # args
            None,  # exc_info
            "",  # funcName
            extra=kwargs
        )
        
        # Handle the record
        self.logger.handle(record)

def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)
