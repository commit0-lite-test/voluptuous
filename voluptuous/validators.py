from __future__ import annotations
import datetime
import re
import sys
import typing
from decimal import Decimal, InvalidOperation
from functools import wraps
from voluptuous.error import (
    BooleanInvalid,
    CoerceInvalid,
    ContainsInvalid,
    DateInvalid,
    DatetimeInvalid,
    DirInvalid,
    EmailInvalid,
    ExactSequenceInvalid,
    FalseInvalid,
    FileInvalid,
    InInvalid,
    Invalid,
    LengthInvalid,
    MatchInvalid,
    MultipleInvalid,
    NotInInvalid,
    PathInvalid,
    RangeInvalid,
    TrueInvalid,
    TypeInvalid,
    UrlInvalid,
)
from voluptuous.schema_builder import Schema, Schemable, message

if typing.TYPE_CHECKING:
    pass
Enum: typing.Union[type, None]
try:
    from enum import Enum
except ImportError:
    Enum = None
if sys.version_info >= (3,):
    import urllib.parse as urlparse

    basestring = str
else:
    import urlparse
USER_REGEX = re.compile(
    "(?:(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$|^\"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\[\\001-\\011\\013\\014\\016-\\177])*\"$))\\Z",
    re.IGNORECASE,
)
DOMAIN_REGEX = re.compile(
    "(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+(?:[A-Z]{2,6}\\.?|[A-Z0-9-]{2,}\\.?$)|^\\[(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)(\\.(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)){3}\\]$)\\Z",
    re.IGNORECASE,
)
__author__ = "tusharmakkar08"


def truth(f: typing.Callable) -> typing.Callable:
    """Convenience decorator to convert truth functions into validators.

    >>> @truth
    ... def isdir(v):
    ...   return os.path.isdir(v)
    >>> validate = Schema(isdir)
    >>> validate('/')
    '/'
    >>> with raises(MultipleInvalid, 'not a valid value'):
    ...   validate('/notavaliddir')
    """

    @wraps(f)
    def wrapper(v: typing.Any) -> typing.Any:
        t = f(v)
        if not t:
            raise ValueError
        return v

    return wrapper


class Coerce(object):
    """Coerce a value to a type.

    If the type constructor throws a ValueError or TypeError, the value
    will be marked as Invalid.

    Default behavior:

        >>> validate = Schema(Coerce(int))
        >>> with raises(MultipleInvalid, 'expected int'):
        ...   validate(None)
        >>> with raises(MultipleInvalid, 'expected int'):
        ...   validate('foo')

    With custom message:

        >>> validate = Schema(Coerce(int, "moo"))
        >>> with raises(MultipleInvalid, 'moo'):
        ...   validate('foo')
    """

    def __init__(
        self,
        type: typing.Union[type, typing.Callable],
        msg: typing.Optional[str] = None,
    ) -> None:
        self.type = type
        self.msg = msg
        self.type_name = type.__name__

    def __call__(self, v: typing.Any) -> typing.Any:
        """Validate that the value is equal to the target."""
        """Validate that the value is in the specified container."""
        """Clamp the value to the specified range."""
        """Validate that the value is within the specified range."""
        """Validate that the value is equal to the target."""
        """Validate that the value is in the specified container."""
        """Clamp the value to the specified range."""
        """Validate that the value is within the specified range."""
        """Coerce the value to the specified type."""
        try:
            return self.type(v)
        except (ValueError, TypeError, InvalidOperation):
            msg = self.msg or f"expected {self.type_name}"
            if (
                not self.msg
                and Enum is not None
                and isinstance(self.type, type)
                and issubclass(self.type, Enum)
            ):
                msg += f" or one of {', '.join(str(e.value) for e in self.type)}"
            raise CoerceInvalid(msg)

    def __repr__(self):
        return f"Coerce({self.type_name}, msg={self.msg!r})"


