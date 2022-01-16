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


def get_default_global_config(path: str = None):
    return GlobalConfig(
        yaml.safe_load(DEFAULT_GLOBAL_CONFIG_PATH.read_text()), path
    )


class GlobalConfig(Config):
    def __init__(self, config: dict, path=None):
        super().__init__(config, path)

    def __getattribute__(self, name: str) -> Any:
        if name == "global_defaults":
            return DevcontainerConfig(self.__dict__["global_defaults"])
        if name == "aliases" and (
            name not in self.__dict__ or self.__dict__[name] is None
        ):
            self.__dict__[name] = dict()

        return super().__getattribute__(name)

    def resolve_template_dir(self):
        template_dir = Path(self.template_dir)
        if not template_dir.is_absolute():
            config_path = self.absolute_config_path.parent
            return config_path / template_dir

        return template_dir

    def resolve_alias(self, alias: str):
        alias_map = self.aliases if self.aliases else {}
        return Path(alias_map[alias]) if alias in alias_map else alias

    def add_alias(self, alias: str, path: str):
        self.aliases[alias] = path

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
        default_config = get_default_global_config(config_path.as_posix())
        global_config = GlobalConfig(
            yaml.safe_load(global_config_content), config_path.as_posix()
        )
        return default_config.merge(global_config)
