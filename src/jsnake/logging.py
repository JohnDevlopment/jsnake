"""Logging module."""
from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, overload
from .utils import get_env
from enum import IntEnum
import logging

if TYPE_CHECKING:
    from typing import Literal, Any

class LoggingError(Exception):
    """Logging error."""

class Level(IntEnum):
    """Logging level."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def find_by_keyword(cls, key: str) -> Level | None:
        """Locate the enumeration based on KEY."""
        return cls.__members__.get(key)

class _TextWriteIO(Protocol):
    """Supports standard text IO operations."""

    def write(self, text: str, /): ...

    def flush(self): ...

    def close(self) -> None: ...

def _get_default_level() -> Level:
    level: Any = get_env('SNEK_LEVEL')
    if level is not None:
        try:
            ilevel = int(level)
            return Level(ilevel)
        except:
            pass

        if level in ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'):
            level = Level.find_by_keyword(level)
            if level is not None:
                assert isinstance(level, Level)
                return level

    return Level.INFO

DEFAULT_LEVEL = Level.INFO
Logger = logging.Logger

_rootLogger: Logger
_cache: dict[str, Logger] = {}
_initialized = False

def init(name: str):
    """
    Initialize the logging hiererchy with NAME as the root.

    This MUST be called before any other function in this module.
    """
    global _rootLogger, _initialized

    # Get default level
    global DEFAULT_LEVEL
    DEFAULT_LEVEL = _get_default_level()

    # Set flag
    _initialized = True

    # Create root logger
    _rootLogger = logging.getLogger(name)
    add_handler(_rootLogger, 'null')

@overload
def add_handler(logger: Logger, kind: Literal['stream'], *, stream: _TextWriteIO | None=None):
    ...

@overload
def add_handler(logger: Logger, kind: Literal['file'], *, file: str, mode: str='wt'):
    ...

@overload
def add_handler(logger: Logger, kind: Literal['null']):
    ...

def add_handler(logger: Logger, kind: str, **kw: Any):
    """
    Add the specified type of handler to LOGGER.

    The keyword arguments depend on what KIND of handler to add.

    stream:
      * stream = the stream to output to. should be derived from IO.
                 if omitted, defaults to sys.stderr

    file:
      * mode = same as the mode argument in open() (default: 'wt')
      * encoding = same as the encoding argumet in open()
      * file = the name of the file

    stack:
      * limit = size limit for the record stack

    null:
      none
    """
    if not _initialized:
        raise LoggingError("You must call init() before using any of the other functions.")

    hdl = None
    formatter = logging.Formatter(f"%(levelname)s %(name)s: [%(asctime)s] %(message)s")

    if kind == 'stream':
        hdl = logging.StreamHandler(kw.get('stream'))
        hdl.setFormatter(formatter)
    elif kind == 'file':
        filehdl_args: tuple[str, str | None] = (kw.get('mode', 'wt'), kw.get('encoding'))
        hdl = logging.FileHandler(kw['file'], *filehdl_args)
        hdl.setFormatter(formatter)
    elif kind == 'null':
        hdl = logging.NullHandler(logger.level)

    assert hdl is not None
    logger.addHandler(hdl)

def get_logger(name: str="", level: Level | None=None, stream: bool=True) -> Logger:
    """
    Returns a logger with the specified NAME.

    If NAME is omitted or set to an empty string,
    the root logger for this library is returned.

    Any logger returned by this is part of the
    logger hierchy. That is to say, a logger named
    `io` is a direct child of the root logger. And
    `io.read` is a direct descendent of `io`, which
    is a descendent of the root logger.

    The LEVEL dictates the severity level
    of the logger. Unless it is specified,
    it defaults to the value of SNEK_LEVEL
    if defined, or Level.INFO otherwise.
    """
    global _cache

    if not _initialized:
        raise LoggingError("You must call init() before using any of the other functions.")

    # Return the root logger if name is "" or "yt_dlp_tk"
    parts = name.split(".")
    isroot = parts[0] == "" and len(parts) == 1
    if isroot: return _rootLogger

    # Insert root name into the array
    root_name = _rootLogger.name
    if parts[0] not in ("", root_name):
        parts.insert(0, root_name)
    if parts[0] == "":
        parts[0] = root_name

    # Join list into a string
    name = ".".join(parts)

    # Return the cached logger
    if name in _cache:
        return _cache[name]

    # Default logger
    if level is None:
        level = DEFAULT_LEVEL

    # Get the logger and set its level
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Add stream handler
    if stream: # pragma: no cover
        add_handler(logger, 'stream')

    # Cache the logger for future calls
    _cache[name] = logger

    return logger
