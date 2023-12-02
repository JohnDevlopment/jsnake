"""This module handles dialog boxes."""

from __future__ import annotations
from tkinter import (
    LEFT,
    CENTER,
    ACTIVE,
    NW,
    Tk,
    Misc,
    ttk,
    Toplevel,
    _get_temp_root, # pyright: ignore
    _destroy_temp_root # pyright: ignore
)
#from tkinter.simpledialog import _setup_dialog, _place_window # pyright: ignore
from tkinter.simpledialog import _setup_dialog # pyright: ignore
from typing import TYPE_CHECKING, cast, Callable
from ._images import load_image
from ..logging import get_logger
import re, functools

if TYPE_CHECKING:
    from typing import Any, Optional

class ExDialog(Toplevel):
    """A base class for all dialogs."""

    def __init__(self, parent=None, *, title=None, _parallel=False):
        master = parent or _get_temp_root()
        self.master = master

        Toplevel.__init__(self, master, class_="Dialog")

        self.withdraw() # remain invisible while we figure out the geometry

        parent = cast(Tk | None, parent)
        if parent is not None and parent.winfo_viewable():
            self.wm_transient(parent)

        if title:
            self.title(title)

        _setup_dialog(self)

        self.parent = parent

        # Create body
        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        # Get window to set focus on
        if self.initial_focus is None:
            self.initial_focus = self
        self.initial_focus = cast(Misc, self.initial_focus)

        self.buttonbox()

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        _place_window(self, parent)

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        if not _parallel:
            self.wait_window(self)

    def destroy(self):
        """Destroy the window."""
        self.initial_focus = None
        Toplevel.destroy(self)
        _destroy_temp_root(self.master)

    # Construction hooks
    #

    def body(self, body):
        """
        Called by :py:meth:`__init__` to create the body.

        :param ttk.Frame body: The dialog body

        :return: The widget that should gain focus
        :rtype: Misc or None

        This method should be overridden.
        """
        pass

    def buttonbox(self):
        """Called by :py:meth:`__init__` to create the buttons."""
        box = ttk.Frame(self)

        BUTTON_PACK_OPTS = dict(side=LEFT, padx=5, pady=5)

        ttk.Button(box, text="OK", command=self.ok,
                   default=ACTIVE).pack(BUTTON_PACK_OPTS)

        ttk.Button(box, text="Cancel",
                   command=self.cancel).pack(BUTTON_PACK_OPTS)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # Button semantics
    #

    def ok(self, event=None):
        """Called when the OK button is pressed."""
        if not self.validate():
            cast(Misc, self.initial_focus).focus_set()
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()

    def validate(self):
        """
        Validate the data.

        :return: True or False depending on whether the
                 data inputted into the dialog is valid
        :rtype: bool

        By default, this always evaluates as true.

        This is called before the dialog is
        destroyed. Override this method to implement
        custom validation.
        """
        return True

    def cancel(self, event=None):
        """Called when the Cancel button is pressed."""
        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    def apply(self):
        """
        Process the data.

        This is called after the dialog is destroyed. By
        default, this method does nothing.
        """
        pass

# Place a toplevel window at the center of parent or screen
# It is a Python implementation of ::tk::PlaceWindow.
def _place_window(w: Toplevel, parent: Optional[Tk]=None):
    w.wm_withdraw() # Remain invisible while we figure out the geometry
    w.update_idletasks() # Actualize geometry information

    logger = get_logger(__name__)

    minwidth = w.winfo_reqwidth()
    minheight = w.winfo_reqheight()
    maxwidth = w.winfo_vrootwidth()
    maxheight = w.winfo_vrootheight()

    logger.debug("Min size: (%d, %d)", minwidth, minheight)
    logger.debug("Max size: (%d, %d)", maxwidth, maxheight)

    if parent is not None and parent.winfo_ismapped():
        x = parent.winfo_rootx() + (parent.winfo_width() - minwidth) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - minheight) // 2

        vrootx = w.winfo_vrootx()
        vrooty = w.winfo_vrooty()

        logger.debug("Inital xy: (%d, %d). Xroot xy: (%d, %d)", x, y, vrootx, vrooty)

        x = min(x, vrootx + maxwidth - minwidth)
        x = max(x, vrootx)
        y = min(y, vrooty + maxheight - minheight)
        y = max(y, vrooty)

        logger.debug("Calculated xy: (%d, %d)", x, y)

        if w._windowingsystem == 'aqua':
            # Avoid the native menu bar which sits on top of everything.
            y = max(y, 22)
    else:
        x = (w.winfo_screenwidth() - minwidth) // 2
        y = (w.winfo_screenheight() - minheight) // 2

        logger.debug("Calculated xy: (%d, %d)", x, y)

    w.wm_maxsize(maxwidth, maxheight)
    # Become visible at the desired location
    w.wm_deiconify()
    w.wm_geometry(f"+{x}+{y}")

