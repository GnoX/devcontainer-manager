import os
import platform
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from .base_config import BaseYamlConfigModel, BaseYamlConfigModelWithBase, default_if_none
from .types import MountString
from .util import get_project_root_basename, render_recursive_template


class DevcontainerConfig(BaseYamlConfigModel):
    name: Optional[str] = Field("{{ project_root_basename }}", description="dev container name")

    workspace_folder: Optional[Path] = Field(
        Path("/mnt/workspace"),
        description="path in container where source will be mounted",
    )

    workspace_mount: Optional[MountString] = Field(
        MountString("${localWorkspaceFolder}:{{ devcontainer.workspace_folder }}"),
        description=(
            "same as workspaceMount in devcontainer.json - path for workspace and where\n"
            "to mount it; there are two available formats:\n"
            "   - same as devcontainer.json\n"
            "   - shortened form - '<local-path>:<remote-path>' - this will be translated\n"
            "     to 'src=<local-path>,dst=<remote-path>,type=bind,consistency=cached'"
        ),
    )
    shutdown_action: Optional[str] = Field(
        "none",
        description="same as shutdownAction in devcontainer.json",
    )
    user_env_probe: Optional[str] = Field(
        "loginInteractiveShell",
        description="same as userEnvProbe in devcontainer.json",
    )
    image: Optional[str] = Field(
        "{{ devcontainer.name }}-dev",
        description="devcontainer image to use",
    )
    mounts: Optional[List[MountString]] = Field(
        default_factory=list,
        description=(
            "additional mounts for container in format: `src:dst`, for example this\n"
            "will mount home folder to /mnt/home in the container\n"
            "mounts:\n"
            "   - /home/developer:/mnt/home"
        ),
    )
    container_name: Optional[str] = Field(
        "{{ devcontainer.name }}",
        description=(
            "name of the container - this will be passed as `--name <arg>` in `docker run`"
        ),
    )
    container_hostname: Optional[str] = Field(
        "{{ devcontainer.name }}",
        description=(
            "container hostname - this will be passed as `--hostname <arg>` in `docker run`\n"
            "this option is to make shell display the hostname as specified name instead\n"
            "of randomly generated container hex code"
        ),
    )
    run_args: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "aditional arguments that will be passed to `docker run` - i.e. adding gpus:\n"
            "run_args:\n"
            "- gpus=all"
        ),
    )

    extensions: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "default extensions to install - will be directly translated to devcontainer.json\n"
            "extensions"
        ),
    )
    additional_options: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "list of additional options to that will be appended to devcontainer config\n"
            "for example:\n"
            "additional_options:\n"
            "  - >\n"
            '    "dockerFile": "{{ docker.file }}"\n'
            '  - \'"appPort": "8080"\''
        ),
    )

    _not_none = validator("*", pre=True, allow_reuse=True)(default_if_none)


class DockerConfig(BaseYamlConfigModel):
    file: Optional[Path] = Field(
        None,
        description=(
            "path for base dockerfile to use for building custom image\n"
            "null means that the dockerfile will not be generated\n"
            "if the path is valid, two files will be generated - devcontainer.Dockerfile\n"
            "and build.sh script for building this dockerfile"
        ),
    )

    additional_commands: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "additional lines to append to dockerfile - this is useful if the main dockerfile\n"
            "does not contain developer tools, for example to add fish and git:\n"
            "\n"
            "additional_commands:\n"
            "- >\n"
            "  RUN apt-get update && apt-get install\n"
            "     fish procps git git-lfs\n"
            "  && rm -rf /var/lib/apt/lists/*\n"
            '- ENV SHELL="/usr/bin/fish"\n'
            "- ENV LANG=C.UTF-8 LANGUAGE=C.UTF-8 LC_ALL=C.UTF-8\n"
            '- SHELL ["fish", "--command"]\n'
            '- ENTRYPOINT ["fish"]'
        ),
    )

    _not_none = validator("*", pre=True, allow_reuse=True)(default_if_none)


class GlobalVariables(BaseModel):
    project_root_basename: str = Field(
        default_factory=get_project_root_basename, description="root directory of current project"
    )
    uid: str = Field(default_factory=os.getuid, description="id of current user")
    login: str = Field(default_factory=os.getlogin, description="username of current user")
    hostname: str = Field(default_factory=platform.node, description="hostname of current machine")

    def to_readme_string(self):
        global_variables_info = []
        for k in self.dict():
            field = self.__fields__[k]
            global_variables_info.append(f"{{{{ {k} }}}}: {field.field_info.description}")
        return "\n".join(global_variables_info) + "\n"


class Config(BaseYamlConfigModelWithBase):
    project_path: Path = Field(
        Path(),
        description=(
            "root path for current project relative to current working directory or\n"
            "absolute path"
        ),
    )
    devcontainer: Optional[DevcontainerConfig] = DevcontainerConfig()
    docker: Optional[DockerConfig] = DockerConfig()

    _not_none = validator("*", pre=True, allow_reuse=True)(default_if_none)

    def resolve(self, config_path: Path = None) -> "ResolvedConfig":
        values = self.dict()
        values.update(GlobalVariables().dict())

        cfg_copy: Config = self.copy(deep=True)
        cfg_copy.devcontainer.workspace_mount = (
            self.devcontainer.workspace_mount.to_devcontainer_format()
        )
        cfg_copy.devcontainer.mounts = [
            mount.to_devcontainer_format() for mount in cfg_copy.devcontainer.mounts
        ]

        rendered_template = render_recursive_template(cfg_copy.json(), values)
        new_config = Config.parse_raw(rendered_template)
        new_config.config_path = config_path if config_path is not None else self.config_path
        return ResolvedConfig.parse_obj(new_config.dict(exclude={"config_path": {}}))

    @classmethod
    def none(cls):
        return Config.construct(
            base_config=None,
            devcontainer=DevcontainerConfig.none(),
            docker=DockerConfig.none(),
        )


class ResolvedConfig(Config):
    @root_validator
    def validate_nested(cls, values):
        cls._validate_docker_path(values)
        return values

    def _validate_docker_path(values):
        docker: DockerConfig = values.get("docker")
        config_path: Path = values.get("config_path").resolve().parent
        docker_config_path = docker.file
        if docker_config_path is None:
            return

        if not docker_config_path.is_absolute():
            docker_config_path = (config_path / docker_config_path).resolve()

        if not docker_config_path.exists():
            raise ValueError(
                f"invalid value for 'docker.file' - path '{docker_config_path}' " "does not exist"
            )
        docker.file = Path(docker_config_path).read_text()
