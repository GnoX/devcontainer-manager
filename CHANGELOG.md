# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]
### Added
- config options:
    - devcontainer.workspace_mount - same as workspaceMount in devcontainer.json
    - user_env_probe - same as userEnvProbe
    - shutdown_action - same as shutdownAction
    - additional_options_json - list of additional json options to append to
      devcontainer.json
### Changed
- renamed config options:
    - devcontainer.path -> path
    - devcontainer.workspace_path -> devcontainer.workspace_folder
    - dockerfile -> docker

### Fixed
- crash in generate if devcontainer folder does not exist

## [0.1.2] - 2021-01-07
### Added
- first release on pypi with basic config template creation, devcontainer
  generation supporting most of the container options and generation of
  Dockerfile with build script.
