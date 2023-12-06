from __future__ import annotations
from tkinter import ttk
import tkinter as tk
from _tkinter import TkappType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Type
    from .types import _Widget, _StateSpec, _SupportsStateMethods

    _StringDict = dict[str, Any]

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
    """
    Class to define value holders for widgets.

    .. note:: This class should not be used directly.
       Instead, use one of its subclasses.
    """

    def __init__(self, master: _Widget=None, value: Any=None,
                 name: str | None=None, temp: bool=False):
        """
        Initialize the variable.

        :param master: the widget's master. If ``None``,
                       use the root
        :type master: widget or None

        :param Any value: the variable's initial value

        :param name: the name of the variable.  If omitted,
                     it defaults to ``PY_VARx``, where ``x`` is
                     some number. If it matches an already existing
                     variable, and `value` is omitted, then the existing
                     value is retained
        :type name: str or None

        :param bool temp: whether the variable is temporary
        """
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

class BooleanVar(Variable):
    """Value holder for boolean variables."""

    _default = False

    def __init__(self, master=None, value=None,
                 name=None, temp=False):
        """
        Construct a boolean variable.

        :param master: see :paramref:`Variable.master`

        :param value: see :paramref:`Variable.value`.
                      Defaults to ``False``

        :param name: see :paramref:`Variable.name`

        :param temp: see :paramref:`Variable.temp`
        """
        super().__init__(master, value, name, temp)

    def get(self):
        """Return value of variable as string."""
        tk: TkappType = self.tk
        return tk.getboolean(super().get())

    def set(self, value):
        """
        Set the variable to `value`.

        :param Any value: Any value that is understood
                          by Tcl as a boolean
        """
        tk: TkappType = self.tk
        return super().set(tk.getboolean(value))

    initialize = set

class StringVar(Variable):
    """
    Value holder for string variables.

    >>> v = StringVar(value="some string")
    >>> v.get()
    some string
    """

    def __init__(self, master: _Widget=None, value: Any=None,
                 name: str | None=None, temp: bool=False):
        """
        Construct a string variable.

        :param master: see :paramref:`Variable.master`

        :param value: see :paramref:`Variable.value`.
                      Defaults to ``""``
        :type value: str or None

        :param name: see :paramref:`Variable.name`

        :param temp: see :paramref:`Variable.temp`
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

class _StateMethods:
    # @overload
    # def state(self, state_spec: None=None) -> str:
    #     ...

    # @overload
    # def state(self, state_spec: _StateSpec) -> None:
    #     ...

    def state(self, state_spec=None):
        """
        Query or modify the widget state.

        :param state_spec: If provided, specifies a widget
                           state
        :type state_spec: tuple or None

        :return: ``None`` if `state_spec` is provided, otherwise
                 the current state
        """
        if state_spec is None:
            return self.cget('state') # pyright: ignore
        self.configure(state=state_spec) # pyright: ignore

    def instate(self, state_spec, callback=None, *args, **kw):
        """
        Test the widget's state.

        :param state_spec: The widget state
                           to test for
        :type state_spec: tuple[str, ...]

        :param function callback: If provided, specifies
                                  the function to call if
                                  the current state matches
                                  `state_spec`. `\*args` and
                                  `\*\*kw` are passed to the
                                  function

        :return: ``True`` or ``False`` depending on whether the widget
                 state matches `state_spec`
        """
        test = self.state() == state_spec
        if callback is None:
            return test

        if test:
            callback(*args, **kw)

class TkBusyCommand(tk.Widget):
    """
    A class representing "tk busy" command.

    Call :py:meth:`hold` to mark a window as busy, and :py:meth:`forget` to unmark it.

    This class can be instantiated in a ``with`` statement: the window's busy status
    will be handled automatically.
    """

    def __init__(self, master: tk.Widget, window: tk.Widget, /):
        """
        Construct a TkBusyCommand object.

        :param tk.Widget master: the master of this widget

        :param tk.Widget window: the window you intend to
                                 mark as busy
        """
        super().__init__(master, 'frame')
        self._root = master
        self._tk = self._root.tk
        self._widget = window

    def forget(self) -> None:
        """Release the busy-hold on the widget and its descendents."""
        if self.is_busy:
            self._tk.call('tk', 'busy', 'forget', self._widget)
            self._tk.call('update')

    def hold(self) -> None:
        """Make the window and its descendants appear busy."""
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

    Can be used with the ``with`` statement.

    .. code-block:: python

       with InState(entry, ('!disabled',)):
           # Edit the entry contents
           ...
    """

    def __init__(self, owner: _SupportsStateMethods, state_spec: _StateSpec):
        """
        Create an object to change the state of `owner`.

        :param owner: any object which contains a ``state`` method

        :param state_spec: a state spec, whose form depends on
                           whether `owner` is a Ttk themed widget
                           or not: if not, either 'normal' or
                           'disabled'; otherwise, a tuple of one
                           or more bit flags
        :type state_spec: str or tuple[str, ...]
        """
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
