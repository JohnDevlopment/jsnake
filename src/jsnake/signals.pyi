from typing import Protocol, overload, Any

class observer(Protocol):
    """An observer that takes one or more signals."""

    def on_notify(self, sig: str, obj: Any, *args: Any, **kw: Any):
        """Called when OBJ has notified of signal SIG."""
        ...

class _signal_function(Protocol):
    def __call__(self, obj: object, *args: Any, **kw: Any) -> None:
        ...

_SignalBinds = tuple[_signal_function, tuple[Any, ...], dict[str, Any]]

class signal:
    """Implements the observer pattern."""

    name: str
    observers: list[observer | _SignalBinds]
    observer_count: int
    obj: object

    def __init__(self, name: str, obj: object=None): ...

    @overload
    def connect(self, obj_or_func: observer, *binds: Any, **kw: Any) -> None:
        ...

    @overload
    def connect(self, obj_or_func: _signal_function, *binds: Any, **kw: Any) -> None:
        ...

    @overload
    def disconnect(self, obj_or_func: observer, *binds: Any, **kw: Any) -> None:
        ...

    @overload
    def disconnect(self, obj_or_func: _signal_function, *binds: Any, **kw: Any) -> None:
        ...

    def emit(self, *args: Any, **kw: Any) -> None:
        ...

    def __str__(self) -> str:
        ...
