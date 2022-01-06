import json
from collections import OrderedDict
from pathlib import Path

import jinja2
import typer
import yaml
from cookiecutter.main import cookiecutter
from mergedeep import merge

TEMPLATE_DIR = Path(__file__).parent / "templates"


def default_config():
    return OrderedDict(
        devcontainer=OrderedDict(
            path=".devcontainer",
            name="dev_env",
            workspace_path="/mnt/workspace",
            image="dev-env-dev",
            mounts=[],
            run_args=[],
            container_name="{{ devcontainer.name }}",
            container_hostname="{{ devcontainer.name }}",
            extensions=["ms-python.python"],
        ),
        dockerfile=None,
    )


app = typer.Typer()


def setup_yaml():
    mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
    yaml.add_representer(
        OrderedDict,
        lambda dumper, data: dumper.represent_mapping(
            mapping_tag, data.items()
        ),
    )
    yaml.add_constructor(
        mapping_tag,
        lambda loader, node: OrderedDict(loader.construct_pairs(node)),
    )


def conf_callback(ctx: typer.Context, param: typer.CallbackParam, value: Path):
    if value:
        try:
            conf = yaml.safe_load(value.read_text())

            ctx.default_map = ctx.default_map or {}
            ctx.default_map.update(conf)
        except Exception as ex:
            raise typer.BadParameter(str(ex))
    return value


def override_config_from_args(config, args):
    config = dict(config)
    for arg in args:
        current_level = config
        last_level = config
        parts = arg.split("=")
        if len(parts) != 2:
            raise typer.BadParameter(f"Invalid argument {arg}")

        name, value = parts
        name_parts = name.split(".")

        for part in name_parts:
            if part not in current_level:
                raise typer.BadParameter(f"Invalid argument {arg}")

            last_level = current_level
            current_level = current_level[part]
        last_level[part] = value
    return config


@app.command(context_settings={"allow_extra_args": True})
def generate(
    ctx: typer.Context,
    config_path: Path = typer.Argument("config.yaml", callback=conf_callback),
):
    config = default_config()

    config_str = config_path.read_text()
    config_parsed = yaml.safe_load(config_str)
    config_parsed_args = yaml.dump(
        override_config_from_args(config_parsed, ctx.args)
    )
    config_rendered = yaml.safe_load(
        jinja2.Template(config_parsed_args).render(**config_parsed)
    )
    config = merge(default_config(), config_rendered)

    dockerfile = config["dockerfile"]
    if dockerfile is not None:
        if "content" in dockerfile:
            dockerfile_path = Path(dockerfile["content"])
            if dockerfile_path.exists():
                dockerfile["content"] = dockerfile_path.read_text()
        if "additional_commands" not in dockerfile:
            dockerfile["additional_commands"] = []

    cookiecutter_config = TEMPLATE_DIR / "cookiecutter.json"
    cookiecutter_config.write_text(json.dumps(config, indent=4))
    cookiecutter(
        TEMPLATE_DIR.as_posix(), no_input=True, overwrite_if_exists=True
    )

    if dockerfile is None:
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
