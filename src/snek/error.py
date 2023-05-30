# Utility functions and classes.

from __future__ import annotations
from typing import TYPE_CHECKING, Generic, TypeVar
from enum import IntEnum

if TYPE_CHECKING:
    from typing import Any

class ErrorEnum(IntEnum):
    """Error enum."""

T = TypeVar('T')
E = TypeVar('E', ErrorEnum, None, covariant=True)

class Result(Generic[T, E]):
    """A result with either an Ok value or an Err value."""

    def __init__(self, ok_value: T, err_value: E=None):
        self.__okval = ok_value
        self.__errval = err_value

    @property
    def ok(self) -> T:
        """The Ok value."""
        return self.__okval

    @property
    def err(self) -> E:
        """The Err value."""
        return self.__errval

###

class EnvError(RuntimeError):
    """Failed to obtain environment variable."""

class ConstantError(RuntimeError):
    """Value cannot be changed."""

class InvalidSignal(RuntimeError):
    """The observer does not support this particular signal."""
