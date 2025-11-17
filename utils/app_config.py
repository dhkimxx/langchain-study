import yaml
import os


class AppConfig:
    _instance = None

    def __new__(cls, config_path: str = "config.yaml"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            with open(config_path, "r") as f:
                cls._instance._cfg = yaml.safe_load(f)
        return cls._instance

    @property
    def vector_db_path(self) -> str:
        return self._cfg["app"]["vector_db_path"]

    @property
    def techletter_base_url(self) -> str:
        return self._cfg["app"]["techletter_base_url"]

    def get_chain_config(self, name: str) -> dict:
        return self._cfg["chains"][name]


CONFIG = AppConfig()
