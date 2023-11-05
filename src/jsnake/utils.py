"""Utility functions and classes."""

from __future__ import annotations
from typing import cast, Literal, Any
import os, re

_SizeUnit = Literal['b', 'kb', 'mb', 'gb']

# Classes
#

class Filesize:
    """
    A representation of a file size.

    You can initialize an object with a string
    denoting the size (see :py:meth:`from_string`) or
    with a numeric value (see :py:meth:`from_value`).

    .. code-block:: python
       :caption: Examples

       fs = Filesize.from_string("30 mb")
       str(fs) # "30 mb"
       fs.approximate # False

       fs = Filesize.from_string("~10 kb")
       str(fs) # "~10 kb"
       fs.approximate # True

       fs = Filesize.from_value(1024)
       str(fs) # "1 kb"
    """

    def __init__(self, size=0.0, raw_byte_size=0.0, unit: _SizeUnit='b',
                 approximate: bool = False):
        self.size = size #: Size value
        self.raw_byte_size = raw_byte_size #: Size in bytes
        self.unit = unit #: Size unit
        self.approximate = approximate #: True if size is approximate

    def __str__(self) -> str:
        size = self.size
        if self.unit == 'b':
            size = int(size)

        return "{}{} {}".format(
            "~" if self.approximate else "",
            str(size),
            self.unit
        )

    def __repr__(self) -> str:
        return f"Filesize(size={self.size!r}, {self.raw_byte_size!r}, {self.unit!r}, {self.approximate!r})"

    def __add__(self, other: Filesize, /):
        raw_size = other.raw_byte_size + self.raw_byte_size
        return self.from_value(raw_size)

    @classmethod
    def from_string(cls, string: str):
        """
        Parse a string expressing a file size.

        :param str string: A string consisting of a number
                           followed by a size unit. The number
                           cannot have any leading zeroes. The
                           number and unit can be separated by
                           whitespace, not it is not neccessary.
                           The unit can be ``b``, ``kb``, ``mb``,
                           or ``gb``. If the first character is
                           a ``~``, then the value is considered
                           approximate

        :return: An object representing the size denoted in `string`.
        :rtype: Filesize

        .. rubric:: Examples

        >>> Filesize.from_string('30 b')
        '30 b'
        >>> Filesize.from_string('30mb')
        '30.0 mb'
        >>> Filesize.from_string('~30 kb')
        '~30.0 kb'
        """
        # Regexp: Parse one or more numbers followed by optional
        # whitespace and a suffix composed of any one of the letters
        # m, M, g, G, k, or K, followed by a b or B.
        m = re.search(r'~?([1-9][0-9]*)\s*([mMgGkK]?[bB])', string)
        if m is None:
            raise ValueError(f"invalid string '{string}'")
        num, unit =  m.group(1, 2)

        # Search for a ~ at the beginning of the matched substring
        approximate = False
        if m.group(0)[0] == '~':
            # ~ is found, thus size is approximate
            approximate = True

        assert isinstance(unit, str)
        assert unit in ['b', 'kb', 'mb', 'gb']

        # Type checker conversion
        unit = cast(_SizeUnit, unit)

        # Mapping of multipliers
        multipliers = {
            'b': 1.0,
            'kb': 1024.0,
            'mb': 1048576.0,
            'gb': 1073741824.0
        }

        # Construct class
        obj = cls()

        obj.size = float(num)
        obj.unit = unit
        obj.raw_byte_size = float(num) * multipliers[unit]
        obj.approximate = approximate

        return obj

    @classmethod
    def from_value(cls, value: float, approximate: bool=False):
        """
        Return a ``Filesize`` representing a the specified size.

        :param float value: A number representing a file size in bytes.

        :param bool approximate: Whether the size is approximate.

        :return: The object representation of `value`.
        :rtype: Filesize

        >>> Filesize.from_string("10 mb")
        Filesize(size=10.0, 10485760.0, 'mb', False)
        >>> Filesize.from_string("~5 kb")
        Filesize(size=5.0, 5120.0, 'kb', True)
        """
        raw_size = value
        suffixes = ('b', 'kb', 'mb', 'gb')
        i = 0
        while value >= 1024.0:
            value /= 1024.0
            i += 1

        # Construct class
        obj = cls()

        obj.size = round(value, 2)
        obj.unit = suffixes[i]
        obj.raw_byte_size = raw_size
        obj.approximate = approximate

        return obj

class attr_dict(dict[str, Any]):
    """
    A dictionary that supports attribute notation.

    >>> d = attr_dict()
    >>> d['one'] = 1
    >>> d['one']
    1
    >>> d.one
    1
    """

    def __raise_if_not_string(self, key: str, /) -> None:
        if not isinstance(key, str):
            raise TypeError(f"invalid key '{key}', not a string")

    def __getattr__(self, key: str) -> Any:
        self.__raise_if_not_string(key)
        return self[key]

    def __setattr__(self, key: str, value) -> None:
        self.__raise_if_not_string(key)
        self[key] = value

class ConstantError(RuntimeError):
    """Value cannot be changed."""

class readonly_dict(dict[str, Any]):
    """
    A dictionary whose values cannot be changed.

    The only difference between this and a normal
    ``dict`` is that :py:exc:`ConstantError` is raised
    should the user attempt to set an item after initialization.
    """

    def __setitem__(self, key, value): # pyright: ignore
        raise ConstantError(f"cannot assign elements to {type(self).__name__}")

# Functions
#

def binary_search(array, pattern) -> int:
    """
    Do a binary search in an array.

    :param list array: an array of values. Its contents must
                       be of a type that supports ``>``
                       and ``==`` operators. Its contents
                       must also be sorted from lowest to highest

    :param pattern: the pattern to search for in `array`. It
                    should be the same type as `array`'s contents
                    or a type that can be compared with the elements
                    in `array`

    :return: the first index where `pattern` was found, or -1
             on failure
    :rtype: int
    """
    res = -1
    low, high = 0, len(array)-1

    if low > high: return -1

    while (high - low) > 1:
        mid = (high + low) // 2

        v = array[mid]
        if v == pattern:
            return mid
        elif v < pattern:
            low = mid + 1
        else:
            high = mid - 1

    if array[low] == pattern:
        res = low
    elif array[high] == pattern:
        res = high

    return res

def get_env(envname: str) -> str | None:
    """
    Get an environment variable, return None if it doesn't exist.

    :param str envname: a variable defined in the environment

    :return: the string value of `envname` if `envname` is set,
             or ``None`` otherwise
    :rtype: str or None
    """
    return os.getenv(envname)
