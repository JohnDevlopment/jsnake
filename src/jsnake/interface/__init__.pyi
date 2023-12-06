from .types import _StateSpec, _SupportsStateMethods
from typing import Any, Callable, Type, overload
from typing_extensions import Self
from tkinter import Misc, Widget
from _typeshed import Incomplete
import tkinter, _tkinter

_StringDict = dict[str, Any]

class Variable(tkinter.Variable):
    tk: _tkinter.TkappType

    def __init__(self, master: Misc=..., value: Any=..., name: str=..., temp: bool=...) -> None:
        ...

class BooleanVar(Variable):
    def __init__(self, master: Misc=..., value: bool=..., name: str=..., temp: bool=...) -> None:
        ...

    def set(self, value: bool) -> None:
        ...

    def get(self) -> bool:
        ...

    initialize = set

class StringVar(Variable):
    def __init__(self, master: Misc=..., value: str=..., name: str=..., temp: bool=...) -> None:
        ...

    def get(self) -> str:
        ...

    initialize = set

class _WidgetMixin:
    @classmethod
    def override_init_docstring(cls, parent: Type[Widget]) -> None:
        ...

    def override_geomtry_methods(self, cls: Type[Widget]) -> None:
        ...

    def __str__(self) -> str:
        ...

    # Resource functions

    def set_custom_resources(self, **kw: Any) -> None:
        ...

    def set_custom_resource(self, key: str, value: Any) -> None:
        ...

    def get_custom_resource(self, key: str) -> Any:
        ...

    def resource_defined(self, key: str) -> bool:
        ...

    def set_meta(self, key: str, value: Any) -> None:
        ...

    def get_meta(self, key: str, default: Any=None) -> Any:
        ...

class _StateMethods:
    @overload
    def state(self) -> str:
        ...

    @overload
    def state(self, state_spec: None) -> str:
        ...

    @overload
    def state(self, state_spec: Incomplete) -> None:
        ...

    def instate(self, state_spec, callback: Callable[..., None]=..., *args: Any, **kw: Any) -> None:
        ...

class TkBusyCommand(Widget):
    def __init__(self, master: Widget, window: Widget, /) -> None:
        ...

    def forget(self) -> None:
        ...

    def hold(self) -> None:
        ...

    @property
    def is_busy(self) -> bool:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(self, *args: Any) -> None:
        ...

class InState:
    def __init__(self, owner: _SupportsStateMethods, state_spec: _StateSpec) -> None:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(self, *args: Any) -> None:
        ...
