from __future__ import annotations
from tkinter import ttk, constants as tkconst
from .utils import _WidgetMixin
from ..signals import signal, InvalidSignalError
from typing import TYPE_CHECKING
import tkinter as tk, sys

if TYPE_CHECKING:
    from typing import Any
    from .utils import _Widget

class ExSpinbox(ttk.Spinbox, _WidgetMixin):
    """Extended entry widget."""

    def __init__(self, master: _Widget=None, *, text: str | None=None, **kw: Any):
        """
        EXTRA OPTIONS

            text = specify a textual string to display next
                   to the entry

        SIGNALS

            text_changed(new_text: str)
                The 'text' parameter has changed. Provides
                the new string for the label.
        """
        self.on_text_changed = signal('text_changed', self)
        self.on_text_changed.connect(self)

        self.frame = ttk.Frame(master, padding='0 0 0 16')
        self.label = ttk.Label(self.frame, text=text or "")

        super().__init__(self.frame, **kw)

        self.entry_name = ttk.Entry.__str__(self)

        # Custom resources
        self.set_custom_resources(text=text)
        self.on_text_changed.emit(text or "")

        self.pack()

        self.override_geomtry_methods(ttk.Entry)

    def configure(self, *, text: str | None=None, **kw: Any):
        if text is not None:
            self.set_custom_resource('text', text)
            self.on_text_changed.emit(text)

        super().configure(kw)

    def cget(self, key: str) -> Any:
        if self.resource_defined(key):
            return self.get_custom_resource(key)

        return super().cget(key)

    def config(self, *, text: str | None=None, **kw: Any):
        return self.configure(text=text, **kw)

    def get(self) -> float:
        """Return the value as a float."""
        return float(super().get())

    def on_notify(self, sig: str, obj=None, *args: Any, **kw: Any) -> None: # pyright: ignore
        match sig:
            case 'text_changed':
                text: str = args[0]
                label = self.label
                if text:
                    kw = {}
                    if not label.winfo_ismapped():
                        if self.frame.winfo_ismapped():
                            kw['before'] = self.entry_name
                        label.pack(**kw)
                    label.configure(text=text)
                else:
                    if label.winfo_ismapped():
                        label.pack_forget()

            case _:
                raise InvalidSignalError(sig)

ExSpinbox.override_init_docstring(ttk.Spinbox)
