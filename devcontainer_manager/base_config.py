from functools import reduce
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field, validator
from pydantic.fields import ModelField
from pydantic_yaml import YamlModel

from .util import dict_merge
from .yaml import yaml

if TYPE_CHECKING:
    Model = TypeVar("Model", bound="BaseModel")


def default_if_none(cls, v, field: ModelField):
    if v is None:
        if getattr(field, "default", None) is not None:
            return field.default
        if field.default_factory is not None:
            return field.default_factory()
    else:
        return v


class BaseYamlConfigModel(YamlModel):
    config_path: Path = Field(Path("."), exclude=True)

    def __or__(self, other: "Model") -> "Model":
        return type(self).parse_obj(
            dict_merge(
                self.dict(exclude={"config_path": {}}, exclude_defaults=True),
                other.dict(exclude={"config_path": {}}, exclude_defaults=True),
            )
        )

    @classmethod
    def parse_file(
        cls: Type["Model"],
        path: Union[str, Path],
        **kwargs,
    ) -> "Model":
        obj = super(BaseYamlConfigModel, cls).parse_file(path, **kwargs)
        obj.config_path = Path(path)
        return obj

    def yaml(self, with_descriptions=False, **dict_kwargs):
        if with_descriptions:
            yaml_dict = yaml.load(self.yaml(**dict_kwargs))
            _construct_yaml_dict_with_comments(type(self), yaml_dict)
        else:
            yaml_dict = self.dict(**dict_kwargs)
        return yaml.dump_str(yaml_dict)

    def write_yaml(self, path: Path = None, create_parents: bool = True, **yaml_kwargs):
        if path is None:
            path = self.config_path
        if create_parents:
            path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(self.yaml(**yaml_kwargs))

    @classmethod
    @property
    def NONE(cls: Type["Model"]) -> "Model":
        return cls.construct(**{field: None for field in cls.__fields__})


class BaseYamlConfigModelWithBase(BaseYamlConfigModel):
    base_config: Optional[List[Path]] = Field(default_factory=list)

    @validator("base_config", pre=True)
    def ensure_base_config_type(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [Path(v)]
        if isinstance(v, Iterable):
            return list(v)
        if isinstance(v, Path):
            return [v]
        raise ValueError(f"invalid value for base_config: '{v}'")

    def merge_bases(self):
        base_configs = [
            config_path if config_path.is_absolute() else self.config_path.parent / config_path
            for config_path in self.base_config
        ]
        base_configs = [
            type(self).parse_file(config_path).merge_bases() for config_path in base_configs
        ]
        if not base_configs:
            return self

        bases_merged = reduce(lambda a, b: a | b, base_configs)
        return bases_merged | self


def _construct_yaml_dict_with_comments(cls, d, column=0):
    for k, v in d.items():
        field = cls.__fields__[k]
        if issubclass(field.type_, BaseModel):
            _construct_yaml_dict_with_comments(field.type_, v, column + 4)

        if field.field_info.description:
            d.yaml_set_comment_before_key(k, field.field_info.description, column=column)
            d.yaml_add_newline_before_key(k)
