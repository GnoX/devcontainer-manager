# VSCode Devcontainer Manager

[![PyPI](https://img.shields.io/pypi/v/devcontainer-manager?logo=pypi&style=flat-square)](https://pypi.org/project/devcontainer-manager)

Devcontainer Manager is a command line tool that manages Visual Studio Code
devcontainer configurations written in python.

## Installation

Project can be installed using pip:
```shell
pip install devcontainer-manager
```

This installs command line utility `devcontainer_manager`, see `--help` option for
all available commands.


## Usage

### Configuration

First step is to create default master configuration with
```shell
devcontainer_manager create-template <config-path>
```
This creates yaml file with all available options set to default. You can then
open the file and change the options in editor.

If you specify `config-path` without `.yaml` suffix then it is considered
global template.  Global templates are saved to
`~/.devcontainer_manager/templates/<config-path>.yaml` and alias is created.
This can then be used in generate directly as `config-path`, for example:
```
devcontainer_manager create-template python
# modify ~/.devcontainer_manager/templates/python.yaml
devcontainer_manager generate python
```

The following code displays all of the options and defaults

[//]: # (template_config_block_start)
```yaml
base_config: []

# custom path for devcontainer settings
path: .devcontainer
devcontainer:

    # dev container name
    name: '{{ project_root_basename }}'

    # path in container where source will be mounted
    workspace_folder: /mnt/workspace

    # same as workspaceMount in devcontainer.json - path for workspace and where
    # to mount it; there are two available formats:
    #    - same as devcontainer.json
    #    - shortened form - '<local-path>:<remote-path>' - this will be translated
    #      to 'src=<local-path>,dst=<remote-path>,type=bind,consistency=cached'
    workspace_mount: ${localWorkspaceFolder}:{{ devcontainer.workspace_folder }}

    # same as shutdownAction in devcontainer.json
    shutdown_action: none

    # same as userEnvProbe in devcontainer.json
    user_env_probe: loginInteractiveShell

    # devcontainer image to use
    image: '{{ devcontainer.name }}-dev'

    # additional mounts for container in format: `src:dst`, for example this
    # will mount home folder to /mnt/home in the container
    # mounts:
    #    - /home/developer:/mnt/home
    mounts: []

    # name of the container - this will be passed as `--name <arg>` in `docker run`
    container_name: '{{ devcontainer.name }}'

    # container hostname - this will be passed as `--hostname <arg>` in `docker run`
    # this option is to make shell display the hostname as specified name instead
    # of randomly generated container hex code
    container_hostname: '{{ devcontainer.name }}'

    # aditional arguments that will be passed to `docker run` - i.e. adding gpus:
    # run_args:
    # - gpus=all
    run_args: []

    # default extensions to install - will be directly translated to devcontainer.json
    # extensions
    extensions: []

    # list of additional options to that will be appended to devcontainer config
    # for example:
    # additional_options:
    #   - >
    #     "dockerFile": "{{ docker.file }}"
    #   - '"appPort": "8080"'
    additional_options: []
docker:

    # path for base dockerfile to use for building custom image
    # null means that the dockerfile will not be generated
    # if the path is valid, two files will be generated - devcontainer.Dockerfile
    # and build.sh script for building this dockerfile
    file:

    # additional lines to append to dockerfile - this is useful if the main dockerfile
    # does not contain developer tools, for example to add fish and git:
    #
    # additional_commands:
    # - >
    #   RUN apt-get update && apt-get install
    #      fish procps git git-lfs
    #   && rm -rf /var/lib/apt/lists/*
    # - ENV SHELL="/usr/bin/fish"
    # - ENV LANG=C.UTF-8 LANGUAGE=C.UTF-8 LC_ALL=C.UTF-8
    # - SHELL ["fish", "--command"]
    # - ENTRYPOINT ["fish"]
    additional_commands: []
```
[//]: # (template_config_block_end)

Note that you can use `jinja2` templates in the config itself to reference other
options as displayed in `container_name` and `container_hostname`.


### Devconfig Generation
To generate the configuration
```shell
devcontainer_manager generate [config-paths]
```

Using default config, this would generate `devcontainer.json` and `overrides.yaml`
(more in the [Project Overrides](#per-project-template-overrides) section) files
(as docker.path is null by default).

If you specify more configs, then they are merged from left to right.

If config-paths is not specified then `.devcontainer/overrides.yaml` is used for
generation if it exists.


### Global Configuration
Global configuration can be found in `~/.devcontainer_manager/config.yaml` and
contains following options:

[//]: # (global_config_block_start)
```yaml
base_config: []

# default values for all configs for the current environment
defaults: {}

# directory for global templates
template_dir: templates

# default path for per-project override config (. is in '.devcontainer/')
override_config_path: overrides.yaml
```
[//]: # (global_config_block_end)

### Per Project Template Overrides
To edit overrides, you can manually edit generated `.devcontainer/overrides.yaml`.

Once the overrides exist, you can then call each subsequent generation using
```sh
devcontainer_manager generate
```
This is also useful for easy generation when the master template changes.
