from asyncio import create_subprocess_exec, get_running_loop
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from json import dump, load
from os import makedirs
from os.path import dirname, exists, join
from shutil import which
from typing import Any, AsyncIterator, Optional, TypeVar, cast
from urllib.request import urlopen
from zipfile import ZipFile

T = TypeVar("T")


async def anext(aiter: AsyncIterator[T], default: Optional[T] = None) -> Optional[T]:
    try:
        return await aiter.__anext__()
    except StopAsyncIteration:
        return default


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
    proc = await create_subprocess_exec(prog, *args, stdout=PIPE, stderr=PIPE, cwd=cwd)
    stdout, stderr = await proc.communicate()
    code = cast(int, proc.returncode)
    return ProcReturn(code=code, out=stdout.decode(), err=stderr.decode())


class DownloadError(Exception):
    pass


async def download(uri: str, dest: str, name: str) -> None:
    makedirs(dest, exist_ok=True)
    if which("wget"):
        ret = await call("wget", "-O", name, "--", uri, cwd=dest)
        if ret.code:
            raise DownloadError(ret.err)
    elif which("curl"):
        ret = await call("curl", "--location", "--output", name, "--", uri, cwd=dest)
        if ret.code:
            raise DownloadError(ret.err)
    else:
        loop = get_running_loop()

        def cont() -> None:
            with urlopen(uri) as fd:
                data = fd.read()
                with open(join(dest, name), "wb") as f:
                    f.write(data)

        return await loop.run_in_executor(None, cont)


async def fetch(uri: str) -> str:
    loop = get_running_loop()

    def cont() -> str:
        with urlopen(uri) as fd:
            return fd.read().decode()

    return await loop.run_in_executor(None, cont)


def unzip(path: str) -> None:
    parent = dirname(path)
    with ZipFile(path) as zp:
        zp.extractall(parent)
