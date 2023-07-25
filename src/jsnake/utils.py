# Utility functions and classes.

from __future__ import annotations
from typing import TYPE_CHECKING, cast, Literal, Any
from .errors import ConstantError
from dataclasses import dataclass
import os, re, unittest

if TYPE_CHECKING:
    from typing import Any, NoReturn
    from typing_extensions import Self

@dataclass
class Filesize:
    """A representation of a file size."""

    size: float
    unit: Literal['b', 'kb', 'mb', 'gb']
    raw_byte_size: float
    approximate: bool

    def __str__(self) -> str:
        return "{}{}{}".format(
            "~" if self.approximate else "",
            str(self.size),
            " " + self.unit
        )

    def __post_init__(self):
        if isinstance(self.size, int):
            # Convert integer to float
            self.size = float(self.size)

        if isinstance(self.raw_byte_size, int):
            # Convert integer to float
            self.raw_byte_size = float(self.raw_byte_size)

    def __add__(self, other: Filesize, /) -> Self:
        raw_size = other.raw_byte_size + self.raw_byte_size
        return self.from_value(raw_size)

    @classmethod
    def from_string(cls, string: str) -> Self:
        """
        Parse a string expressing a file size.

        :param str string: A string consisting of a number
                           followed by a size unit. The format is
                           a valid integer with one or more digits,
                           followed by zero or more spaces, and a
                           unit consisting of b, k, m, and g.
                           K, m, and g can be captialized and followed
                           by an optional 'b' (e.g., kb, Mb, g, etc.).

        :return: An object representing the size denoting in `string`.
        :rtype: Filesize
        """
        # Regexp: Parse one or more numbers followed by optional
        # whitespace and a suffix composed of any one of the letters
        # m, M, g, G, k, or K, followed by an optional b.
        m = re.search(r'([1-9][0-9]*)\s*([mMgGkK]b?)', string)
        if m is None:
            raise ValueError("")
        num, unit =  m.group(1, 2)

        # Add a 'b' if it's missing
        if not (unit := unit.lower()).endswith('b'):
            unit += "b"

        assert isinstance(unit, str)
        assert unit in ['b', 'kb', 'mb', 'gb']

        # Type checker conversion
        unit = cast(Literal['b', 'kb', 'mb', 'gb'], unit)

        # Mapping of multipliers
        multipliers = {
            'b': 1.0,
            'kb': 1024.0,
            'mb': 1048576.0,
            'gb': 1073741824.0
        }

        # Construct class
        return cls(
            float(num),
            unit,
            float(num) * multipliers[unit],
            False
        )

    @classmethod
    def from_value(cls, value: float, approximate: bool=False) -> Self:
        """
        Return a ``Filesize`` representing a the specified size.

        :param float value: A number representing a file size in bytes.

        :param bool approximate: Whether the size is approximate.

        :return: The object representation of `value`.
        :rtype: Filesize
        """
        raw_size = value
        suffixes = ('b', 'kb', 'mb', 'gb')
        i = 0
        while value >= 1024.0:
            value /= 1024.0
            i += 1

        return cls(round(value, 2), suffixes[i], raw_size, approximate)

class attr_dict(dict[str, Any]):
    """A dictionary that supports attribute notation."""

    def __getattr__(self, key: str) -> Any:
        return self[key]

    def __setattr__(self, key: str, value) -> None:
        self[key] = value

class readonly_dict(dict[str, Any]):
    """A dictionary whose values cannot be changed."""

    def __setitem__(self, key, value) -> NoReturn: # pyright: ignore
        raise ConstantError(f"cannot assign elements to {type(self).__name__}")

def get_env(envname: str) -> str | None:
    """Get an environment variable, return None if it doesn't exist."""
    temp = os.getenv(envname)
    return temp

class TestClasses(unittest.TestCase):
    def test_attr_dict(self):
        d = attr_dict()

        d['one'] = 1
        self.assertEqual(d['one'], 1)
        self.assertEqual(d['one'], d.one)

        d.two = 2
        self.assertEqual(d.two, 2)
        self.assertEqual(d.two, d['two'])

    def test_readonly_dict(self):
        d = readonly_dict(one=1, two=2)
        with self.assertRaises(ConstantError):
            d['three'] = 3

    def test_Filesize(self):
        fs = Filesize(1, 'kb', 1024, False)
        self.assertEqual(str(fs), "1.0 kb")

        fs = Filesize.from_string("1 kb")
        self.assertEqual(str(fs), "1.0 kb")

        fs = Filesize.from_value(1073741824)
        self.assertEqual(str(fs), "1.0 gb")

if __name__ == "__main__":
    unittest.main()
