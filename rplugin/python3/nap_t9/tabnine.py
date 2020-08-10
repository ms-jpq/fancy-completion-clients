from asyncio import (
    StreamReader,
    StreamWriter,
    Task,
    create_subprocess_exec,
    create_task,
    sleep,
)
from asyncio.subprocess import DEVNULL, PIPE, Process
from dataclasses import asdict, dataclass, field
from itertools import chain
from json import dumps, loads
from os import linesep, listdir
from os import name as os_name
from os.path import exists, join
from platform import system
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    Optional,
    Sequence,
    cast,
)

from pynvim import Nvim
from pynvim.api.buffer import Buffer

from .consts import __artifacts__
from .nvim import call
from .types import Comm, Completion, Context, Seed, Source

__exec_home__ = join(__artifacts__, "binaries")


@dataclass(frozen=True)
class TabNineRequestL2:
    max_num_results: int
    before: str
    after: str
    filename: str
    region_includes_beginning: bool = False
    region_includes_end: bool = False


@dataclass(frozen=True)
class TabNineRequestL1:
    Autocomplete: TabNineRequestL2


@dataclass(frozen=True)
class TabNineRequest:
    request: TabNineRequestL1
    version: str = "2.9.2"


@dataclass(frozen=True)
class TabNineResponseL1:
    new_prefix: str
    old_suffix: str
    new_suffix: str
    kind: Optional[int] = None
    detail: Optional[str] = None
    documentation: Optional[str] = None
    deprecated: Optional[bool] = None


@dataclass(frozen=True)
class TabNineResponse:
    old_prefix: str
    results: Sequence[TabNineResponseL1]
    user_message: Sequence[str] = field(default_factory=tuple)


SYS_MAP = {
    "Darwin": "apple-darwin",
    "Linux": "unknown-linux-gnu",
    "Windows": "pc-windows-gnu",
}


def parse_ver() -> Iterator[str]:
    triple = f"x86_64-{SYS_MAP[system()]}"
    exe_name = "TabNine.exe" if os_name == "nt" else "TabNine"
    path = join(triple, exe_name)
    lookup = listdir(__exec_home__) if exists(__exec_home__) else ()
    for d in lookup:
        full_path = join(__exec_home__, d, path)
        if exists(full_path):
            yield full_path


async def init_lua(nvim: Nvim) -> Dict[str, int]:
    def cont() -> Dict[str, int]:
        nvim.api.exec_lua("_nap_tabnine = require 'nap/tabnine'", ())
        entry_kind = nvim.api.exec_lua("return _nap_tabnine.list_entry_kind()", ())
        return entry_kind

    return await call(nvim, cont)


def decode_tabnine_l1(l1: Any) -> Iterator[TabNineResponseL1]:
    if type(l1) is list:
        t9 = cast(Sequence[Dict[str, Any]], l1)
        for el in t9:
            yield TabNineResponseL1(**el)


def decode_tabnine(resp: Any) -> Optional[TabNineResponse]:
    if type(resp) is dict:
        t9 = cast(Dict[str, Any], resp)
        old_prefix = t9["old_prefix"]
        maybe_results = t9["results"]
        results = tuple(decode_tabnine_l1(maybe_results))
        r = TabNineResponse(old_prefix=old_prefix, results=results)
        return r
    else:
        return None


def tabnine_subproc() -> Optional[
    Callable[[TabNineRequest], Awaitable[Optional[TabNineResponse]]]
]:
    t9exe = next(parse_ver(), None)
    SEP = linesep.encode()
    proc, stdin, stdout = None, None, None
    task: Task = create_task(sleep(0))

    async def init() -> None:
        nonlocal proc, stdin, stdout
        if proc and proc.returncode is None:  # type: ignore
            pass
        else:
            proc = await create_subprocess_exec(
                cast(str, t9exe), stdin=PIPE, stdout=PIPE, stderr=DEVNULL
            )

    async def request(req: TabNineRequest) -> Any:
        nonlocal task
        await init()
        p = cast(Process, proc)
        stdin = cast(StreamWriter, p.stdin)
        stdout = cast(StreamReader, p.stdout)

        stdin.write(dumps(asdict(req)).encode())
        stdin.write(SEP)
        task.cancel()
        task = create_task(stdout.readuntil(SEP))
        data = await task
        json = data.decode()
        resp = loads(json)
        return decode_tabnine(resp)

    if t9exe:
        return request
    else:
        return None


async def buf_lines(nvim: Nvim) -> Sequence[str]:
    def cont() -> Sequence[str]:
        buf: Buffer = nvim.api.get_current_buf()
        lines = nvim.api.buf_get_lines(buf, 0, -1, True)
        return lines

    return await call(nvim, cont)


async def encode_tabnine_request(
    nvim: Nvim, context: Context, max_results: int
) -> TabNineRequest:
    row = context.position.row + 1
    lines = await buf_lines(nvim)
    lines_before = lines[:row]
    lines_after = lines[row:]
    before = linesep.join(chain(lines_before, (context.line_before,)))
    after = linesep.join(chain((context.line_after,), lines_after))

    l2 = TabNineRequestL2(
        max_num_results=max_results,
        before=before,
        after=after,
        filename=context.filename,
    )
    l1 = TabNineRequestL1(Autocomplete=l2)
    req = TabNineRequest(request=l1)
    return req


def parse_rows(
    t9: TabNineResponse, context: Context, entry_kind_lookup: Dict[int, str],
) -> Iterator[Completion]:
    position = context.position
    old_prefix = t9.old_prefix

    for row in t9.results:
        r_kind = row.kind
        kind = entry_kind_lookup.get(r_kind, "Unknown") if r_kind else None

        yield Completion(
            position=position,
            old_prefix=old_prefix,
            new_prefix=row.new_prefix,
            old_suffix=row.old_suffix,
            new_suffix=row.new_suffix,
            kind=kind,
            doc=row.documentation,
        )


async def main(comm: Comm, seed: Seed) -> Source:
    nvim, log = comm.nvim, comm.log
    max_results = seed.limit * 2
    tabnine_inst = tabnine_subproc()
    entry_kind = await init_lua(nvim)
    entry_kind_lookup = {v: k for k, v in entry_kind.items()}

    async def source(context: Context) -> AsyncIterator[Completion]:
        if not tabnine_inst:
            pass
        else:
            req = await encode_tabnine_request(
                nvim, context=context, max_results=max_results
            )
            resp = await tabnine_inst(req)
            if resp:
                for row in parse_rows(
                    resp, context=context, entry_kind_lookup=entry_kind_lookup
                ):
                    if row.old_prefix != context.alnums_before:
                        msg = f"{context.alnums_before}, {row.old_prefix}"
                        log.debug("%s", msg)
                    yield row

    return source
