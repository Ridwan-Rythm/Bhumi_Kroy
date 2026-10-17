"""Mock of DC office / Gazette lists: khas, vested (Ka/Kha), abandoned, acquisition."""
from app.adapters.base import BaseAdapter


class KhasAdapter(BaseAdapter):
    source = "khas"
