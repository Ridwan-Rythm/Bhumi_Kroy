"""Pydantic models derived from contract section 6 (the TypeScript block is the reference).

They are used to (a) export contracts/report.schema.json, (b) document the API in OpenAPI and
(c) let tests prove that every report the engine emits has exactly the contract shape.
They are NOT used to parse requests: request validation lives in app.engine.pipeline so that every
failure comes back in the contract error shape with a precise `field`.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

Q = Literal["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
SourceName = Literal["land_records", "registry", "mutation", "court", "khas", "bank"]
SourceStatus = Literal["OK", "NO_RECORD", "PARTIAL", "STALE", "UNAVAILABLE", "ERROR"]
Maturity = Literal["M0", "M1", "M2", "M3", "M4"]
Linkage = Literal["EXACT", "TEXT_MATCH", "PARTY_NAME_ONLY"]
Verdict = Literal["GREEN", "GREY", "AMBER", "RED", "INTEGRITY_ALERT"]
Severity = Literal["INTEGRITY", "CRITICAL", "HIGH", "MEDIUM", "INFO", "COVERAGE"]
Confidence = Literal["HIGH", "MEDIUM", "LOW"]
Coverage = Literal["COVERED", "PARTIAL", "NOT_COVERED"]
MatchTier = Literal["STRONG", "PROBABLE", "WEAK", "NONE", "NOT_RUN"]
Survey = Literal["CS", "SA", "RS", "BS"]
EventKind = Literal["SURVEY_ENTRY", "SALE", "GIFT", "INHERITANCE", "PARTITION", "COURT_DECREE", "ACQUISITION",
                    "MORTGAGE", "MORTGAGE_RELEASE", "LT_NOTICE", "MUTATION_PENDING", "MUTATION_APPLIED"]
LedgerReason = Literal["hash_mismatch", "link_broken", "checkpoint_mismatch", "signature_invalid",
                       "height_mismatch"]
VerifyState = Literal["GENUINE_CURRENT", "GENUINE_EXPIRED", "GENUINE_SUPERSEDED", "TAMPERED",
                      "INTEGRITY_ALERT", "UNKNOWN"]
Param = str | int | float | bool | None


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---- requests -------------------------------------------------------------------------------------
class PlotQuery(Strict):
    district_id: str
    upazila_id: str
    mouza_id: str
    survey: Survey | None = None
    khatian_no: str
    dag_no: str


class SellerQuery(Strict):
    name: str
    father_or_husband: str | None = None


class Consents(Strict):
    bank: bool


class CheckRequest(Strict):
    plot: PlotQuery
    seller: SellerQuery
    consents: Consents | None = None


class VerifyByCode(Strict):
    short_code: str


class VerifyByPayload(Strict):
    payload_b64: str
    signature_b64: str


class TamperRequest(Strict):
    plot_id: str
    kind: str


class AddEventRequest(Strict):
    plot_id: str
    kind: str


class ClockRequest(Strict):
    offset_days: int


# ---- report ---------------------------------------------------------------------------------------
class Finding(Strict):
    rule_id: str
    severity: Severity
    confidence: Confidence
    question: Q | None
    evidence: list[str]
    params: dict[str, Param]


class SourceResult(Strict):
    source: SourceName
    status: SourceStatus
    as_of: str | None
    maturity: Maturity
    linkage: Linkage | None
    latency_ms: int
    record_count: int
    reason: Literal["consent_required", "timeout", "outage", "stale", "not_digitised"] | None


class TimelineEvent(Strict):
    date: str
    kind: EventKind
    survey: Survey | None
    from_masked: str | None
    to_masked: str | None
    share: str | None
    area_decimal: float | None
    record_ref: str
    source: SourceName
    flagged_by: list[str]


class NotChecked(Strict):
    code: str
    params: dict[str, Param]


class Checkpoint(Strict):
    height: int
    head_hash: str
    ts: str
    key_id: str
    signature_b64: str


class LedgerBlock(Strict):
    ok: bool
    broken_at_seq: int | None
    reason: LedgerReason | None
    height: int
    head_hash: str
    checkpoint: Checkpoint | None


class ReportPlot(Strict):
    plot_id: str
    district_id: str
    upazila_id: str
    mouza_id: str
    jl_no: str
    survey: Survey | None
    khatian_no: str
    dag_no: str
    area_decimal: float | None
    land_class: str | None


class SellerMatch(Strict):
    tier: MatchTier
    score: float | None


class ReportSeller(Strict):
    name: str
    father_or_husband: str | None
    match: SellerMatch


class HoldersSummary(Strict):
    holder_count: int
    seller_share: str | None


class Report(Strict):
    report_id: str | None
    short_code: str | None
    synthetic: Literal[True]
    issued_at: str
    valid_until: str | None
    plot: ReportPlot
    seller: ReportSeller
    consents: Consents
    verdict: Verdict
    coverage: dict[Q, Coverage]
    findings: list[Finding]
    sources: list[SourceResult]
    holders_summary: HoldersSummary
    timeline: list[TimelineEvent]
    not_checked: list[NotChecked]
    ledger: LedgerBlock
    key_id: str
    signed_payload_b64: str | None
    signature_b64: str | None


# ---- other responses ------------------------------------------------------------------------------
class VerifyReport(Strict):
    report_id: str
    short_code: str
    plot_id: str
    verdict: Verdict
    issued_at: str
    valid_until: str


class VerifyDiff(Strict):
    change: Literal["ADDED"]
    kind: EventKind
    record_ref: str
    date: str


class VerifyLedger(Strict):
    ok: bool
    broken_at_seq: int | None
    reason: LedgerReason | None


class VerifyResult(Strict):
    state: VerifyState
    signature_valid: bool
    report: VerifyReport | None
    diff: list[VerifyDiff] | None
    ledger: VerifyLedger
    checked_at: str


class Mouza(Strict):
    id: str
    name_bn: str
    name_en: str
    jl_no: str


class Upazila(Strict):
    id: str
    name_bn: str
    name_en: str
    mouzas: list[Mouza]


class District(Strict):
    id: str
    name_bn: str
    name_en: str
    upazilas: list[Upazila]


class Locations(Strict):
    districts: list[District]


class SamplePlot(Strict):
    sample_id: str
    plot_id: str
    scenario: str
    label_bn: str
    label_en: str
    expected_verdict: Verdict
    request: CheckRequest


class PubKey(Strict):
    key_id: str
    alg: Literal["Ed25519"]
    public_key_b64: str


class DemoEntry(Strict):
    seq: int
    ts: str
    source: SourceName
    record_id: str
    record_hash: str
    prev_hash: str
    entry_hash: str
    status: Literal["ok", "broken"]


class DemoCheckpoint(Checkpoint):
    valid: bool


class DemoLedger(Strict):
    plot_id: str
    ok: bool
    broken_at_seq: int | None
    reason: LedgerReason | None
    entries: list[DemoEntry]
    checkpoint: DemoCheckpoint | None


class ErrorBody(Strict):
    code: Literal["VALIDATION_ERROR", "NOT_FOUND", "RATE_LIMITED", "DEMO_DISABLED", "NOT_IMPLEMENTED", "INTERNAL"]
    message: str
    field: str | None


class ErrorResponse(Strict):
    error: ErrorBody
