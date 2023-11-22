from config.settings_default import DefaultSettings


class DockerSettings(DefaultSettings):
    def __init__(self):
        super().__init__()
        self.LOGGING['handlers']['external'] = {
            'level': 'WARNING',
            'formatter': 'verbose',
            'facility': 'local0',
            'class': 'logging.handlers.SysLogHandler',
            'address': ('syslog-storage', 514),
        }
        self.LOGGING['root'] = {
            'handlers': ['console', 'external'],
            'level': 'INFO',
        }
