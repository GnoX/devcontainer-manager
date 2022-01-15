from pathlib import Path
from typing import Any

import oyaml as yaml

from .config import Config, DevcontainerConfig

GLOBAL_CONFIG_PATH = Path().home() / ".devcontainer_manager" / "config.yaml"
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
        if GLOBAL_CONFIG_PATH.exists():
            global_config_content = GLOBAL_CONFIG_PATH.read_text()
        else:
            global_config_content = DEFAULT_GLOBAL_CONFIG_PATH.read_text()
            GLOBAL_CONFIG_PATH.parent.mkdir(exist_ok=True, parents=True)
            GLOBAL_CONFIG_PATH.write_text(global_config_content)

        return GlobalConfig(
            yaml.safe_load(global_config_content),
            GLOBAL_CONFIG_PATH.as_posix(),
        )
