import yaml
from typing import Dict, Any

class TestConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_commands(self) -> Dict[str, Any]:
        return self.config_data.get('commands', {})
