# Backend notes (Ridwan)

## Status
Built and verified (125 tests pass, 1 skipped): signer, SQLite layer, deterministic seed (ten golden samples + five Tier-2 extra plots), six adapters, hash-chain ledger with signed checkpoints, title graph, Tier-1 and Tier-2 rules, coverage, verdict, report builder, pipeline, verify service, demo service.

**Not built yet** (needs `fastapi`, `pydantic`, `pytest`, `httpx`, `jsonschema`, `ruff`, which the build sandbox could not install): `app/main.py`, `app/models.py` (pydantic), `app/api/*` routes, `contracts/report.schema.json` export, rate limiting, CORS, HTTP-level tests, `ruff`, real-`pytest` run, `docs/ARCHITECTURE.md`, `docs/EVALUATION.md`, S0 tag `contract-v1`. The routes are meant to be thin wrappers over `app/services/*` and `app/engine/pipeline.run_check`.

Tests are plain functions without fixtures, so they run under `pytest` unchanged. They were run with a small local runner, not pytest itself.

## Decisions to confirm
1. **Services layer.** Route logic lives in `app/services/` (verify, demo) and `app/engine/pipeline.py`, so it is testable without FastAPI. Not in the plan's file list.
2. **UNKNOWN verify state** returns `ledger: {ok:false, broken_at_seq:null, reason:null}` ("not examined"). The contract requires the field but is silent on this case. Frontend: key off `state`, not `ledger.ok`, when `state == UNKNOWN`/`TAMPERED`.
3. **add-event refuses to run on a tampered chain** (`VALIDATION_ERROR`). Otherwise signing a fresh checkpoint over a tampered chain would launder the tamper.
4. **Replay-based Tier-2 rules (R-CHAIN-01, R-OWN-03) only run when land_records, registry and mutation all answered completely.** Found by a test: with the registry down, R-CHAIN-01 reported a missing deed as a broken chain on a clean plot.
5. **Adapter `as_of` is relative to "now"** (`as_of_age_days` in adapter config, default 1), so seeded data does not go stale as real time passes and the demo clock shift (`/demo/clock`) works.
6. **Q4 depends only on khas**, so a stale khas gives `NOT_COVERED` (not `PARTIAL`), per the 8.1 rule.
7. **Ledger replay sets `height_mismatch`** also when the newest entry is deleted (chain still links, checkpoint is ahead).
8. Mouza names and JL numbers are invented; a name may coincide with a real village. District/upazila are real.

## Waiting on Nazifa
`app/namematch` is the stub (`IS_STUB = True`; exact-string match only). `P-008` and `P-008B` are skipped until the real matcher lands; an engine-wiring test with a fake matcher already checks that PROBABLE gives AMBER+R-OWN-02 and STRONG gives GREEN+R-INFO-01.

## Performance
`python scripts/bench.py`: p50 ≈ 254 ms, p95 ≈ 256 ms over 50 runs (adapter latency is simulated 120-250 ms, in parallel).
