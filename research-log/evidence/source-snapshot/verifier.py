"""Verify one JSON tool call and report its first failure."""

import json

from .tools import TOOLS


def _object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def _invalid_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def verify(response, task):
    try:
        call = json.loads(response, object_pairs_hook=_object,
                          parse_constant=_invalid_constant)
    except (ValueError, TypeError, RecursionError):
        return "invalid_json"
    if (not isinstance(call, dict) or call.keys() != {"tool", "arguments"}
            or not isinstance(call["tool"], str)
            or not isinstance(call["arguments"], dict)):
        return "invalid_format"
    if call["tool"] != task.tool or call["tool"] not in TOOLS:
        x = call["tool"]
        return "wrong_tool"
    args = call["arguments"]
    if args != task.arguments or any(isinstance(v, bool) for v in args.values()):
        return "wrong_arguments"
    try:
        result = TOOLS[call["tool"]](**args)
    except (ValueError, TypeError, KeyError, ArithmeticError):
        return "execution_error"
    return "success" if result == task.expected_result else "wrong_result"
