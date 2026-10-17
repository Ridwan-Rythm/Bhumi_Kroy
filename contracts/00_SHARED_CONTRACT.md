# LandCheck — Shared Contract v1 (one-day sprint)

> **Both of you work from this file.** Ridwan copies it to `contracts/00_SHARED_CONTRACT.md` in step A0.1. Until the repo is up, Nazifa reads her copy of this file.
> **Frozen at S0.** After S0: additive, optional changes only. Ridwan makes them after you both agree in chat, with a commit message `contract: <what>`. Never rename or remove a field, enum value or endpoint.
> If this file and any generated schema or type disagree, **this file wins**.
> Plan v2 is copied to `docs/PLAN.md`. It explains the *why*. This file is the *what, who and when* for one day.

**Names:** Person **A = Ridwan** (backend, engine, trust). Person **B = Nazifa** (frontend, Bangla content, name matching, submission documents). You can swap the names; do not change the split.

---

## 1. One-day scope

We have today (17 Oct) to build. The deadline is 18 Oct. v2 was written for weeks, so these are the changes for a single day. They are decisions, not drift.

| # | Decision for the one-day sprint | Replaces in plan v2 |
|---|---|---|
| D1 | **Report PDF = a print-optimised HTML page** (`/report/:id/print`) and the browser's "Save as PDF". No WeasyPrint, no Docker. The browser shapes Bangla correctly. The signature covers the report *data*, not the PDF (as v2 B10.5 already says). | B10.5 WeasyPrint |
| D2 | **All user-visible text lives only in the frontend.** The backend emits language-neutral codes (`rule_id`, `params`, `not_checked[].code`). Nazifa owns all Bangla and English copy. | B8.5 messages in rule YAML |
| D3 | **One hash chain per plot**, with its own signed checkpoints. A tamper on one plot cannot break another plot, and verification stays fast. | B4.3 single global chain |
| D4 | **Rules in two tiers.** Tier 1 (needed by the 10 golden samples) must ship. Tier 2 only after S2. Invariants I1, I2, I7 only. | B8.3 all 18 Must rules |
| D5 | **Name matching level 1 only.** Level 2 (phonetic) is a stretch. | B8.4 |
| D6 | **Golden plots are built by a deterministic builder script.** A mini generator plus benchmark is a stretch. | B13 |
| D7 | **No hosted instance.** `make dev` locally, a recorded video as the fallback. | B10.6 |
| D8 | **Deferred:** seller-document upload, Merkle checkpoints, WhatsApp share (stretch), Docker Compose, audio, PWA, server-side PDF. | B5.1 |

### Non-negotiables (never cut, in this order)
1. The vertical slice (P-001 and P-003 from UI to API) by S1.
2. Bangla UI visible on the RED result.
3. The tamper vs legitimate-update demo (P-010).
4. "What we did not check" and the coverage-aware verdict (unknown never becomes GREEN).
5. Tests for every Tier-1 rule and the golden plots.
6. `README.md` with run steps, data description and AI tools, plus both AI-usage logs.
7. The visible "SYNTHETIC — NOT A REAL LAND RECORD" watermark.

### Cut order if behind
Stretch items → Tier-2 rules → reorder/replace/replay tamper kinds → glossary tooltips → slide polish → UI polish beyond Home, Result and Verify.

---

## 2. Who owns what (this is what prevents merge conflicts)

**Rule: you only edit files you own. If something you don't own must change, message the owner. No "tiny fixes" in the other person's folder.** If git ever reports a merge conflict, stop. It means someone edited a file they don't own. Do not resolve it with "ours/theirs" blindly; message the other person.

