# logger.py

import logging
import os
import yaml
from logging.handlers import RotatingFileHandler

class LoggerSingleton:
    _instance = None

    @staticmethod
    def get_instance(config_path="config/config.yaml"):
        if LoggerSingleton._instance is None:
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            LoggerSingleton(config)
        return LoggerSingleton._instance

    def __init__(self, config):
        if LoggerSingleton._instance is not None:
            raise Exception("LoggerSingleton is a singleton!")

        log_file = config['logging']['log_file']
        log_level = config['logging']['log_level'].upper()
        max_bytes = config['logging']['max_bytes']
        backup_count = config['logging']['backup_count']

        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger("ApplicationLogger")
        logger.setLevel(getattr(logging, log_level))

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_level))

        logger.addHandler(file_handler)
        LoggerSingleton._instance = logger
