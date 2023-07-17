# Utility functions and classes.

from __future__ import annotations
from typing import TYPE_CHECKING, cast
from .errors import ConstantError
from dataclasses import dataclass
import os, re

if TYPE_CHECKING:
    from typing import Any, Literal

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

    def __add__(self, other: Filesize, /):
        raw_size = other.raw_byte_size + self.raw_byte_size
        return self.from_value(raw_size)

    @classmethod
    def from_string(cls, string: str):
        """Return a Filesize by converting STRING."""
        m = re.search(r'([1-9][0-9]*)\s*([mMgGkK]b?)', string)
        assert m is not None
        num, unit =  m.group(1, 2)

        if not (unit := unit.lower()).endswith('b'):
            # logging.info("Filesize missing suffix 'b', added.")
            unit += "b"

        assert isinstance(unit, str)
        assert unit in ['b', 'kb', 'mb', 'gb']

        unit = cast(Literal['b', 'kb', 'mb', 'gb'], unit)

        multipliers = {
            'b': 1.0,
            'kb': 1024.0,
            'mb': 1048576.0,
            'gb': 1073741824.0
        }

        return cls(
            float(num),
            unit,
            float(num) * multipliers[unit],
            False
        )

    @classmethod
    def from_value(cls, value: float, approximate: bool=False) -> Filesize:
        """Return a Filesize by converting VALUE bytes."""
        raw_size = value
        suffixes = ('b', 'kb', 'mb', 'gb')
        i = 0
        while value > 1024.0:
            value /= 1024.0
            i += 1

        return cls(round(value, 2), suffixes[i], raw_size, approximate)

class attr_dict(dict):
    """A dictionary that supports attribute notation."""

    def __getattr__(self, key: str) -> Any:
        return self[key]

    def __setattr__(self, key: str, value) -> None:
        self[key] = value

class readonly_dict(dict):
    """A dictionary whose values cannot be changed."""

    def __setitem__(self, key, value): # pyright: ignore
        raise ConstantError(f"cannot assign elements to {type(self).__name__}")

def get_env(envname: str) -> str | None:
    """Get an environment variable, return None if it doesn't exist."""
    temp = os.getenv(envname)
    return temp
