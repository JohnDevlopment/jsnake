from __future__ import annotations
from tkinter import ttk
import tkinter as tk
from typing import Any, Literal, cast, Protocol, Type, TypeVar, Sequence

T_co = TypeVar("T_co", contravariant=True)
T = TypeVar("T")
# U = TypeVar("U")

_Column = tuple[str, str, int] # pyright: ignore
_Widget = tk.Widget | None
_StateSpec = Literal['normal', 'disabled'] | tuple[str, ...]

class _WidgetMixin: # pyright: ignore
    @classmethod
    def override_init_docstring(cls, parent: Type[tk.Widget]) -> None:
        ...

    def override_geomtry_methods(self, cls: Type[tk.Widget]) -> None:
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

class _SupportsStateMethods(Protocol):
    def state(self, *args) -> Any: ...

class _ResourceManager:
    __slots__ = ('resources',)

    def __init__(self, **kw: Any): ...

    def __getitem__(self, key: str, /) -> Any: ...

    def __setitem__(self, key: str, value: Any, /) -> None: ...

    def __contains__(self, key: str) -> bool: ...

class Variable(tk.Variable):
    """Class to define value holders for widgets."""

    def __init__(self, master: _Widget=None, value=None,
                 name: str | None=None, temp: bool=False): ...

    def __del__(self): ...

    @property
    def tk(self): ...

class StringVar(Variable):
    def __init__(self, master: _Widget=None, value: Any=None,
                 name: str | None=None, temp: bool=False):
        ...

    def get(self) -> str:
        ...

class TkBusyCommand(tk.Widget):
    def __init__(self, master: tk.Widget, window, /):
        ...

    def forget(self):
        ...

    def hold(self):
        ...

    @property
    def is_busy(self) -> bool:
        ...

    def __enter__(self):
        ...

    def __exit__(self, *args):
        ...

class InState:
    def __init__(self, owner: _SupportsStateMethods, state_spec: _StateSpec):
        self.owner = owner
        ...

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback): # pyright: ignore
        ...

class SupportsRichComparisons(Protocol[T_co]):
    def __eq__(self, other: T_co) -> bool:
        ...

    def __ne__(self, other: T_co) -> bool:
        ...

    def __lt__(self, other: T_co) -> bool:
        ...

    def __le__(self, other: T_co) -> bool:
        ...

    def __gt__(self, other: T_co) -> bool:
        ...

    def __ge__(self, other: T_co) -> bool:
        ...

def binary_search(array: Sequence[T], pattern: T) -> int:
    ...
