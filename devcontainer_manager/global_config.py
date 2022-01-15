import os
from pathlib import Path
from typing import Any

import oyaml as yaml

from .config import Config, DevcontainerConfig

GLOBAL_CONFIG_ENV_VAR = "DEVCONTAINER_MANAGER_DIR"

GLOBAL_CONFIG_FILENAME = "config.yaml"
GLOBAL_CONFIG_PATH = (
    Path().home() / ".devcontainer_manager" / GLOBAL_CONFIG_FILENAME
)
DEFAULT_GLOBAL_CONFIG_PATH = (
    Path(__file__).parent / "config" / "default_global_config.yaml"
)


class GlobalConfig(Config):
    def __init__(self, config: dict, path=None):
        super().__init__(config, path)

    def __getattribute__(self, name: str) -> Any:
        if name in ["global_defaults"]:
            return DevcontainerConfig(self.__dict__["global_defaults"])
        return super().__getattribute__(name)

    @staticmethod
    def load():
        config_path = os.environ.get(GLOBAL_CONFIG_ENV_VAR, None)
        if config_path is None:
            config_path = GLOBAL_CONFIG_PATH
        else:
            config_path = Path(config_path) / GLOBAL_CONFIG_FILENAME

        if config_path.exists():
            global_config_content = config_path.read_text()
        else:
            global_config_content = DEFAULT_GLOBAL_CONFIG_PATH.read_text()
            config_path.parent.mkdir(exist_ok=True, parents=True)
            config_path.write_text(global_config_content)

        return GlobalConfig(
            yaml.safe_load(global_config_content), config_path.as_posix()
        )
