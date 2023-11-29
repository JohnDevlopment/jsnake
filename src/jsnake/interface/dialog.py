"""This module handles dialog boxes."""

from __future__ import annotations
from tkinter import (
    LEFT,
    ACTIVE,
    Tk,
    Misc,
    ttk,
    Toplevel,
    _get_temp_root, # pyright: ignore
    _destroy_temp_root # pyright: ignore
)
from tkinter.simpledialog import _setup_dialog, _place_window # pyright: ignore
from typing import cast

class ExDialog(Toplevel):
    """A base class for all dialogs."""

    def __init__(self, parent=None, title=None, parallel=False):
        master = parent or _get_temp_root()
        self.master = master

        Toplevel.__init__(self, master)

        self.withdraw() # remain invisible while we figure out the geometry

        parent = cast(Tk | None, parent)
        if parent is not None and parent.winfo_viewable():
            self.wm_transient(parent)

        if title:
            self.title(title)

        _setup_dialog(self)

        self.parent = parent
        self.result = None

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
        if not parallel:
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
