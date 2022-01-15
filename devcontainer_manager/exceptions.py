class InvalidArgumentException(Exception):
    pass


class ConfigMovedException(Exception):
    pass


class InvalidMountStringException(Exception):
    def __init__(self, mnt_str, *args: object) -> None:
        super().__init__(f"Mount string is invalid: '{mnt_str}'", *args)
