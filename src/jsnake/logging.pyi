from typing import Protocol, overload, Literal, Any
from enum import IntEnum
import logging

class Level(IntEnum):
    """Logging level."""

    DEBUG: int
    INFO: int
    WARN: int
    ERROR: int
    CRITICAL: int

    @classmethod
    def find_by_keyword(cls, key: str) -> Level | None:
        ...

class _TextWriteIO(Protocol):
    """Supports standard text IO operations."""

    def write(self, text: str, /): ...

    def flush(self): ...

    def close(self) -> None: ...

def _get_default_level(envname: str) -> Level:
    ...

DEFAULT_LEVEL: Level
Logger = logging.Logger

def init(name: str, envprefix: str="JSNAKE") -> None:
    ...

@overload
def add_handler(logger: Logger, kind: Literal['stream'], *, stream: _TextWriteIO | None=None) -> None:
    ...

@overload
def add_handler(logger: Logger, kind: Literal['file'], *, file: str, mode: str='wt') -> None:
    ...

@overload
def add_handler(logger: Logger, kind: Literal['null']) -> None:
    ...

def get_logger(name: str="", level: Level | None=None, stream: bool=True) -> Logger:
    ...