@message("value was not true", cls=TrueInvalid)
@truth
def IsTrue(v: typing.Any) -> bool:
    """Assert that a value is true, in the Python sense.

    >>> validate = Schema(IsTrue())

    "In the Python sense" means that implicitly false values, such as empty
    lists, dictionaries, etc. are treated as "false":

    >>> with raises(MultipleInvalid, "value was not true"):
    ...   validate([])
    >>> validate([1])
    [1]
    >>> with raises(MultipleInvalid, "value was not true"):
    ...   validate(False)

    ...and so on.

    >>> try:
    ...  validate([])
    ... except MultipleInvalid as e:
    ...   assert isinstance(e.errors[0], TrueInvalid)
    """
    return bool(v)


@message("value was not false", cls=FalseInvalid)
def IsFalse(v: typing.Any) -> typing.Any:
    """Assert that a value is false, in the Python sense.

    (see :func:`IsTrue` for more detail)

    >>> validate = Schema(IsFalse())
    >>> validate([])
    []
    >>> with raises(MultipleInvalid, "value was not false"):
    ...   validate(True)

    >>> try:
    ...  validate(True)
    ... except MultipleInvalid as e:
    ...   assert isinstance(e.errors[0], FalseInvalid)
    """
    if bool(v):
        raise ValueError
    return v


@message("expected boolean", cls=BooleanInvalid)
def Boolean(v: typing.Any) -> bool:
    """Convert human-readable boolean values to a bool.

    Accepted values are 1, true, yes, on, enable, and their negatives.
    Non-string values are cast to bool.

    >>> validate = Schema(Boolean())
    >>> validate(True)
    True
    >>> validate("1")
    True
    >>> validate("0")
    False
    >>> with raises(MultipleInvalid, "expected boolean"):
    ...   validate('moo')
    >>> try:
    ...  validate('moo')
    ... except MultipleInvalid as e:
    ...   assert isinstance(e.errors[0], BooleanInvalid)
    """
    if isinstance(v, str):
        v = v.lower()
        if v in ("1", "true", "yes", "on", "enable"):
            return True
        if v in ("0", "false", "no", "off", "disable"):
            return False
        raise ValueError
    return bool(v)


class _WithSubValidators(object):
    """Base class for validators that use sub-validators.

    Special class to use as a parent class for validators using sub-validators.
    This class provides the `__voluptuous_compile__` method so the
    sub-validators are compiled by the parent `Schema`.
    """

    def __init__(
        self,
        *validators: Schemable,
        msg: typing.Optional[str] = None,
        required: bool = False,
        discriminant: typing.Optional[typing.Callable] = None,
        **kwargs: typing.Any,
    ) -> None:
        self.validators = validators
        self.msg = msg
        self.required = required
        self.discriminant = discriminant

    def __voluptuous_compile__(self, schema: Schema) -> typing.Callable:
        self._compiled: typing.List[typing.Callable] = []
        old_required = schema.required
        self.schema = schema
        for v in self.validators:
            schema.required = self.required
            self._compiled.append(schema._compile(v))
        schema.required = old_required
        return self._run

    def __call__(self, v: typing.Any) -> typing.Any:
        return self._exec((Schema(val) for val in self.validators), v)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(repr(v) for v in self.validators)}, msg={self.msg!r})"

    def _run(self, v: typing.Any) -> typing.Any:
        raise NotImplementedError

    def _exec(self, schemas: typing.Iterable[Schema], v: typing.Any) -> typing.Any:
        raise NotImplementedError


class Any(_WithSubValidators):
    """Use the first validated value.

    :param msg: Message to deliver to user if validation fails.
    :param kwargs: All other keyword arguments are passed to the sub-schema constructors.
    :returns: Return value of the first validator that passes.

    >>> validate = Schema(Any('true', 'false',
    ...                       All(Any(int, bool), Coerce(bool))))
    >>> validate('true')
    'true'
    >>> validate(1)
    True
    >>> with raises(MultipleInvalid, "not a valid value"):
    ...   validate('moo')

    msg argument is used

    >>> validate = Schema(Any(1, 2, 3, msg="Expected 1 2 or 3"))
    >>> validate(1)
    1
    >>> with raises(MultipleInvalid, "Expected 1 2 or 3"):
    ...   validate(4)
    """


Or = Any


