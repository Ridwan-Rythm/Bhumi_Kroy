"""Mock of consent-gated bank lien data. Without consent: UNAVAILABLE (consent_required)."""
from app.adapters.base import BaseAdapter, Ctx


class BankAdapter(BaseAdapter):
    source = "bank"

    def consent_ok(self, ctx: Ctx) -> bool:
        return bool(ctx.consents.get("bank", True))
