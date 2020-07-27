from asyncio import Queue
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Awaitable, Callable, Optional, Sequence

from pynvim import Nvim


@dataclass(frozen=True)
class Seed:
    limit: float
    timeout: float
    config: Optional[Any] = None


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
    alnums_after: str

    syms: str
    syms_before: str
    syms_after: str


# end exclusve
@dataclass(frozen=True)
class LEdit:
    begin: Position
    end: Position
    new_text: str


@dataclass(frozen=True)
class Completion:
    position: Position
    old_prefix: str
    new_prefix: str
    old_suffix: str
    new_suffix: str
    label: Optional[str] = None
    sortby: Optional[str] = None
    kind: Optional[str] = None
    doc: Optional[str] = None
    ledits: Sequence[LEdit] = field(default_factory=tuple)


Source = Callable[[Context], AsyncIterator[Completion]]
Factory = Callable[[Nvim, Queue, Seed], Awaitable[Source]]