class Union(_WithSubValidators):
    """Use the first validated value among those selected by discriminant.

    :param msg: Message to deliver to user if validation fails.
    :param discriminant(value, validators): Returns the filtered list of validators based on the value.
    :param kwargs: All other keyword arguments are passed to the sub-schema constructors.
    :returns: Return value of the first validator that passes.

    >>> validate = Schema(Union({'type':'a', 'a_val':'1'},{'type':'b', 'b_val':'2'},
    ...                         discriminant=lambda val, alt: filter(
    ...                         lambda v : v['type'] == val['type'] , alt)))
    >>> validate({'type':'a', 'a_val':'1'}) == {'type':'a', 'a_val':'1'}
    True
    >>> with raises(MultipleInvalid, "not a valid value for dictionary value @ data['b_val']"):
    ...   validate({'type':'b', 'b_val':'5'})

    ```discriminant({'type':'b', 'a_val':'5'}, [{'type':'a', 'a_val':'1'},{'type':'b', 'b_val':'2'}])``` is invoked

    Without the discriminant, the exception would be "extra keys not allowed @ data['b_val']"
    """


Switch = Union


class All(_WithSubValidators):
    """Value must pass all validators.

    The output of each validator is passed as input to the next.

    :param msg: Message to deliver to user if validation fails.
    :param kwargs: All other keyword arguments are passed to the sub-schema constructors.

    >>> validate = Schema(All('10', Coerce(int)))
    >>> validate('10')
    10
    """


And = All


class Match(object):
    """Value must be a string that matches the regular expression.

    >>> validate = Schema(Match(r'^0x[A-F0-9]+$'))
    >>> validate('0x123EF4')
    '0x123EF4'
    >>> with raises(MultipleInvalid, 'does not match regular expression ^0x[A-F0-9]+$'):
    ...   validate('123EF4')

    >>> with raises(MultipleInvalid, 'expected string or buffer'):
    ...   validate(123)

    Pattern may also be a compiled regular expression:

    >>> validate = Schema(Match(re.compile(r'0x[A-F0-9]+', re.I)))
    >>> validate('0x123ef4')
    '0x123ef4'
    """

    def __init__(
        self, pattern: typing.Union[re.Pattern, str], msg: typing.Optional[str] = None
    ) -> None:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern = pattern
        self.msg = msg

    def __call__(self, v: typing.Any) -> str:
        """Match the value against the regular expression."""
        try:
            match = self.pattern.match(v)
        except TypeError:
            raise MatchInvalid("expected string or buffer")
        if not match:
            raise MatchInvalid(
                self.msg or f"does not match regular expression {self.pattern.pattern}"
            )
        return v

    def __repr__(self) -> str:
        return f"Match({self.pattern.pattern!r}, msg={self.msg!r})"


class Replace(object):
    """Regex substitution.

    >>> validate = Schema(All(Replace('you', 'I'),
    ...                       Replace('hello', 'goodbye')))
    >>> validate('you say hello')
    'I say goodbye'
    """

    def __init__(
        self,
        pattern: typing.Union[re.Pattern, str],
        substitution: str,
        msg: typing.Optional[str] = None,
    ) -> None:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern = pattern
        self.substitution = substitution
        self.msg = msg

    def __call__(self, v: str) -> str:
        """Validate that the value matches the specified date format."""
        """Validate that the value matches the specified datetime format."""
        """Validate that the value matches the specified date format."""
        """Validate that the value matches the specified datetime format."""
        """Apply the regex substitution to the value."""
        return self.pattern.sub(self.substitution, v)

    def __repr__(self) -> str:
        return f"Replace({self.pattern.pattern!r}, {self.substitution!r}, msg={self.msg!r})"


@message("expected an email address", cls=EmailInvalid)
def Email(v: typing.Any) -> str:
    """Verify that the value is an email address or not.

    >>> s = Schema(Email())
    >>> with raises(MultipleInvalid, 'expected an email address'):
    ...   s("a.com")
    >>> with raises(MultipleInvalid, 'expected an email address'):
    ...   s("a@.com")
    >>> with raises(MultipleInvalid, 'expected an email address'):
    ...   s("a@.com")
    >>> s('t@x.com')
    't@x.com'
    """
    if not isinstance(v, str):
        raise ValueError
    if "@" not in v:
        raise ValueError
    user, domain = v.rsplit("@", 1)
    if not USER_REGEX.match(user):
        raise ValueError
    if not DOMAIN_REGEX.match(domain):
        raise ValueError
    return v


