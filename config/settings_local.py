from config.settings_default import DefaultSettings


class LocalSettings(DefaultSettings):
    def __init__(self):
        super().__init__()
        self.LOGGING['handlers']['file'] = {
            'level': 'WARNING',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': 'py_log.log',
        }
        self.LOGGING['root'] = {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        }
