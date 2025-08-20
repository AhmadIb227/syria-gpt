"""Logging configuration for Syria GPT API."""

import logging
import logging.config
from typing import Dict, Any
from config.settings import settings


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment."""
    
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "[%(asctime)s] %(levelname)-8s %(name)-12s [%(filename)s:%(lineno)d] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed" if settings.DEBUG else "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if not settings.DEBUG else "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    return config


def setup_logging() -> logging.Logger:
    """Setup application logging."""
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    
    logger = logging.getLogger("syria_gpt")
    logger.info(f"Logging configured for {settings.ENVIRONMENT} environment")
    
    return logger