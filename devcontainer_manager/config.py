from collections import OrderedDict
from pathlib import Path
from typing import List

import jinja2
import yaml
from cookiecutter.config import merge_configs

from .exceptions import InvalidArgumentException


def default_config():
    return OrderedDict(
        devcontainer=OrderedDict(
            path=".devcontainer",
            name="dev_env",
            workspace_path="/mnt/workspace",
            image="dev-env-dev",
            mounts=[],
            run_args=[],
            container_name="{{ devcontainer.name }}",
            container_hostname="{{ devcontainer.name }}",
            extensions=["ms-python.python"],
        ),
        dockerfile=None,
    )


def override_config_from_args(config, args):
    config = dict(config)
    for arg in args:
        current_level = config
        last_level = config
        parts = arg.split("=")
        if len(parts) != 2:
            raise InvalidArgumentException(f"Invalid parameter {arg}")

        name, value = parts
        name_parts = name.split(".")

        for part in name_parts:
            if part not in current_level:
                raise InvalidArgumentException(f"Invalid parameter {arg}")

            last_level = current_level
            current_level = current_level[part]
        last_level[part] = value
    return config


def parse_config(config_path: Path, dot_args: List[str] = None):
    if dot_args is None:
        dot_args = []

    config_dict = yaml.safe_load(config_path.read_text())
    config_override = yaml.dump(
        override_config_from_args(config_dict, dot_args)
    )
    config_dict = yaml.safe_load(
        jinja2.Template(config_override).render(**config_dict)
    )
    config = merge_configs(default_config(), config_dict)

    dockerfile = config["dockerfile"]
    if dockerfile is not None:
        if "content" in dockerfile:
            dockerfile_path = Path(dockerfile["content"])
            if dockerfile_path.exists():
                dockerfile["content"] = dockerfile_path.read_text()
        if "additional_commands" not in dockerfile:
            dockerfile["additional_commands"] = []

    return config