| Path | Owner | Notes |
|---|---|---|
| `contracts/**` | A | Frozen at S0, then additive changes only |
| `backend/**` | A | **Except** the next row |
| `backend/app/namematch/**`, `backend/tests/namematch/**` | **B** | A creates a stub at S0 with the signature in §8. B replaces it in step B2 |
| `frontend/**` | B | |
| `README.md` | B | A creates a placeholder at S0 and supplies raw notes in `docs/backend_notes.md` |
| `docs/concept_note/**`, `docs/slides/**`, `docs/DEMO_SCRIPT.md`, `docs/VIDEO_STORYBOARD.md` | B | |
| `docs/PLAN.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION.md`, `docs/backend_notes.md` | A | `docs/PLAN.md` is a copy of plan v2 |
| `Makefile`, `.github/**`, `.gitignore`, `LICENSE`, `CLAUDE.md` | A | |
| `docs/ai_usage/ridwan.md` | A | Own log only |
| `docs/ai_usage/nazifa.md` | B | Own log only |

Lockfiles follow their folder (`frontend/package-lock.json` is B's, `backend/requirements.txt` is A's). **B may not add Python dependencies**: the name matcher uses the standard library only.

### Git protocol
1. A pushes the scaffold to `main` and tags it `contract-v1` (end of S0). B clones.
2. Branches: A works on `feat/engine`, B on `feat/ui`. Do not commit to `main` directly after S0.
3. Commit small and often with the prefixes `engine:`, `ui:`, `docs:`. **No force-push, no rebase of pushed commits, no history rewriting** (the rulebook wants the real history). Merge PRs with **"Create a merge commit"**, not squash.
4. **Merge to `main` whenever your tests are green.** S-points are deadlines, not the only chance.
5. Sync ritual (each person, at every S-point and whenever you merge):
   ```bash
   git fetch origin
   git merge origin/main        # clean by design
   make test                    # A: backend tests · B: cd frontend && npm run build && npm test
   git push -u origin <your-branch>
   gh pr create --base main --fill      # or open the PR on github.com; merge-commit it
   ```
   Then the partner runs `git fetch origin && git merge origin/main`.
6. Never run a formatter or linter `--fix` outside your own folders.
7. If you need the partner's work earlier, ask them to merge to `main` early. Do not cherry-pick between branches.

---

## 3. Timeline and sync points

H0 is when you both sit down. Times are hours from then.

| Sync | When | What must be true on `main` |
|---|---|---|
| **S0** | H0:45 | Scaffold, this contract and `report.schema.json` on `main`, tagged `contract-v1`. `contracts/fixtures/signed_sample*.json` exist. Both branches created. |
| **S1** | H4:00 | **Vertical slice:** P-001 → GREEN and P-003 → RED go from the real UI form through the real API to the Result screen. Mock mode off. |
| **S2** | H8:00 | **Feature complete:** all 10 samples (§9) pass through the UI, verify page and demo console work, name matcher merged, all Tier-1 rules and their Bangla and English text exist. |
| **S3** | H11:00 | **Feature freeze + integration pass:** every golden plot checked in the UI on a clean clone. Bug fixes only after this point. Teach-back (20 min each). |
| **S4** | H14:00 | Concept note, README, demo script, video and slides done. CI green. A fresh `git clone` runs with `make setup && make dev`. |
| — | H14:00–16:00 | Submission buffer: upload, final checks, rehearsal. |

15-minute check-in at every S-point: what's done, what's blocked, what can we cut.

---

## 4. Run, ports, environment

- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev` → `http://localhost:5173`. Vite proxies `/api` and `/demo` to port 8000.
- Backend environment: `DEMO_MODE=1` enables `/demo/*`. `DB_PATH` defaults to `backend/data/landcheck.db`. `SIGNING_KEY_B64` is optional; if it is missing the backend generates a key into `backend/.keys/` (gitignored).
- Frontend environment: `VITE_USE_MOCK=1` serves fixtures from `frontend/src/mocks/`. `VITE_USE_MOCK=0` calls the real API.
- Makefile (A): `make setup` · `make seed` · `make backend` · `make frontend` · `make dev` (prints the two commands) · `make test` · `make reset`.
- CORS allows `http://localhost:5173`.

---

## 5. API

