from __future__ import annotations
from tkinter import ttk
import tkinter as tk
from typing import Any, Literal, cast, Protocol, Type
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    _StringDict = dict[str, Any]

# Type checker helpers
#

_Column = tuple[str, str, int] # pyright: ignore
_Widget = tk.Widget | None
_StateSpec = Literal['normal', 'disabled'] | tuple[str, ...]

class _SupportsStateMethods(Protocol):
    def state(self, *args) -> Any: ...

###

# Classes
#

class _ResourceManager:
    __slots__ = ('resources',)

    def __init__(self, **kw: Any):
        self.resources: _StringDict = {k: v for k, v in kw.items()}

    def __getitem__(self, key: str, /) -> Any:
        return self.resources[key]

    def __setitem__(self, key: str, value: Any, /) -> None:
        self.resources[key] = value

    def __contains__(self, key: str) -> bool:
        return self.resources.__contains__(key)

class Variable(tk.Variable):
    """Class to define value holders for widgets."""

    def __init__(self, master: _Widget=None, value: Any=None,
                 name: str | None=None, temp: bool=False):
        super().__init__(master, value, name)
        self.temp = temp

    def __del__(self):
        """Overridden to do nothing unless self.temp is True."""
        if self.temp:
            super().__del__() # pyright: ignore

    @property
    def tk(self):
        master: tk.Widget = self._root # pyright: ignore
        return master.tk

class StringVar(Variable):
    """Value holder for string variables."""

    def __init__(self, master: _Widget=None, value: Any=None,
                 name: str | None=None, temp: bool=False):
        """
        Construct a string variable.

        MASTER is the master widget.
        VALUE is an optional value that defaults to "".
        NAME is an optional Tcl name which defaults to PY_VARnum.

        If NAME matches an existing variable and VALUE is omitted,
        then the existing value is retained.
        """
        super().__init__(master, value, name, temp)

    def get(self) -> str:
        """Return value of variable as string."""
        value: Any = self.tk.globalgetvar(self._name) # pyright: ignore
        if isinstance(value, str):
            return value
        return str(value)

class _WidgetMixin: # pyright: ignore
    # @classmethod
    # def override_init_docstring(cls, parent: Type[tk.Widget]) -> None:
    #     import re
    #     parent_doc = cast(str, parent.__init__.__doc__)
    #     new_doc = parent_doc + cast(str, cls.__init__.__doc__)
    #     m = re.search(r'a[ ]*(.*?widget)', r'an extended \1')
    #     if m is not None:
    #         pass
    #     # new_doc = re.sub(r'a[ ]*(.*?widget)', r'an extended \1', new_doc)
    #     cls.__init__.__doc__ = new_doc

    def override_geomtry_methods(self, cls: Type[tk.Widget]) -> None:
        """
        Overrides self's geometry methods to point to its parent's.

        The parent of this widget shall be the frame (self.frame).
        """
        frame: ttk.Frame = getattr(self, 'frame')

        # HACK: Copy geometry methods of self.frame without overriding other methods
        widget_methods = vars(cls).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(widget_methods)

        for m in methods:
            if m [0] != "_" and m not in ("config", "configure"):
                setattr(self, m, getattr(frame, m))

    def __str__(self) -> str:
        return self.frame.__str__() # pyright: ignore

    # Resource functions
    #

    def set_custom_resources(self, **kw: Any) -> None:
        """Set custom resources in the resource manager."""
        self.__options = _ResourceManager(**kw)

    def set_custom_resource(self, name: str, value: Any) -> None:
        """Set the resource NAME to VALUE."""
        self.__options[name] = value

    def get_custom_resource(self, name: str) -> Any:
        """Get the resource associated with NAME."""
        return self.__options[name]

    def resource_defined(self, name: str) -> bool:
        """Return true if NAME is defined in self._options"""
        return name in self.__options

    # Metadata functions
    #

    def __check_metatable_exists(self):
        try:
            temp = self.__metadata # pyright: ignore
        except:
            self.__metadata: _StringDict = {}

    def set_meta(self, key: str, value: Any) -> None:
        """Set the meta field KEY to VALUE."""
        # if not hasattr(self, '__metadata'):
        #     self.__metadata: _StringDict = {}

        self.__check_metatable_exists()

        if not isinstance(key, str):
            raise TypeError("key must be a string")

        self.__metadata[key] = value

    def get_meta(self, key: str, default: Any=None) -> Any:
        """Get the meta field KEY, or DEFAULT if it does not exist."""
        # if not hasattr(self, '__metadata'):
        #     self.__metadata: _StringDict = {}

        self.__check_metatable_exists()

        if not isinstance(key, str):
            raise TypeError("key must be a string")

        return self.__metadata.get(key, default)

class TkBusyCommand(tk.Widget):
    """A class representing "tk busy" command.

    Use the hold() and forget() methods to mark a window as busy.

    This class can be instantiated in a 'with' statement: the window is automatically held
    and released as one exits the context.
    """
    def __init__(self, master: tk.Widget, window, /):
        """
        Construct a TkBusyCommand object.

        MASTER is the Tk master of this class.
        WINDOW is the Widget that you intend to mark as busy.
        """
        super().__init__(master, 'frame')
        self._root = master
        self._tk = self._root.tk
        self._widget = window

    def forget(self):
        """Releases the busy-hold on the widget and its descendents."""
        if self.is_busy:
            self._tk.call('tk', 'busy', 'forget', self._widget)
            self._tk.call('update')

    def hold(self):
        """Makes the window appear busy."""
        if not self.is_busy:
            self._tk.call('tk', 'busy', 'hold', self._widget)
            self._tk.call('update')

    @property
    def is_busy(self) -> bool:
        """True if the window is busy."""
        return tk.getboolean(self._tk.call('tk', 'busy', 'status', self._widget))

    def __enter__(self):
        self.hold()
        return self

    def __exit__(self, *args): # pyright: ignore
        self.forget()

class InState:
    """
    Used for temporary state changes of widgets.

    Can be used with a context manager.
    """

    def __init__(self, owner: _SupportsStateMethods, state_spec: _StateSpec):
        self.owner = owner
        self.state_spec = state_spec
        self.old_state: _StateSpec = ()

        if state_spec in ['normal', 'disabled']:
            self.old_state = 'normal' if state_spec == 'disabled' else 'disabled'
        else:
            flags = []
            for st in state_spec:
                flags.append(
                    f"!{st}" if not st.startswith("!") else st[1:]
                )

            self.old_state = tuple(flags)

    def __enter__(self):
        self.owner.state(self.state_spec)

    def __exit__(self, exc_type, exc_value, traceback): # pyright: ignore
        self.owner.state(self.old_state)
