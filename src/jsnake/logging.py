"""Logging module."""
from __future__ import annotations
from .utils import get_env
from enum import IntEnum
import logging

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
    def find_by_keyword(cls, key):
        """
        Do a keyword lookup of the enum.

        :param str key: A key used to search the enum. Should
                        be one of the defined members

        :return: The logging level object corresponding to `key`
        :rtype: Level or None
        """
        return cls.__members__.get(key)

def _get_default_level(envname: str) -> Level:
    level = get_env(envname)
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

def init(name: str, envprefix: str="JSNAKE"):
    """
    Initialize the logging hiererchy.

    :param str name: The name of the root logger

    :param str envprefix: The prefix to the environment name used
                          to get the default logging level

    The default level for loggers is taken from the environment variable
    ``X_LEVEL``, where ``X`` is the value of `envprefix`.

    .. warning::
       This MUST be called before any other function in this module.
    """
    global _rootLogger, _initialized

    # Get default level
    global DEFAULT_LEVEL
    DEFAULT_LEVEL = _get_default_level(f"{envprefix}_LEVEL")

    # Set flag
    _initialized = True

    # Create root logger
    _rootLogger = logging.getLogger(name)
    add_handler(_rootLogger, 'null')

def add_handler(logger: Logger, kind: str, **kw):
    """
    Add the specified type of handler to a logger.

    :params str kind: The kind of handler to add. Can be stream,
                      file, or null

    :param kw: Keyword arguments which differ based on `kind`
    :type kw: dict[str, Any]

    :raises LoggingError: If the logging module has not been initialized, or
                          if `kind` is invalid

    .. note:: Keyword arguments

       The keyword arguments depend on what `kind` of handler to add.

       stream:
         * stream = the stream to output to. Should be derived from IO.
                    If omitted, defaults to ``sys.stderr``

       file:
         * mode = same as the mode argument in open() (default: 'wt')
         * encoding = same as the encoding argumet in open()
         * file = the name of the file

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

    if hdl is None:
        raise LoggingError(f"Invalid handler type '{kind}'.")

    logger.addHandler(hdl)

def get_logger(name: str="", level: Level | None=None, stream: bool=True):
    """
    Returns a logger with the specified name.

    :param str name: The name of the logger

    :param level: Severity level of the returned logger
    :type level: Level or None

    :param bool stream: If true, add a stream handler that
                        lets the logger print to the screen

    :return: a logger for `name`, unless `name` is empty,
             in which case the root logger
    :rtype: Logger

    .. note::

       Any logger returned by this is part of the
       logger hierchy. That is to say, a logger named
       `io` is a direct child of the root logger. And
       `io.read` is a direct descendent of `io`, which
       is a descendent of the root logger.
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

if __debug__:
    import unittest, tempfile
    from pathlib import Path

    class TestLogging(unittest.TestCase):
        def test_logger(self):
            init("logging")

            logger = get_logger('test1', Level.INFO)
            with self.assertLogs(logger, Level.INFO) as cm:
                logger.info("first message")

            logger = get_logger('test1.bar', stream=False)
            with self.assertLogs(logger, Level.INFO) as cm:
                logger.info("second message")

            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = Path(tmpdir) / "asfsdf.log"
                add_handler(logger, 'file', file=str(file_path))
                with self.assertLogs(logger, Level.INFO) as cm:
                    logger.info("third message")

    if __name__ == "__main__":
        unittest.main()
