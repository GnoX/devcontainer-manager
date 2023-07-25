from pathlib import Path
from typing import Dict, Optional

from pydantic import Field, validator

from .base_config import BaseYamlConfigModel, default_if_none

DEFAULT_ALIAS_FILENAME = "aliases.yaml"


class AliasConfig(BaseYamlConfigModel):
    aliases: Optional[Dict[str, Path]] = Field(
        default_factory=dict,
        description=(
            "aliases for templates, can be added using,\n`devcontainer_manager alias --help`"
        ),
    )

    _not_none = validator("*", pre=True, allow_reuse=True)(default_if_none)

    def is_alias(self, alias: str):
        if isinstance(alias, Path):
            alias = alias.as_posix()
        return alias in self.aliases

    def resolve(self, alias: str):
        if isinstance(alias, Path):
            alias = alias.as_posix()
        alias_path = self.aliases.get(alias, alias)
        if not alias_path.is_absolute():
            alias_path = self.config_path.parent / alias_path
        return alias_path

    def path_to_alias(self, path: Path):
        path = path.resolve()
        ret = [
            k
            for k, p in self.aliases.items()
            if p.resolve() == path or path.relative_to(self.config_path.parent) == p
        ][0]
        return path if not ret else ret
