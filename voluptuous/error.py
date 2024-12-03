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

Invalid = InvalidError  # Alias for backward compatibility

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


class MultipleInvalidError(InvalidError):
    def __init__(
        self, errors: typing.Optional[typing.List[InvalidError]] = None
    ) -> None:
        super().__init__("Multiple errors")
        self.errors = errors[:] if errors else []

    def __repr__(self) -> str:
        return "MultipleInvalidError(%r)" % self.errors

    def __str__(self) -> str:
        return str(self.errors[0]) if self.errors else "No errors"


class RequiredFieldInvalidError(InvalidError):
    """Required field was missing."""


class ObjectInvalidError(InvalidError):
    """The value we found was not an object."""


class DictInvalidError(InvalidError):
    """The value found was not a dict."""


class ExclusiveInvalidError(InvalidError):
    """More than one value found in exclusion group."""


class InclusiveInvalidError(InvalidError):
    """Not all values found in inclusion group."""


class SequenceTypeInvalidError(InvalidError):
    """The type found is not a sequence type."""


class TypeInvalidError(InvalidError):
    """The value was not of required type."""


class ValueInvalidError(InvalidError):
    """The value was found invalid by evaluation function."""


class ContainsInvalidError(InvalidError):
    """List does not contain item"""


class ScalarInvalidError(InvalidError):
    """Scalars did not match."""


class CoerceInvalidError(InvalidError):
    """Impossible to coerce value to type."""


class AnyInvalidError(InvalidError):
    """The value did not pass any validator."""


class AllInvalidError(InvalidError):
    """The value did not pass all validators."""


class MatchInvalidError(InvalidError):
    """The value does not match the given regular expression."""


class RangeInvalidError(InvalidError):
    """The value is not in given range."""


class TrueInvalidError(InvalidError):
    """The value is not True."""


class FalseInvalidError(InvalidError):
    """The value is not False."""


class BooleanInvalidError(InvalidError):
    """The value is not a boolean."""


class UrlInvalidError(InvalidError):
    """The value is not a URL."""


class EmailInvalidError(InvalidError):
    """The value is not an email address."""


class FileInvalidError(InvalidError):
    """The value is not a file."""


class DirInvalidError(InvalidError):
    """The value is not a directory."""


class PathInvalidError(InvalidError):
    """The value is not a path."""


class LiteralInvalidError(InvalidError):
    """The literal values do not match."""


class LengthInvalidError(InvalidError):
    """The value has an invalid length."""


class DatetimeInvalidError(InvalidError):
    """The value is not a formatted datetime string."""


class DateInvalidError(InvalidError):
    """The value is not a formatted date string."""


class InInvalidError(InvalidError):
    pass


class NotInInvalidError(InvalidError):
    pass


class ExactSequenceInvalidError(InvalidError):
    pass


class NotEnoughValidError(InvalidError):
    """The value did not pass enough validations."""


class TooManyValidError(InvalidError):
    """The value passed more than expected validations."""
