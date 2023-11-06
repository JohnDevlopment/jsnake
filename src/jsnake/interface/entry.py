from __future__ import annotations
from tkinter import ttk
from ..signals import signal
from . import _WidgetMixin
from typing import TYPE_CHECKING
import tkinter as tk, sys

if TYPE_CHECKING:
    from typing import Any, Literal
    from .utils import _Widget

class ExEntry(ttk.Entry, _WidgetMixin):
    """Extended entry widget."""

    def __init__(self, master: _Widget=None, *, scrollx: bool=False,
                 text: str | None=None, clearbutton: bool=False, **kw: Any):
        """
        Construct an extended entry widget with the parent `master`.

        :param master: This window's parent

        :keyword bool clearbutton: If true, a button is displayed next to the entry
                                   that clears the entry text when pressed

        :keyword bool scrollx: If true, a horizontal scrollbar is added

        :keyword text: A textual string to display as a label next to the entry
        :type text: str or None
        """
        # Add signal 'x_scrollbar_changed'
        self.on_x_scrollbar_changed = signal('x_scrollbar_changed', self)
        self.on_x_scrollbar_changed.connect(self._on_x_scrollbar_changed)

        # Add signal 'label_changed'
        self.on_label_changed = signal('label_changed', self)
        self.on_label_changed.connect(self._on_label_changed)

        # This signal is emitted whenever the text inside the entry changes
        self.on_text_changed = signal('text_changed', self)
        self.on_text_changed.connect(self._on_text_changed)

        # Add signal 'clearbutton_changed'
        self.on_clearbutton_changed = signal('clearbutton_changed', self)
        self.on_clearbutton_changed.connect(self._on_clearbutton_changed)

        # Frame this enter goes inside
        self.frame = ttk.Frame(master, padding='0 0 0 16')

        # Label that displays the contents of the text property
        self.label = ttk.Label(self.frame, text=text or "")

        # X scrollbar
        self.xbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.xview)

        # Button that clears the text
        self.clearbutton = ttk.Button(self.frame, text="X", command=self.clear)

        # Bind the X scroll command to the scrollbar
        kw['xscrollcommand'] = self.xbar.set

        super().__init__(self.frame, **kw)

        # Add validation to entry
        self.config(validate="all",
                    validatecommand=(self.register(self.__validate_entry),
                                     '%V', '%P'))

        self.entry_name = ttk.Entry.__str__(self)

        # Custom resources
        self.set_custom_resources(scrollx=scrollx, text=text, clearbutton=clearbutton)

        # Pack the entry
        self.grid(row=0, column=1)

        # Emit signals so that the program can react to the initialized options
        self.on_x_scrollbar_changed.emit(scrollx)
        self.on_label_changed.emit(text or "")
        self.on_clearbutton_changed.emit(clearbutton)
        self.on_text_changed.emit("")

        self.override_geomtry_methods(ttk.Entry)

    def clear(self) -> None:
        """Clear the entry."""
        self.delete(0, tk.END)
        self.on_text_changed.emit("")

    def configure(self, *, scrollx: bool | None=None,
                  clearbutton: bool | None=None,
                  text: str | None=None, **kw: Any):
        if scrollx is not None:
            self.set_custom_resource('scrollx', scrollx)
            self.on_x_scrollbar_changed.emit(scrollx)

        if clearbutton is not None:
            self.set_custom_resource('clearbutton', clearbutton)
            self.on_clearbutton_changed.emit(clearbutton)

        if text is not None:
            self.set_custom_resource('text', text)
            self.on_label_changed.emit(text)

        super().configure(kw)

    def cget(self, key: str) -> Any:
        if self.resource_defined(key):
            return self.get_custom_resource(key)

        return super().cget(key)

    def config(self, *, scrollx: bool | None=None,
                  text: str | None=None, **kw: Any):
        return self.configure(scrollx=scrollx, text=text, **kw)

    def __validate_entry(self,
                         reason: Literal['focusin', 'focusout', 'key', 'forced'],
                         new_text: str) -> bool:
        # Entry validation
        if reason.startswith('focus'):
            # Skip focus(in/out) events
            return True

        # Insertions or deletions warrent this signal
        self.on_text_changed.emit(new_text)

        return True

    ## Signals
    #

    def _on_label_changed(self, obj: object, new_text: str, **kw):
        label = self.label
        if new_text:
            # There is text to display

            if not label.winfo_ismapped():
                # Map the label
                self.label.grid(row=0, column=0)

            # Configure the text
            label.configure(text=new_text)

            return

        # No text, unmap the label if it is visible
        if label.winfo_ismapped():
            label.grid_forget()

    def _on_x_scrollbar_changed(self, obj: object, state: bool, **kw):
        if state:
            if not self.xbar.winfo_ismapped():
                # Map the scrollbar if it isn't already
                self.xbar.grid(row=1, column=1, sticky='ew')
                return

            if self.xbar.winfo_ismapped():
                # The scrollbar is visible, so unmap it
                self.xbar.grid_forget()

    def _on_clearbutton_changed(self, obj: object, state: bool, **kw):
        clearbutton = self.clearbutton

        # If enabled, map the button if not already
        if state and not clearbutton.winfo_ismapped():
            clearbutton.grid(row=0, column=2)
            return

        # If disabled, unmap the button if it is visible
        if not state and clearbutton.winfo_ismapped():
            clearbutton.grid_forget()

    def _on_text_changed(self, obj: object, new_text: str, **kw):
        # Enable the 'clear' button if there's text, otherwise disable it
        new_state = ("!disabled",) if new_text else ("disabled",)
        self.clearbutton.state(new_state)

# ExEntry.override_init_docstring(ttk.Entry)
