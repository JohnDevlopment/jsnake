from __future__ import annotations
from tkinter import ttk
from . import _WidgetMixin
from ..signals import signal
from typing import TYPE_CHECKING
import tkinter as tk, sys

if TYPE_CHECKING:
    from typing import Any, Sequence, TypeVar, Callable
    from .utils import _Widget, SupportsRichComparisons, binary_search

    T = TypeVar("T")

    _KeyFunction = Callable[[T], SupportsRichComparisons]

class ExListbox(tk.Listbox, _WidgetMixin):
    """Extended entry widget."""

    def __init__(self, master: _Widget=None, *, scrolly: bool=False, **kw: Any):
        """
        Construct an extended listbox widget with the parent `master`.

        :param master: The parent window. If ``None``, defaults to the root window

        :keyword bool scrolly: If true, a vertical scrollbar is added

        :keyword **kw: Arguments forwarded to :py:class:`tkinter.Listbox`
        """
        # Signals
        #: | ``on_item_selected(item: str | float)``
        #: Emitted when a single item is selected.
        self.on_item_selected = signal('item_selected', self)

        #: | ``on_items_selected(items: Sequence[str | float])``
        #: Emitted when multiple items are selected.
        self.on_items_selected = signal('items_selected', self)

        #: | ``on_values_set(values: Sequence[str | float])``
        #: Emitted when values are set via :py:meth:`set_values`.
        self.on_values_set = signal('values_set', self)

        #: | ``on_values_set(enabled: bool)``
        #: Emitted when the state of the vertical scrollbar is changed.
        #: `enabled` indicates whether the scrollbar is visible and can be used.
        self.on_y_scrollbar_changed = signal('y_scrollbar_changed', self)
        self.on_y_scrollbar_changed.connect(self._on_y_scrollbar_changed)

        # Frame this enter goes inside
        self.frame = ttk.Frame(master)

        # Y scrollbar
        self.ybar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.yview)

        kw['yscrollcommand'] = self.ybar.set

        super().__init__(self.frame, **kw)

        self.set_custom_resources(scrolly=scrolly)

        self.pack(fill=tk.BOTH)

        # Emit signals
        self.on_item_selected.emit("")
        self.on_items_selected.emit(["", ""])
        self.on_values_set.emit([])
        self.on_y_scrollbar_changed.emit(scrolly)

        self.override_geomtry_methods(tk.Listbox)

        # Bindings
        def _listbox_selected(event: tk.Event): # pyright: ignore
            sel = self.curselection()
            if len(sel) == 0: return

            if len(sel) == 1:
                self.on_item_selected.emit(sel[0])
            else:
                self.on_items_selected.emit(sel)

        self.bind("<<ListboxSelect>>", _listbox_selected, True)

    def configure(self, scrolly: bool | None=None, **kw: Any):
        if scrolly is not None:
            self.set_custom_resource('scrolly', scrolly)
            self.on_y_scrollbar_changed.emit(scrolly)
        super().configure(kw)

    def cget(self, key: str) -> Any:
        if self.resource_defined(key):
            return self.get_custom_resource(key)
        return super().cget(key)

    @property
    def size(self) -> int:
        """Number of items."""
        l = self.get(0, tk.END)
        assert isinstance(l, (list, tuple))
        return len(l)

    # Methods that manipulate/query entries
    #

    def clear(self) -> None:
        """Clear the listbox of all entries."""
        self.delete(0, tk.END)

    def curselection(self) -> Sequence[int]:
        """
        Return the current selection.

        :return: a list of indices corresponding to
                 selected entries
        """
        sel = super().curselection()
        if not sel:
            return ()

        return sel

    def search(self, pattern: str, /) -> int:
        """
        Search the listbox for an item matching a pattern.

        :param str pattern: the used to match against the
                            listbox items

        :return: the index of the first match on success,
                 or -1 on failure
        :rtype: int
        """
        values = list(self.get(0, tk.END))

        if len(values) >= 15:
            return binary_search(values, pattern)

        res = -1
        i = 0

        for val in values:
            if val == pattern:
                res = i
                break

            i += 1

        return res

    def select(self, first: str | int, see: bool=True) -> None:
        """
        Select an item.

        :param first: the index of the item to select. Can be any item
                      supported by :py:meth:`index`

        :param see: if true, the selected entry will be made visible
        """
        self.tk.call("::tk::ListboxBeginSelect", self._w, self.index(first), 1) # pyright: ignore
        self.tk.call("::tk::CancelRepeat")
        self.activate(first)

        if see:
            self.see(first)

    def set_values(self, values: Sequence[str | float], /) -> None:
        """
        Replace the items in the listbox.

        :param values: the new list of values
        """
        self.clear()
        self.insert(tk.END, *values)
        self.update()
        self.on_values_set.emit(values)

    def sort(self, *, key: _KeyFunction | None=None, reverse=False) -> None:
        """
        Sort the elements in the listbox.

        :keyword key: a function called on each element
                      prior to being sorted. It must return
                      a value that can be compared
        :type key: function or None

        :keyword bool reverse: if true, sort in reverse order
        """
        values = list(self.get(0, tk.END))
        assert isinstance(values, list)

        if len(values) > 1:
            self.set_values(sorted(values, key=key, reverse=reverse))

    # Signal handlers
    #

    def _on_y_scrollbar_changed(self, obj: object, enabled: bool, **kw) -> None:
        if enabled:
            if not self.ybar.winfo_ismapped():
                # Map the scrollbar if it isn't already
                self.ybar.pack(side=tk.RIGHT, fill=tk.Y, before=self)

            return

        if self.ybar.winfo_ismapped():
            # Disabled; the scrollbar is visible, so unmap it
            self.ybar.pack_forget()
