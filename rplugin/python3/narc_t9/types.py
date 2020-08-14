from asyncio import Queue
from dataclasses import dataclass, field
from logging import Logger
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Sequence,
    Set,
)

from pynvim import Nvim


@dataclass(frozen=True)
class MatchOptions:
    transpose_band: int
    unifying_chars: Set[str]


@dataclass(frozen=True)
class Comm:
    nvim: Nvim
    chan: Queue
    log: Logger


@dataclass(frozen=True)
class Seed:
    match: MatchOptions
    limit: float
    timeout: float
    config: Dict[str, Any]


@dataclass(frozen=True)
class Position:
    row: int
    col: int


# |...                            line                            ...|
# |...        line_before          🐭          line_after         ...|
# |...   <syms_before><alum_before>🐭<alnums_after><syms_after>   ...|
@dataclass(frozen=True)
class Context:
    position: Position

    filename: str
    filetype: str

    line: str
    line_normalized: str
    line_before: str
    line_before_normalized: str
    line_after: str
    line_after_normalized: str

    alnums: str
    alnums_normalized: str
    alnums_before: str
    alnums_before_normalized: str
    alnums_after: str
    alnums_after_normalized: str

    syms: str
    syms_before: str
    syms_after: str

    alnum_syms: str
    alnum_syms_normalized: str
    alnum_syms_before: str
    alnum_syms_before_normalized: str
    alnum_syms_after: str
    alnum_syms_after_normalized: str


@dataclass(frozen=True)
class MEdit:
    old_prefix: str
    new_prefix: str
    old_suffix: str
    new_suffix: str


# end exclusve
@dataclass(frozen=True)
class LEdit:
    begin: Position
    end: Position
    new_text: str


@dataclass(frozen=True)
class Snippet:
    kind: str
    match: str
    content: str


@dataclass(frozen=True)
class Completion:
    position: Position
    label: Optional[str] = None
    sortby: Optional[str] = None
    kind: Optional[str] = None
    doc: Optional[str] = None
    medit: Optional[MEdit] = None
    ledits: Sequence[LEdit] = field(default_factory=tuple)
    snippet: Optional[Snippet] = None
    unique: bool = True


Source = Callable[[Context], AsyncIterator[Completion]]
Factory = Callable[[Comm, Seed], Awaitable[Source]]


@dataclass(frozen=True)
class SnippetSeed:
    match: MatchOptions
    config: Dict[str, Any]


@dataclass(frozen=True)
class SnippetContext:
    position: Position
    snippet: Snippet


SnippetEngine = Callable[[SnippetContext], Awaitable[None]]
SnippetEngineFactory = Callable[[Comm, SnippetSeed], Awaitable[SnippetEngine]]
