from pathlib import Path
from typing import Dict, Optional

from pydantic import Field, validator

from .base_config import BaseYamlConfigModel, default_if_none

DEFAULT_ALIAS_FILENAME = "aliases.yaml"


class AliasConfig(BaseYamlConfigModel):
    aliases: Optional[Dict[str, Path]] = Field(
        default_factory=dict,
        description=(
            "aliases for templates, can be added using,\n" "`devcontainer_manager alias --help`"
        ),
    )

    _not_none = validator("*", pre=True, allow_reuse=True)(default_if_none)

    def resolve(self, alias):
        return self.aliases.get(alias, alias)
