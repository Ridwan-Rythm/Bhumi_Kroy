from app.adapters.bank import BankAdapter
from app.adapters.base import SOURCES, Ctx, SourceResult, fetch_all
from app.adapters.court import CourtAdapter
from app.adapters.khas import KhasAdapter
from app.adapters.land_records import LandRecordsAdapter
from app.adapters.mutation import MutationAdapter
from app.adapters.registry import RegistryAdapter

ALL_ADAPTERS = [LandRecordsAdapter(), RegistryAdapter(), MutationAdapter(), CourtAdapter(),
                KhasAdapter(), BankAdapter()]

__all__ = ["ALL_ADAPTERS", "SOURCES", "Ctx", "SourceResult", "fetch_all"]
