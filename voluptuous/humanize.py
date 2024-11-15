import typing
from voluptuous.error import Invalid, MultipleInvalid

MAX_VALIDATION_ERROR_ITEM_LENGTH = 500


def humanize_error(
    data: typing.Any,
    validation_error: Invalid,
    max_sub_error_length: int = MAX_VALIDATION_ERROR_ITEM_LENGTH,
) -> str:
    """Provide a more helpful + complete validation error message than that provided automatically
    Invalid and MultipleInvalid do not include the offending value in error messages,
    and MultipleInvalid.__str__ only provides the first error.
    """
    if isinstance(validation_error, MultipleInvalid):
        return _format_multiple_errors(data, validation_error, max_sub_error_length)
    else:
        return _format_single_error(data, validation_error, max_sub_error_length)


def _format_single_error(data: typing.Any, error: Invalid, max_length: int) -> str:
    path = _get_path_string(error.path)
    value = _get_value_from_path(data, error.path)
    value_str = _truncate_value(repr(value), max_length)
    return f"{error}: value was {value_str} at {path}"


def _format_multiple_errors(
    data: typing.Any, errors: MultipleInvalid, max_length: int
) -> str:
    error_messages = []
    for error in errors.errors:
        error_messages.append(_format_single_error(data, error, max_length))
    return "\n".join(error_messages)


def _get_path_string(path: typing.List[typing.Hashable]) -> str:
    return ".".join(map(str, path)) if path else "top level"


def _get_value_from_path(
    data: typing.Any, path: typing.List[typing.Union[str, int]]
) -> typing.Any:
    for key in path:
        if isinstance(data, (dict, list)) and key in data:
            data = data[key]
        elif isinstance(key, str) and hasattr(data, key):
            data = getattr(data, key)
        else:
            return "<unavailable>"
    return data


def _truncate_value(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."
