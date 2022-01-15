import copy
import re
from pathlib import Path
from typing import Any, Dict, List, Union

import oyaml as yaml

from .exceptions import (
    ConfigMovedException,
    InvalidArgumentException,
    InvalidMountStringException,
)
from .util import get_project_root_basename, render_recursive_template

OVERRIDE_CONFIG = "overrides.yaml"

DEVCONTAINER_MOUNT_STR_REGEX = re.compile(r"^src=(.+),dst=(.+)(,.+)?")
SIMPLE_MOUNT_REGEX = re.compile(r"(?P<src>.+):(?P<dst>.+)")
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "default_config.yaml"


def default_config(path: str = None):
    return Config.parse(DEFAULT_CONFIG_PATH.as_posix(), path)


def resolve_mount_string(mnt_str: str):
    match = SIMPLE_MOUNT_REGEX.match(mnt_str)
    if match is not None:
        return (
            f"src={match.group('src')},"
            f"dst={match.group('dst')},"
            "type=bind,consistency=cached"
        )

    match = DEVCONTAINER_MOUNT_STR_REGEX.match(mnt_str)
    if match is not None:
        return mnt_str

    raise InvalidMountStringException(mnt_str)


def dict_merge(d, overwrite):
    new_config = copy.deepcopy(d)

    for k, v in overwrite.items():
        if isinstance(v, dict):
            orig_dict = d[k] if k in d else dict()
            new_config[k] = dict_merge(orig_dict, v)
        elif isinstance(v, list):
            orig_list = d[k] if k in d else list()
            new_config[k] = list(set(orig_list + v))
        else:
            new_config[k] = v

    return new_config


class WritableNamespace:
    def __init__(self, d):
        self.__dict__ = d if d is not None else {}

    def __getattr__(self, name: str) -> Any:
        return WritableNamespace(None)

    def __bool__(self):
        return bool(self.__dict__)

    def __repr__(self) -> str:
        attr_str = ", ".join([f"{k}='{v}'" for k, v in self.__dict__.items()])
        return f"{self.__class__.__name__}({attr_str})"

    def __eq__(self, o: object) -> bool:
        if o is None and not self.__dict__:
            return True

        return super().__eq__(o)


class Config(WritableNamespace):
    def __init__(self, config: dict, path=None):
        super().__init__(config)
        if isinstance(path, Path):
            path = str(path)
        self.config_path = path

    def as_dict(self):
        d = self.__dict__.copy()
        d.pop("config_path")
        return d

    def as_yaml(self) -> str:
        return yaml.dump(self.as_dict())

    def write_yaml(self, config_path=None):
        config_path = self._get_config_path(config_path)
        config_path.parent.mkdir(exist_ok=True, parents=True)
        config_path.write_text(self.as_yaml())

    def yaml_exists(self):
        return self._get_config_path().exists()

    def merge(self, other: "Config"):
        return type(self)(dict_merge(self.as_dict(), other.as_dict()))

    def render(self):
        project_name = get_project_root_basename().strip()
        if project_name is None:
            project_name = "dev-env"

        values = copy.deepcopy(self.as_dict())
        values["project_root_basename"] = project_name

        config_dict = yaml.safe_load(
            render_recursive_template(yaml.dump(self.as_dict()), values)
        )
        config = DevcontainerConfig(config_dict)
        config = default_config().merge(config)

        if config.docker.file:
            dockerfile_path = Path(config.docker.file)
            if dockerfile_path.exists():
                config.docker.file = dockerfile_path.read_text()

        config.devcontainer.workspace_mount = resolve_mount_string(
            config.devcontainer.workspace_mount
        )
        return config

    def override(self, args: List[str]):
        overrides: Dict[str, Any] = dict()
        config = dict(self.__dict__)

        for arg in args:
            current_level = config
            current_overrides = overrides

            parts = arg.split("=")
            if len(parts) != 2:
                raise InvalidArgumentException(f"Invalid parameter {arg}")

            name, value = parts
            name_parts = name.split(".")

            for part in name_parts:
                if part not in current_level:
                    raise InvalidArgumentException(f"Invalid parameter {arg}")

                last_overrides = current_overrides
                if part not in current_overrides:
                    current_overrides[part] = {}
                current_overrides = current_overrides[part]
                current_level = current_level[part]
            if value.startswith("[") and value.endswith("]"):
                last_overrides[part] = [
                    v.strip() for v in value[1:-1].split(",")
                ]
            else:
                last_overrides[part] = value

        overrides["base_config"] = self.config_path
        return OverrideConfig(overrides)

    def _get_config_path(self, config_path=None):
        if config_path is None:
            config_path = self.config_path

        if config_path is None:
            return RuntimeError("Config path is empty")

        config_path = Path(config_path)
        if config_path.is_dir():
            return RuntimeError(
                f"Config path must be file but is dir: '{config_path}'"
            )
        return config_path

    @staticmethod
    def parse(path: str, override_path: str = None):
        file_path = Path(path)
        if override_path is None:
            override_path = file_path.as_posix()
        override = Path(override_path).resolve().as_posix()

        if file_path.exists() and file_path.is_file():
            config_dict = yaml.safe_load(file_path.read_text())
            if "base_config" in config_dict:
                return OverrideConfig(config_dict, override)

            return DevcontainerConfig(config_dict, override)


class DevcontainerConfig(Config):
    def __init__(self, config: dict, path: Union[str, Path] = None):
        super().__init__(config, path)

    def __getattribute__(self, name: str) -> Any:
        if name in ["devcontainer", "docker"]:
            d = self.__dict__[name] if name in self.__dict__ else None
            return WritableNamespace(d)

        return super().__getattribute__(name)


class OverrideConfig(DevcontainerConfig):
    def __init__(self, config: dict, path: Union[str, Path] = None):
        base_config_path = Path(config["base_config"])
        if not base_config_path.exists():
            raise ConfigMovedException(
                f"Config '{base_config_path}' was deleted or moved"
            )

        super().__init__(config, path)
        self.config_base = DevcontainerConfig(
            yaml.safe_load(base_config_path.read_text())
        )

    def __getattribute__(self, name: str) -> Any:
        if (
            name not in ["__dict__", "config_base"]
            and name not in self.__dict__
            and name in self.config_base.__dict__
        ):
            return getattr(self.config_base, name)

        return super().__getattribute__(name)

    def as_dict(self):
        return super().as_dict()["config_base"].as_dict()

    def as_yaml(self) -> str:
        d = super().as_dict().copy()
        d.pop("config_base")
        return yaml.dump(d)
