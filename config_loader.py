# config_loader.py

import yaml

class ConfigManager:
    _instance = None

    @staticmethod
    def get_instance(config_path="config/config.yaml"):
        if ConfigManager._instance is None:
            ConfigManager(config_path)
        return ConfigManager._instance

    def __init__(self, config_path):
        if ConfigManager._instance is not None:
            raise Exception("This class is a singleton!")

        self.config_path = config_path
        self.config = self._load_config()

        ConfigManager._instance = self

    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return {}

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value else default
