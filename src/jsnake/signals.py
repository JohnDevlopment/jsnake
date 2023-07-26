"""Signals, objects which implement the command pattern."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, TypeGuard, Protocol

    class _signal_function(Protocol):
        def __call__(self, obj: object, *args: Any, **kw: Any) -> None:
            ...

    _SignalBinds = tuple[_signal_function, tuple[Any, ...], dict[str, Any]]

class InvalidSignalError(RuntimeError):
    """Invalid signal."""

class signal:
    """Implements the observer pattern."""

    __slots__ = ('name', 'observers', 'observer_count', 'obj')

    def __init__(self, name: str, obj: object=None):
        """
        Construct a signal with the given name.

        :param str name: The name of the signal

        :param object obj: The object which is considered
                           the signal's owner. If omitted,
                           the caller's ``self`` is used, or
                           its module if ``self`` is unavailable
        """
        self.name = name #: Name of the signal
        self.observers = [] #: List of observers/binds
        self.observer_count = 0 #: Number of observers
        self.obj = obj #: Object this is bound to

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

    def connect(self, obj_or_func, *binds, **kw):
        """
        Connect the signal.

        :param obj_or_func: A class which has an ``on_notify``
                            method, or a function

        :param *binds: Positional arguments that get bound to the
                       connected observer/function

        :param **kw: Keyword arguments that get bound to the connected
                     observe/function

        .. code-block:: python

           def on_notified(obj: object, *args, **kw):
               ...

           class observer:
               def on_notify(self, sig: str, obj: object, *args, **kw):
                   ...

        Unless `obj_or_func` is a function, it is treated as an object which
        defines a ``on_notify`` method. That method is expected to take as
        arguments the name of the signal, the object that is bound to it
        (see :py:func:`__init__`), and the arguments passed to :py:func:`emit`
        (see documentation).

        If `obj_or_func` is a function, it shall accept the same arguments
        in the same order.
        """
        if callable(obj_or_func):
            bind = self._form_signal_bind(obj_or_func, *binds, **kw)
            self.observers.append(bind)
        else:
            self.observers.append(obj_or_func)

        self.observer_count += 1

    def disconnect(self, obj_or_func, *binds, **kw):
        """
        Disconnect the signal.

        :param *binds: Positional arguments that get bound to the
                       connected observer/function

        :param **kw: Keyword arguments that get bound to the connected
                     observe/function

        .. note::
           Arguments must be the same as the ones passed to :py:func:`connect`.
        """
        if callable(obj_or_func):
            bind = self._form_signal_bind(obj_or_func, *binds, **kw)
            self.observers.remove(bind)
        else:
            self.observers.remove(obj_or_func)

        self.observer_count -= 1

    @staticmethod
    def _is_signal_bind(arg) -> TypeGuard[_SignalBinds]:
        return isinstance(arg, tuple)

    def emit(self, *args: Any, **kw: Any):
        """
        Emit the signal, notifying all registered observers of the event.

        :param Any *args: Positional arguments that get forwarded to any
                          registered observers

        :param **kw: Keyword arguments that get forwarded to the registered
                     observers
        """
        for obv in self.observers:
            if self._is_signal_bind(obv):
                # Is a signal bind (tuple with a function, *args, and **kw)
                fn, sargs, skw = obv
                args = args + sargs
                kw.update(skw)

                # Call function with appended arguments
                fn(self.obj, *args, **kw)
            else:
                # Is an observer, call its notify method
                obv.on_notify(self.name, self.obj, *args, **kw)

    def __str__(self) -> str:
        return self.name
