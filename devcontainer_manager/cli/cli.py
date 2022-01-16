import json
from pathlib import Path
from typing import Optional

import typer
from cookiecutter.main import cookiecutter

from devcontainer_manager.global_config import GlobalConfig

from ..config import OVERRIDE_CONFIG, Config, OverrideConfig, default_config
from . import alias

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


app = typer.Typer()
app.add_typer(alias.app, name="alias")


@app.command(context_settings={"allow_extra_args": True})
def generate(
    ctx: typer.Context, template: Optional[str] = typer.Argument(None)
):
    global_config = GlobalConfig.load()
    if template is None:
        template_path = Path(".devcontainer") / OVERRIDE_CONFIG
        if not template_path.exists():
            typer.echo(
                "Template argument not specified and "
                "`.devcontainer/overrides.yaml` does not exist"
            )
            raise typer.Exit(1)
        template = template_path.as_posix()
    else:
        template = global_config.resolve_alias(template)

    config = Config.parse(template)

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
def create_template(
    template_path: str = typer.Argument("template"),
    force: bool = typer.Option(False, "--force", "-f"),
):
    global_config = GlobalConfig.load()
    path = Path(template_path)

    global_template = False
    if path.suffix not in [".yaml", ".yml"]:
        global_template = True
        path = path.with_suffix(".yaml")

    if global_template:
        if path.is_absolute():
            typer.echo(
                "Error: --local not specified but path is absolute", err=True
            )
            raise typer.Exit(1)

        path = global_config.resolve_template_dir() / path

    config = default_config(path.as_posix())
    if config.yaml_exists() and not force:
        if not typer.confirm(f"Config '{path}' already exists, overwrite?"):
            raise typer.Exit(1)

    config.write_yaml(path)
    typer.echo(
        "Config written to " f"'{typer.style(path, typer.colors.GREEN)}'"
    )

    if global_template:
        global_config.add_alias(path.stem, path.as_posix())
        global_config.write_yaml()
        typer.echo(
            "Alias created: "
            f"'{typer.style(path.stem, fg=typer.colors.BLUE)}'"
        )


def main():
    app()


if __name__ == "__main__":
    main()
