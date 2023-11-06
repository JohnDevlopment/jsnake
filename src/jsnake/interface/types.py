from __future__ import annotations
from typing import Literal, Protocol, Any
import tkinter as tk

class _SupportsStateMethods(Protocol):
    def state(self, *args) -> Any: ...

_Column = tuple[str, str, int]
_Widget = tk.Widget | None
_StateSpec = Literal['normal', 'disabled'] | tuple[str, ...]
