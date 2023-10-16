"""
Logging module.

.. note:: Before you can start using the other
   methods, call :py:func:`init`.

This module includes functions for creating and modifying loggers.
When you first initialize this module via :py:func:`init`, ``jsnake``
sets the default severity level via the environment. By default,
:py:func:`init` looks for ``JSNAKE_LEVEL`` in the environment, but you
can set the prefix "JSNAKE" to something else (see function for details).

.. code-block:: python

   from jsnake.logging import init, get_logger
   logger = get_logger('foo')
   logger.info("Info")
   logger.info("My name is %s", "Foo")
"""

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
    """
    Set the default logging level using ENVNAME.

    If ENVNAME is undefined or its value is invalid,
    `Level.INFO` is returned.
    """
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

def init(name, envprefix="JSNAKE"):
    """
    Initialize the logging module.

    :param str name: The name of the root logger

    :param str envprefix: The prefix to the environment name used
                          to get the default logging level

    The default level for loggers is taken from the environment variable
    ``X_LEVEL``, where ``X`` is the value of `envprefix`. For example,
    if using the default of "JSNAKE", the environment name used will
    be ``JSNAKE_LEVEL``.

    .. note::
       This **must** be called before any other function in this module.
    """
    global _rootLogger, _initialized, DEFAULT_LEVEL

    # Get default level
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

    Keyword arguments
    -----------------

    The keyword arguments depend on what `kind` of handler to add.

    * stream
        * stream
            * The stream to output to. Should be derived from IO.
              If omitted, defaults to ``sys.stderr``.
    * file
        * mode
            * Same as the mode argument in open() (default: 'wt').

        * encoding
            * Same as the encoding argumet in open().

        * file
            * The name of the file.
    * null
        * No arguments.
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

def get_logger(name="", level=None, stream=True):
    """
    Return a logger with the specified `name`.

    :param str name: The name of the logger

    :param level: Severity level of the returned logger
    :type level: Level or None

    :param bool stream: If true, add a stream handler that
                        lets the logger print to the screen

    :return: a logger for `name`, unless `name` is empty,
             in which case the root logger
    :rtype: Logger

    :raises LoggingError: If :py:func:`init` was not called
                          prior to calling this function

    A new logger is created upon the first invocation with
    the specified `name`. If `stream` equals true, a stream
    handler is added to it, but this only applies to the
    creation of the logger. The newly created logger is cached
    and then returned on subsequent calls with the same `name`.

    To add a stream handler to the logger after its creation,
    call :py:func:`add_handler`.

    Loggers created through this function are actually from
    Python's ``logging`` module. This matters because of
    a certain trait that loggers have.

    .. note:: Logging Hierarchy
       A logger's `name` can potentially be a dot-separated
       hierarchical value, like ``foo.bar.baz`` (though it could
       also be just plain ``foo``). Loggers that are further down
       the hierarchical list are children of the loggers which
       are higher up the list. For example, given the `name`
       ``foo``, loggers ``foo.bar``, ``foo.bar.baz``, and
       ``foo.bam``, are all descendants of ``foo``.
    """
    global _cache

    if not _initialized:
        raise LoggingError("You must call init() before using any of the other functions.")

    # Return the root logger if name is "" or "yt_dlp_tk"
    parts = name.split(".")
    isroot = parts[0] == "" and len(parts) == 1
    if isroot:
        return _rootLogger

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
