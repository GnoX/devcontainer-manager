import io
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import CommentMark
from ruamel.yaml.tokens import CommentToken

yaml = YAML(pure=True)
yaml.default_flow_style = False
yaml.width = 4096
yaml.indent(mapping=4, sequence=4, offset=2)


def yaml_to_str(dict):
    buf = io.StringIO()
    yaml.dump(dict, buf)
    return buf.getvalue()


yaml.dump_str = yaml_to_str


def represent_none(representer, _):
    return representer.represent_scalar("tag:yaml.org,2002:null", "")


def represent_as_str(representer, data):
    return representer.represent_scalar("tag:yaml.org,2002:str", str(data))


yaml.representer.add_representer(type(None), represent_none)
yaml.representer.add_multi_representer(Path, represent_as_str)
yaml.representer.add_multi_representer(str, represent_as_str)


if not hasattr(CommentedMap, "yaml_set_comment_before_key"):

    def yaml_set_comment_before_key(self, key, comment, column=None):
        key_comment = self.ca.items.setdefault(key, [None, [], None, None])
        comment_list = key_comment[1]
        if comment_list is None:
            key_comment[1] = []
            comment_list = key_comment[1]
        if comment:
            comment_start = "# "
            if comment[-1] == "\n":
                comment = comment[:-1]  # strip final newline if there
        else:
            comment_start = "#"
        if column is None:
            if comment_list:
                # if there already are other comments get the column from them
                column = comment_list[-1].start_mark.column
            else:
                column = 0

        comment = f"\n{' ' * (column)}# ".join(comment.splitlines())
        start_mark = CommentMark(column)
        comment_list.append(CommentToken(comment_start + comment + "\n", start_mark, None))
        return self

    CommentedMap.yaml_set_comment_before_key = yaml_set_comment_before_key

if not hasattr(CommentedMap, "yaml_add_newline_after_key"):

    def yaml_add_newline_after_key(self, key, n=1):
        key_comment = self.ca.items.setdefault(key, [None, None, None, None])
        key_comment[2] = CommentToken("\n" * (n + 1), CommentMark(0), None)
        return self

    CommentedMap.yaml_add_newline_after_key = yaml_add_newline_after_key


if not hasattr(CommentedMap, "yaml_add_newline_before_key"):

    def yaml_add_newline_before_key(self, key, n=1):
        key_comment = self.ca.items.setdefault(key, [None, [], None, None])
        key_comment[1].insert(0, CommentToken("\n" * n, CommentMark(0), None))
        return self

    CommentedMap.yaml_add_newline_before_key = yaml_add_newline_before_key
