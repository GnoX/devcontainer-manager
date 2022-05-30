import re
from pathlib import Path

from devcontainer_manager.config import Config
from devcontainer_manager.global_config import GlobalConfig

PROJECT_DIR = Path(__file__).parent


def replace_block(block_name, source, block_text):
    regex = re.compile(
        rf"(?<=\[//\]: # \({block_name}_block_start\))"
        r"\s*(.*?)\s*"
        rf"(?=\[//\]: # \({block_name}_block_end\))",
        re.MULTILINE | re.DOTALL,
    )
    matches = regex.search(source)
    if not matches:
        return source
    left = source[0 : matches.start()]
    right = source[matches.end() :]

    return f"{left}\n{block_text}\n{right}"


def main():
    config_yaml = Config().yaml(with_descriptions=True)
    global_config_yaml = GlobalConfig().yaml(
        with_descriptions=True,
        exclude={"defaults": {k: True for k in Config.__fields__}},
    )

    readme = replace_block(
        "template_config", (PROJECT_DIR / "README.md").read_text(), f"```yaml\n{config_yaml}```"
    )

    readme = replace_block("global_config", readme, f"```yaml\n{global_config_yaml}```")

    (PROJECT_DIR / "README.md").write_text(readme)


if __name__ == "__main__":
    main()
