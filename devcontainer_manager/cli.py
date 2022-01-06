import json
from pathlib import Path

import typer
import yaml
from cookiecutter.main import cookiecutter

from devcontainer_manager.util import setup_yaml

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
    config_path: Path = typer.Argument("config.yaml", callback=conf_callback),
):
    config = parse_config(config_path, ctx.args)

    cookiecutter_config = TEMPLATE_DIR / "cookiecutter.json"
    cookiecutter_config.write_text(json.dumps(config, indent=4))
    cookiecutter(
        TEMPLATE_DIR.as_posix(), no_input=True, overwrite_if_exists=True
    )

    if config["dockerfile"] is None:
        devcontainer_dir = Path(config["devcontainer"]["path"])
        (devcontainer_dir / "Dockerfile").unlink()
        (devcontainer_dir / "build.sh").unlink()


@app.command()
def create_config(config_path: Path = Path("config.yaml")):
    config = default_config()
    config_path.write_text(yaml.dump(config, default_flow_style=False))


def main():
    setup_yaml()
    app()


if __name__ == "__main__":
    main()
