from pathlib import Path

from pydantic import Field, validator

from .alias import DEFAULT_ALIAS_FILENAME, AliasConfig
from .base_config import BaseYamlConfigModelWithBase, default_if_none
from .config import Config
from .settings import Settings


class GlobalConfig(BaseYamlConfigModelWithBase):
    defaults: Config = Field(
        default_factory=Config,
        description="default values for all configs for the current environment",
    )
    template_dir: Path = Field(
        Path("./templates"),
        description="directory for global templates",
    )
    override_config_path: Path = Field(
        Path("overrides.yaml"),
        description=("default path for per-project override config (. is in '.devcontainer/')"),
    )

    _not_none = validator("*", pre=True, allow_reuse=True)(default_if_none)

    def load_alias_config(self):
        alias_config_path = self.config_path.parent / DEFAULT_ALIAS_FILENAME
        if not alias_config_path.exists():
            AliasConfig().write_yaml(alias_config_path)

        return AliasConfig.parse_file(alias_config_path)

    @classmethod
    def load(
        cls, settings: Settings = Settings(), create_if_not_exist: bool = False
    ) -> "GlobalConfig":
        config_path = settings.global_config_path
        if not config_path.exists():
            if create_if_not_exist:
                global_config = GlobalConfig()
                global_config.write_yaml(config_path, with_descriptions=True)
                global_config.config_path = config_path
                return global_config
            return None
        return GlobalConfig.parse_file(config_path)
