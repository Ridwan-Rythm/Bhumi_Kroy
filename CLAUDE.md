# CLAUDE.md — instructions for any AI session in this repo

1. Read the gitignored file `.whoami` at the repo root. It contains `A` (Ridwan, backend) or `B` (Nazifa, frontend).
2. Read `contracts/00_SHARED_CONTRACT.md` (source of truth) before changing anything.

## Person A (Ridwan) — owned paths
`backend/**` (except the namematch folders) · `contracts/**` · `docs/PLAN.md` · `docs/ARCHITECTURE.md` · `docs/EVALUATION.md` · `docs/backend_notes.md` · `Makefile` · `.github/**` · `.gitignore` · `LICENSE` · `CLAUDE.md` · `docs/ai_usage/ridwan.md`
**Forbidden for A:** `frontend/**` · `README.md` · `docs/concept_note/**` · `docs/slides/**` · `docs/DEMO_SCRIPT.md` · `docs/VIDEO_STORYBOARD.md` · `backend/app/namematch/**` · `backend/tests/namematch/**` · `docs/ai_usage/nazifa.md`

## Person B (Nazifa) — owned paths
`frontend/**` · `README.md` · `docs/concept_note/**` · `docs/slides/**` · `docs/DEMO_SCRIPT.md` · `docs/VIDEO_STORYBOARD.md` · `backend/app/namematch/**` · `backend/tests/namematch/**` · `docs/ai_usage/nazifa.md`
**Forbidden for B:** everything owned by A.

## Standing rules (contract section 10)
- Synthetic data only. No real NIDs, phones, owners or parcels. No requests to government sites.
- No generative AI or ML in the verdict path. Rules are plain deterministic Python. Library crypto only.
- The backend emits language-neutral codes only; all user-visible text lives in the frontend.
- Never write "safe", "clean title" or "guaranteed" in product copy.
- Never rename or remove a contract field, enum value or endpoint. Contract changes are additive, agreed in chat first, commit message `contract: <what>`.
- Log every AI-tool use in your own `docs/ai_usage/*.md`: `date | tool | purpose | files | reviewed by <you>: yes/no`.
- Small commits with the prefix `engine:` (A) or `ui:` (B). No force-push, no history rewriting. Merge PRs with a merge commit.
- Never run a formatter or linter `--fix` outside your own folders.