All paths are under `/api/v1` unless stated. JSON in, JSON out. Errors are `{"error": {"code", "message", "field"}}` with codes `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `RATE_LIMITED` (429), `DEMO_DISABLED` (404), `NOT_IMPLEMENTED` (501), `INTERNAL` (500).

| Method + path | Body | Returns |
|---|---|---|
| `GET /health` | — | `{"ok": true, "demo_mode": bool}` |
| `GET /meta/locations` | — | `Locations` |
| `GET /meta/samples` | — | `SamplePlot[]` (the ten samples, §9) |
| `GET /meta/pubkey` | — | `PubKey` |
| `POST /check` | `CheckRequest` | `Report` (HTTP 200 for every verdict, including RED, GREY and INTEGRITY_ALERT) |
| `GET /reports/{report_id}` | — | `Report` as issued, or 404 |
| `POST /verify` | `{short_code}` **or** `{payload_b64, signature_b64}` | `VerifyResult` |
| `POST /demo/tamper` | `{plot_id, kind}` | `DemoLedger` |
| `POST /demo/add-event` | `{plot_id, kind}` | `{"ok": true, "added": {record_ref, kind, date}}` |
| `POST /demo/reset` | — | `{"ok": true}` |
| `GET /demo/ledger/{plot_id}` | — | `DemoLedger` |
| `POST /demo/clock` *(optional)* | `{offset_days}` | `{"ok": true, "now": ISO}` |

The `/demo/*` paths are **not** under `/api/v1`, and they return `DEMO_DISABLED` unless `DEMO_MODE=1`.

**`/demo/reset` rebuilds plots, records, ledger and checkpoints from the seed but KEEPS the `reports` table.** Reports issued before a reset must still be verifiable (the P-010 demo depends on it). `/verify` by `{payload_b64, signature_b64}` never needs the stored report row, because the signed payload already carries `plot_id` and `ledger_height`.

- **Tamper kinds:** `edit_field`, `edit_and_rehash`, `delete_entry`, `swap_signature` (A must implement these four). `reorder`, `replace_entry`, `replay_checkpoint` return `NOT_IMPLEMENTED` until built. The UI must handle that code gracefully.
- **Add-event kinds:** `new_mortgage`, `new_mutation_pending`.
- **Verify precedence (backend):** `TAMPERED` > `UNKNOWN` > `INTEGRITY_ALERT` > `GENUINE_SUPERSEDED` > `GENUINE_EXPIRED` > `GENUINE_CURRENT`.
  - Invalid signature → `TAMPERED`. Unknown short code → `UNKNOWN`.
  - The ledger check for the plot fails on current data → `INTEGRITY_ALERT`.
  - Any ledger entry with `seq` greater than the report's `ledger_height` for the same plot → `GENUINE_SUPERSEDED` plus `diff[]`.
  - `now` later than `valid_until` → `GENUINE_EXPIRED`.
- **`POST /check` on a plot whose ledger fails** returns verdict `INTEGRITY_ALERT`. `report_id`, `short_code`, `valid_until`, `signed_payload_b64` and `signature_b64` are `null`, and nothing is stored.
- **Rate limit:** 30 requests per minute per IP on `/check` and `/verify`.
- **Digits:** the backend accepts Bangla (০–৯) and ASCII digits in every numeric string and stores ASCII.

---

## 6. Data shapes (TypeScript is the reference; Python models are derived from it)

```ts
type Q = "Q1" | "Q2" | "Q3" | "Q4" | "Q5" | "Q6";
type SourceName = "land_records" | "registry" | "mutation" | "court" | "khas" | "bank";
type SourceStatus = "OK" | "NO_RECORD" | "PARTIAL" | "STALE" | "UNAVAILABLE" | "ERROR";
type Maturity = "M0" | "M1" | "M2" | "M3" | "M4";
type Linkage = "EXACT" | "TEXT_MATCH" | "PARTY_NAME_ONLY";
type Verdict = "GREEN" | "GREY" | "AMBER" | "RED" | "INTEGRITY_ALERT";
type Severity = "INTEGRITY" | "CRITICAL" | "HIGH" | "MEDIUM" | "INFO" | "COVERAGE";
type Confidence = "HIGH" | "MEDIUM" | "LOW";
type Coverage = "COVERED" | "PARTIAL" | "NOT_COVERED";
type MatchTier = "STRONG" | "PROBABLE" | "WEAK" | "NONE" | "NOT_RUN";
type Survey = "CS" | "SA" | "RS" | "BS";
type EventKind = "SURVEY_ENTRY" | "SALE" | "GIFT" | "INHERITANCE" | "PARTITION" | "COURT_DECREE"
  | "ACQUISITION" | "MORTGAGE" | "MORTGAGE_RELEASE" | "LT_NOTICE" | "MUTATION_PENDING" | "MUTATION_APPLIED";
type LedgerReason = "hash_mismatch" | "link_broken" | "checkpoint_mismatch" | "signature_invalid" | "height_mismatch";
type Param = string | number | boolean | null;

interface CheckRequest {
  plot: { district_id: string; upazila_id: string; mouza_id: string; survey?: Survey;
          khatian_no: string; dag_no: string };          // digit strings may be Bangla or ASCII
  seller: { name: string; father_or_husband?: string };
  consents?: { bank: boolean };                          // default { bank: true }
}

interface Finding {
  rule_id: string;               // e.g. "R-LIEN-01" (full list in §8)
  severity: Severity;
  confidence: Confidence;
  question: Q | null;
  evidence: string[];            // record refs, e.g. ["BNK-0003"]
  params: Record<string, Param>; // interpolated by the frontend
}

interface SourceResult {
  source: SourceName;
  status: SourceStatus;
  as_of: string | null;          // ISO 8601
  maturity: Maturity;
  linkage: Linkage | null;
  latency_ms: number;
  record_count: number;
  reason: "consent_required" | "timeout" | "outage" | "stale" | "not_digitised" | null;
}

interface TimelineEvent {
  date: string;                  // "YYYY-MM-DD" or ""
  kind: EventKind;
  survey: Survey | null;
  from_masked: string | null;    // masked synthetic names, shown as-is, never translated
  to_masked: string | null;
  share: string | null;          // fraction text, e.g. "1/2"
  area_decimal: number | null;
  record_ref: string;
  source: SourceName;
  flagged_by: string[];          // rule_ids that cite this event
}

interface NotChecked { code: string; params: Record<string, Param> }   // codes in §8.3

interface Checkpoint { height: number; head_hash: string; ts: string; key_id: string; signature_b64: string }

interface LedgerBlock {
  ok: boolean; broken_at_seq: number | null; reason: LedgerReason | null;
  height: number; head_hash: string; checkpoint: Checkpoint | null;
}

interface Report {
  report_id: string | null;      // null only when verdict == INTEGRITY_ALERT
  short_code: string | null;     // "K7M2-9QXA"
  synthetic: true;
  issued_at: string;
  valid_until: string | null;    // issued_at + 7 days
  plot: { plot_id: string; district_id: string; upazila_id: string; mouza_id: string; jl_no: string;
          survey: Survey | null; khatian_no: string; dag_no: string;
          area_decimal: number | null; land_class: string | null };   // land_class is data, shown as-is
  seller: { name: string; father_or_husband: string | null;
            match: { tier: MatchTier; score: number | null } };
  consents: { bank: boolean };
  verdict: Verdict;
  coverage: Record<Q, Coverage>;
  findings: Finding[];
  sources: SourceResult[];       // always six entries
  holders_summary: { holder_count: number; seller_share: string | null };
  timeline: TimelineEvent[];
  not_checked: NotChecked[];
  ledger: LedgerBlock;
  key_id: string;
  signed_payload_b64: string | null;   // base64url (no padding) of the exact signed bytes, §7
  signature_b64: string | null;        // base64url (no padding) Ed25519 signature
}

interface VerifyResult {
  state: "GENUINE_CURRENT" | "GENUINE_EXPIRED" | "GENUINE_SUPERSEDED" | "TAMPERED" | "INTEGRITY_ALERT" | "UNKNOWN";
  signature_valid: boolean;
  report: { report_id: string; short_code: string; plot_id: string; verdict: Verdict;
            issued_at: string; valid_until: string } | null;
  diff: { change: "ADDED"; kind: EventKind; record_ref: string; date: string }[] | null;
  ledger: { ok: boolean; broken_at_seq: number | null; reason: LedgerReason | null };
  checked_at: string;
}

interface Locations { districts: { id: string; name_bn: string; name_en: string;
  upazilas: { id: string; name_bn: string; name_en: string;
    mouzas: { id: string; name_bn: string; name_en: string; jl_no: string }[] }[] }[] }

interface SamplePlot { sample_id: string; plot_id: string; scenario: string;
  label_bn: string; label_en: string; expected_verdict: Verdict; request: CheckRequest }

interface PubKey { key_id: string; alg: "Ed25519"; public_key_b64: string }   // base64url, no padding

interface DemoLedger {
  plot_id: string; ok: boolean; broken_at_seq: number | null; reason: LedgerReason | null;
  entries: { seq: number; ts: string; source: SourceName; record_id: string; record_hash: string;
             prev_hash: string; entry_hash: string; status: "ok" | "broken" }[];
  checkpoint: (Checkpoint & { valid: boolean }) | null;
}
```

---

## 7. Canonical JSON, hashing, signing

- `canonical(obj)` = `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`.
- **Ledger entry** (per plot, `seq` starts at 1): fields `{plot_id, seq, ts, source, record_id, record_hash, prev_hash}`. `record_hash` is `"sha256:" + hex` over `canonical(record data)`. `entry_hash` is the same over the entry fields. Genesis `prev_hash` is `"sha256:" + "0"*64`.
- **Checkpoint:** `{plot_id, height, head_hash, ts, key_id}`, signed with Ed25519 over `canonical(...)`. The seed signs one checkpoint per plot. Every legitimate append (add-event) and every issued report signs a fresh one. A report pins the latest checkpoint.
- **Signed payload** (this is what the QR carries): `{v: 1, report_id, short_code, plot_id, verdict, issued_at, valid_until, ledger_height, ledger_head, findings_hash, key_id}`.
  - `findings_hash` = `"sha256:" + hex` over `canonical(findings sorted by (rule_id, evidence))`.
- **`signed_payload_b64`** = base64url (no padding) of `canonical(payload)`. **`signature_b64`** = base64url (no padding) Ed25519 signature over those same bytes.
- **The browser never re-canonicalises.** It decodes `signed_payload_b64` to bytes and runs `nacl.sign.detached.verify(bytes, signature, publicKey)`. Then it parses the bytes as JSON to display fields.
- **QR text** is built by the frontend: `${window.location.origin}/verify#${signed_payload_b64}.${signature_b64}`. The backend never builds it.
- **Short code:** 8 characters from `ABCDEFGHJKMNPQRSTUVWXYZ23456789`, shown as `XXXX-XXXX`.
- **Key id:** `demo-2026-01`. The public key is served at `/api/v1/meta/pubkey`. Library crypto only (`cryptography`, `hashlib`; `tweetnacl` in the browser).

---

## 8. Rules, codes and interfaces

### 8.1 Coverage and verdict

| Question | Required sources |
|---|---|
| Q1 | land_records, mutation |
| Q2 | land_records, registry |
| Q3 | mutation, court |
| Q4 | khas |
| Q5 | bank, registry |
| Q6 | ledger (always checked; COVERED when `ledger.ok`) |

- A source **qualifies** when its status is `OK`, or `NO_RECORD` with maturity ≥ M2 **and** linkage `EXACT`, `TEXT_MATCH` or null. `NO_RECORD` with `PARTY_NAME_ONLY` does **not** qualify, because it means "nothing under these names".
- `STALE`, `PARTIAL`, `UNAVAILABLE` and `ERROR` never qualify. Stale threshold: `as_of` older than 30 days.
- A question is `COVERED` when all required sources qualify, `PARTIAL` when at least one but not all do, and `NOT_COVERED` when none do.
- **Verdict precedence:** any `INTEGRITY` finding → `INTEGRITY_ALERT`; else any `CRITICAL` → `RED`; else any `HIGH` or `MEDIUM` → `AMBER`; else any question not `COVERED` → `GREY`; else `GREEN`. `INFO` and `COVERAGE` findings never create RED or AMBER. **A GREEN verdict with any question not COVERED is a bug.**
- Default source setup unless a plot says otherwise: land_records M3, registry M2, mutation M3, court M2, khas M2, bank M3 with consent given.

### 8.2 Rule catalogue (`rule_id`, tier, severity, params)

| Rule | Tier | Severity | Q | `params` |
|---|---|---|---|---|
| R-OWN-01 | 1 | CRITICAL | Q1 | — |
| R-OWN-02 | 1 | MEDIUM | Q1 | `tier` ("WEAK" or "PROBABLE") |
| R-DISP-01 | 1 | CRITICAL | Q3 | `case_ref`, `court`, `linkage` |
| R-DISP-02 | 1 | MEDIUM | Q3 | `case_ref` |
| R-DISP-03 | 1 | MEDIUM (HIGH when `applicant_is_seller` is false) | Q3 | `mutation_ref`, `applicant_is_seller` |
| R-RES-01 | 1 | CRITICAL | Q4 | `record_ref` |
| R-RES-02 | 1 | CRITICAL | Q4 | `list` ("KA", "KHA" or "ABANDONED"), `record_ref` |
| R-LIEN-01 | 1 | CRITICAL | Q5 | `lien_ref`, `bank_name` |
| R-SALE-01 | 1 | CRITICAL | Q5 | `deed_a`, `deed_b`, `overlap` |
| R-CHAIN-03 | 1 | HIGH (MEDIUM if small) | Q2 | `from_survey`, `to_survey`, `from_area`, `to_area`, `drift_pct` |
| R-CHAIN-04 | 1 | MEDIUM | Q2 | `from_class`, `to_class` |
| R-INT-01 | 1 | INTEGRITY | Q6 | `reason`, `broken_at_seq` |
| R-INT-02 | 1 | COVERAGE | Q6 | `source`, `as_of` |
| R-INT-03 | 1 | COVERAGE | Q6 | `source`, `reason` |
| R-INFO-01 | 1 | INFO | Q1 | — (a STRONG name match: "still confirm NID and father's name") |
| R-INFO-02 | 1 | INFO | Q2 | `depth` (number of generations) |
| R-INFO-03 | 1 | INFO | Q2 | `last_transfer_date` |
| R-OWN-03 | 2 | CRITICAL | Q1 | `seller_share`, `selling_share` |
| R-CHAIN-01 | 2 | HIGH | Q2 | — |
| R-CHAIN-02 | 2 | HIGH | Q2 | `share_sum` |
| R-RES-03 | 2 | CRITICAL | Q4 | `record_ref` |
| R-INT-04 | 2 | HIGH | Q6 | `source_a`, `source_b` |

The frontend must have title, explanation and next-step text (Bangla and English) for **every** rule ID above, Tier 2 included. An unknown `rule_id` must render a safe generic fallback and never crash.

### 8.3 `not_checked[].code` values

| Code | Params | When |
|---|---|---|
| `source_unavailable` | `source`, `reason` | UNAVAILABLE or ERROR |
| `source_stale` | `source`, `as_of` | STALE |
| `source_partial` | `source` | PARTIAL |
| `linkage_party_name_only` | `source` | NO_RECORD with PARTY_NAME_ONLY |
| `low_maturity` | `source`, `maturity` | maturity below M2 |
| `static_physical_possession` | — | always |
| `static_boundaries` | — | always |
| `static_unregistered_agreements` | — | always |
| `static_equitable_mortgage` | — | always |
| `static_seller_documents` | — | always |
| `static_legal_review` | — | always |

### 8.4 Name-match interface (B implements, A calls)

```python
# backend/app/namematch/__init__.py  — OWNED BY B. A ships a stub at S0 with exactly this signature.
def match_name(seller_name: str, seller_father: str | None,
               record_name: str, record_father: str | None) -> dict:
    """Returns {"tier": "STRONG"|"PROBABLE"|"WEAK"|"NONE", "score": float,
                "name_score": float, "father_score": float | None}"""
```
Tier thresholds are in plan v2 B8.4. The engine takes the best tier among the current holders. R-OWN-01 fires on NONE, R-OWN-02 on WEAK or PROBABLE, R-INFO-01 on STRONG.

---

## 9. Golden samples (acceptance tests for BOTH sides)

`/meta/samples` returns exactly these ten entries. A builds the data so each produces exactly this output. B builds fixtures and UI that render exactly this. "Rule IDs" lists non-INFO findings; INFO findings may appear in addition.

| Sample | Scenario | Setup | Verdict | Rule IDs | Coverage |
|---|---|---|---|---|---|
| P-001 | Clean plot | Seller matches record (name and father). All six sources OK; court NO_RECORD with TEXT_MATCH; bank consent given. | GREEN | none | all COVERED |
| P-002 | Seller is not the holder | Different person typed. Everything else clean. | RED | R-OWN-01 | — |
| P-003 | Mortgage + pending mutation | Active lien from the bank; mutation PENDING with applicant ≠ seller. | RED | R-LIEN-01 (CRITICAL), R-DISP-03 (HIGH) | — |
| P-004 | Open title suit | Court returns an OPEN case, TEXT_MATCH. | RED | R-DISP-01 | — |
| P-005 | Khas land | Khas adapter returns a KHAS record. | RED | R-RES-01 | — |
| P-006 | Double sale | Registry has two sale deeds of the same share with overlapping dates. | RED | R-SALE-01 | — |
| P-007 | Area drift + class change | Land records: RS 20.0 decimal → BS 14.5 decimal, class ধান → বাড়ি, no split or conversion record. | AMBER | R-CHAIN-03 (HIGH), R-CHAIN-04 (MEDIUM) | — |
| P-008 | Name variant, no father's name | Typed `মোঃ আব্দুল করিম`; record `মোহাম্মদ আবদুল করিম`. | AMBER | R-OWN-02 (`tier` = PROBABLE) | — |
| P-008B | Same plot, father's name given | As P-008 plus the correct father's name. | GREEN (+ R-INFO-01) | none | all COVERED |
| P-009 | Unknown is not safe | Court NO_RECORD with PARTY_NAME_ONLY; bank UNAVAILABLE (outage). | GREY | R-INT-03 | Q3 PARTIAL, Q5 PARTIAL, rest COVERED |

**P-010 is a demo script, not a plot** (video beat 3 and live demo), built on P-001:
1. Issue a P-001 report R1 (GREEN).
2. `/demo/tamper` `edit_field` → `/check` P-001 returns **INTEGRITY_ALERT**; `/verify` R1 returns INTEGRITY_ALERT.
3. `/demo/reset`. `/demo/add-event` `new_mortgage` → `/verify` R1 returns **GENUINE_SUPERSEDED** with a MORTGAGE diff; a new `/check` is RED (R-LIEN-01).
4. Bonus (the "what stops an admin re-hashing?" answer): `/demo/tamper` `edit_and_rehash` → INTEGRITY_ALERT with reason `checkpoint_mismatch`.

The ten samples, the same ten names and the same expected verdicts must appear in `backend/tests/test_golden.py` (A) and `frontend/src/mocks/samples.json` (B).

---

## 10. Standing rules (both of you, always)

- Synthetic data only: no real NIDs, phone numbers, owners or parcel identifiers. Real district and upazila names are used for realism; mouzas, JL numbers, plots and people are invented. **Ask the organizers to confirm this.** Without a reply, keep the default and the watermark.
- No scraping, no requests to government sites, no testing against live systems.
- No generative AI or ML in the verdict path. Rules are plain deterministic Python.
- Never write "safe", "clean title" or "guaranteed" in any product copy. GREEN says: "No red flags found in the sources we checked. This is not a guarantee."
- Disclaimer on every result screen and on the printable report: advisory only, not a legal opinion, consult a lawyer and inspect the land.
- Log every AI-tool use in your own `docs/ai_usage/*.md` as you go: `date | tool | purpose | files | reviewed by <you>: yes/no`. Both of you must be able to explain every line you committed.
- Real commit history only. Both of you commit daily. No force-push.
- Definition of done for any task: code, tests, bilingual strings (where relevant), reachable from the demo path, committed in your own folder.
