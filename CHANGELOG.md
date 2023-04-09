# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- fixed alias resolving during config generation if alias is used as base config
- fixed docker file path validation when path is set from a template

## [1.3.0] - 2022-12-11
### Changed
- changed `base_config` in composed configs to use aliases instead of full
  paths

### Removed
- removed option to generate `.vscode` settings folder as it was only useful
  for specifying `docker.host` which does not work with new devcontainer
  versions

## [1.2.3] - 2022-11-14
### Fixed
- fixed crash on python <3.9 due to union operator available only from 3.9

## [1.2.2] - 2022-11-14
### Added
- added readme section about pre-defined config variables


## [1.2.1] - 2022-11-13
### Added
- added option `--print` to print the config without generation

## [1.2.0] - 2022-11-13
### Added
- added `vscode` config option that generates `.vscode/settings.json` with
  specified options - for now, it completely overrides `settings.json`, so
  use with caution
- added variables `uid`, `login` and `hostname` that can be used in any config

### Changed
- replaced option `path` by `project_path` as now this tool generates multiple
  folders

### Fixed
- fixed crash when running container with uppercase project root folder names

## [1.1.4] - 2022-06-13
### Fixed
- fixed crash for override configs

## [1.1.3] - 2022-06-11
### Fixed
- fixed crash for pythons <3.9 and >3.10

## [1.1.2] - 2022-06-06
### Fixed
- fixed mounts not being resolved in devcontainer.json

## [1.1.1] - 2022-05-30
### Added
- added message with template path after running generate with global template

## [1.1.0] - 2022-05-30
### Added
- added flag `--build` to `generate` subcommand that runs docker build after
  config generation
- added `--version` flag

### Fixed
- fixed crash for python < 3.9 due to wrong type annotations
- added missing required packages `pydantic` and `pydantic_yaml`

## [1.0.0] - 2022-05-30
### Added
- added config key `base_config` that accepts list of other configs, these configs
  will be merged in list order

### Changed
- completely rewriten configs to pydantic
- global config structure was changed, to migrate, change:
  - `global_defaults` renamed to `defaults`
  - `aliases` moved to separate config - `aliases.yaml`
  - added new option `override_config_path` by default `overrides.yaml`
- config structure migration:
  - rename `additional_options_json` to `additional_options`
- changed `devcontainer_manager generate` arguments - now it accepts multiple configurations
  which will be merged in order of arguments from left to right

## [0.4.4] 2022-01-22
### Changed
- switched PyYAML to ruamel.yaml - yaml comments in configs will now be preserved

### Fixed
- fixed config list items being deduplicated and shuffled

## [0.4.3] 2022-01-16
### Changed
- disabled default flow style dumping for older yaml versions
## [0.4.2] 2022-01-16
### Fixed
- included missing default configs in package

## [0.4.1] 2022-01-16
### Fixed
- included subpackages in setup
## [0.4.0] 2022-01-16
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

## [0.3.0] - 2022-01-16
### Added
- template variable `project_root_basename` that resolves to root folder basename
  of project git repository
- global config with default overrides `~/.devcontainer_manager/config.yaml`

### Changed
- changed default of `devcontainer.name` to `project_root_basename`

## [0.2.0] - 2022-01-15
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

## [0.1.2] - 2022-01-07
### Added
- first release on pypi with basic config template creation, devcontainer
  generation supporting most of the container options and generation of
  Dockerfile with build script.
