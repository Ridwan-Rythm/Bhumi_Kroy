"""Mock of the sub-registry deed index (plan B7.4). Real counterpart: Department of Registration."""
from app.adapters.base import BaseAdapter


class RegistryAdapter(BaseAdapter):
    source = "registry"
