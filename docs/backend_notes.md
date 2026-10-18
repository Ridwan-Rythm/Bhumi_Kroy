# Backend notes (Ridwan)

## Status
Built and verified: **161 backend tests pass (1 skipped), `ruff check backend` is clean**. Signer, SQLite layer, deterministic seed (ten golden samples + five Tier-2 extra plots), six adapters, hash-chain ledger with signed checkpoints, title graph, Tier-1 and Tier-2 rules, coverage, verdict, report builder, pipeline, verify and demo services, **and the HTTP layer**: `app/main.py`, `app/api/routes.py`, `app/api/ratelimit.py` (30 requests/min per IP on /check and /verify, shared), CORS for the two Vite dev origins (plus `CORS_ORIGINS`), contract-shaped errors for every failure including unexpected crashes, `app/models.py` (pydantic, derived from contract section 6) and `contracts/report.schema.json` (generated, checked in CI).

Still open: `docs/ARCHITECTURE.md`, `docs/EVALUATION.md`, the real name matcher (Nazifa), the `contract-v1` tag (needs the original history, see below).

Commands: `make setup`, `make backend`, `make test`, `make check` (what CI runs), `make schema` (rewrite report.schema.json), `make mocks` (rewrite the frontend fixtures from the real API).

## Review findings fixed (second review)
- **Rolled-back ledger** (delete the newest entry and its checkpoints): `verify` now compares the report's pinned `ledger_height` with the chain. Higher than the current height gives `INTEGRITY_ALERT` with reason `height_mismatch`.
- **`ledger_head` is checked**: the entry hash at the pinned height must equal the signed `ledger_head`, otherwise `INTEGRITY_ALERT` / `checkpoint_mismatch` (history replaced, e.g. reloaded from a different seed).
- **Consequence to know about:** a report issued *after* `/demo/add-event` and verified *after* `/demo/reset` is now an `INTEGRITY_ALERT`, because the entry it pinned no longer exists. Reports issued before the add-event are unaffected, so the P-010 script still works. This is the honest answer for a ledger that went backwards.
- Malformed `consents` (`[1]`, `"yes"`, `[]`), a non-string `father_or_husband` and a list-valued `survey` give `VALIDATION_ERROR`, never a 500.
- Short codes must be exactly 8 characters from the alphabet (one hyphen or space in the middle is fine). Other characters are no longer dropped silently; a malformed code is `UNKNOWN`.
- `report_id` is MAX+1 per year and the INSERT retries on a primary-key clash, so two writers cannot both issue the same id.
- The signing key file is created 0600 in a 0700 folder; an older, looser file is tightened on load.
- `tests/test_hardening.py` covers all of these; `test_samples_json_matches_the_builder` fails if `seed/golden/samples.json` is stale.

## Decisions to confirm
1. **Services layer.** Route logic lives in `app/services/` (verify, demo) and `app/engine/pipeline.py`, so it is testable without FastAPI. Not in the plan's file list.
2. **UNKNOWN verify state** returns `ledger: {ok:false, broken_at_seq:null, reason:null}` ("not examined"). The contract requires the field but is silent on this case. Frontend: key off `state`, not `ledger.ok`, when `state == UNKNOWN`/`TAMPERED`.
3. **add-event refuses to run on a tampered chain** (`VALIDATION_ERROR`). Otherwise signing a fresh checkpoint over a tampered chain would launder the tamper.
4. **Replay-based Tier-2 rules (R-CHAIN-01, R-OWN-03) only run when land_records, registry and mutation all answered completely.** Found by a test: with the registry down, R-CHAIN-01 reported a missing deed as a broken chain on a clean plot.
5. **Adapter `as_of` is relative to "now"** (`as_of_age_days` in adapter config, default 1), so seeded data does not go stale as real time passes and the demo clock shift (`/demo/clock`) works.
6. **Q4 depends only on khas**, so a stale khas gives `NOT_COVERED` (not `PARTIAL`), per the 8.1 rule.
7. **Ledger replay sets `height_mismatch`** also when the newest entry is deleted (chain still links, checkpoint is ahead). `verify` also uses `height_mismatch` when a report pins a height above the current one.
8. Mouza names and JL numbers are invented; a name may coincide with a real village. District/upazila are real.

## Waiting on Nazifa
`app/namematch` is the stub (`IS_STUB = True`; exact-string match only). `P-008` and `P-008B` are skipped until the real matcher lands; an engine-wiring test with a fake matcher already checks that PROBABLE gives AMBER+R-OWN-02 and STRONG gives GREEN+R-INFO-01.

## Performance
`python scripts/bench.py`: p50 ≈ 254 ms, p95 ≈ 256 ms over 50 runs (adapter latency is simulated 120-250 ms, in parallel).

## Mock fixtures
`frontend/src/mocks/*.json` are generated from the real API by `python -m scripts.export_mocks` (frozen clock, seeded short codes, the same throwaway key as `contracts/fixtures/signed_sample*.json`). CI regenerates them and fails if they differ from what is committed. One honest exception: because `app/namematch` is still the stub, **P-008 and P-008B only** use a two-line stand-in matcher (PROBABLE without a father's name, STRONG with one). Everything else about those two reports is real engine output.

## Git history
The first upload to this repository was two "Add files via upload" commits. The `engine:` commits from the original work are not in it. History must not be rewritten: push the original `feat/engine` branch (or merge it), and tag `contract-v1` on the commit that holds the contract and `report.schema.json`.
