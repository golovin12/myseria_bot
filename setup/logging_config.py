import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {name} {lineno}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {lineno}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'external': {
            'level': 'WARNING',
            'formatter': 'verbose',
            'facility': 'local0',
            'class': 'logging.handlers.SysLogHandler',
            'address': ('syslog-storage', 514),
        },
        'admin_sender': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'management.logging_handlers.AdminHandler',
        },
    },
    'loggers': {
        "admin": {
            "handlers": ["admin_sender"],
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console", "external"],
        "level": "INFO",
    },
}


def configure_logging():
    logging.config.dictConfig(LOGGING)