@message("expected a fully qualified domain name URL", cls=UrlInvalid)
def FqdnUrl(v: typing.Any) -> str:
    """Verify that the value is a fully qualified domain name URL.

    >>> s = Schema(FqdnUrl())
    >>> with raises(MultipleInvalid, 'expected a fully qualified domain name URL'):
    ...   s("http://localhost/")
    >>> s('http://w3.org')
    'http://w3.org'
    """
    if not isinstance(v, str):
        raise ValueError
    try:
        parsed = urlparse.urlparse(v)
        if not parsed.scheme or not parsed.netloc or parsed.netloc == "localhost":
            raise ValueError
    except Exception:
        raise ValueError
    return v


@message("expected a URL", cls=UrlInvalid)
def Url(v: typing.Any) -> str:
    """Verify that the value is a URL.

    >>> s = Schema(Url())
    >>> with raises(MultipleInvalid, 'expected a URL'):
    ...   s(1)
    >>> s('http://w3.org')
    'http://w3.org'
    """
    if not isinstance(v, str):
        raise ValueError
    try:
        parsed = urlparse.urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError
    except Exception:
        raise ValueError
    return v


@message("Not a file", cls=FileInvalid)
@truth
def IsFile(v: typing.Any) -> typing.Any:
    """Verify the file exists.

    >>> os.path.basename(IsFile()(__file__)).startswith('validators.py')
    True
    >>> with raises(FileInvalid, 'Not a file'):
    ...   IsFile()("random_filename_goes_here.py")
    >>> with raises(FileInvalid, 'Not a file'):
    ...   IsFile()(None)
    """
    pass


@message("Not a directory", cls=DirInvalid)
@truth
def IsDir(v: typing.Any) -> typing.Any:
    """Verify the directory exists.

    >>> IsDir()('/')
    '/'
    >>> with raises(DirInvalid, 'Not a directory'):
    ...   IsDir()(None)
    """
    pass


@message("path does not exist", cls=PathInvalid)
@truth
def PathExists(v: typing.Any) -> typing.Any:
    """Verify the path exists, regardless of its type.

    >>> os.path.basename(PathExists()(__file__)).startswith('validators.py')
    True
    >>> with raises(Invalid, 'path does not exist'):
    ...   PathExists()("random_filename_goes_here.py")
    >>> with raises(PathInvalid, 'Not a Path'):
    ...   PathExists()(None)
    """
    pass


def Maybe(
    validator: Schemable, msg: typing.Optional[str] = None
) -> typing.Callable[[typing.Any], typing.Any]:
    """Validate that the object matches given validator or is None.

    :raises Invalid: If the value does not match the given validator and is not
        None.

    >>> s = Schema(Maybe(int))
    >>> s(10)
    10
    >>> with raises(Invalid):
    ...  s("string")

    """
    schema = Schema(validator)

    @wraps(validator)
    def f(v: typing.Any) -> typing.Any:
        if v is None:
            return v
        return schema(v)

    return f


