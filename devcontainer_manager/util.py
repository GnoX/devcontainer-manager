import copy
import subprocess
from pathlib import Path

import jinja2


def render_recursive_template(template: str, values: dict):
    prev = template
    while True:
        rendered = jinja2.Template(prev, undefined=jinja2.StrictUndefined).render(values)
        if rendered == prev:
            return rendered
        prev = rendered


def get_project_root_basename() -> str:
    try:
        git_folder_path = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        ).stdout
        return Path(git_folder_path).name.strip()
    except subprocess.CalledProcessError:
        return None


def dict_merge(d, overwrite):
    new_config = copy.deepcopy(d)

    for k, v in overwrite.items():
        if isinstance(v, dict):
            orig_dict = d[k] if k in d and d[k] else dict()
            new_config[k] = dict_merge(orig_dict, v)
        elif isinstance(v, list):
            orig_list = d[k] if k in d and d[k] else list()
            new_config[k] = orig_list + v
        else:
            if v is not None:
                new_config[k] = v

    return new_config
