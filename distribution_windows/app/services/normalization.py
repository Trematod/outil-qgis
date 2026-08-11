"""Normalisation déterministe des numéros de dossier."""

import math
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedNumber:
    original: Any
    value: str
    changed: bool
    usable: bool
    reason: str | None = None


_DASHES = re.compile(r"[-\u2010\u2011\u2012\u2013\u2014\u2212]")


def normalize_case_number(value: Any) -> NormalizedNumber:
    """Return the source value and its normalized value without overwriting it."""
    if value is None or _is_nan(value):
        return NormalizedNumber(value, "", False, False, "Numéro vide")

    original_text = str(value)
    normalized = original_text.strip().split("/", maxsplit=1)[0]
    normalized = _DASHES.sub("", normalized)
    normalized = re.sub(r"\s+", "", normalized)

    if not normalized:
        return NormalizedNumber(value, "", original_text != normalized, False, "Numéro vide")

    changed = original_text != normalized
    return NormalizedNumber(value, normalized, changed, True)


def _is_nan(value: Any) -> bool:
    return isinstance(value, float) and math.isnan(value)