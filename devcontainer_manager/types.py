import re
from typing import Optional

DEVCONTAINER_MOUNT_STR_REGEX = re.compile(r"^src=(?P<src>.+),dst=(?P<dst>.+)(?P<args>,.+)?")
SIMPLE_MOUNT_REGEX = re.compile(r"(?P<src>.+):(?P<dst>.+)")


class MountString(str):
    __slots__ = ("src", "dst")

    def __new__(cls, v: Optional[str], **kwargs):
        return str.__new__(cls, v if v is not None else cls.build(**kwargs))

    def __init__(
        self,
        mount_string: str,
        *,
        src: str = None,
        dst: str = None,
    ):
        str.__init__(mount_string)
        if src is None or dst is None:
            arg_dict = type(self).validate_string(mount_string)
            src = arg_dict["src"]
            dst = arg_dict["dst"]

        self.src = src
        self.dst = dst

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        if value.__class__ == cls:
            return value

        if not isinstance(value, str):
            raise TypeError("mount must be string")

        return cls(value, **cls.validate_string(value))

    @classmethod
    def validate_string(cls, value: str):
        if value == "{{ base }}":
            return dict(src="{{ base }}", dst="{{ base }}")

        match = SIMPLE_MOUNT_REGEX.match(value)
        if match is None:
            match = DEVCONTAINER_MOUNT_STR_REGEX.match(value)
        if match is None:
            raise Exception()

        return dict(src=match.group("src"), dst=match.group("dst"))

    @classmethod
    def build(cls, *, src: str, dst: str):
        return f"{src}:{dst}"

    def to_devcontainer_format(self):
        return MountString(
            f"src={self.src}," f"dst={self.dst}," "type=bind,consistency=cached",
        )

    def __repr__(self) -> str:
        return f"MountString({self})"
