import json
import os
from pathlib import Path

class ConfigManager:
    _config_data = None

    @classmethod
    def load_config(cls):
        """ loads the configuration from a JSON file and caches it for future use. """
        if cls._config_data is None:
            # finding the config.json file relative to this script's location
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "config.json"

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Configuration file not found at: {config_path}")

            with open(config_path, "r", encoding="utf-8") as file:
                cls._config_data = json.load(file)
        
        return cls._config_data

    @classmethod
    def get_api_url(cls) -> str:
        return cls.load_config()["api"]["exchange_rate_url"]

    @classmethod
    def get_api_timeout(cls) -> int:
        return cls.load_config()["api"]["timeout_seconds"]

    @classmethod
    def get_crm_db_path(cls) -> str:
        return cls.load_config()["database"]["crm_db_path"]

    @classmethod
    def get_bank_db_path(cls) -> str:
        return cls.load_config()["database"]["bank_db_path"]

    @classmethod
    def get_allowed_deviation(cls) -> float:
        return cls.load_config()["business_logic"]["allowed_deviation_cents"]

# quick test to verify the configuration is loaded correctly
if __name__ == "__main__":
    print(f"Loaded API URL: {ConfigManager.get_api_url()}")
    print(f"CRM DB Path: {ConfigManager.get_crm_db_path()}")