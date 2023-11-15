import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {name} {lineno} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {name} {lineno} {message}',
            'style': '{',
        },
        'django': {
            'format': 'django: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': 'py_log.log',
        },
        'admin_sender': {
            'level': 'INFO',
            'formatter': 'verbose',
            'class': 'setup.logging_config.AdminHandler',
        },
    },
    'loggers': {
        "admin": {
            "handlers": ["admin_sender"],
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}


def configure_logging():
    logging.config.dictConfig(LOGGING)


class AdminHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        ...
        # todo отправлять сообщения админу через бота
