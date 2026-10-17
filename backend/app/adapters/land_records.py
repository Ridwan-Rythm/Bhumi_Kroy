"""Mock of DLRMS / e-Porcha khatians (plan B7.4). Real counterpart: Ministry of Land portals."""
from app.adapters.base import BaseAdapter


class LandRecordsAdapter(BaseAdapter):
    source = "land_records"
