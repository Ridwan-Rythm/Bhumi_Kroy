"""Mock of court cause lists. Cases carry a linkage (EXACT / TEXT_MATCH / PARTY_NAME_ONLY).

With no cases the source answers NO_RECORD, whose coverage value depends on maturity and linkage.
"""
from app.adapters.base import BaseAdapter


class CourtAdapter(BaseAdapter):
    source = "court"

    def default_status(self, records: list[dict]) -> str:
        return "OK" if records else "NO_RECORD"
