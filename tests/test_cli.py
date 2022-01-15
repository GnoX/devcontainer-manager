import os
import shutil
from pathlib import Path

import oyaml as yaml
import pytest
from typer.testing import CliRunner

from devcontainer_manager.cli import app
from devcontainer_manager.config import DEFAULT_CONFIG_PATH, OVERRIDE_CONFIG
from devcontainer_manager.global_config import (
    DEFAULT_GLOBAL_CONFIG_PATH,
    GLOBAL_CONFIG_ENV_VAR,
    GLOBAL_CONFIG_FILENAME,
)


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@pytest.fixture(scope="module")
def default_config_dict():
    return yaml.safe_load(DEFAULT_CONFIG_PATH.read_text())


@pytest.fixture(scope="module")
def default_config_yaml(default_config_dict):
    return yaml.dump(default_config_dict)


@pytest.fixture(scope="function", autouse=True)
def global_config_path():
    data_path = Path("tests/data")
    data_path.mkdir(exist_ok=True, parents=True)
    os.environ[GLOBAL_CONFIG_ENV_VAR] = data_path.as_posix()
    yield data_path / GLOBAL_CONFIG_FILENAME
    shutil.rmtree(data_path)


@pytest.fixture(scope="module")
def default_global_config_yaml():
    return (
        yaml.dump(yaml.safe_load(DEFAULT_GLOBAL_CONFIG_PATH.read_text()))
        .replace("null", "")
        .strip()
    )


@pytest.fixture(scope="function")
def config_path(tmp_path):
    return tmp_path / "config.yaml"


@pytest.fixture(scope="function")
def config_dict(tmp_path):
    devcontainer_path = tmp_path / ".devcontainer"
    devcontainer_path.mkdir()
    config = dict(
        path=devcontainer_path.as_posix(),
        devcontainer=dict(
            name="test_name",
            workspace_folder="/mnt/test",
            workspace_mount="test_src:test_dst",
            shutdown_action="test_shutdown",
            user_env_probe="test_user_env_probe",
            image="test_image",
            test_mounts=["src=test_mnt_src,dst=test_mnt_dst"],
            container_name="test_container_name",
            container_hostname="test_container_hostname",
            test_run_args=["test_run_arg=test"],
            test_extensions=["test_extension"],
            test_additional_options=['"test_option": "test_value"'],
        ),
    )
    return config


def test_cli_create_config_command_creates_configs(
    runner,
    config_path,
    default_config_yaml,
    global_config_path,
    default_global_config_yaml,
):
    result = runner.invoke(app, ["create-config", config_path.as_posix()])

    assert result.exit_code == 0
    assert config_path.read_text() == default_config_yaml
    assert global_config_path.read_text().strip() == default_global_config_yaml


def test_cli_create_config_command_config_already_created(config_path, runner):
    config_path.write_text("test")

    result = runner.invoke(
        app, ["create-config", config_path.as_posix()], input="n\n"
    )

    assert result.exit_code == 1
    assert config_path.read_text() == "test"


def test_cli_create_config_command_config_force_recreate(
    config_path, runner, default_config_yaml
):
    config_path.write_text("test")

    result = runner.invoke(
        app, ["create-config", config_path.as_posix()], input="y\n"
    )

    assert result.exit_code == 0
    assert config_path.read_text() == default_config_yaml


def test_cli_generate_command(runner, config_path, config_dict):
    config_path.write_text(yaml.dump(config_dict))
    devcontainer_path = Path(config_dict["path"])

    result = runner.invoke(app, ["generate", config_path.as_posix()])

    devcontainer_json_path = devcontainer_path / "devcontainer.json"
    override_path = devcontainer_path / OVERRIDE_CONFIG

    assert result.exit_code == 0
    assert not (devcontainer_path / "Dockerfile").exists()
    assert not (devcontainer_path / "build.sh").exists()
    assert devcontainer_json_path.exists()
    assert override_path.exists()

    assert override_path.read_text().strip() == f"base_config: {config_path}"
