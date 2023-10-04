from __future__ import annotations
from ..signals import signal
from abc import ABC, abstractmethod
from typing import cast, Any
import pytest, sys

class Animal(ABC):
    def __init__(self):
        self.on_fed = signal("fed", self)
        self.test_signal = signal("test_signal")
        self.data: Any = None

    @abstractmethod
    def feed(self) -> None:
        return "Animal happy"

class Dog(Animal):
    def feed(self):
        self.on_fed.emit("dog")

class Cat(Animal):
    def feed(self):
        self.on_fed.emit("cat")

def _on_animal_fed(obj: object, _type: str, **kw):
    obj = cast(Animal, obj)
    obj.data = _type

def test_signals():
    # Dog
    Fido = Dog()
    assert Fido.on_fed.obj is Fido, "'Fido' bound object is not this module"

    Fido.on_fed.connect(_on_animal_fed)
    assert Fido.on_fed.count == 1

    Fido.feed()
    assert Fido.data == "dog"

    Fido.on_fed.disconnect(_on_animal_fed)
    assert Fido.on_fed.count == 0

    # Cat
    Missy = Cat()
    assert Missy.on_fed.obj is Missy, "'Missy' bound object is not this module"

    Missy.on_fed.connect(_on_animal_fed)
    assert Missy.on_fed.count == 1

    Missy.feed()
    assert Missy.data == "cat"

    Missy.on_fed.disconnect(_on_animal_fed)
    assert Missy.on_fed.count == 0

def test_strings():
    on_edit = signal("edit")
    assert str(on_edit) == "edit"
    assert on_edit.name == "edit"
    assert str(on_edit) == on_edit.name

def test_errors():
    thismod = sys.modules[__name__]

    some_signal = signal("test")
    assert some_signal.obj is thismod

    with pytest.raises(TypeError):
        some_signal.connect(4) # pyright: ignore
