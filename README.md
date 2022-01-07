# VSCode Devcontainer Manager

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
devcontainer_manager create-config <config-path>
```
This creates yaml file with all available options set do default. You can then
open the file and change the options in editor.

NOTE: There is currently no way to set the parameters from the command line.

The following code displays all of the options and defaults
```yaml
devcontainer:
    # path to generate devcontainer files
    path: .devcontainer

    # name of the dev container
    name: dev_env

    # path in container where source will be mounted
    workspace_path: /mnt/workspace

    # devcontainer image to use
    image: dev-env-dev

    # additional mounts for container in format: `src:dst`, for example this
    # will mount home folder to /mnt/home in the container
    # mounts:
    #   - /home/developer:/mnt/home
    mounts: []

    # name of the container - this will be passed as `--name <arg>` in `docker run`
    container_name: "{{ devcontainer.name }}"

    # container hostname - this will be passed as `--hostname <arg>` in `docker run`
    # this option is to make shell display the hostname as specified name instead
    # of randomly generated container hex code
    container_hostname: "{{ devcontainer.name }}"

    # aditional arguments that will be passed to `docker run` - i.e. adding gpus:
    # run_args:
    # - gpus=all
    run_args: []

    # default extensions to install - will be directly translated to devcontainer.json
    # extensions
    extensions: []

dockerfile:
    # path for base dockerfile to use for building custom image
    # null means that the dockerfile will not be generated
    # if the path is valid, two files will be generated - devcontainer.Dockerfile
    # and build.sh script for building this dockerfile
    path: null

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

Note that you can use `jinja2` templates in the config itself to reference other
options as displayed in `container_name` and `container_hostname`.


### Devconfig Generation
To generate the configuration
```shell
devcontainer_manager generate <config-path> [key_overrides]
```

Using default config, this would generate `devcontainer.json`
and `overrides.yaml` (more in the [Overrides](#per-project-template-overrides)
section) files (as dockerfile.path is null by default).

### Per Project Template Overrides
Note that `generate` command does have optional arguments that take form of
`key.subkey=value`, for example you always want to override the container name
```shell
devcontainer_manager generate /templates/python.yaml devcontainer.name=project_name
```

OR you can manually edit `.devcontainer/overrides.yaml`.

Once the overrides exist, you can then call each subsequent generation using
```sh
devcontainer_manager generate .devcontainer/overrides.yaml
```
This is also useful for easy generation when the master template changes.


`overrides.yaml` config contains `base_config` key that specifies absolute
path to template config, so if this file is moved, re-generation will fail.

## TODOS and Ideas
- automatic indexing of all overrides of master template
- templates from repositories, snippets or web pages
- automatic project name detection for simpler override generation
- better documentation and examples
- tests and CI
