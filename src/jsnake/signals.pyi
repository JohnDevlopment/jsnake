from typing import Protocol, overload, Any

class _signal_function(Protocol):
    def __call__(self, obj: object, *args: Any, **kw: Any) -> None:
        ...

_SignalBinds = tuple[_signal_function, tuple[Any, ...], dict[str, Any]]

class signal:
    """Implements the observer pattern."""

    def __init__(self, name: str, obj: object=None): ...

    @property
    def name(self):
        ...

    @property
    def count(self):
        ...

    @property
    def obj(self):
        ...

    def connect(self, func: _signal_function, *binds: Any, **kw: Any) -> None:
        ...

    def disconnect(self, func: _signal_function, *binds: Any, **kw: Any) -> None:
        ...

    def emit(self, *args: Any, **kw: Any) -> None:
        ...

    def __str__(self) -> str:
        ...
