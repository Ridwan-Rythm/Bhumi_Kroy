// Copied EXACTLY from contracts/00_SHARED_CONTRACT.md section 6. Do not rename anything.
// If the API differs from this file, tell Ridwan: the contract wins.

export type Q = "Q1" | "Q2" | "Q3" | "Q4" | "Q5" | "Q6";
export type SourceName = "land_records" | "registry" | "mutation" | "court" | "khas" | "bank";
export type SourceStatus = "OK" | "NO_RECORD" | "PARTIAL" | "STALE" | "UNAVAILABLE" | "ERROR";
export type Maturity = "M0" | "M1" | "M2" | "M3" | "M4";
export type Linkage = "EXACT" | "TEXT_MATCH" | "PARTY_NAME_ONLY";
export type Verdict = "GREEN" | "GREY" | "AMBER" | "RED" | "INTEGRITY_ALERT";
export type Severity = "INTEGRITY" | "CRITICAL" | "HIGH" | "MEDIUM" | "INFO" | "COVERAGE";
export type Confidence = "HIGH" | "MEDIUM" | "LOW";
export type Coverage = "COVERED" | "PARTIAL" | "NOT_COVERED";
export type MatchTier = "STRONG" | "PROBABLE" | "WEAK" | "NONE" | "NOT_RUN";
export type Survey = "CS" | "SA" | "RS" | "BS";
export type EventKind =
  | "SURVEY_ENTRY"
  | "SALE"
  | "GIFT"
  | "INHERITANCE"
  | "PARTITION"
  | "COURT_DECREE"
  | "ACQUISITION"
  | "MORTGAGE"
  | "MORTGAGE_RELEASE"
  | "LT_NOTICE"
  | "MUTATION_PENDING"
  | "MUTATION_APPLIED";
export type LedgerReason =
  | "hash_mismatch"
  | "link_broken"
  | "checkpoint_mismatch"
  | "signature_invalid"
  | "height_mismatch";
export type Param = string | number | boolean | null;

export interface CheckRequest {
  plot: {
    district_id: string;
    upazila_id: string;
    mouza_id: string;
    survey?: Survey;
    khatian_no: string;
    dag_no: string;
  }; // digit strings may be Bangla or ASCII
  seller: { name: string; father_or_husband?: string };
  consents?: { bank: boolean }; // default { bank: true }
}

export interface Finding {
  rule_id: string; // e.g. "R-LIEN-01" (full list in section 8)
  severity: Severity;
  confidence: Confidence;
  question: Q | null;
  evidence: string[]; // record refs, e.g. ["BNK-0003"]
  params: Record<string, Param>; // interpolated by the frontend
}

export interface SourceResult {
  source: SourceName;
  status: SourceStatus;
  as_of: string | null; // ISO 8601
  maturity: Maturity;
  linkage: Linkage | null;
  latency_ms: number;
  record_count: number;
  reason: "consent_required" | "timeout" | "outage" | "stale" | "not_digitised" | null;
}

export interface TimelineEvent {
  date: string; // "YYYY-MM-DD" or ""
  kind: EventKind;
  survey: Survey | null;
  from_masked: string | null; // masked synthetic names, shown as-is, never translated
  to_masked: string | null;
  share: string | null; // fraction text, e.g. "1/2"
  area_decimal: number | null;
  record_ref: string;
  source: SourceName;
  flagged_by: string[]; // rule_ids that cite this event
}

export interface NotChecked {
  code: string;
  params: Record<string, Param>;
} // codes in section 8.3

export interface Checkpoint {
  height: number;
  head_hash: string;
  ts: string;
  key_id: string;
  signature_b64: string;
}

export interface LedgerBlock {
  ok: boolean;
  broken_at_seq: number | null;
  reason: LedgerReason | null;
  height: number;
  head_hash: string;
  checkpoint: Checkpoint | null;
}

export interface Report {
  report_id: string | null; // null only when verdict == INTEGRITY_ALERT
  short_code: string | null; // "K7M2-9QXA"
  synthetic: true;
  issued_at: string;
  valid_until: string | null; // issued_at + 7 days
  plot: {
    plot_id: string;
    district_id: string;
    upazila_id: string;
    mouza_id: string;
    jl_no: string;
    survey: Survey | null;
    khatian_no: string;
    dag_no: string;
    area_decimal: number | null;
    land_class: string | null; // land_class is data, shown as-is
  };
  seller: {
    name: string;
    father_or_husband: string | null;
    match: { tier: MatchTier; score: number | null };
  };
  consents: { bank: boolean };
  verdict: Verdict;
  coverage: Record<Q, Coverage>;
  findings: Finding[];
  sources: SourceResult[]; // always six entries
  holders_summary: { holder_count: number; seller_share: string | null };
  timeline: TimelineEvent[];
  not_checked: NotChecked[];
  ledger: LedgerBlock;
  key_id: string;
  signed_payload_b64: string | null; // base64url (no padding) of the exact signed bytes, section 7
  signature_b64: string | null; // base64url (no padding) Ed25519 signature
}

export interface VerifyResult {
  state:
    | "GENUINE_CURRENT"
    | "GENUINE_EXPIRED"
    | "GENUINE_SUPERSEDED"
    | "TAMPERED"
    | "INTEGRITY_ALERT"
    | "UNKNOWN";
  signature_valid: boolean;
  report: {
    report_id: string;
    short_code: string;
    plot_id: string;
    verdict: Verdict;
    issued_at: string;
    valid_until: string;
  } | null;
  diff: { change: "ADDED"; kind: EventKind; record_ref: string; date: string }[] | null;
  ledger: { ok: boolean; broken_at_seq: number | null; reason: LedgerReason | null };
  checked_at: string;
}

export interface Locations {
  districts: {
    id: string;
    name_bn: string;
    name_en: string;
    upazilas: {
      id: string;
      name_bn: string;
      name_en: string;
      mouzas: { id: string; name_bn: string; name_en: string; jl_no: string }[];
    }[];
  }[];
}

export interface SamplePlot {
  sample_id: string;
  plot_id: string;
  scenario: string;
  label_bn: string;
  label_en: string;
  expected_verdict: Verdict;
  request: CheckRequest;
}

export interface PubKey {
  key_id: string;
  alg: "Ed25519";
  public_key_b64: string;
} // base64url, no padding

export interface DemoLedger {
  plot_id: string;
  ok: boolean;
  broken_at_seq: number | null;
  reason: LedgerReason | null;
  entries: {
    seq: number;
    ts: string;
    source: SourceName;
    record_id: string;
    record_hash: string;
    prev_hash: string;
    entry_hash: string;
    status: "ok" | "broken";
  }[];
  checkpoint: (Checkpoint & { valid: boolean }) | null;
}

// ---- Not part of section 6: request/response helpers taken from section 5 ----
export type VerifyRequest = { short_code: string } | { payload_b64: string; signature_b64: string };
export type TamperKind =
  | "edit_field"
  | "edit_and_rehash"
  | "delete_entry"
  | "swap_signature"
  | "reorder"
  | "replace_entry"
  | "replay_checkpoint";
export type AddEventKind = "new_mortgage" | "new_mutation_pending";
export type ApiErrorCode =
  | "VALIDATION_ERROR"
  | "NOT_FOUND"
  | "RATE_LIMITED"
  | "DEMO_DISABLED"
  | "NOT_IMPLEMENTED"
  | "INTERNAL";
