# OWNED BY NAZIFA. Replaced in step B2. Do not edit.
"""Stub name matcher with the exact signature from contract section 8.4."""

IS_STUB = True


def match_name(seller_name: str, seller_father: str | None,
               record_name: str, record_father: str | None) -> dict:
    """Returns {"tier": "STRONG"|"PROBABLE"|"WEAK"|"NONE", "score": float,
                "name_score": float, "father_score": float | None}"""
    same = (seller_name or "").strip() == (record_name or "").strip()
    return {
        "tier": "STRONG" if same else "NONE",
        "score": 1.0 if same else 0.0,
        "name_score": 1.0 if same else 0.0,
        "father_score": None,
    }