class Range(object):
    """Limit a value to a range.

    Either min or max may be omitted.
    Either min or max can be excluded from the range of accepted values.

    :raises Invalid: If the value is outside the range.

    >>> s = Schema(Range(min=1, max=10, min_included=False))
    >>> s(5)
    5
    >>> s(10)
    10
    >>> with raises(MultipleInvalid, 'value must be at most 10'):
    ...   s(20)
    >>> with raises(MultipleInvalid, 'value must be higher than 1'):
    ...   s(1)
    >>> with raises(MultipleInvalid,
    ...             'value must be lower than 10'):
    ...   Schema(Range(max=10, max_included=False))(20)
    """

    def __init__(
        self,
        min: typing.Optional[typing.Any] = None,
        max: typing.Optional[typing.Any] = None,
        min_included: bool = True,
        max_included: bool = True,
        msg: typing.Optional[str] = None,
    ) -> None:
        self.min = min
        self.max = max
        self.min_included = min_included
        self.max_included = max_included
        self.msg = msg

    def __call__(self, v: typing.Any) -> typing.Any:
        try:
            if self.min_included:
                if self.min is not None and not v >= self.min:
                    raise RangeInvalid(self.msg or f"value must be at least {self.min}")
            elif self.min is not None and not v > self.min:
                raise RangeInvalid(self.msg or f"value must be higher than {self.min}")
            if self.max_included:
                if self.max is not None and not v <= self.max:
                    raise RangeInvalid(self.msg or f"value must be at most {self.max}")
            elif self.max is not None and not v < self.max:
                raise RangeInvalid(self.msg or f"value must be lower than {self.max}")
            return v
        except TypeError:
            raise RangeInvalid(
                self.msg or "invalid value or type (must have a partial ordering)"
            )

    def __repr__(self) -> str:
        return (
            f"Range(min={self.min!r}, max={self.max!r}, "
            f"min_included={self.min_included!r}, max_included={self.max_included!r}, "
            f"msg={self.msg!r})"
        )


class Clamp(object):
    """Clamp a value to a range.

    Either min or max may be omitted.

    >>> s = Schema(Clamp(min=0, max=1))
    >>> s(0.5)
    0.5
    >>> s(5)
    1
    >>> s(-1)
    0
    """

    def __init__(
        self,
        min: typing.Optional[typing.Any] = None,
        max: typing.Optional[typing.Any] = None,
        msg: typing.Optional[str] = None,
    ) -> None:
        self.min = min
        self.max = max
        self.msg = msg

    def __call__(self, v: typing.Any) -> typing.Any:
        try:
            if self.min is not None and v < self.min:
                v = self.min
            if self.max is not None and v > self.max:
                v = self.max
            return v
        except TypeError:
            raise RangeInvalid(
                self.msg or "invalid value or type (must have a partial ordering)"
            )

    def __repr__(self) -> str:
        return f"Clamp(min={self.min}, max={self.max})"


class Length(object):
    """The length of a value must be in a certain range."""

    def __init__(
        self,
        min: typing.Optional[int] = None,
        max: typing.Optional[int] = None,
        msg: typing.Optional[str] = None,
    ) -> None:
        self.min = min
        self.max = max
        self.msg = msg

    def __call__(self, v: typing.Sized) -> typing.Sized:
        """Validate that the length of the value is within the specified range."""
        try:
            if self.min is not None and len(v) < self.min:
                raise LengthInvalid(
                    self.msg or f"length of value must be at least {self.min}"
                )
            if self.max is not None and len(v) > self.max:
                raise LengthInvalid(
                    self.msg or f"length of value must be at most {self.max}"
                )
            return v
        except TypeError:
            raise RangeInvalid(self.msg or "invalid value or type")

    def __repr__(self) -> str:
        return f"Length(min={self.min}, max={self.max})"


class Datetime(object):
    """Validate that the value matches the datetime format."""

    DEFAULT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(
        self, format: typing.Optional[str] = None, msg: typing.Optional[str] = None
    ) -> None:
        self.format = format or self.DEFAULT_FORMAT
        self.msg = msg

    def __call__(self, v: str) -> str:
        try:
            datetime.datetime.strptime(v, self.format)
        except (TypeError, ValueError):
            raise DatetimeInvalid(
                self.msg or f"value does not match expected format {self.format}"
            )
        return v

    def __repr__(self) -> str:
        return f"Datetime(format={self.format!r})"


class Date(Datetime):
    """Validate that the value matches the date format."""

    DEFAULT_FORMAT = "%Y-%m-%d"

    def __call__(self, v: str) -> str:
        try:
            datetime.datetime.strptime(v, self.format)
        except (TypeError, ValueError):
            raise DateInvalid(
                self.msg or f"value does not match expected format {self.format}"
            )
        return v

    def __repr__(self) -> str:
        return f"Date(format={self.format!r})"


