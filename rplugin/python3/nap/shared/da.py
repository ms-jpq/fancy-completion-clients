from json import dump, load
from os import makedirs
from os.path import dirname, exists
from typing import Any, Optional


def slurp(path: str) -> str:
    with open(path) as fd:
        return fd.read()


def load_json(path: str) -> Optional[Any]:
    if exists(path):
        with open(path, encoding="utf8") as fd:
            return load(fd)
    else:
        return None


def dump_json(path: str, json: Any) -> None:
    parent = dirname(path)
    makedirs(parent, exist_ok=True)
    with open(path, "w") as fd:
        return dump(json, fd, ensure_ascii=False, indent=2)
