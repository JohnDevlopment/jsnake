from __future__ import annotations
from ..utils import attr_dict, Filesize, binary_search, readonly_dict, get_env
from ..errors import ConstantError
import pytest

def test_attrdict():
    d = attr_dict()
    d['one'] = 1
    assert d.one == 1

def test_readonlydict():
    d = readonly_dict(one=1, two=2)
    with pytest.raises(ConstantError):
        d['three'] = 3

@pytest.mark.parametrize(
    "varname,expected",
    [
        ('JSNAKE_BOOL', "true"),
        ('JSNAKE_STRING', "string"),
        ('JSNAKE_INT', "1"),
        ('JSNAKE_FLOAT', "1.15"),
        ('JSNAKE_LIST', '[1, 2.05, "3"]')
    ]
)
def test_getenv(varname: str, expected: str):
    val = get_env(varname)
    assert val is not None, f"no value for env var '{varname}'"
    assert val == expected

class TestFilesizeClass:
    @pytest.mark.parametrize(
        "string,size,unit,raw_size,approximate",
        [
            ("30 b", 30.0, 'b', 30.0, False),
            ("30 kb", 30.0, 'kb', 30720.0, False),
            ("30 mb", 30.0, 'mb', 31457280.0, False),
            ("30 gb", 30.0, 'gb', 32212254720.0, False),

            ("~30 kb", 30.0, 'kb', 30720.0, True),
            ("~30 mb", 30.0, 'mb', 31457280.0, True),
            ("~30 gb", 30.0, 'gb', 32212254720.0, True)
        ]
    )
    def test_fromstring(self, string: str, size: float,
                        unit: str, raw_size: float, approximate: bool):
        fs = Filesize.from_string(string)
        assert fs.size == size
        assert fs.raw_byte_size == raw_size
        assert fs.approximate == approximate

    def test_errors(self):
        with pytest.raises(ValueError):
            Filesize.from_string("asdfsdaf")

    def test_addition(self):
        fs = Filesize.from_string("3 mb")
        fs2 = fs + fs

        assert str(fs) == "3.0 mb"
        assert str(fs2) == "6.0 mb"

    @pytest.mark.parametrize(
        "value,approximate,expected",
        [
            (30.0,          False, "30 b"),
            (30720.0,       False, "30.0 kb"),
            (31457280.0,    False, "30.0 mb"),
            (32212254720.0, False, "30.0 gb"),

            (30720.0,       True, "~30.0 kb"),
            (31457280.0,    True, "~30.0 mb"),
            (32212254720.0, True, "~30.0 gb")
        ]
    )
    def test_fromvalue(self, value: float, approximate: bool, expected):
        fs = Filesize.from_value(value, approximate)
        assert str(fs) == expected

class TestBinarySearch:
    def test_numbers(self):
        array = list(range(1, 5000))
        assert binary_search(array, 300) > 0
        assert binary_search(array, -2) < 0
