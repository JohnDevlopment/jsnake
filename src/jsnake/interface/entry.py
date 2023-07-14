from __future__ import annotations
from tkinter import ttk
from .utils import _WidgetMixin
from ..signals import signal, InvalidSignalError
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
        EXTRA OPTIONS

            scrollx     = if true, add a scrollbar
            text        = specify a textual string to display next
                          to the entry
            clearbutton = if set to True, a button is displayed
                          that clears the text when pressed

        SIGNALS

            x_scrollbar_changed(state: bool)
                The horizontal scrollbar has changed. STATE
                is true if enabled and false otherwise.

            label_changed(new_text: str)
                The 'text' parameter has changed. Provides
                the new string for the label.

            clearbutton_changed(enabled: bool)
                The 'clearbutton' parameter has changed.
                Provides the enabled status of the button.

            text_changed(new_text: str)
                The text inside the entry has changed. Provides
                the updated content.
        """
        # Add signal 'x_scrollbar_changed'
        self.on_x_scrollbar_changed = signal('x_scrollbar_changed', self)
        self.on_x_scrollbar_changed.connect(self)

        # Add signal 'label_changed'
        self.on_label_changed = signal('label_changed', self)
        self.on_label_changed.connect(self)

        # This signal is emitted whenever the text inside the entry changes
        self.on_text_changed = signal('text_changed', self)
        self.on_text_changed.connect(self)

        # Add signal 'clearbutton_changed'
        self.on_clearbutton_changed = signal('clearbutton_changed', self)
        self.on_clearbutton_changed.connect(self)

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

    def on_notify(self, sig: str, obj=None, *args: Any, **kw: Any) -> None: # pyright: ignore
        match sig:
            case 'x_scrollbar_changed':
                scrollx: bool = args[0]
                if scrollx:
                    if not self.xbar.winfo_ismapped():
                        # Map the scrollbar if it isn't already
                        self.xbar.grid(row=1, column=1, sticky='ew')
                else:
                    if self.xbar.winfo_ismapped():
                        # The scrollbar is visible, so unmap it
                        self.xbar.grid_forget()

            case 'label_changed':
                text: str = args[0]
                label = self.label
                if text:
                    if not label.winfo_ismapped():
                        # Map the label if it isn't already visible
                        self.label.grid(row=0, column=0)

                    # Configure the text
                    label.configure(text=text)
                else:
                    if label.winfo_ismapped():
                        # The label is visible, so unmap it
                        label.grid_forget()

            case 'clearbutton_changed':
                # The 'clearbutton' option has been configured
                clearbutton = self.clearbutton

                enabled: bool = args[0]
                if enabled:
                    if not clearbutton.winfo_ismapped():
                        # Map the button if it's invisible
                        clearbutton.grid(row=0, column=2)
                else:
                    if clearbutton.winfo_ismapped():
                        # Unmap the visible button
                        clearbutton.grid_forget()

            case 'text_changed':
                # The text inside the entry has changed
                new_text: str = args[0]

                # Enable the 'clear' button if there's text, otherwise disable it
                new_state = ("!disabled",) if new_text else ("disabled",)
                self.clearbutton.state(new_state)

            case _:
                # Invalid signal, therefore raise exception
                raise InvalidSignalError(sig)

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

ExEntry.override_init_docstring(ttk.Entry)

def _test_nontemp_variables():
    from .utils import StringVar

    for varname in ['NAME', 'RADIO']:
        var = StringVar(name=varname)
        print(f"{varname}:", var.get())

def _test_temp_variables():
    from .utils import StringVar

    for varname in ['TEMPNAME', 'TEMPRADIO']:
        var = StringVar(name=varname, temp=True)
        print(f"{varname}:", var.get())

def make_interface():
    from .utils import StringVar

    root = tk.Tk()
    root.title("Test ExEntry")

    frame = ttk.Frame()
    frame.pack(fill=tk.BOTH, expand=True)

    # Non-temp variables
    subframe = ttk.Labelframe(frame, text="Non-Temp Vars")
    subframe.pack()

    ExEntry(subframe, text="Name", textvariable=StringVar(name='NAME'))\
        .pack()

    var = StringVar(name='RADIO', value='one')
    ttk.Radiobutton(subframe, variable=var, value='one', text="One").pack()
    ttk.Radiobutton(subframe, variable=var, value='two', text="Two").pack()
    ttk.Radiobutton(subframe, variable=var, value='three', text="Three").pack()

    ttk.Button(subframe, text='Test', command=_test_nontemp_variables).pack()

    # Temp variables
    subframe = ttk.Labelframe(frame, text="Temp Vars")
    subframe.pack()

    ExEntry(subframe, text="Temp Name", textvariable=StringVar(name='TEMPNAME', temp=True))\
        .pack()

    var = StringVar(name='TEMPRADIO', value='one', temp=True)
    ttk.Radiobutton(subframe, variable=var, value='one', text="One").pack()
    ttk.Radiobutton(subframe, variable=var, value='two', text="Two").pack()
    ttk.Radiobutton(subframe, variable=var, value='three', text="Three").pack()

    ttk.Button(subframe, text='Test', command=_test_temp_variables).pack()

    # ExEntry options
    subframe = ttk.Labelframe(frame, text="Options")
    subframe.pack()

    entry = ExEntry(subframe)
    entry.pack()
    entry.after(2000, lambda: entry.config(clearbutton=True))

    return root

def test () -> int:
    root = make_interface()
    root.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(test())
