import json
from pathlib import Path

import oyaml as yaml
import typer
from cookiecutter.main import cookiecutter

from .config import default_config, parse_config

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
    config = parse_config(config_path, ctx.args)

    cookiecutter_config = TEMPLATE_DIR / "cookiecutter.json"
    cookiecutter_config.write_text(json.dumps(config, indent=4))
    cookiecutter(
        TEMPLATE_DIR.as_posix(), no_input=True, overwrite_if_exists=True
    )

    devcontainer_dir = Path(config["devcontainer"]["path"])
    if config["dockerfile"]["file"] is None:
        (devcontainer_dir / "devcontainer.Dockerfile").unlink()
        (devcontainer_dir / "build.sh").unlink()


@app.command()
def create_config(
    config_path: Path = typer.Argument("devcontainer_config.yaml"),
    force: bool = False,
):
    config = default_config()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists() and (
        not force
        or not typer.confirm(
            f"Config '{config_path}' already exists, overwrite?"
        )
    ):
        raise typer.Abort()

    config_path.write_text(yaml.dump(config))


def main():
    app()


if __name__ == "__main__":
    main()
