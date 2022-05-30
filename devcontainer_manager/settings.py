from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    global_config_filename = "config.yaml"
    global_config_dir = Path().home() / ".devcontainer_manager"

    @property
    def global_config_path(self):
        return self.global_config_dir / self.global_config_filename

    class Config:
        env_prefix = "devcontainer_manager_"
        case_insensitive = True