class In(object):
    """Validate that a value is in a collection."""

    def __init__(
        self, container: typing.Container, msg: typing.Optional[str] = None
    ) -> None:
        self.container = container
        self.msg = msg

    def __call__(self, v: typing.Any) -> typing.Any:
        try:
            check = v not in self.container
        except TypeError:
            check = True
        if check:
            try:
                raise InInvalid(
                    self.msg or f"value must be one of {sorted(self.container)}"
                )
            except TypeError:
                raise InInvalid(
                    self.msg
                    or f"value must be one of {sorted(self.container, key=str)}"
                )
        return v

    def __repr__(self) -> str:
        return f"In({self.container!r})"


class NotIn(object):
    """Validate that a value is not in a collection."""

    def __init__(
        self, container: typing.Container, msg: typing.Optional[str] = None
    ) -> None:
        self.container = container
        self.msg = msg

    def __call__(self, v: typing.Any) -> typing.Any:
        """Validate that the value is not in the specified container."""
        try:
            check = v in self.container
        except TypeError:
            check = True
        if check:
            try:
                raise NotInInvalid(
                    self.msg or f"value must not be one of {sorted(self.container)}"
                )
            except TypeError:
                raise NotInInvalid(
                    self.msg
                    or f"value must not be one of {sorted(self.container, key=str)}"
                )
        return v

    def __repr__(self) -> str:
        return f"NotIn({self.container!r})"


class Contains(object):
    """Validate that the given schema element is in the sequence being validated.

    >>> s = Contains(1)
    >>> s([3, 2, 1])
    [3, 2, 1]
    >>> with raises(ContainsInvalid, 'value is not allowed'):
    ...   s([3, 2])
    """

    def __init__(self, item: typing.Any, msg: typing.Optional[str] = None) -> None:
        self.item = item
        self.msg = msg

    def __call__(self, v: typing.Sequence) -> typing.Sequence:
        """Validate that the sequence contains the specified values in any order."""
        """Validate that the sequence matches the exact sequence of validators."""
        """Validate that the sequence contains the specified values in any order."""
        """Validate that the sequence matches the exact sequence of validators."""
        """Validate that the item is in the sequence."""
        try:
            check = self.item not in v
        except TypeError:
            check = True
        if check:
            raise ContainsInvalid(self.msg or "value is not allowed")
        return v

    def __repr__(self) -> str:
        return f"Contains({self.item!r})"


class ExactSequence(object):
    """Matches each element in a sequence against the corresponding element in
    the validators.

    :param msg: Message to deliver to user if validation fails.
    :param kwargs: All other keyword arguments are passed to the sub-schema
        constructors.

    >>> from voluptuous import Schema, ExactSequence
    >>> validate = Schema(ExactSequence([str, int, list, list]))
    >>> validate(['hourly_report', 10, [], []])
    ['hourly_report', 10, [], []]
    >>> validate(('hourly_report', 10, [], []))
    ('hourly_report', 10, [], [])
    """

    def __init__(
        self,
        validators: typing.Iterable[Schemable],
        msg: typing.Optional[str] = None,
        **kwargs: typing.Any,
    ) -> None:
        self.validators = validators
        self.msg = msg
        self._schemas = [Schema(val, **kwargs) for val in validators]

    def __call__(self, v: typing.Sequence) -> typing.Sequence:
        if not isinstance(v, (list, tuple)) or len(v) != len(self._schemas):
            raise ExactSequenceInvalid(self.msg)
        try:
            v = type(v)((schema(x) for x, schema in zip(v, self._schemas)))
        except Invalid as e:
            raise e if self.msg is None else ExactSequenceInvalid(self.msg)
        return v

    def __repr__(self) -> str:
        return f"ExactSequence([{', '.join(repr(v) for v in self.validators)}])"


