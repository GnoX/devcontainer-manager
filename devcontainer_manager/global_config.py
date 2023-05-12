from functools import cached_property
from pathlib import Path

from pydantic import Field, validator

from .alias import DEFAULT_ALIAS_FILENAME, AliasConfig
from .base_config import BaseYamlConfigModelWithBase, default_if_none
from .config import Config
from .settings import Settings


class GlobalConfig(BaseYamlConfigModelWithBase):
    template_dir: Path = Field(
        Path("./templates"),
        description="directory for global templates",
    )
    override_config_path: Path = Field(
        Path(".devcontainer/overrides.yaml"),
        description="default path for per-project override config (. is in '.devcontainer/')",
    )

    default_config_path: Path = Field(
        "{{ template_dir }}/default.yaml",
        description="path to global config that will be used as base for all other configs",
    )

    _not_none = validator("*", pre=True, allow_reuse=True)(default_if_none)

    class Config:
        keep_untouched = (cached_property,)

    def load_alias_config(self) -> AliasConfig:
        alias_config_path = self.config_path.parent / DEFAULT_ALIAS_FILENAME
        if not alias_config_path.exists():
            AliasConfig().write_yaml(alias_config_path)

        return AliasConfig.parse_file(alias_config_path)

    @cached_property
    def defaults(self):
        config_path = self.default_config_path
        if not self.default_config_path.is_absolute():
            config_path = self.config_path.parent / self.default_config_path
        return Config.parse_file(config_path)

    @classmethod
    def load(
        cls, settings: Settings = Settings(), create_if_not_exist: bool = False
    ) -> "GlobalConfig":
        config_path = settings.global_config_path.resolve()
        if not config_path.exists():
            if create_if_not_exist:
                global_config = GlobalConfig()
                global_config.write_yaml(config_path, with_descriptions=True)
                global_config.config_path = config_path
                return cls.load(settings)
            return None

        global_config = GlobalConfig.parse_file(config_path, resolve=True)
        default_config_path = global_config.default_config_path
        if not default_config_path.is_absolute():
            default_config_path = config_path.parent / default_config_path
            if not default_config_path.exists():
                Config().write_yaml(default_config_path, with_descriptions=True)

        return global_config