class ExMessagebox(ExDialog):
    """Message box."""

    def __init__(self, parent=None, *,
                 command=None,
                 default=None,
                 details="",
                 icon="info",
                 message="",
                 title=None,
                 type="ok"):
        # Type
        PATTERN = r"abortretryignore|ok(?:cancel)?|retrycancel|yesno(?:cancel)?"
        if not re.match(PATTERN, type):
            values = "abortretryignore, ok, okcancel, retrycancel, yesno, or yesnocancel"
            raise ValueError(f"Invalid type '{type}': must be {values}")
        self.type = type

        # Icon
        if icon is None:
            raise TypeError("Icon param is null")
        self.icon = icon

        self.message = message
        self.details = details

        # Command
        if command and not callable(command):
            raise ValueError(f"Invalid command {command!r}: must be a function or None")
        self.command = cast(Callable[[str], None] | None, command)

        self.result: str = "" #: The symbolic name of the clicked button

        # Default
        VALID_DEFAULTS = ["abort", "ignore", "retry", "yes", "no", "ok", "cancel"]
        if default and default not in VALID_DEFAULTS:
            raise ValueError(f"Invalid default {default!r}: can be one of {', '.join(sorted(VALID_DEFAULTS))}")

        self.default = default or self._get_sensible_default(self.type)

        super().__init__(parent, title=title or self.icon.capitalize(),
                         _parallel=(command is not None))

    @staticmethod
    def _get_sensible_default(string: str):
        PATTERN = r"(abort|ok|retry|yes).*"
        m = re.match(PATTERN, string)
        assert m is not None
        return m[1]

    def body(self, body: ttk.Frame):
        icon = ttk.Label(body, image=load_image(self.icon))

        msg = ttk.Label(body, text=self.message, anchor=NW, justify=LEFT)

        icon.grid(row=0, column=0, rowspan=(2 if self.details else 1))
        msg.grid(row=0, column=1)
        if self.details:
            dtls = ttk.Label(body, text=self.details, anchor=NW, justify=CENTER)
            dtls.grid(row=1, column=1)

    def buttonbox(self):
        box = ttk.Frame(self)

        BUTTON_PACK_OPTS = dict(side=LEFT, padx=5, pady=5)
        BUTTON_EXTRA_OPTS = dict(default=ACTIVE)

        button_specs: list[str] = []

        CANCEL = "Cancel"
        OK = "OK"
        YES = "Yes"
        NO = "No"

        match self.type:
            case "okcancel" | "ok" as n:
                button_specs.append(OK)
                if "cancel" in n:
                    button_specs.append(CANCEL)

            case "abortretryignore":
                button_specs = [
                    "Abort",
                    "Retry",
                    "Ignore"
                ]

            case "retrycancel":
                button_specs = ["retry", CANCEL]

            case "yesno" | "yesnocancel" as n:
                button_specs = [YES, NO]
                if "cancel" in n:
                    button_specs.append(CANCEL)

            case _:
                raise Exception("Unreachable code")

        def _set_result(value: str) -> None:
            self.result = value
            self.ok()

        buttons: dict[str, ttk.Button] = {}

        # Buttons
        for label, func in button_specs:
            symname = label.lower()
            opts = BUTTON_EXTRA_OPTS if self.default == symname else {}

            fn = functools.partial(_set_result, symname)
            btn = ttk.Button(box, text=label, command=fn, **opts)
            btn.pack(BUTTON_PACK_OPTS)

            buttons[symname] = btn

        box.pack()

    def apply(self):
        if self.command is not None:
            self.command(self.result)

def test():
    from tkinter import Tk
    root = Tk()

    def _show_dialog(_type, command=None, *, _debug=False):
        # Display dialog of type _TYPE. COMMAND specifies a callback
        # function for when the dialog is destroyed.
        if _debug:
            print(_type, command)

        dlg = ExMessagebox(type=_type, icon="info", command=command,
            message="You do something and an error shows up.",
            details="What do you do?")
        if command is None:
            print(f"{dlg.result = }")

    def _dialog_callback(v: str):
        print(f"Dialog callback with result {v}")

    # These frames will separate the buttons for creating different
    # kinds of dialogs.
    lfBlocking = ttk.Labelframe(root, text="Blocking Dialogs")
    lfBlocking.pack(pady=5)

    lfNonblocking = ttk.Labelframe(root, text="Non-Blocking Dialogs")
    lfNonblocking.pack(pady=5)

    for _type in ["abortretryignore", "ok", "okcancel", "retrycancel", "yesno", "yesnocancel"]:
        # Create buttons that display the different kinds of dialogs.
        # For each type of dialog, two buttons are created, one for
        # blocking dialogs and one or non-blocking.
        ttk.Button(lfBlocking, text=_type.capitalize(),
                   command=functools.partial(_show_dialog, _type)).pack()

        ttk.Button(lfNonblocking, text=_type.capitalize(),
                   command=functools.partial(_show_dialog, _type,
                       _dialog_callback)).pack()

    ttk.Button(root, text="Exit", command=root.quit).pack()

    root.mainloop()

if __name__ == "__main__":
    test()
