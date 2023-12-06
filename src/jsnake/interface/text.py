from __future__ import annotations
from . import _WidgetMixin, _StateMethods
from ..signals import signal
from tkinter import ttk
from typing import TYPE_CHECKING
import tkinter as tk, re

if TYPE_CHECKING:
    from typing import Literal, Optional

class ExText(tk.Text, _WidgetMixin, _StateMethods):
    """Extended text widget."""

    def _tk_color_name_to_number(self, color: str, /) -> str:
        if re.match(r'#[0-9a-f]{6}', color):
            return color

        r, g, b = self.winfo_rgb(color)
        icolor = ((r & 0xff00) << 8) | (g & 0xff00) | (b >> 8)
        return f"#{icolor:06x}"

    def __init__(self, master=None, *,
                 scrollx=False, scrolly=False,
                 normalbackground=None,
                 disabledbackground=None,
                 **kw):
        # Define signals
        self.on_x_scrollbar_changed = signal('x_scrollbar_changed', self)
        self.on_y_scrollbar_changed = signal('y_scrollbar_changed', self)
        self.on_background_changed = signal('background_changed', self)
        self.on_state_changed = signal('state_changed', self)

        self.frame = ttk.Frame(master)

        self.xbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
            command=self.xview)

        self.ybar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
            command=self.yview)

        # Connect signals
        self.on_x_scrollbar_changed.connect(
            self._on_scrollbar_changed,
            scrollbar=self.xbar,
            side=tk.BOTTOM,
            fill=tk.X
        )
        self.on_y_scrollbar_changed.connect(
            self._on_scrollbar_changed,
            scrollbar=self.ybar,
            side=tk.RIGHT,
            fill=tk.Y,
            before=self
        )
        self.on_background_changed.connect(self._on_background_changed)
        self.on_state_changed.connect(self._on_state_changed)

        kw['xscrollcommand'] = self.xbar.set
        kw['yscrollcommand'] = self.ybar.set

        super().__init__(self.frame, **kw)

        # Custom resources
        def _default_bg(color: str | None, *state_flags: str):
            defbg = ttk.Style().lookup('TEntry', 'fieldbackground', state_flags)
            return color or defbg

        normalbackground = _default_bg(normalbackground, "!disabled")
        disabledbackground = _default_bg(disabledbackground, "disabled")

        self.set_custom_resources(
            scrollx=scrollx, scrolly=scrolly,
            normalbackground=normalbackground,
            disabledbackground=disabledbackground
        )

        self.pack(fill=tk.BOTH)

        self.override_geomtry_methods(tk.Text)

        # Emit signals
        self.on_x_scrollbar_changed.emit(scrollx)
        self.on_y_scrollbar_changed.emit(scrolly)
        self.on_background_changed.emit("normal",
                                        self.get_custom_resource('normalbackground'))
        self.on_background_changed.emit("disabled",
                                        self.get_custom_resource('disabledbackground'))

    def configure(self, **kw):
        missing = object()

        # scrollx
        scrollx: bool | object = kw.pop('scrollx', missing)
        if scrollx is not missing:
            if not isinstance(scrollx, bool):
                raise TypeError("-scrollx must be a boolean")
            self.set_custom_resource('scrollx', scrollx)
            self.on_x_scrollbar_changed.emit(scrollx)

        # scrolly
        scrolly: bool | object = kw.pop('scrolly', missing)
        if scrolly is not missing:
            if not isinstance(scrolly, bool):
                raise TypeError("-scrolly must be a boolean")
            self.set_custom_resource('scrolly', scrolly)
            self.on_y_scrollbar_changed.emit(scrolly)

        # normal background
        normalbackground: str | object = kw.pop('normalbackground', missing)
        if normalbackground is not missing:
            if not isinstance(normalbackground, str):
                raise TypeError("-normalbackground must be a string")
            color = self._tk_color_name_to_number(normalbackground)
            self.set_custom_resource('normalbackground', color)
            self.on_background_changed.emit("normal", color)

        # disabled background
        disabledbackground: str | object = kw.pop('disabledbackground', missing)
        if disabledbackground is not missing:
            if not isinstance(disabledbackground, str):
                raise TypeError("-disabledbackground must be a string")
            color = self._tk_color_name_to_number(disabledbackground)
            self.set_custom_resource('disabledbackground', color)
            self.on_background_changed.emit("disabled", color)

        super().configure(**kw)

        if 'state' in kw:
            self.on_state_changed.emit(kw['state'])

    def cget(self, key: str, /):
        if self.resource_defined(key):
            return self.get_custom_resource(key)

        return super().cget(key)

    def _on_scrollbar_changed(self, obj: object,
                              enabled: bool, **kw) -> None:
        assert 'scrollbar' in kw
        assert 'side' in kw
        assert 'fill' in kw

        sbar: ttk.Scrollbar = kw.pop('scrollbar')
        side: Literal['left', 'right', 'top', 'bottom'] = kw.pop('side')
        fill: Literal['none', 'x', 'y', 'both'] = kw.pop('fill')

        if enabled:
            if not sbar.winfo_ismapped():
                # Map the scrollbar if it isn't already
                sbar.pack(side=side, fill=fill, **kw)
                return

        if sbar.winfo_ismapped():
            # Disabled; the scrollbar is visible, so unmap it
            sbar.pack_forget()

    def _on_background_changed(self, obj: object, bgstate: str, color: str, **kw) -> None:
        if bgstate == self.state():
            self.configure(background=color)

    def _on_state_changed(self, obj, state: str, **kw):
        color = self.cget(state + "background")
        self.configure(background=color)

from . import StringVar, BooleanVar

def test():
    from tkinter import Tk, ttk
    from functools import partial

    root = Tk()

    frame = ttk.Frame(root)
    frame.pack(fill='both', expand=True)

    textbox = ExText(frame)
    textbox.pack()

    # Radio buttons
    subframe = ttk.Frame(frame)
    subframe.pack(fill='both')

    def _scroll(var: BooleanVar, opt: str):
        kw = {opt: var.get()}
        textbox.configure(**kw)

    ttk.Checkbutton(
        subframe,
        text="Vertical Scrollbar",
        variable=BooleanVar(value=False, name="SCROLLY"),
        onvalue=True,
        offvalue=False,
        command=partial(_scroll, BooleanVar(name="SCROLLY"), "scrolly")
    ).pack(side=tk.LEFT)

    ttk.Checkbutton(
        subframe,
        text="Horizontal Scrollbar",
        variable=BooleanVar(value=False, name="SCROLLX"),
        onvalue=True,
        offvalue=False,
        command=partial(_scroll, BooleanVar(name="SCROLLX"), "scrollx")
    ).pack(side='left')

    def _state(var: StringVar):
        state = var.get()
        textbox.state(state)

    var = StringVar(value="normal")
    ttk.Checkbutton(
        subframe,
        text="Textbox state",
        variable=var,
        onvalue="normal",
        offvalue="disabled",
        command=lambda: _state(var)
    ).pack(side=tk.LEFT)

    root.mainloop()

if __name__ == "__main__":
    test()
