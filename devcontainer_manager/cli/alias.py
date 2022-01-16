from pathlib import Path
from typing import List

import typer

from ..global_config import GlobalConfig

app = typer.Typer()


def complete_aliases(ctx: typer.Context, args: List[str], incomplete: str):
    global_config = GlobalConfig.load()
    param_aliases = ctx.params.get("alias") or []
    for alias, path in global_config.aliases.items():
        if alias.startswith(incomplete) and alias not in param_aliases:
            yield (alias, path)


@app.command()
def add(
    alias: str = typer.Argument(...), config_path: str = typer.Argument(...)
):
    path = Path(config_path)
    global_config = GlobalConfig.load()
    global_config.aliases[alias] = path.resolve().as_posix()
    global_config.write_yaml()


@app.command()
def remove(
    alias: List[str] = typer.Argument(..., shell_complete=complete_aliases),
):
    global_config = GlobalConfig.load()
    for alias_remove in alias:
        if alias_remove in global_config.aliases:
            global_config.aliases.pop(alias_remove)
            global_config.write_yaml()
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
    for alias, path in global_config.aliases.items():
        file_exists = Path(path).exists()
        file_color = typer.colors.GREEN if file_exists else typer.colors.RED
        aliases_msg += (
            f"  {typer.style(alias, fg=typer.colors.BLUE)}: "
            f"{typer.style(path, fg=file_color)}"
            "\n"
        )
    typer.echo(aliases_msg)
