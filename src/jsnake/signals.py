"""Signals, objects which implement the command pattern."""

from __future__ import annotations
from typing import Protocol, Any, cast

class _signal_function(Protocol):
    def __call__(self, obj: object, *args: Any, **kw: Any) -> None:
        ...

class InvalidSignalError(RuntimeError):
    """Invalid signal."""

class signal:
    """Implements the observer pattern."""

    __slots__ = ('name', '_observers', 'obj')

    def __init__(self, name, obj=None):
        """
        Construct a signal with the given name.

        :param str name: The name of the signal

        :param object obj: The object which is considered
                           the signal's owner. If omitted,
                           the caller's ``self`` is used, or
                           its module if ``self`` is unavailable
        """
        self.name: str = name #: Name of the signal
        self._observers = []
        self.obj = obj #: Object bound to the signal

        if obj is None:
            import inspect, sys

            # Get current frame
            frame = inspect.currentframe()
            if frame is None: return

            # Go up one level, to the function calling this one
            frame = frame.f_back
            if frame is None: return

            # Get the 'self' argument if present
            _locals = frame.f_locals
            obj = _locals.get('self')
            if obj is None:
                # Not present, use the module instead
                obj = sys.modules[frame.f_globals['__name__']]

            self.obj = obj

    def _form_signal_bind(self, fn, *args, **kw):
        return fn, args, kw

    @property
    def count(self):
        """Number of registered functions."""
        return len(self._observers)

    def connect(self, func, *binds, **kw):
        """
        Connect the signal.

        :param function func: A function that matches :ref:`signal-function`

        :param \*binds: Positional arguments that get bound to `func`

        :param \*\*kw: Keyword arguments that get bound to `func`

        :raises TypeError: If `func` is not callable

        .. _signal-function:

        .. rubric:: Signal Function

        .. code-block:: python

           def on_notified(obj: object, *args, **kw):
               ...

        `func` must accept at least one argument, that being the
        object bound to the signal (see :py:meth:`__init__`), but may
        include any bindings found in `\*binds` and `\*\*kw`.
        `\*binds` will be at the end of the argument list, after
        any arguments passed to :py:meth:`emit`. Keyword arguments,
        both those passed to :py:meth:`emit` and those passed here,
        will be found in the keywords part of the signature.
        """
        if not callable(func):
            raise TypeError("First argument must be a function")

        bind = self._form_signal_bind(func, *binds, **kw)
        self._observers.append(bind)

    def disconnect(self, func, *binds, **kw):
        """
        Disconnect the signal.

        :param \*binds: Positional arguments that get bound to `func`

        :param \*\*kw: Keyword arguments that get bound to `func`

        :raises ValueError: If this signal is not connected to `func` with
                            this particular set of parameters

        .. note::
           Arguments must be the same as the ones passed to :py:func:`connect`.
        """
        bind = self._form_signal_bind(func, *binds, **kw)
        self._observers.remove(bind)

    @staticmethod
    def _is_signal_bind(arg):
        return isinstance(arg, tuple)

    def emit(self, *args, **kw):
        """
        Emit the signal.

        :param \*args: Positional arguments that get forwarded to any
                       registered functions

        :param \*\*kw: Keyword arguments that get forwarded to the registered
                       functions

        Functions that are connected to this signal will accept arguments
        in the following order: the `obj` parameter passed to :py:meth:`__init__`,
        `\*args` and `\*\*kw` from this function, and `\*args` and `\*\*kw` from
        :py:meth:`connect`.
        """
        for obv in self._observers:
            assert self._is_signal_bind(obv), "argument is not a signal binding"

            # Is a signal bind (tuple with a function, *args, and **kw)
            fn, sargs, skw = obv
            args = args + sargs
            kw.update(skw)

            # Call function with appended arguments
            fn = cast(_signal_function, fn)
            fn(self.obj, *args, **kw)

    def __str__(self) -> str:
        return self.name
