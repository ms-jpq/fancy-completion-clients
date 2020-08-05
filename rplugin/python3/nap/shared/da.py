from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from json import dump, load
from os import makedirs
from os.path import dirname, exists
from shutil import which
from typing import Any, Optional, cast
from zipfile import ZipFile


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


@dataclass(frozen=True)
class ProcReturn:
    code: int
    out: str
    err: str


async def call(prog: str, *args: str, cwd: str) -> ProcReturn:
    proc = await create_subprocess_exec(prog, *args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    code = cast(int, proc.returncode)
    return ProcReturn(code=code, out=stdout.decode(), err=stderr.decode())


class DownloadError(Exception):
    pass


async def download(uri: str, dest: str, name: str) -> None:
    if which("wget"):
        ret = await call("wget", "-O", dest, "--", uri, cwd=dest)
        if ret.code:
            raise DownloadError(ret.err)
    elif which("curl"):
        ret = await call(
            "curl", "--location", "--create-dirs", "--output", dest, "--", uri, cwd=dest
        )
        if ret.code:
            raise DownloadError(ret.err)
    else:
        raise DownloadError("neither curl or wget found in PATH")


def unzip(path: str) -> None:
    with ZipFile(path) as zp:
        zp.extractall()
