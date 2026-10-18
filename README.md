# Bhumi_Kroy

**Check before you buy.** A bilingual (Bangla / English) web prototype for the LandTech 2026 Innovation Hackathon, Problem 5.
A buyer enters a plot and the seller's name. Bhumi_Kroy asks six source adapters, runs deterministic rules, and answers
with a verdict, **what it found, what it could not check, and what to ask next**. The report is signed (Ed25519), time-limited
and carries a QR code that anyone can verify, backed by a hash-chained, tamper-evident ledger of the underlying records.

> **All data is synthetic.** No real NID, phone number, owner or parcel is used. District and upazila names are real for realism;
> mouzas, JL numbers, plots and people are invented. Every result screen and the printable report show
> "SYNTHETIC — NOT A REAL LAND RECORD". No scraping, no calls to government systems, no generative AI in the verdict path.

## Run it

Requirements: Python 3.12, Node 22.

```bash
git clone <repo-url>
cd Bhumi_Kroy
make setup     # installs backend (pip) and frontend (npm ci) dependencies
```

Open **two terminals** from the repo root.

**Terminal 1: backend** (http://localhost:8000)

```bash
make backend
```

**Terminal 2: frontend** (http://localhost:5173, Vite proxies `/api` and `/demo` to port 8000)

```bash
make frontend
```

The backend seeds the demo data itself on first start. To re-seed manually, run `make seed`.

`DEMO_MODE=1` enables the `/demo/*` endpoints. `make backend` sets it for you.

### Without `make` (Windows PowerShell)

```powershell
# one-time setup
pip install -r backend/requirements-dev.txt
cd frontend; npm ci; cd ..

# terminal 1
cd backend
$env:DEMO_MODE = "1"
python -m uvicorn app.main:app --port 8000

# terminal 2
cd frontend
npm run dev
```

### Without `make` (macOS / Linux)

```bash
# terminal 1
cd backend && DEMO_MODE=1 python -m uvicorn app.main:app --port 8000

# terminal 2
cd frontend && npm run dev
```

No backend? `VITE_USE_MOCK=1 make frontend` serves saved responses from `frontend/src/mocks/` (a yellow banner says so).

| Command | What it does |
|---|---|
| `make test` | backend pytest + frontend vitest |
| `make lint` | `ruff check backend` + `eslint` |
| `make check` | everything CI runs (lint, tests, build, schema and contract checks) |
| `make schema` | rewrite `contracts/report.schema.json` from the pydantic models |
| `make mocks` | rewrite the frontend fixtures from the real API |
| `make reset` | delete and re-seed the database |

Environment (backend): `DEMO_MODE=1`, `DB_PATH` (default `backend/data/landcheck.db`), `SIGNING_KEY_B64` (optional; otherwise a key is
generated into `backend/.keys/`, which is git-ignored), `CORS_ORIGINS`, `RATE_LIMIT_PER_MIN` (default 30).

## What it answers

Six questions, each tied to the sources that can answer it. A question is only "checked" when every source it needs answered properly.

| | Question | Sources |
|---|---|---|
| Q1 | Is the seller the owner? | land records, mutation |
| Q2 | Is the chain of ownership consistent? | land records, registry |
| Q3 | Is there a court case or pending mutation? | mutation, court |
| Q4 | Is it government khas / vested land? | khas lists |
| Q5 | Is there a mortgage or double sale? | bank, registry |
| Q6 | Is the record history intact? | the ledger |

Verdict order: any integrity failure → **INTEGRITY_ALERT**; else any critical finding → **RED**; else any high or medium → **AMBER**;
else any question not fully checked → **GREY**; else **GREEN** ("No red flags found in the sources we checked. This is not a guarantee.").
A GREEN with an unchecked question is a bug and is tested for. The report always lists **what we did not check**.

## The data

`backend/seed/` builds a deterministic synthetic world: districts and upazilas (real names), invented mouzas, 9 plots with ownership
histories, six mock sources (land records, registry, mutation, court, khas, bank) and the ledger. Ten **golden samples**
(`backend/seed/golden/samples.json`: P-001 … P-009, plus P-008B, which is P-008 with the father's name filled in) cover green, grey,
amber and red outcomes. **P-010** is not a plot but the scripted tamper-versus-legitimate-update demo, run on P-001
(`/demo/tamper`, `/demo/reset`, `/demo/add-event`). The builder is a script, so the same seed always gives the same data.

## Layout

```
backend/    FastAPI app, engine (rules, verdict), adapters, ledger, seed, tests      (Ridwan)
frontend/   React + Vite + Tailwind, react-i18next (bn default), mocks, tests         (Nazifa)
contracts/  00_SHARED_CONTRACT.md, report.schema.json, signed sample fixtures
docs/       PLAN.md, backend_notes.md, ai_usage/
```

API summary (`/api/v1`): `GET /health`, `/meta/locations`, `/meta/samples`, `/meta/pubkey`; `POST /check`, `/verify`; `GET /reports/{id}`.
Demo (only with `DEMO_MODE=1`, outside `/api/v1`): `POST /demo/tamper`, `/demo/add-event`, `/demo/reset`, `/demo/clock`; `GET /demo/ledger/{plot_id}`.
Every error is `{"error": {"code", "message", "field"}}`. Full details are in `contracts/00_SHARED_CONTRACT.md`.

## Known limits (honest list)

- `backend/app/namematch` is still a stub (exact match only). P-008 and P-008B are skipped in the backend tests until the real matcher
  lands; their frontend fixtures use a labelled stand-in.
- The `replace_entry` and `replay_checkpoint` demo tamper kinds answer `NOT_IMPLEMENTED`.
- Bangla text in `frontend/src/i18n/bn.json` has not yet been read by a native speaker; every string is listed in `frontend/src/i18n/REVIEW.md`.
- Rate limiting is in memory (one process). The key file is local; there is no hosted instance.

## AI tools used

Claude (Anthropic, claude.ai) was used for code, tests and documentation. Every use is logged with files and review status in
`docs/ai_usage/ridwan.md` and `docs/ai_usage/nazifa.md`. The verdict path contains no AI or ML: rules are plain deterministic Python.
