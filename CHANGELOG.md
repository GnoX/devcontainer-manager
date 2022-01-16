# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- alias commands for templates
  - `alias add example config.yaml` - adds alias example
    for `config.yaml` file, this can then be used with with generate command -
    `generate example`
  - `alias list` - lists added examples
  - `alias remove example` - removes alias `example` if it exists
- if `generate` command is ran without arguments, script generates template using
  `.devcontainer/overrides.yaml` config if it exists
### Changed
- `create-config` renamed to `create-template` and added global template
  functionality - if extension is not specified, global template is created
  in folder specified by global config `template_dir` and alias is created
- default for image name is now `{{ devcontainer.name }}-dev`

## [0.3.0] - 2021-01-16
### Added
- template variable `project_root_basename` that resolves to root folder basename
  of project git repository
- global config with default overrides `~/.devcontainer_manager/config.yaml`

### Changed
- changed default of `devcontainer.name` to `project_root_basename`

## [0.2.0] - 2021-01-15
### Added
- config options:
    - `devcontainer.workspace_mount` - same as workspaceMount in `devcontainer.json`
    - `user_env_probe` - same as `userEnvProbe`
    - `shutdown_action` - same as `shutdownAction`
    - `additional_options_json` - list of additional json options to append to
      `devcontainer.json`
### Changed
- renamed config options:
    - `devcontainer.path` -> `path`
    - `devcontainer.workspace_path` -> `devcontainer.workspace_folder`
    - `dockerfile` -> `docker`

### Fixed
- crash in generate if devcontainer folder does not exist

## [0.1.2] - 2021-01-07
### Added
- first release on pypi with basic config template creation, devcontainer
  generation supporting most of the container options and generation of
  Dockerfile with build script.