class Unique(object):
    """Ensure an iterable does not contain duplicate items.

    Only iterables convertible to a set are supported (native types and
    objects with correct __eq__).

    JSON does not support set, so they need to be presented as arrays.
    Unique allows ensuring that such array does not contain dupes.

    >>> s = Schema(Unique())
    >>> s([])
    []
    >>> s([1, 2])
    [1, 2]
    >>> with raises(Invalid, 'contains duplicate items: [1]'):
    ...   s([1, 1, 2])
    >>> with raises(Invalid, "contains duplicate items: ['one']"):
    ...   s(['one', 'two', 'one'])
    >>> with raises(Invalid, regex="^contains unhashable elements: "):
    ...   s([set([1, 2]), set([3, 4])])
    >>> s('abc')
    'abc'
    >>> with raises(Invalid, regex="^contains duplicate items: "):
    ...   s('aabbc')
    """

    def __init__(self, msg: typing.Optional[str] = None) -> None:
        self.msg = msg

    def __call__(self, v: typing.Iterable) -> typing.Iterable:
        """Validate that the iterable contains unique items."""
        try:
            set_v = set(v)
        except TypeError as e:
            raise TypeInvalid(self.msg or f"contains unhashable elements: {e}")
        if len(set_v) != len(v):
            seen = set()
            dupes = list(set(x for x in v if x in seen or seen.add(x)))
            raise Invalid(self.msg or f"contains duplicate items: {dupes}")
        return v

    def __repr__(self) -> str:
        return "Unique()"


class Equal(object):
    """Ensure that value matches target.

    >>> s = Schema(Equal(1))
    >>> s(1)
    1
    >>> with raises(Invalid):
    ...    s(2)

    >>> with raises(Invalid):
    ...    s('moo')

    Validators are not supported, match must be exact:

    >>> s = Schema(Equal(str))
    >>> with raises(Invalid):
    ...     s('foo')
    """

    def __init__(self, target: typing.Any, msg: typing.Optional[str] = None) -> None:
        self.target = target
        self.msg = msg

    def __call__(self, v: typing.Any) -> typing.Any:
        if v != self.target:
            raise Invalid(
                self.msg or f"Values are not equal: value:{v} != target:{self.target}"
            )
        return v

    def __repr__(self) -> str:
        return f"Equal({self.target!r})"


class Unordered(object):
    """Ensures sequence contains values in unspecified order.

    >>> s = Schema(Unordered([2, 1]))
    >>> s([2, 1])
    [2, 1]
    >>> s([1, 2])
    [1, 2]
    >>> s = Schema(Unordered([str, int]))
    >>> s(['foo', 1])
    ['foo', 1]
    >>> s([1, 'foo'])
    [1, 'foo']
    """

    def __init__(
        self,
        validators: typing.Iterable[Schemable],
        msg: typing.Optional[str] = None,
        **kwargs: typing.Any,
    ) -> None:
        self.validators = validators
        self.msg = msg
        self._schemas = [Schema(val, **kwargs) for val in validators]

    def __call__(self, v: typing.Sequence) -> typing.Sequence:
        if not isinstance(v, (list, tuple)):
            raise Invalid(self.msg or f"Value {v} is not sequence!")
        if len(v) != len(self._schemas):
            raise Invalid(
                self.msg
                or f"List lengths differ, value:{len(v)} != target:{len(self._schemas)}"
            )
        consumed = set()
        missing = []
        for index, value in enumerate(v):
            found = False
            for i, s in enumerate(self._schemas):
                if i in consumed:
                    continue
                try:
                    s(value)
                except Invalid:
                    pass
                else:
                    found = True
                    consumed.add(i)
                    break
            if not found:
                missing.append((index, value))
        if len(missing) == 1:
            el = missing[0]
            raise Invalid(
                self.msg
                or f"Element #{el[0]} ({el[1]}) is not valid against any validator"
            )
        elif missing:
            raise MultipleInvalid(
                [
                    Invalid(
                        self.msg
                        or f"Element #{el[0]} ({el[1]}) is not valid against any validator"
                    )
                    for el in missing
                ]
            )
        return v

    def __repr__(self) -> str:
        return f"Unordered([{', '.join(repr(v) for v in self.validators)}])"


