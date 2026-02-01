import logging
import logging.config
import os

def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
            },
            # You can add a file handler here if needed
            # "file": {
            #     "class": "logging.FileHandler",
            #     "filename": "app.log",
            #     "formatter": "standard",
            #     "level": "DEBUG",
            # },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True
            },
            "services": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "core": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "infra": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
        }
    }
    
    logging.config.dictConfig(logging_config)

def get_logger(name):
    return logging.getLogger(name)
