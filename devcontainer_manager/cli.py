import json
from pathlib import Path

import oyaml as yaml
import typer
from cookiecutter.main import cookiecutter

from devcontainer_manager.global_config import GlobalConfig

from .config import OVERRIDE_CONFIG, Config, OverrideConfig, default_config

TEMPLATE_DIR = Path(__file__).parent / "templates"

app = typer.Typer()


def conf_callback(ctx: typer.Context, param: typer.CallbackParam, value: Path):
    if value:
        try:
            conf = yaml.safe_load(value.read_text())

            ctx.default_map = ctx.default_map or {}
            ctx.default_map.update(conf)
        except Exception as ex:
            raise typer.BadParameter(str(ex))
    return value


@app.command(context_settings={"allow_extra_args": True})
def generate(
    ctx: typer.Context,
    config_path: Path = typer.Argument(
        "devcontainer_config.yaml", callback=conf_callback
    ),
):
    config = Config.parse(config_path.as_posix())
    global_config = GlobalConfig.load()

    if isinstance(config, OverrideConfig):
        override_config = config
    else:
        override_config = config.override(ctx.args)
        override_path = Path(config.path) / OVERRIDE_CONFIG
        override_config.write_yaml(override_path)

    default_merged = default_config().merge(global_config.global_defaults)
    global_merged = default_merged.merge(override_config)
    rendered = global_merged.render()

    cookiecutter_config = TEMPLATE_DIR / "cookiecutter.json"
    cookiecutter_config.write_text(json.dumps(rendered.as_dict(), indent=4))
    cookiecutter(
        TEMPLATE_DIR.as_posix(), no_input=True, overwrite_if_exists=True
    )

    devcontainer_dir = Path(config.path)
    if not config.docker.file:
        (devcontainer_dir / "devcontainer.Dockerfile").unlink()
        (devcontainer_dir / "build.sh").unlink()


@app.command()
def create_config(
    config_path: Path = typer.Argument("devcontainer_config.yaml"),
    force: bool = typer.Option(False, "--force", "-f"),
):
    GlobalConfig.load()
    config = default_config(config_path.as_posix())

    if config.yaml_exists() and not force:
        if not typer.confirm(
            f"Config '{config_path}' already exists, overwrite?"
        ):
            raise typer.Abort()

    config.write_yaml(config_path)


def main():
    app()


if __name__ == "__main__":
    main()
