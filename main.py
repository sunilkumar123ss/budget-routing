"""Deterministic offline routing based on configured capacities and budgets."""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys


def amount(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("invalid money value") from error
    if not result.is_finite() or result < 0:
        raise ValueError("money values must be finite and nonnegative")
    return result


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value