class Number(object):
    """Verify the number of digits that are present in the number(Precision),
    and the decimal places(Scale).

    :raises Invalid: If the value does not match the provided Precision and Scale.

    >>> schema = Schema(Number(precision=6, scale=2))
    >>> schema('1234.01')
    '1234.01'
    >>> schema = Schema(Number(precision=6, scale=2, yield_decimal=True))
    >>> schema('1234.01')
    Decimal('1234.01')
    """

    def __init__(
        self,
        precision: typing.Optional[int] = None,
        scale: typing.Optional[int] = None,
        msg: typing.Optional[str] = None,
        yield_decimal: bool = False,
    ) -> None:
        self.precision = precision
        self.scale = scale
        self.msg = msg
        self.yield_decimal = yield_decimal

    def __call__(self, v: str) -> typing.Union[str, Decimal]:
        """:param v: is a number enclosed with string
        :return: Decimal number
        """
        precision, scale, decimal_num = self._get_precision_scale(v)
        if (
            self.precision is not None
            and self.scale is not None
            and (precision != self.precision)
            and (scale != self.scale)
        ):
            raise Invalid(
                self.msg
                or f"Precision must be equal to {self.precision}, and Scale must be equal to {self.scale}"
            )
        else:
            if self.precision is not None and precision != self.precision:
                raise Invalid(
                    self.msg or f"Precision must be equal to {self.precision}"
                )
            if self.scale is not None and scale != self.scale:
                raise Invalid(self.msg or f"Scale must be equal to {self.scale}")
        if self.yield_decimal:
            return decimal_num
        else:
            return v

    def __repr__(self) -> str:
        return (
            f"Number(precision={self.precision}, scale={self.scale}, msg={self.msg!r})"
        )

    def _get_precision_scale(self, number: str) -> typing.Tuple[int, int, Decimal]:
        """:param number:
        :return: tuple(precision, scale, decimal_number)
        """
        try:
            decimal_num = Decimal(number)
        except InvalidOperation:
            raise Invalid(self.msg or f"{number} is not a valid number")

        sign, digits, exponent = decimal_num.as_tuple()

        if exponent >= 0:
            precision = len(digits) + exponent
            scale = 0
        else:
            precision = len(digits)
            scale = -exponent

        return precision, scale, decimal_num


class SomeOf(_WithSubValidators):
    """Value must pass at least some validations, determined by the given parameter.
    Optionally, number of passed validations can be capped.

    The output of each validator is passed as input to the next.

    :param min_valid: Minimum number of valid schemas.
    :param validators: List of schemas or validators to match input against.
    :param max_valid: Maximum number of valid schemas.
    :param msg: Message to deliver to user if validation fails.
    :param kwargs: All other keyword arguments are passed to the sub-schema constructors.

    :raises NotEnoughValid: If the minimum number of validations isn't met.
    :raises TooManyValid: If the maximum number of validations is exceeded.

    >>> validate = Schema(SomeOf(min_valid=2, validators=[Range(1, 5), Any(float, int), 6.6]))
    >>> validate(6.6)
    6.6
    >>> validate(3)
    3
    >>> with raises(MultipleInvalid, 'value must be at most 5, not a valid value'):
    ...     validate(6.2)
    """

    def __init__(
        self,
        validators: typing.List[Schemable],
        min_valid: typing.Optional[int] = None,
        max_valid: typing.Optional[int] = None,
        **kwargs: typing.Any,
    ) -> None:
        """Initialize SomeOf validator.

        :param validators: List of schemas or validators to match input against.
        :param min_valid: Minimum number of valid schemas.
        :param max_valid: Maximum number of valid schemas.
        :param kwargs: All other keyword arguments are passed to the sub-schema constructors.
        """
        assert (
            min_valid is not None or max_valid is not None
        ), f'when using "{type(self).__name__}" you should specify at least one of min_valid and max_valid'
        self.min_valid = min_valid or 0
        self.max_valid = max_valid or len(validators)
        super(SomeOf, self).__init__(*validators, **kwargs)

    def __repr__(self) -> str:
        return (
            f"SomeOf(min_valid={self.min_valid}, "
            f"validators=[{', '.join(repr(v) for v in self.validators)}], "
            f"max_valid={self.max_valid}, msg={self.msg!r})"
        )
