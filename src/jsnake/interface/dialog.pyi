from tkinter import Toplevel, Misc, ttk, Event
from typing import Optional

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
