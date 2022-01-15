import copy
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List

import jinja2
import oyaml as yaml

from .exceptions import (
    ConfigMovedException,
    InvalidArgumentException,
    InvalidMountStringException,
)

OVERRIDE_CONFIG = "overrides.yaml"

DEVCONTAINER_MOUNT_STR_REGEX = re.compile(r"^src=(.+),dst=(.+)(,.+)?")
SIMPLE_MOUNT_REGEX = re.compile(r"(?P<src>.+):(?P<dst>.+)")


def default_config():
    return OrderedDict(
        path=".devcontainer",
        devcontainer=OrderedDict(
            name="dev_env",
            workspace_mount="${localWorkspaceFolder}:/mnt/workspace",
            workspace_folder="/mnt/workspace",
            user_env_probe="loginInteractiveShell",
            shutdown_action="none",
            image="dev-env-dev",
            mounts=[],
            run_args=[],
            container_name="{{ devcontainer.name }}",
            container_hostname="{{ devcontainer.name }}",
            extensions=[],
            additional_options_json=[],
        ),
        docker=OrderedDict(file=None, additional_commands=[]),
    )


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


def get_config_overrides(config: dict, args: List[str]):
    config = dict(config)
    overrides: Dict[str, Any] = dict()

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
            last_overrides[part] = [v.strip() for v in value[1:-1].split(",")]
        else:
            last_overrides[part] = value
    return overrides


def merge_configs(default, overwrite):
    new_config = copy.deepcopy(default)

    for k, v in overwrite.items():
        if isinstance(v, dict):
            new_config[k] = merge_configs(default[k], v)
        elif isinstance(v, list):
            new_config[k] = list(set(default[k] + v))
        else:
            new_config[k] = v

    return new_config


def parse_config(
    config_path: Path, dot_args: List[str] = None, return_overrides=False
):
    if dot_args is None:
        dot_args = []
    config_dict = yaml.safe_load(config_path.read_text())

    if "base_config" in config_dict:
        base_config_path = Path(config_dict["base_config"])
        if not base_config_path.exists():
            raise ConfigMovedException(
                f"Config '{base_config_path}' was deleted or moved"
            )
        config_dict.pop("base_config")

        config_base = yaml.safe_load(base_config_path.read_text())
        config_override = yaml.dump(merge_configs(config_base, config_dict))
    else:
        overrides = get_config_overrides(config_dict, dot_args)

        config_override = merge_configs(config_dict, overrides)
        config_dict = config_override
        config_override = yaml.dump(config_override)

        devcontainer_dir = Path(config_dict["path"])
        override_config = devcontainer_dir / OVERRIDE_CONFIG

        overrides["base_config"] = config_path.resolve().as_posix()
        override_config.parent.mkdir(parents=True, exist_ok=True)
        override_config.write_text(yaml.dump(overrides))

    config_dict = yaml.safe_load(
        jinja2.Template(config_override).render(**config_dict)
    )
    config = merge_configs(default_config(), config_dict)

    docker_config = config["docker"]
    if docker_config is not None:
        if "file" in docker_config and docker_config["file"] is not None:
            dockerfile_path = Path(docker_config["file"])
            if dockerfile_path.exists():
                docker_config["file"] = dockerfile_path.read_text()
        if "additional_commands" not in docker_config:
            docker_config["additional_commands"] = []

    config["devcontainer"]["workspace_mount"] = resolve_mount_string(
        config["devcontainer"]["workspace_mount"]
    )

    return config if not return_overrides else (config, overrides)
