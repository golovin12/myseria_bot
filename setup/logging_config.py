import logging.config


def configure_logging(logging_config):
    logging.config.dictConfig(logging_config)
