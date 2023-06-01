# Utility functions and classes.

from __future__ import annotations
from typing import TYPE_CHECKING
from .errors import ConstantError
import os

if TYPE_CHECKING:
    from typing import Any

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
