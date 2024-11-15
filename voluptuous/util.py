import typing
from voluptuous.error import LiteralInvalid, TypeInvalid
from voluptuous.schema_builder import default_factory

__author__ = "tusharmakkar08"


def Lower(v: str) -> str:
    """Transform a string to lower case.

    >>> s = Schema(Lower)
    >>> s('HI')
    'hi'
    """
    return v.lower()


def Upper(v: str) -> str:
    """Transform a string to upper case.

    >>> s = Schema(Upper)
    >>> s('hi')
    'HI'
    """
    return v.upper()


def Capitalize(v: str) -> str:
    """Capitalise a string.

    >>> s = Schema(Capitalize)
    >>> s('hello world')
    'Hello world'
    """
    return v.capitalize()


def Title(v: str) -> str:
    """Title case a string.

    >>> s = Schema(Title)
    >>> s('hello world')
    'Hello World'
    """
    return v.title()


def Strip(v: str) -> str:
    """Strip whitespace from a string.

    >>> s = Schema(Strip)
    >>> s('  hello world  ')
    'hello world'
    """
    return v.strip()


class DefaultTo(object):
    """Sets a value to default_value if none provided.

    >>> s = Schema(DefaultTo(42))
    >>> s(None)
    42
    >>> s = Schema(DefaultTo(list))
    >>> s(None)
    []
    """

    def __init__(
        self, default_value: typing.Any, msg: typing.Optional[str] = None
    ) -> None:
        self.default_value = default_factory(default_value)
        self.msg = msg

    def __call__(self, v: typing.Any) -> typing.Any:
        """Return the default value if v is None, otherwise return v."""
        if v is None:
            v = self.default_value()
        return v

    def __repr__(self) -> str:
        return f"DefaultTo({self.default_value()})"


class SetTo(object):
    """Set a value, ignoring any previous value.

    >>> s = Schema(validators.Any(int, SetTo(42)))
    >>> s(2)
    2
    >>> s("foo")
    42
    """

    def __init__(self, value: typing.Any) -> None:
        self.value = default_factory(value)

    def __call__(self, v: typing.Any) -> typing.Any:
        """Return the set value, ignoring the input."""
        return self.value()

    def __repr__(self) -> str:
        return f"SetTo({self.value()})"


class Set(object):
    """Convert a list into a set.

    >>> s = Schema(Set())
    >>> s([]) == set([])
    True
    >>> s([1, 2]) == set([1, 2])
    True
    >>> with raises(Invalid, regex="^cannot be presented as set: "):
    ...   s([set([1, 2]), set([3, 4])])
    """

    def __init__(self, msg: typing.Optional[str] = None) -> None:
        self.msg = msg

    def __call__(self, v: typing.Any) -> set:
        """Convert the input to a set."""
        try:
            set_v = set(v)
        except Exception as e:
            raise TypeInvalid(self.msg or f"cannot be presented as set: {e}")
        return set_v

    def __repr__(self) -> str:
        return "Set()"


class Literal(object):
    def __init__(self, lit: typing.Any) -> None:
        self.lit = lit

    def __call__(
        self, value: typing.Any, msg: typing.Optional[str] = None
    ) -> typing.Any:
        """Check if the value matches the literal."""
        if self.lit != value:
            raise LiteralInvalid(msg or f"{value} not match for {self.lit}")
        return self.lit

    def __str__(self) -> str:
        return str(self.lit)

    def __repr__(self) -> str:
        return repr(self.lit)
