"""Input normalisation: Bangla/ASCII digits, whitespace, zero-width characters."""
from __future__ import annotations

import re
import unicodedata

_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"))


def to_ascii_digits(text: str) -> str:
    return text.translate(_BN_DIGITS)


def normalize_number_string(text: str) -> str:
    """khatian_no / dag_no: ASCII digits, no spaces or zero-width chars."""
    text = unicodedata.normalize("NFC", str(text)).translate(_ZERO_WIDTH)
    text = to_ascii_digits(text)
    return re.sub(r"\s+", "", text)


def clean_text(text: str) -> str:
    """Names: NFC, zero-width removed, whitespace collapsed. Content is otherwise untouched."""
    text = unicodedata.normalize("NFC", str(text)).translate(_ZERO_WIDTH)
    return re.sub(r"\s+", " ", text).strip()
