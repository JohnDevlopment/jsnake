from __future__ import annotations
from tkinter import ttk
from .utils import _WidgetMixin
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

    __slots__ = ()

    def __init__(self, master: _Widget=None, *, scrolly: bool=False, **kw: Any):
        """
        Construct an extended listbox widget with the parent `master`.

        :param master: The parent window. If ``None``, defaults to the root window

        :keyword bool scrolly: If true, a vertical scrollbar is added
        """
        # Frame this enter goes inside
        self.frame = ttk.Frame(master)

        # X scrollbar
        self.ybar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.xview)

        super().__init__(self.frame, **kw)

        self.set_custom_resources(scrolly=scrolly)

        self.pack(fill=tk.BOTH)

        self.override_geomtry_methods(tk.Listbox)

        # Signals
        self.on_item_selected = signal('item_selected', self)
        self.on_items_selected = signal('items_selected', self)
        self.on_values_set = signal('values_set', self)

        # Bindings
        def _listbox_selected(event: tk.Event): # pyright: ignore
            sel = self.curselection()
            if len(sel) == 1:
                self.on_item_selected.emit(sel[0])
                return

            self.on_items_selected.emit(sel)

        self.bind("<<ListboxSelect>>", _listbox_selected, True)

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

    ###

    # def configure(self, **kw: Any):
    #     super().configure(kw)

    # def cget(self, key: str) -> Any:
    #     if self.resource_defined(key):
    #         return self.get_custom_resource(key)

    #     return super().cget(key)

# class ExListbox(Listbox, _ExWidgetMixin):
#     """A Listbox but with extra features."""

#     __slots__ = ()

#     isttk = False

#     def __init__(self, master=None, cnf={}, **kw):
#         extraOpts, cnf, kw = self.parse_extra_options(cnf, kw, 'values')
#         Listbox.__init__(self, master, cnf, **kw)
#         values = extraOpts.get('values', [])
#         if len(values):
#             oldState = self.cget('state')
#             self.config(state=NORMAL)
#             self.insert(END, *values)
#             self.config(state=oldState)

#     def clear(self):
#         """Clears the listbox."""
#         self.delete(0, END)

#     def curselection(self):
#         """
#         Return the indices of currently selected item.

#         If the selection is clear, then None is returned.
#         Otherwise the value returned depends on the 'selectmode'
#         option: if set to 'browse', it is a single integer;
#         if not set to 'browse' it is a tuple containing one or more indices.
#         """
#         sel = super().curselection()
#         if len(sel) == 0: return None

#         if self.cget('selectmode') == 'browse':
#             return sel[0]

#         return sel

#     def search(self, pattern: str):
#         """
#         Searches the listbox for an item matching PATTERN.

#         Internally, one of two search algorithms is used: for
#         a list of 15 or less items, a linear array search is done;
#         but for lists with over 15 items, a binary search is done instead.
#         """
#         values: list = list(self.get(0, END))

#         if len(values) >= 15:
#             return binary_search(values, pattern)

#         res = -1
#         i = k_counter(0)
#         for val in values:
#             if val == pattern:
#                 res = i.value
#                 break
#             +i

#         return res

#     def select(self, first, see=True):
#         """
#         Selects the item at index FIRST.

#         This is effectively the same as selecting an item with
#         the mouse. As such, the <<ListboxSelect>> event is generated.
#         """
#         self.tk.call('::tk::ListboxBeginSelect', self._w, self.index(first), 1)
#         self.tk.call('::tk::CancelRepeat')
#         self.activate(first)
#         if see:
#             self.see(first)

#     def set_values(self, values: list, /):
#         """Replace the listbox items with those in VALUES."""
#         self.clear()
#         self.insert(END, *values)
#         self.update()

#     def sort(self, *, key=None, reverse=False):
#         """
#         Sorts the elements of the listbox.

#         Internally, list.sort() is used to sort the elements,
#         KEY and REVERSE being passed to it.
#         """
#         vals = list(self.get(0, END))
#         assert isinstance(vals, list), f"not list, is {type(vals)}"
#         if len(vals) > 1:
#             self.set_values(sorted(vals, key=key, reverse=reverse))

#     ## Properties

#     @property
#     def size(self) -> int:
#         """Number of items."""
#         l = self.get(0, END)
#         assert isinstance(l, (list,tuple)), type(l)
#         return len(l)

# # Compound widgets

# class ScrolledListbox(ExListbox):
#     """
#     A scrolled listbox megawidget.
#     """

#     __slots__ = ('frame', 'vbar')

#     def __init__(self, master, **kw):
#         """
#         Construct a scrolled listbox with a scroll direction.

#         *ARGS and **KW are forwarded to the underlying ExListbox.
#         """
#         self.frame = ttk.Frame(master)
#         self.vbar = ttk.Scrollbar(self.frame, orient='vertical')
#         self.vbar.pack(side=RIGHT, fill=Y)

#         kw.update({'yscrollcommand': self.vbar.set})
#         super().__init__(self.frame, **kw)
#         self.pack(side=LEFT, fill=BOTH, expand=True)
#         self.vbar.config(command=self.yview)

#         # HACK: Copy geometry methods of self.frame without overriding Listbox methods
#         lb_meths = vars(ExListbox).keys()
#         methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
#         methods = methods.difference(lb_meths)

#         for m in methods:
#             if m[0] != '_' and m != 'config' and m != 'configure':
#                 setattr(self, m, getattr(self.frame, m))

#     def __str__(self) -> str:
#         return str(self.frame)
