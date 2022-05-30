import os

import pytest
from typer.testing import CliRunner

from devcontainer_manager.cli.cli import app
from devcontainer_manager.config import Config
from devcontainer_manager.global_config import GlobalConfig
from devcontainer_manager.settings import Settings


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@pytest.fixture(scope="function", autouse=True)
def global_settings(tmp_path):
    data_path = tmp_path / "global"
    data_path.mkdir(exist_ok=True, parents=True)
    os.environ[f"{Settings.Config.env_prefix}_{'global_config_dir'}"] = data_path.as_posix()
    return Settings()


@pytest.fixture(scope="function")
def config_path(tmp_path):
    return tmp_path / "config.yaml"


def test_cli_create_template_command_creates_configs(
    runner,
    config_path,
):
    result = runner.invoke(app, ["create-template", config_path.as_posix()])

    assert result.exit_code == 0
    assert Config.parse_file(config_path) == Config()
    assert GlobalConfig.load() == GlobalConfig()


def test_cli_create_template_command_config_already_created(config_path, runner):
    config_path.write_text("test")

    result = runner.invoke(app, ["create-template", config_path.as_posix()], input="n\n")

    assert result.exit_code == 1
    assert config_path.read_text() == "test"


def test_cli_create_template_command_config_force_recreate(
    config_path,
    runner,
):
    config_path.write_text("test")

    result = runner.invoke(app, ["create-template", config_path.as_posix()], input="y\n")

    assert result.exit_code == 0
    assert Config.parse_file(config_path) == Config()
