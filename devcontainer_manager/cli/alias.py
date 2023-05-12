from pathlib import Path
from typing import List

import typer

from ..global_config import GlobalConfig

app = typer.Typer()


def complete_aliases(param_name: str = "alias"):
    def _complete(ctx: typer.Context, args: List[str], incomplete: str):
        global_config = GlobalConfig.load()
        param_aliases = ctx.params.get(param_name) or []
        for alias, path in global_config.load_alias_config().aliases.items():
            if alias.startswith(incomplete) and alias not in param_aliases:
                yield (alias, path.as_posix())

    return _complete


@app.command()
def add(alias: str = typer.Argument(...), config_path: str = typer.Argument(...)):
    path = Path(config_path).resolve()
    global_config = GlobalConfig.load()
    global_config_dir = global_config.config_path.resolve().parent

    alias_config = global_config.load_alias_config()

    if path.as_posix().startswith(global_config_dir.as_posix()):
        path = path.relative_to(global_config_dir)

    alias_config.aliases[alias] = path
    alias_config.write_yaml()
    typer.echo(f"Alias created: '{typer.style(alias, fg=typer.colors.BLUE)}'")


@app.command()
def remove(
    alias: List[str] = typer.Argument(..., autocompletion=complete_aliases("alias")),
):
    alias_config = GlobalConfig.load().load_alias_config()

    for alias_remove in alias:
        if alias_remove in alias_config.aliases:
            alias_config.aliases.pop(alias_remove)
            alias_config.write_yaml()
        else:
            message = (
                f"{typer.style('Error: ', fg=typer.colors.RED)}"
                "Nothing removed, alias "
                f"'{typer.style(alias_remove, fg=typer.colors.BLUE)}' "
                "does not exist"
            )
            typer.echo(message)


@app.command()
def list():
    global_config = GlobalConfig.load()
    typer.echo("Available aliases:")
    aliases_msg = ""
    for alias, path in global_config.load_alias_config().aliases.items():
        path = Path(path)
        if not path.is_absolute():
            path = global_config.config_path.parent / path

        file_color = typer.colors.GREEN if path.exists() else typer.colors.RED
        aliases_msg += (
            f"  {typer.style(alias, fg=typer.colors.BLUE)}: "
            f"{typer.style(path, fg=file_color)}"
            "\n"
        )
    typer.echo(aliases_msg)
