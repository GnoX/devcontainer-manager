import subprocess
from pathlib import Path

import jinja2


def render_recursive_template(template: str, values: dict):
    prev = template
    while True:
        rendered = jinja2.Template(prev).render(**values)
        if rendered != prev:
            prev = rendered
        else:
            return rendered


def get_project_root_basename() -> str:
    try:
        git_folder_path = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        ).stdout
        return Path(git_folder_path).name
    except subprocess.CalledProcessError:
        return None
