import typing


class Error(Exception):
    """Base validation exception."""


class SchemaError(Error):
    """An error was encountered in the schema."""


class InvalidError(Error):
    """The data was invalid.

    :attr msg: The error message.
    :attr path: The path to the error, as a list of keys in the source data.
    :attr error_message: The actual error message that was raised, as a
        string.

    """

    def __init__(
        self,
        message: str,
        path: typing.Optional[typing.List[typing.Hashable]] = None,
        error_message: typing.Optional[str] = None,
        error_type: typing.Optional[str] = None,
    ) -> None:
        Error.__init__(self, message)
        self._path = path or []
        self._error_message = error_message or message
        self.error_type = error_type

    @property
    def path(self) -> typing.List[typing.Hashable]:
        """Return the path to the error."""
        return self._path

    def __str__(self) -> str:
        path = " @ data[%s]" % "][".join(map(repr, self.path)) if self.path else ""
        output = Exception.__str__(self)
        if self.error_type:
            output += " for " + self.error_type
        return output + path


class MultipleInvalid(InvalidError):
    def __init__(
        self, errors: typing.Optional[typing.List[InvalidError]] = None
    ) -> None:
        super().__init__("Multiple errors")
        self.errors = errors[:] if errors else []

    def __repr__(self) -> str:
        return "MultipleInvalid(%r)" % self.errors

    def __str__(self) -> str:
        return str(self.errors[0]) if self.errors else "No errors"


class RequiredFieldInvalid(InvalidError):
    """Required field was missing."""


class ObjectInvalid(InvalidError):
    """The value we found was not an object."""


class DictInvalid(InvalidError):
    """The value found was not a dict."""


class ExclusiveInvalid(InvalidError):
    """More than one value found in exclusion group."""


class InclusiveInvalid(InvalidError):
    """Not all values found in inclusion group."""


class SequenceTypeInvalid(InvalidError):
    """The type found is not a sequence type."""


class TypeInvalid(InvalidError):
    """The value was not of required type."""


class ValueInvalid(InvalidError):
    """The value was found invalid by evaluation function."""


class ContainsInvalid(InvalidError):
    """List does not contain item"""


class ScalarInvalid(InvalidError):
    """Scalars did not match."""


class CoerceInvalid(InvalidError):
    """Impossible to coerce value to type."""


class AnyInvalid(InvalidError):
    """The value did not pass any validator."""


class AllInvalid(InvalidError):
    """The value did not pass all validators."""


class MatchInvalid(InvalidError):
    """The value does not match the given regular expression."""


class RangeInvalid(InvalidError):
    """The value is not in given range."""


class TrueInvalid(InvalidError):
    """The value is not True."""


class FalseInvalid(InvalidError):
    """The value is not False."""


class BooleanInvalid(InvalidError):
    """The value is not a boolean."""


class UrlInvalid(InvalidError):
    """The value is not a URL."""


class EmailInvalid(InvalidError):
    """The value is not an email address."""


class FileInvalid(InvalidError):
    """The value is not a file."""


class DirInvalid(InvalidError):
    """The value is not a directory."""


class PathInvalid(InvalidError):
    """The value is not a path."""


class LiteralInvalid(InvalidError):
    """The literal values do not match."""


class LengthInvalid(InvalidError):
    """The value has an invalid length."""


class DatetimeInvalid(InvalidError):
    """The value is not a formatted datetime string."""


class DateInvalid(InvalidError):
    """The value is not a formatted date string."""


class InInvalid(InvalidError):
    pass


class NotInInvalid(InvalidError):
    pass


class ExactSequenceInvalid(InvalidError):
    pass


class NotEnoughValid(InvalidError):
    """The value did not pass enough validations."""


class TooManyValid(InvalidError):
    """The value passed more than expected validations."""
