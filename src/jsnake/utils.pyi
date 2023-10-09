from typing import Literal, Any
from .errors import ConstantError
from dataclasses import dataclass
from typing import Any, NoReturn
from typing_extensions import Self
import os, re, unittest

class Filesize:
    size: float
    unit: Literal['b', 'kb', 'mb', 'gb']
    raw_byte_size: float
    approximate: bool

    def __add__(self, other: Filesize, /) -> Self:
        ...

    @classmethod
    def from_string(cls, string: str) -> Self:
        ...

    @classmethod
    def from_value(cls, value: float, approximate: bool=False) -> Self:
        ...

class attr_dict(dict[str, Any]):
    def __getattr__(self, key: str) -> Any:
        ...

    def __setattr__(self, key: str, value) -> None:
        ...

def binary_search(array: Any, pattern: Any) -> int:
    ...

class readonly_dict(dict[str, Any]):
    def __setitem__(self, key, value) -> NoReturn: # pyright: ignore
        ...

def get_env(envname: str) -> str | None:
    ...
