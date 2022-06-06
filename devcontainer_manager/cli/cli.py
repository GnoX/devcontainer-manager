import subprocess
from functools import reduce
from pathlib import Path
from typing import List, Optional

import typer
from cookiecutter.main import cookiecutter

from .. import __version__
from ..config import Config
from ..global_config import GlobalConfig
from . import alias

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
COOKIECUTTER_CONFIG = TEMPLATE_DIR / "cookiecutter.json"


app = typer.Typer()
app.add_typer(alias.app, name="alias")


@app.command()
def generate(
    templates: Optional[List[str]] = typer.Argument(None),
    build: bool = typer.Option(False, "--build", "-b"),
):
    global_config = GlobalConfig.load(create_if_not_exist=True)
    from_override = not templates

    if from_override:
        template_path = global_config.defaults.path / global_config.override_config_path
        if not template_path.exists():
            typer.echo(
                "Template argument not specified and "
                "`.devcontainer/overrides.yaml` does not exist"
            )
            raise typer.Exit(1)
        templates = [template_path.as_posix()]
    else:
        templates = [global_config.load_alias_config().aliases.get(t, t) for t in templates]

    configs = [Config.parse_file(t).merge_bases() for t in templates]
    merged_config = global_config.merge_bases().defaults | reduce(lambda a, b: a | b, configs)

    COOKIECUTTER_CONFIG.write_text(
        merged_config.resolve().json(indent=4, exclude={"base_config": True})
    )
    cookiecutter(TEMPLATE_DIR.as_posix(), no_input=True, overwrite_if_exists=True)

    if not from_override:
        config_paths = [cfg.config_path.resolve() for cfg in configs]
        override_config = Config.NONE
        override_config.base_config = config_paths
        override_config.write_yaml(
            global_config.defaults.path / global_config.override_config_path
        )

    devcontainer_dir = Path(merged_config.path)
    if not merged_config.docker.file:
        (devcontainer_dir / "devcontainer.Dockerfile").unlink()
        (devcontainer_dir / "build.sh").unlink()

    if build:
        subprocess.run(["bash", ".devcontainer/build.sh"], check=True)


@app.command()
def create_template(
    template_path: str = typer.Argument(...),
    force: bool = typer.Option(False, "--force", "-f"),
    with_descriptions: bool = typer.Option(True, "-d/-D", "--with-description/--no-description"),
):
    global_config = GlobalConfig.load(create_if_not_exist=True)

    path = Path(template_path)

    global_template = False
    if path.suffix not in [".yaml", ".yml"]:
        global_template = True
        path = path.with_suffix(".yaml")

    if global_template:
        if global_config.template_dir.is_absolute():
            typer.echo("Error: --local not specified but path is absolute", err=True)
            raise typer.Exit(1)
        path = global_config.config_path.parent / global_config.template_dir / path

    if path.exists() and not force:
        if not typer.confirm(f"Config '{path}' already exists, overwrite?"):
            raise typer.Exit(1)

    Config().write_yaml(path, with_descriptions=with_descriptions)
    typer.echo("Config written to " f"'{typer.style(path, typer.colors.GREEN)}'")

    if global_template:
        alias_config = global_config.load_alias_config()
        alias_config.aliases[path.stem] = path.as_posix()
        alias_config.write_yaml()
        typer.echo("Alias created: " f"'{typer.style(path.stem, fg=typer.colors.BLUE)}'")


@app.command()
def version():
    typer.echo(__version__)


@app.callback(invoke_without_command=True)
def _main(version: bool = typer.Option(False, "--version", "-v")):
    if version:
        typer.echo(__version__)
        raise typer.Exit(0)


def main():
    app()


if __name__ == "__main__":
    main()
