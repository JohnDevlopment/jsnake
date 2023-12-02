from tkinter import Toplevel, Misc, ttk, Event
from typing import Optional, Callable, TypeAlias, Literal

_MsgboxType: TypeAlias = Literal['abortretryignore', 'ok', 'okcancel', 'retrycancel', 'yesno', 'yesnocancel']
_MsgBoxCallback: TypeAlias = Callable[[str], None]

class ExDialog(Toplevel):
    def __init__(self, parent: Misc=..., title: str=...) -> None:
        ...

    def destroy(self) -> None:
        ...

    def body(self, body: ttk.Frame) -> Misc | None:
        ...

    def buttonbox(self) -> None:
        ...

    def validate(self) -> bool:
        ...

    def ok(self, event: Event[Misc]=...) -> None:
        ...

    def cancel(self, event: Event[Misc]=...) -> None:
        ...

    def apply(self) -> None:
        ...

class ExMessagebox(ExDialog):
    """Message box."""

    def __init__(self, parent: Misc=..., *,
                 command: _MsgBoxCallback=...,
                 default: Literal['abort', 'cancel', 'ignore', 'ok',
                                  'no', 'retry', 'yes']=...,
                 details: str=...,
                 icon: Literal['info', 'error']=...,
                 message: str=...,
                 title: str=...,
                 type: Literal['abortretryignore', 'ok', 'okcancel',
                               'retrycancel', 'yesno', 'yesnocancel']=...):
        ...
