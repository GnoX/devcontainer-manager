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
    templates: Optional[List[str]] = typer.Argument(
        None, autocompletion=alias.complete_aliases("templates")
    ),
    build: bool = typer.Option(False, "--build", "-b"),
    print_config: bool = typer.Option(False, "--print-config", "--print", "-p"),
):
    global_config: GlobalConfig = GlobalConfig.load(create_if_not_exist=True)
    alias_config = global_config.load_alias_config()
    from_override = not templates

    if from_override:
        template_path = global_config.defaults.project_path / global_config.override_config_path
        overrides_exist = template_path.exists()
        path_color = typer.colors.GREEN if overrides_exist else typer.colors.RED
        typer.echo(f"Reading config from {typer.style(template_path, path_color)}\n")
        if not overrides_exist:
            typer.echo(
                "Template argument not specified and "
                f"{typer.style('.devcontainer/overrides.yaml', path_color)} does not exist"
            )
            raise typer.Exit(1)
        templates = [template_path.as_posix()]
    else:
        templates = [alias_config.resolve(t) for t in templates]

    configs = [Config.parse_file(t).merge_bases() for t in templates]
    merged_config = global_config.merge_bases().defaults | reduce(lambda a, b: a | b, configs)

    if print_config:
        typer.echo(merged_config.yaml())
        raise typer.Exit()

    config_path = global_config.defaults.project_path / global_config.override_config_path
    COOKIECUTTER_CONFIG.write_text(
        merged_config.resolve(config_path).json(indent=4, exclude={"base_config": True})
    )
    cookiecutter(TEMPLATE_DIR.as_posix(), no_input=True, overwrite_if_exists=True)

    if not from_override:
        config_paths = [alias_config.path_to_alias(cfg.config_path) for cfg in configs]
        override_config = Config.none()
        override_config.base_config = config_paths
        override_config.write_yaml(config_path)

    devcontainer_dir = merged_config.project_path / ".devcontainer"
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
        template_dir = global_config.template_dir
        if not template_dir.is_absolute():
            template_dir = global_config.config_path.parent.absolute() / template_dir

        path = template_dir / path

    if path.exists() and not force:
        if not typer.confirm(f"Config '{path}' already exists, overwrite?"):
            raise typer.Exit(1)

    Config().write_yaml(path, with_descriptions=with_descriptions)
    typer.echo(f"Config written to '{typer.style(path, typer.colors.GREEN)}'")

    if global_template:
        alias.add(path.stem, path.as_posix())


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
