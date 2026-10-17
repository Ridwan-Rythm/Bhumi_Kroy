# LandTech 2026 — “Check Before You Buy” (P5) · Plan v2

**Track:** Digital Land Records, Verification & Digitization
**Team:** Abu Ridwan Siddique · Nazifa Rahman
**Version:** v2 — upgrade of `landtech_p5_plan.md` · 16 Oct 2026
**Working name (optional):** যাচাই (*Jachai*) · tagline: কেনার আগে যাচাই করুন

> **How to read this file**
> - **Part A** — an honest review of v1: ranked drawbacks and what changed (10-minute read).
> - **Part B** — the upgraded plan. Copy it into `docs/PLAN.md` in your repo (delete Part A first if you like).
> - **Short on time?** Read the Part A table → B0 (first 48 hours) → B5 (scope) → B17 (work plan).
> - **Tags:** **[VERIFIED]** = backed by a public source listed in Appendix D · **[ASSUMPTION Ax]** = general knowledge or inference, to be validated with mentors/lawyers (list in B19) · **[DECISION]** = a choice this plan makes; change it deliberately, not by drift.
> - Bangla wording in this file is a *sketch*. Have a native speaker, and ideally a lawyer, review it before it goes into the product or the video.

## Contents

**Part A — Review of v1:** A1 Verdict · A2 Drawbacks, ranked · A3 What changed
**Part B — Upgraded plan:** B0 First 48 hours · B1 Summary · B2 Problem and evidence · B3 Positioning · B4 Trust model · B5 Scope · B6 Domain model · B7 Source adapters · B8 Verification engine · B9 Report and verification · B10 Architecture and tech decisions · B11 Security, privacy, ethics · B12 UX · B13 Synthetic data and evaluation · B14 Demo plan · B15 Pitch and Q&A · B16 Concept note · B17 Work plan · B18 Risks · B19 Assumptions and validation · B20 Roadmap · B21 Rulebook and submission checklist · Appendices A–D

---

# PART A — Review of v1

## A1. Verdict

v1 is a strong **problem analysis**. The five buyer questions as a feature filter, the traceability table, the “what we did not check” idea, the fraud scenarios doubling as test cases, and the rulebook checklist are all genuinely good and are kept.

v1 is a weaker **delivery plan**. It has no schedule, too many features for two people, a few technical claims a sharp judge can puncture with one question, and a land-records model that is simpler than real Bangladeshi records.

**If you fix only three things:**
1. Cut scope to a spine you can finish, and put dates on it (B5, B17).
2. Rewrite the trust story: signed checkpoints, append-only updates, honest limits (B4).
3. Make “unknown” a first-class state in code, not just a sentence in the UI (B7, B8).

## A2. Drawbacks in v1, ranked

| # | Drawback in v1 | Why it matters | Severity | Fixed in |
|---|---|---|---|---|
| 1 | No timeline, owners or cut-line. 13 features + 16 FRs + 6 adapters + generator + admin panel + PDF/QR/signature + bilingual UI + tests + video + note + slides, for two people. | The most likely failure is “everything 70% done” and a broken demo. | Critical | B5, B17 |
| 2 | The hash chain is oversold. Anyone who can write to the database can recompute the whole chain; a chain proves nothing unless its head is signed or anchored by someone the attacker doesn't control. | The first sharp judge question (“what stops the admin from re-hashing?”) has no answer in v1. | Critical | B4, B14 |
| 3 | False comfort survives in the logic. Nothing in v1 separates “the source says no problem” from “the source didn't answer / is stale / can't see this kind of record”. | Your own stated risk (“no problem found can mean nothing was checked”) is solved in wording only, not in code. | Critical | B7, B8 |
| 4 | The “ownership chain” is linear and built from CS/SA/RS/BS khatians only. | Real records have dag renumbering and splits between surveys, shares that fragment through inheritance, and a *mutated khatian* as the current record. Without lineage and share arithmetic the mismatch rules produce noise. | High | B6 |
| 5 | Rules are too blunt: “name differs → Critical”, “2+ deeds → Critical”, “open case → Critical”. | False alarms (spelling variants, legitimate A→B→C sales, cases about the owner rather than the land) and missed fraud (partial overlapping sales). | High | B8 |
| 6 | Court and bank sources are modelled too cleanly. | Public court tools search by case number, party or advocate name, not by plot; bank collateral data is confidential and equitable mortgages may leave no public record. A mock that returns “cases linked to this plot” hides the hardest real step. | High | B7 |
| 7 | Bangla name matching is named as hard but never designed. | Q1 (“is the seller the owner?”) is the headline question and depends on it. | High | B8.4 |
| 8 | No validity period or supersession. | A “clean” report from today gets waved around next month. | High | B9 |
| 9 | The QR can be spoofed: a fake report can carry a QR to a lookalike site. | The verify page is only as trustworthy as the address the user lands on. | High | B9 |
| 10 | The admin panel edits records in place. | It contradicts append-only integrity and is a public attack surface. The demo needs a *tamper simulator* plus a *legitimate update*, to show the system tells them apart. | High | B14 |
| 11 | Bangla PDF generation is not planned. | Many Python PDF stacks do not shape Bengali conjuncts correctly by default. Discovering that on the last night kills the “signed Bangla report” beat. | High | B10.5 |
| 12 | No positioning against what already exists: e-Porcha, e-Mutation (already issues a QR-code-based DCR), registry–land-office coordination, the 2026 e-registration ordinance, court cause lists. | Mentors and judges from government will ask “how is this different?”. | Medium | B3 |
| 13 | Overlap with P3 (fraud / double-selling) and document-verification entries. | Public repos show other teams building chain and double-sale engines. If chain detection is your centrepiece you look like “P3-lite”. | Medium | B1, B3 |
| 14 | The “Digitization” half of the track is invisible. | The track is *Verification & Digitization*; v1 shows only verification. | Medium | B7.3, B5 |
| 15 | Flags come without next steps. | A low-literacy buyer is left stuck. “What do I do now?” is the strongest differentiator you can add cheaply. | Medium | B8.5 |
| 16 | No evaluation evidence. “Unit tests for the rules” is not proof. | Your generator knows the ground truth, so you can report precision/recall per fraud scenario. | Medium | B13 |
| 17 | Thin privacy and abuse model. “Synthetic data only” protects the hackathon, not the design. | A tool that reveals owner/case/lien data can help fraudsters pick targets or tune forged identities. | Medium | B11 |
| 18 | “Do not proceed” and green “safe” wording edges toward legal advice. | Needs action-oriented language plus coverage and validity on every verdict. | Medium | B8.2, B12 |
| 19 | “Both must explain every line of code” has no process behind it. | If AI tools help write code, you need an AI log, module ownership and teach-back sessions from day 1. | Medium | B17 |
| 20 | Smaller items: FR13/FR14 overlap; “about 2 seconds” is meaningless on mock data; SQLite vs PostgreSQL undecided; no hosting or fallback for the live demo; assumptions listed with no plan to retire them. | Cheap to fix, embarrassing if missed. | Low | B10, B17, B19 |

## A3. What changed

**Kept:** five buyer questions as the feature filter (plus a sixth, the trust question); traceability; rule-based engine; “what we did not check”; mock adapters with seeded synthetic data; signed report with QR; Bangla/English UI; rulebook checklist.

**Changed:**
- Verdict: three colours → four states plus an integrity alert, and the verdict is coverage-aware.
- Hash chain → append-only ledger with signed checkpoints, with its limits stated openly.
- “Ownership chain” → title graph with share arithmetic and plot lineage.
- Admin panel → demo-only tamper simulator and a legitimate “add event” tool.
- Adapters → one contract with tri-state status, freshness, maturity tier and linkage confidence.
- 13 features / 16 FRs → MoSCoW scope and 21 prioritised FRs.
- “About 2 seconds” → per-source timeouts and a p95 target on simulated latency.

**Added:** positioning, evidence, first-48-hours list, work plan with roles, threat model, evaluation harness, golden plots, video storyboard, pitch and Q&A prep, concept-note outline, risk register, validation plan, roadmap, glossary, examples.

**Cut or deferred:** PostgreSQL option; separate mock *services* (in-process adapters plus one HTTP example instead); PAdES/CCA certificates, ML, and OCR (moved to Could/Won't); detailed scalability claims (one line instead); rate limiting as a functional requirement (kept as a basic NFR).

---

# PART B — Upgraded plan

## B0. First 48 hours (before any feature code)

1. **Ask the organizers** (list in B21): judging rubric, deadlines per stage, submission formats, whether a hosted demo URL is expected.
2. **Send the mentor questions** (B19). Answers change rules, not architecture, so you can build in parallel.
3. **Repo hygiene on day 1:** public repo, CI (tests + lint), `AI_USAGE.md`, commit rules (B17). Both of you commit from the first hour.
4. **Three one-hour spikes.** Each can kill the demo if left late:
   - Bangla PDF: render a page with conjunct-heavy text and digits and check it in two PDF viewers (B10.5).
   - Signing: Ed25519 sign → QR → verify in the browser (B9.3).
   - Name matching: NFC plus normalisation on 20 variant pairs (B8.4).
5. **Freeze scope** with the MoSCoW list (B5). Anything not in Must is a gift, not a plan.
6. **Write the 10 golden plots** (B14) *before* the generator. They are your acceptance tests, your demo and your video.
7. **Define the adapter contract** (B7.1) and stub all six adapters with fixed data. Build the vertical slice on the stubs.

## B1. Summary

**One-liner:** before you pay for land, get one honest, verifiable answer to “Is it safe to buy this plot from this person?” — with proof of what was checked, what was not, and how long the answer stays valid.

**Problem in two sentences:** the facts that decide whether a purchase is safe (owner and share, chain of title, mutation, cases, restrictions, mortgage, prior sales) sit in different offices with no buyer-facing combined answer. Fraud usually surfaces after payment and becomes years of litigation (evidence in B2).

**Users:** primary — a private buyer and their family. Later — lawyers, banks and sub-registrars/AC (Land) using the same engine.

**What we build:** a mobile-first Bangla/English web app; a FastAPI backend with a rule engine; six mock source adapters on seeded synthetic data; an append-only ledger with signed checkpoints; a signed, time-limited report (PDF + QR) with a public verification page; a demo console.

**Six things that make it different:**
1. **Buyer-first.** Five land questions plus one trust question; every feature maps to one of them.
2. **Honest by construction.** Tri-state source results and a coverage-aware verdict; “what we did not check” is generated from data, not hard-coded text.
3. **Explainable.** Every finding = rule ID + source record + plain-Bangla explanation + a concrete next step.
4. **Verifiable.** The report is signed and time-limited; the verify page tells *genuine* from *superseded*, *expired* and *tampered*.
5. **Rollout-ready.** One adapter contract plus data-maturity tiers; each mock maps one-to-one to a real government system (B7.4).
6. **Measured.** A synthetic benchmark with injected fraud and reported precision/recall (B13).

**Demo, four beats:** clean plot → risky plot in Bangla → tamper vs legitimate update → QR verify on a phone.

**What we do not claim:** legal advice; that source data is true; a substitute for a lawyer or a site visit; any use of real data.

## B2. Problem and evidence

**Why it matters in Bangladesh** (use in the concept note; open each source and confirm dates before citing):
- **[VERIFIED]** Courts had 4,516,603 pending cases at 31 Dec 2024, up from 1,789,914 in 2008. A senior secretary of the Ministry of Land has said almost 80% of cases are land-related; other sources put the share at roughly 70–75%. Write “roughly 70–80% depending on the source”.
- **[VERIFIED, date unchecked]** A household survey reported by The Daily Star found one in seven households involved in a land dispute, an average pending time of about 8 years, and a total cost around 45% of annual household income. Confirm the survey year before using it.
- **[VERIFIED]** Named drivers of land disputes include inheritance conflicts, forged documents, illegal occupation and defective surveys.

**The buyer's questions** (every feature must answer one; anything that doesn't gets cut):

| Q | Question |
|---|---|
| Q1 | Is the seller the real owner, and with what share? |
| Q2 | Is the chain of ownership clean, with no gaps or mismatches? |
| Q3 | Is there a pending mutation, court case or dispute? |
| Q4 | Is the land restricted (khas, vested/abandoned, acquisition, other)? |
| Q5 | Is it already mortgaged, or sold to someone else? |
| Q6 | **New:** Is this answer genuine, complete and still current? |

**How buyers check today [VERIFIED — Daily Star and Financial Express guides]:** search the Sub-Registry for deeds (at least 10 years back); get the khatian/porcha from the land office; check certificate cases and auctions at the tahsil/upazila land office; check khas, abandoned and acquisition status at the tahsil, the land-acquisition branch or the DC office; get the latest registration information from the sub-registry or district registrar; check land-tax receipts; remember that mutation is needed before title can be transferred. That is visits to three or four offices, each with its own format.

**Why it is hard** (v1's list, plus new items in bold):
- Fragmented sources; inconsistent records across generations; Bangla spelling variants; fake paper; low digital literacy; false comfort.
- **Time of check vs time of payment:** things change between the report and registration day.
- **Case-to-plot linkage:** court tools index by case number and party names, not by plot [A5].
- **Unrecorded encumbrances:** equitable mortgages and unregistered agreements may be invisible to every source [A6].
- **A system in transition:** e-registration and Smart Mutation are arriving, so adapters must be swappable.

## B3. Positioning — what exists and where we fit

| System | What it already does | Gap for a buyer | Our relation |
|---|---|---|---|
| e-Porcha / DLRMS (Ministry of Land) | Online khatian/porcha copies; the ministry reported 55M+ ownership records online in 2023 **[VERIFIED]** | One office's record; no cross-check against deeds, cases, liens or restrictions | Source → Land Records adapter |
| e-Mutation (Ministry of Land) | Online mutation, cashless since Oct 2022, QR-code-based online DCR, UN Public Service Award 2020 (time cut from 60 to 28 days); “Smart Mutation” announced as its successor (status unverified) **[VERIFIED]** | Shows mutation status, not whether the seller can legitimately sell | Source → Mutation adapter |
| Registry–land-office coordination (Law + Land ministries, a2i) | Cabinet approved automatic mutation after registration (target about 8 days); sub-registries verify the record of rights through a land services gateway; LT notice flows to AC (Land) **[VERIFIED]** | Checks the record at registration time; a buyer gets no pre-payment, multi-source answer | Source → Registry adapter; later, our checks at the registrar's desk |
| e-Registration (Registration (Amendment) Ordinance 2026) | Legal basis for electronic deed presentation and registration; gift declarations brought into registration **[VERIFIED]** | Rollout and coverage unknown; will make deed data structured | Registry adapter matures from M2 to M3/M4 |
| Court cause lists and Amar Adalat app | Online cause lists; case search by case number, party, advocate **[VERIFIED]** | No plot-level index found **[A5]** | Source → Court adapter, with linkage confidence |
| Gazette lists and DC office (vested “Ka/Kha”, abandoned, khas, acquisition) | Legal lists that buyers are told to check at the DC office or land-acquisition branch **[VERIFIED]** | Paper or gazette form; manual lookup | Source → DC/Khas adapter |

**The gap we fill:** no single buyer-facing service combines these sources, cross-checks them, says plainly what it could not see, and hands back an answer you can verify.

**Our stance:** a **verification layer on top of existing systems**. We do not replace e-Porcha or e-Mutation; they are our future adapters.

**Adjacent LandTech 2026 entries.** Public repos show other teams on P3 (officer-facing title-chain and double-selling detection) and on AI-based document verification. Expect judges to have seen chain-detection demos. Do not make that your centrepiece. Lead with the buyer-facing aggregation, coverage honesty, next steps and the verifiable report. Use the chain checks as *inputs* to the report, not as the product's identity. Don't reuse their code or ideas; just know the landscape.

## B4. Trust model — what the signature proves, and what it doesn't

### B4.1 Four layers

```
Source systems (not ours; can be wrong or stale)
   │  adapters snapshot what each source said, and when
   ▼
Ledger — append-only, hash-linked, signed checkpoints     → integrity of OUR STORED COPY
   │  deterministic rule engine
   ▼
Findings + coverage + verdict
   │  canonicalise → sign (Ed25519)
   ▼
Report — time-limited, QR-verifiable                      → integrity of THE ANSWER
```

### B4.2 Claims we can and cannot make

| Claim | Can we prove it? | How |
|---|---|---|
| This report was issued by us and is unaltered | Yes | Signature over the canonical report |
| The source snapshots haven't been altered since we stored them | Yes, unless the attacker also holds the signing key | Hash links plus a signed checkpoint |
| The source data is true | No | We show provenance, freshness and cross-source conflicts |
| Nothing changed after the check | No | Validity window; later changes make the report “superseded” |
| The plot is safe to buy | Never claim this | Advisory wording only |

### B4.3 Ledger rules

- Entry = `{seq, ts, source, record_id, record_hash, prev_hash, entry_hash}`. Hashes are SHA-256 over canonical JSON (sorted keys, UTF-8, no extra whitespace).
- **Nothing is edited.** A correction or new fact is a *new* entry that references the one it supersedes.
- Every N entries, and every time a report is issued, the ledger authority signs a **checkpoint** `{height, head_hash, ts}`. A report pins the checkpoint it was built on.
- **The database is untrusted; the signing key is the root of trust.** The key lives outside the DB (an env secret in the prototype). Someone who edits rows cannot produce a valid checkpoint, so verification fails. Someone who also steals the key can. Say this out loud in the pitch.
- Production direction **[A8]:** key custody under the government authority (HSM, CCA-licensed certificate), key rotation plus a revocation list, and periodic public anchoring of checkpoint hashes so even the authority cannot quietly rewrite history. These are roadmap items, not hackathon scope.

### B4.4 Limits to state on a slide

Key compromise defeats the scheme. Garbage in, garbage out. The ledger gives *detection*, not prevention. In the prototype the signing authority is us; in a real deployment it would have to be the government.

## B5. Scope

### B5.1 MoSCoW

**Must — the spine. Nothing else starts until one plot runs end-to-end.**
- **M1** Guided plot search: cascading location, khatian and dag numbers (Bangla or ASCII digits), sample-plot picker.
- **M2** Six mock adapters on one contract (in-process; one also exposed over HTTP to prove pluggability).
- **M3** Title graph with share and area invariants (B6.2).
- **M4** The 18 Must rules (B8.3), coverage-aware verdict, generated “not checked” list.
- **M5** Result UI: verdict banner, six-question scorecard, findings with rule + source + next step, ownership timeline.
- **M6** Signed report (JSON plus Bangla/English PDF), QR, verify page with at least four states.
- **M7** Ledger with signed checkpoints, tamper simulator, legitimate-update demo.
- **M8** Synthetic generator: 10 golden plots plus an injected-fraud mode.
- **M9** Tests (rules, name match, ledger, verdict, scenarios), README, `AI_USAGE.md`.

**Should — only after Gate 2 (B17):**
- Name matching level 2 (phonetic); validity and supersession with a “what changed” diff; offline-verifiable QR payload; evaluation harness and a results slide; share-as-text for WhatsApp/Messenger; glossary tooltips; Docker Compose plus a hosted demo; chain-of-blocks visual on the verify page.

**Could — gifts, not promises:**
- Seller-document check: upload a photo of the seller's porcha, extract its fields, compare with the record. This doubles as your visible “digitization” feature.
- Pre-recorded Bangla audio of the verdict; PWA/offline shell; officer “pre-registration” view; Merkle-tree checkpoints.

**Won't (this round):**
- Real integrations or scraping (rulebook); ML in the verdict path; PAdES or CCA certificates; payments or escrow; user accounts beyond the demo; nationwide data.

### B5.2 Functional requirements

| ID | Requirement | Pri | Q |
|---|---|---|---|
| FR1 | Search a plot by identifiers; accept Bangla and ASCII digits; cascading location dropdowns | Must | all |
| FR2 | Show current record holder(s) and shares from the latest mutated khatian | Must | Q1 |
| FR3 | Build the title graph across survey generations, including dag lineage | Must | Q2 |
| FR4 | Show mutation history and status, including the deed-registered-but-not-mutated lag | Must | Q3 |
| FR5 | Flag court cases with linkage confidence (EXACT / TEXT_MATCH / PARTY_NAME_ONLY) | Must | Q3 |
| FR6 | Flag restrictions: khas, vested/abandoned, acquisition (more in B6.4) | Must | Q4 |
| FR7 | Flag active and duplicate mortgages | Must | Q5 |
| FR8 | Detect overlapping sales of the same share or area | Must | Q5 |
| FR9 | Detect cross-record mismatches: area (unit-normalised), owner, land class | Must | Q2 |
| FR10 | Apply rules → findings with severity and confidence → coverage-aware verdict | Must | all |
| FR11 | Every finding shows rule ID, source record reference, plain explanation and next step | Must | all |
| FR12 | Show each source's status (OK / NO_RECORD / PARTIAL / STALE / UNAVAILABLE / ERROR), freshness and maturity | Must | Q6 |
| FR13 | Generate “What we did not check” from coverage plus a static out-of-scope list | Must | Q6 |
| FR14 | Issue a signed report (JSON + PDF) with QR, short code and validity window | Must | Q6 |
| FR15 | Verify page: genuine / expired / superseded / tampered / unknown | Must | Q6 |
| FR16 | Verify ledger integrity on every query; an integrity failure overrides the verdict | Must | Q6 |
| FR17 | Bangla and English UI and report | Must | all |
| FR18 | Demo console (tamper simulator, add-event, reset) behind `DEMO_MODE` | Must | demo |
| FR19 | Seller-name matching with tiers (level 1 Must, level 2 Should) | Must / Should | Q1 |
| FR20 | Evaluation harness: injected-fraud benchmark and metrics | Should | — |
| FR21 | Seller-document check (upload, extract, compare) | Could | Q1, Q2 |

### B5.3 Non-functional requirements (measurable)

| Area | Target |
|---|---|
| Integrity | Every issued report verifies. Six tamper types are detected: edit a field, delete an entry, reorder entries, replace an entry, replay an old checkpoint, swap the signature |
| Honesty | No GREEN verdict while any question lacks an OK, clear source (covered by a test) |
| Explainability | 100% of findings carry rule ID, source reference, explanation and next step |
| Performance | p95 report time ≤ 2.5 s with simulated 100–800 ms adapter latency; 1.5 s per-source timeout; per-source progress visible in the UI |
| Usability | Mobile-first (360 px); initial JS ≤ about 200 KB gzipped; usable on throttled 3G; five non-technical readers can state the verdict and next step within 20 seconds |
| Accuracy (synthetic) | ≥ 95% detection on injected defects and ≤ 5% false positives on clean plots (report the actual numbers) |
| Privacy | Synthetic data only; “SYNTHETIC — NOT A REAL LAND RECORD” watermark on UI and PDF; masked personal details |
| Reliability | Seeded data; golden plots produce identical verdicts in CI |
| Maintainability | ≥ 80% line coverage on engine modules; every rule has a fires test, a does-not-fire test and an edge test; README covers setup, data and AI tools |
| Accessibility | Status never conveyed by colour alone; Bangla-digit option; tap targets ≥ 44 px |
| Legal safety | Advisory disclaimer on every verdict screen and on the PDF |

## B6. Domain model — Bangladesh specifics

### B6.1 How a plot is identified

- **Location path:** Division → District → Upazila (or metropolitan thana) → Union/Ward → Mouza. Same-named mouzas exist, and a mouza is usually pinned by its **JL number** within the district **[A2]**.
- **Per survey generation** — CS (Cadastral Survey), SA (State Acquisition), RS (Revisional Survey), BS (Bangladesh Survey), plus city surveys where they apply — a plot has a **dag no.** and sits in a **khatian no.**. Both are unique only *within mouza and survey*.
- **Dag numbers change between surveys** (renumbering, splits, merges). The model needs a **plot lineage** edge list (`dag_old → dag_new`, kind = RENUMBER / SPLIT / MERGE). Without it, “history across generations” is guesswork **[A3]**.
- **Current ownership evidence** is normally the latest **mutated khatian** (porcha) plus land-development-tax records. Survey khatians are the *roots* of the chain, not the present state **[A1]**.
- **Registration → mutation flow [VERIFIED]:** a registered deed triggers a Land Transfer (LT) notice from the Sub-Registry to the AC (Land). Under the 2020 cabinet decision, mutation should follow automatically within about eight days in integrated upazilas; otherwise the buyer applies through e-Mutation. So **“deed registered but no mutation after N days”** is a meaningful signal (R-DISP-05); N must be validated **[A7]**.

### B6.2 Title graph

Model ownership as **events replayed over a plot**, not as a list of khatians.

- **Event types:** SURVEY_ENTRY, SALE, GIFT, INHERITANCE, PARTITION, COURT_DECREE, ACQUISITION, MORTGAGE, MORTGAGE_RELEASE, LT_NOTICE, MUTATION_PENDING, MUTATION_APPLIED.
- Replaying events gives the share table for the plot at any date.
- **Invariants.** Each becomes a rule and a test:

| ID | Invariant |
|---|---|
| I1 | Shares of a plot sum to 1 (± ε) at every point in time |
| I2 | A seller cannot convey more share or area than they held at the deed date |
| I3 | A deed cannot predate the seller's own acquisition of title |
| I4 | Holders in each khatian generation must be explained by events from the previous generation's holders |
| I5 | Area changes between surveys must be explained by a recorded split, acquisition or erosion |
| I6 | No conveyance after the effective date of an acquisition or restriction record |
| I7 | Two sales overlapping in time *and* in share/area are a double sale; a sequence A→B→C is legitimate |

### B6.3 Units, digits, dates

- Areas appear in decimal (শতাংশ), acre, bigha, katha and others; conversion factors can differ by region **[A9]**. Store area in one canonical unit **plus** the original text and unit. Compare with a tolerance per survey pair.
- Accept Bangla (০–৯) and ASCII digits in every numeric field. Store ASCII.
- Dates: store the original string and a parsed Gregorian date.

### B6.4 Restriction taxonomy (feeds the DC/Khas adapter and Q4)

| Type | Meaning for a buyer | Default severity | Basis |
|---|---|---|---|
| KHAS | Government-owned land; a private sale is not valid | Critical | **[VERIFIED]** buyer guides |
| VESTED (Ka / Kha list) | Listed under vested-property law; listings are published in the Gazette and are often challenged in court | Critical | **[VERIFIED]** Supreme Court writ judgments |
| ABANDONED | Listed as abandoned property | Critical | **[VERIFIED]** buyer guides |
| ACQUISITION | Notice or proposal to acquire the land | Critical | **[VERIFIED]** buyer guides |
| CERTIFICATE_CASE / AUCTION | Recovery proceedings or an auction at the tahsil/upazila land office | High | **[VERIFIED]** buyer guides |
| TAX_ARREARS | Unpaid land development tax; guides warn the government may take the property | Medium | **[VERIFIED]** buyer guides |
| OTHER_PROTECTED | Water body, forest, flood-flow zone, waqf/debottar, hill-tracts rules, cantonment, allotted plots with transfer conditions, agricultural-land conversion limits | Critical or High | **[ASSUMPTION A4]** |

This answers v1's open question (“other restrictions beyond khas and acquisition?”): at minimum vested/abandoned property, certificate cases/auctions and tax arrears are named in public buyer guides. The rest needs a lawyer.

### B6.5 Entities

AdminUnit · Plot · PlotLineage · KhatianRecord (survey type CS/SA/RS/BS or MUTATED) · OwnershipShare · Person (masked, synthetic) · Event (typed, B6.2) · Deed · MutationCase · CourtCase · Restriction · Lien · SourceSnapshot (one adapter result) · LedgerEntry · Checkpoint · Report · AuditLog.

## B7. Source adapters

### B7.1 One contract for every adapter

```json
{
  "source": "registry",
  "status": "OK",
  "as_of": "2026-10-15T23:00:00+06:00",
  "maturity": "M3",
  "linkage": "EXACT",
  "records": [ { "id": "REG-0001", "type": "SALE_DEED", "hash": "sha256:…", "data": { } } ],
  "notes": []
}
```

`status` ∈ OK · NO_RECORD · PARTIAL · STALE · UNAVAILABLE · ERROR. `linkage` ∈ EXACT · TEXT_MATCH · PARTY_NAME_ONLY.

### B7.2 What each status means for the verdict

| Status | Meaning | Effect |
|---|---|---|
| OK | The source answered; its records, possibly zero, are authoritative for its scope | Can support “no flag” |
| NO_RECORD | The source answered “nothing found” | Counts as clear **only** if maturity ≥ M2 **and** linkage is EXACT or TEXT_MATCH. With PARTY_NAME_ONLY linkage it means “nothing under these names”, not “nothing on this plot”, so coverage stays partial |
| PARTIAL | Covers only part of the question (for example some courts only) | Partial coverage |
| STALE | `as_of` older than the threshold | Coverage reduced; date shown |
| UNAVAILABLE / ERROR | Timeout, outage, consent missing | No coverage; the verdict cannot be GREEN |

### B7.3 Data-maturity tiers (the “Digitization” story)

| Tier | State of the source | Can it support “clear”? |
|---|---|---|
| M0 | Paper only | No |
| M1 | Scanned images, human lookup only | No |
| M2 | Structured or searchable data, no live API (batch export) | Yes, with a freshness date |
| M3 | Live query interface or API | Yes |
| M4 | Records signed at source | Yes, and strongest |

Each adapter reports its tier, and the report shows it. This turns “why we can't say safe yet” into a rollout roadmap: moving a source up a tier directly raises coverage. It also gives you a track-aligned sentence for the pitch: *verification is only as strong as digitization, and our report shows exactly where each office stands.*

### B7.4 Mock adapter → real counterpart

| Mock adapter | Real counterpart | Interface today | Default tier in the demo |
|---|---|---|---|
| Land Records | DLRMS / e-Porcha, e-Mutation khatians, land-tax data (Ministry of Land) | Web portals; a land services gateway used by registries | M3 |
| Registry | Department of Registration, sub-registry offices; e-registration under the 2026 ordinance | Manual deed-index search today; LT notice to AC (Land) | M2 (M3 for e-registered deeds) |
| Mutation | e-Mutation (Smart Mutation planned) at AC (Land) | Online application tracking | M3 |
| Court | Judiciary cause lists and Amar Adalat; land survey tribunals; money-loan courts **[A5]** | Search by case number, party, advocate | M2, with `PARTY_NAME_ONLY` linkage for some cases |
| DC/Khas | DC office, land-acquisition branch, tahsil; Gazette lists | Mostly paper or Gazette **[A4]** | M1–M2 (mixed) |
| Bank | Banks; registered mortgages also appear at the Sub-Registry; Bangladesh Bank credit data **[A6]** | Confidential and consent-gated | M1, or consent-gated |

### B7.5 Realism rules for the mocks (so the demo teaches the right lesson)

- Every adapter has configurable latency, failure rate, staleness and maturity tier.
- The **Court** adapter returns cases by party names and property-schedule text with a linkage confidence, never an exact plot flag. The engine must cope with `PARTY_NAME_ONLY`.
- The **Bank** adapter needs a simulated consent token. Without it, it returns UNAVAILABLE (reason: consent) and the source lands in “not checked”.
- One adapter is exposed as a thin HTTP service with the same JSON contract. The others run in-process.

## B8. Verification engine

### B8.1 Pipeline

1. Validate and normalise input (digits, units, names).
2. Fan out to all adapters in parallel with a 1.5 s timeout each; keep each result's status, `as_of` and maturity.
3. Verify ledger integrity for every record used (hash links up to a signed checkpoint).
4. Build the title graph and evaluate invariants I1–I7.
5. Run the rules → findings `{rule_id, severity, confidence, evidence refs, message key, next-step key}`.
6. Compute per-question coverage, then the verdict.
7. Compose the bilingual report, sign it, store it, write an audit-log entry.
8. Return structured JSON to the frontend.

### B8.2 Verdict v2 (coverage-aware)

**Coverage.** Each question has required sources. A question is COVERED when all its required sources returned OK, or NO_RECORD that qualifies under B7.2, within the freshness threshold; PARTIAL when only some did; NOT_COVERED when none did.

| Question | Required sources |
|---|---|
| Q1 | Land Records, Mutation |
| Q2 | Land Records, Registry |
| Q3 | Mutation, Court |
| Q4 | DC/Khas |
| Q5 | Bank, Registry |
| Q6 | Ledger (always checked) |

**Verdict states, in order of precedence:**

| State | Condition | Banner wording (en) |
|---|---|---|
| INTEGRITY ALERT | Any ledger or signature check fails | “Data discrepancy detected. No report issued.” |
| RED | At least one Critical finding | “Don't pay yet. Serious red flags found.” |
| AMBER | No Critical, at least one High or Medium | “Resolve these before paying.” |
| GREY | No finding above Info, but at least one question is not COVERED | “We could not check everything.” |
| GREEN | All six questions COVERED and no finding above Info | “No red flags found in the sources we checked. This is not a guarantee.” |

Every verdict screen also shows: the validity window, the per-source status table, “What we did not check”, and the disclaimer.

**Bangla sketches** (review before use):
- INTEGRITY: তথ্যে গরমিল ধরা পড়েছে — প্রতিবেদন দেওয়া হয়নি
- RED: এখনই টাকা দেবেন না — গুরুতর ঝুঁকি পাওয়া গেছে
- AMBER: টাকা দেওয়ার আগে এই বিষয়গুলো মিটিয়ে নিন
- GREY: সব যাচাই করা যায়নি
- GREEN: যাচাই করা উৎসগুলোতে কোনো লাল সংকেত পাওয়া যায়নি — এটি নিরাপত্তার নিশ্চয়তা নয়

### B8.3 Rule catalogue

Pri: **M** = Must (18 rules), **S** = Should, **C** = Could. Rules live as data (YAML metadata plus a Python function); see Appendix C.

| ID | Fires when | Q | Severity | Pri | Next step shown to the buyer |
|---|---|---|---|---|---|
| R-OWN-01 | No current record holder matches the seller (tier NONE) | Q1 | Critical | M | Don't pay. Compare the seller's papers, NID and father's name with the porcha |
| R-OWN-02 | Seller matches only at WEAK or PROBABLE tier | Q1 | Medium | M | Confirm father's/husband's name and NID against the porcha |
| R-OWN-03 | Share or area being sold exceeds the seller's recorded share (I2) | Q1 | Critical | M | Ask for co-owner consent or a partition deed; get legal review |
| R-OWN-04 | Several co-holders, one seller, no partition record | Q1 | High | S | Get all co-holders' written consent or a partition deed |
| R-OWN-05 | Record holder is deceased, seller claims as heir, heirship not mutated | Q1 | High | C | Ask for heirship proof; complete mutation first |
| R-CHAIN-01 | Current holders not explained by events from the previous generation (I4) | Q2 | High | M | Ask for the chain of deeds back to the mother deed |
| R-CHAIN-02 | Shares do not sum to 1 (I1) | Q2 | High | M | Ask the land office to re-verify the khatian |
| R-CHAIN-03 | Area differs across generations beyond tolerance and is unexplained (I5) | Q2 | High (Medium if small) | M | Get a measurement and mouza-map check |
| R-CHAIN-04 | Land class changed with no conversion record | Q2 | Medium | S | Ask for the conversion or permission order |
| R-CHAIN-05 | Deed predates the seller's own acquisition (I3) | Q2 | Critical | S | Treat as possible forgery; legal review |
| R-DISP-01 | Open case linked to the plot (EXACT or TEXT_MATCH) | Q3 | Critical | M | Check the case at the court; don't pay until resolved |
| R-DISP-02 | Open case matches only by party name | Q3 | Medium | M | Ask the seller and a lawyer whether it concerns this land |
| R-DISP-03 | Mutation application pending | Q3 | Medium (High if applicant ≠ seller) | M | Wait for the outcome or get legal advice |
| R-DISP-04 | Mutation rejected or objection filed | Q3 | High | S | Ask for the order; get legal advice |
| R-DISP-05 | Deed registered but no mutation after N days **[A7]** | Q3 | Medium | S | Ask why; check mutation status |
| R-RES-01 | Khas record | Q4 | Critical | M | Do not buy |
| R-RES-02 | Vested (Ka/Kha) or abandoned listing | Q4 | Critical | M | Do not buy without legal clearance |
| R-RES-03 | Acquisition notice or proposal | Q4 | Critical | M | Check with the DC office's land-acquisition branch |
| R-RES-04 | Other protected or restricted class **[A4]** | Q4 | Critical | S | Verify the land class with the land office |
| R-RES-05 | Certificate case, auction, or land-tax arrears | Q3/Q4 | High (arrears: Medium) | S | Ask for current tax receipts; check certificate cases |
| R-LIEN-01 | Active mortgage or lien | Q5 | Critical | M | Get the bank's written release before paying |
| R-LIEN-02 | More than one active lien | Q5 | Critical | S | Same, for every lien |
| R-SALE-01 | Overlapping sales of the same share or area (I7) | Q5 | Critical | M | Do not pay; legal review |
| R-SALE-02 | Rapid successive transfers (fewer than N days) | Q5 | Medium | C | Ask for the full transfer history |
| R-INT-01 | Ledger or checkpoint verification fails | Q6 | Integrity alert | M | Stop; the data cannot be relied on |
| R-INT-02 | A source is STALE | Q6 | Coverage gap | M | Re-run later; check with that office |
| R-INT-03 | A source is UNAVAILABLE or ERROR | Q6 | Coverage gap | M | Re-run later; check with that office |
| R-INT-04 | Cross-source conflict (for example the registry shows a sale to B, land records still show A, no LT notice) | Q6/Q2 | High | M | Ask both offices to reconcile |

**Info findings** (chain depth, date of last transfer, a STRONG name match reminding the buyer to confirm the NID) never change the verdict.

### B8.4 Name matching (Q1 depends on it)

**Level 1 — Must:**
1. Unicode **NFC**; strip zero-width joiners/non-joiners (U+200D, U+200C), punctuation and extra spaces. Some Bengali letters (ড়, ঢ়, য়) exist in both precomposed and base-plus-nukta forms, and NFC makes them compare equal.
2. Treat prefixes and honorifics as optional tokens: মোঃ / মো. / মোহাম্মদ / মুহাম্মদ (Muhammad variants) and মোসাঃ / মোছাঃ / মোসাম্মৎ (female prefix).
3. Apply a small curated canonical-spelling map: আবদুল → আব্দুল, উদ্দীন → উদ্দিন, and similar.
4. Compare tokens with Jaro-Winkler or normalised Levenshtein plus alignment. Given-name tokens weigh more than suffixes.
5. Compare the **father's or husband's name** as well as the person's name. Records usually carry both **[A12]**.

**Level 2 — Should:**
- Phonetic key: collapse শ/ষ/স → স; ন/ণ → ন; জ/য → জ; ি/ী → ি; ু/ূ → ু; and, for older documents, ছ ↔ স (ছিদ্দিক / সিদ্দিক).
- English input: transliterate to a common phonetic skeleton and compare there.

**Output tiers** (starting thresholds; tune on the gold set):

| Tier | Rule of thumb |
|---|---|
| STRONG | name ≥ 0.92 and father/husband ≥ 0.85 |
| PROBABLE | name ≥ 0.85 and father/husband missing or ≥ 0.70 |
| WEAK | name ≥ 0.70 |
| NONE | below that |

**Never auto-clear.** Even STRONG tells the buyer to confirm the NID and the father's name on the porcha.

**Gold set:** at least 60 labelled pairs, including **hard negatives** that are one letter apart but different people (করিম / রহিম, রহমান / রহিম, হোসেন / হাসান). A matcher that is too lenient is more dangerous than one that is too strict. Report accuracy on the set.

### B8.5 Severity, confidence and wording rules

- **Confidence** (High / Medium / Low) changes the wording (“Found…” vs “Possible…”) and the next step, not the verdict. Linkage and match tier are already encoded in each rule's conditions.
- Bangla sentences of about 18 words or fewer; no jargon without a tap-to-explain; every finding ends with one concrete action.
- Never write “safe”, “clean title” or “guaranteed”. Write “No red flags found in the sources we checked”.
- Leave each rule's `legal_basis` empty until a lawyer confirms it. Do not invent citations.

## B9. Report and verification

### B9.1 What the report contains

Header (report ID, short code, issued-at, valid-until, SYNTHETIC watermark) · plot identifiers · seller input and match tier · verdict banner · six-question scorecard · findings (rule, source, explanation, next step) · ownership timeline · source table (status, `as_of`, maturity) · “What we did not check” · ledger checkpoint (height, head hash, signature) · QR, official domain in plain text and short code · disclaimer.

**Disclaimer (en):** This report is advisory and based only on the sources and dates shown. It is not a legal opinion or a guarantee of title. Consult a lawyer and inspect the land before paying.

**Disclaimer (bn sketch):** এই প্রতিবেদন শুধু পরামর্শমূলক এবং কেবল উল্লিখিত উৎস ও তারিখের তথ্যের ওপর ভিত্তি করে তৈরি। এটি আইনি মতামত বা মালিকানার নিশ্চয়তা নয়। টাকা দেওয়ার আগে আইনজীবীর পরামর্শ নিন এবং জমি সরেজমিনে দেখুন।

### B9.2 Validity and supersession

- `valid_until = issued_at + 7 days` **[DECISION; validate A10]**.
- Any new ledger entry for the plot after issue makes the report **superseded**. The verify page re-runs the engine on current data and shows a diff: “what changed since your report”.
- Advice printed on the report: re-check on registration day.

### B9.3 Signature, QR and short code

- **Canonical payload:** `{v, report_id, plot_id, verdict, issued_at, valid_until, ledger_height, ledger_head, findings_hash, key_id}`.
- **Signature:** Ed25519 over the canonical JSON bytes.
- **QR content:** `https://<official-domain>/v#<base64url(payload)>.<base64url(signature)>`. At roughly 350–450 bytes it scans reliably.
- The verify page checks the signature **in the browser** with the embedded public key (for example tweetnacl), then asks the server about supersession and revocation. If the server is unreachable it still says “signature valid; could not check for newer information”.
- The PDF footer prints the **official domain in plain text**, a 10-character short code and the QR. Teach users to type the domain rather than trust a scanned link.
- PDF-level signatures (PAdES) are roadmap **[A8]**.

### B9.4 Verification states

| State | Meaning |
|---|---|
| ✅ Genuine and current | Signature valid, ledger consistent, within validity, nothing newer for this plot |
| ⏳ Genuine but expired | Signature valid, past `valid_until` |
| 🔄 Genuine but superseded | Newer records exist for this plot; shows what changed |
| ❌ Tampered | Signature or report hash fails |
| ⚠️ Integrity alert | The ledger or checkpoint check fails on current data |
| ❓ Unknown | No such report ID or short code |

## B10. Architecture and tech decisions

### B10.1 Architecture

```
Citizen UI (React · Bangla/English · mobile-first)
        │ HTTPS / JSON
        ▼
API (FastAPI) — validation · rate limiting · audit log
        │
        ▼
Verification engine
  name match → title graph → rules → findings → coverage → verdict
        │
        ▼
Source adapters (one contract, B7)
  Land Records │ Registry │ Mutation │ Court │ DC/Khas │ Bank
        │
        ▼
Store (SQLite) + Ledger (hash-linked, signed checkpoints)
        │
        ▼
Report service (HTML → PDF · Ed25519 signature · QR · short code)
        │
        ▼
Verify page (static; in-browser signature check + server supersession check)

Synthetic generator ──► seeds the store (seeded, deterministic)
Demo console (DEMO_MODE only) ──► tamper simulator · add-event · reset
```

### B10.2 Decisions

| Area | Decision | Why |
|---|---|---|
| Backend | FastAPI + Pydantic v2; adapters in-process | Fast to build; typed contracts; contract tests |
| Database | **SQLite** (WAL) via SQLAlchemy **[DECISION]** | Zero ops, deterministic seeding; Postgres is a later swap |
| Rules | Python functions plus YAML metadata (ID, severity, messages, next steps) | Explainable; a lawyer can review the YAML |
| Crypto | `cryptography` (Ed25519) and `hashlib` (SHA-256); no custom crypto | Standard primitives |
| Frontend | React + Vite + TypeScript, Tailwind, react-i18next | Fast; clean bn/en catalogues |
| Fonts | Noto Sans Bengali (open licence), self-hosted and subset | Consistent shaping; works offline |
| PDF | HTML → PDF with WeasyPrint in Docker; fallback Chromium print | Correct Bengali shaping (B10.5) |
| QR | `qrcode` library; payload under about 500 bytes | Scan reliability |
| Verify page | Static page plus an Ed25519 verify library | Offline-verifiable signature |
| CI | GitHub Actions: tests and lint on every push | Quality signal and real commit history |
| Hosting | `docker compose up` locally plus an optional free-tier host | Judges can run it; fallback video |

### B10.3 Repo layout

```
landcheck/
  README.md            AI_USAGE.md        docker-compose.yml
  docs/                PLAN.md  ARCHITECTURE.md  DEMO_SCRIPT.md  concept_note/
  backend/
    app/
      main.py
      api/             check.py  reports.py  verify.py  demo.py
      adapters/        base.py land_records.py registry.py mutation.py court.py khas.py bank.py
      engine/          models.py namematch.py title_graph.py rules/ coverage.py verdict.py
      ledger/          chain.py  checkpoint.py  signer.py
      report/          builder.py  pdf.py  qr.py  templates/
      i18n/            en.json  bn.json
      core/            config.py  security.py  audit.py
    seed/              generator.py  golden/*.json  names_bn.txt  noise.py
    tests/             test_rules_*.py  test_namematch.py  test_ledger.py  test_verdict.py  test_scenarios.py
  frontend/
    src/               pages/ (Home, Form, Checking, Result, Verify, Demo)  components/  i18n/
```

### B10.4 API

```
POST /api/v1/check              {district, upazila, mouza, jl_no?, survey?, khatian_no, dag_no,
                                 seller:{name, father_or_husband?}, lang}
GET  /api/v1/reports/{id}       JSON report
GET  /api/v1/reports/{id}/pdf   PDF
GET  /api/v1/verify/{id}        server-side verification (states in B9.4)
GET  /api/v1/meta/locations     cascading dropdown data
GET  /api/v1/health
POST /demo/tamper               DEMO_MODE only: edits a stored record behind the ledger's back
POST /demo/add-event            DEMO_MODE only: appends a legitimate new event (e.g. a mortgage)
POST /demo/reset                DEMO_MODE only: restores the seeded state
```

### B10.5 Bangla PDF — do this on day 1

- Render via **HTML → PDF with WeasyPrint** (shapes complex scripts through Pango/HarfBuzz) inside Docker, embedding Noto Sans Bengali. Fallback: Chromium print-to-PDF.
- Test string: conjuncts such as ক্ষ, জ্ঞ, দ্ব, স্ত্র, শ্র, কর্ম, plus Bangla digits and mixed Latin text. Open the PDF in two viewers and on a phone.
- Check any alternative PDF library for complex-script shaping *before* committing to it. ReportLab is the common one to test.
- WeasyPrint needs extra system libraries on Windows. If either of you develops on Windows, run the backend in Docker or WSL.
- Sign the report *content* (JSON, short code, QR) rather than relying on a PDF-level signature.

### B10.6 Run and demo logistics

- `docker compose up` brings up backend, frontend and seed data.
- The phone QR scan needs a reachable verify page. Prepare two routes: a public URL, or the laptop's hotspot with a LAN URL **[DECISION]**.
- Keep a recorded video of the full demo as the fallback if the venue network fails.

## B11. Security, privacy, abuse and ethics

### B11.1 Threat model

| # | Threat | Example | Mitigation | Residual risk |
|---|---|---|---|---|
| 1 | Forged report | A fake “green” PDF | Signature over the canonical report; verify page; signed payload in the QR | A user who never verifies |
| 2 | Lookalike verify site | A QR pointing to a copycat page | Official domain printed in plain text; short code; offline-verifiable payload | Phishing can't be fully removed |
| 3 | Tampered stored records | An insider edits a row | Hash links plus signed checkpoints; integrity alert overrides the verdict | Key compromise |
| 4 | Silent in-place edits | An officer rewrites history | Append-only amendments; audit log; two-person rule (roadmap) | Roadmap item |
| 5 | Scraping owner or case data through the tool | Bulk plot enumeration | Rate limits, CAPTCHA, no bulk endpoints, minimal fields, audit log; OTP login in production | Determined large-scale abuse |
| 6 | Oracle attack on name matching | A fraudster tunes a fake identity until it “matches” | Per-plot rate limit; on mismatch say “does not match” without revealing the owner's name; log attempts | Some leakage remains |
| 7 | Privacy of owners and third parties | An aggregated profile of one person | Synthetic only; masking; data minimisation; consent-gated bank data; retention limits | Real deployment needs legal review **[A11]** |
| 8 | Over-reliance as legal advice | “It was green, so I'm safe” | Coverage-aware wording, validity window, next steps, disclaimer | Human behaviour |
| 9 | Wrong or poisoned source data | A bad entry at one office | Provenance and freshness; cross-source conflict rule R-INT-04; correction path via the source office | Truth is outside our control |
| 10 | Availability and abuse | A flood of requests | Caching, per-source timeouts, degrade to UNAVAILABLE | — |
| 11 | Supply chain and AI-written code | An unreviewed dependency or snippet | Pinned dependencies; both of you review; secrets never committed; library crypto only | — |
| 12 | Web injection | Script in a name field | Input validation, output escaping, CSP | — |

### B11.2 Principles

- **Synthetic data only**, with a visible “SYNTHETIC — NOT A REAL LAND RECORD” watermark in the UI and on the PDF **[DECISION]**.
- **Match-based disclosure:** show whether the seller matches, not a dump of the owner's details.
- **Demo endpoints** exist only when `DEMO_MODE=1` and sit behind a passcode on the hosted instance.
- **No generative AI in the verdict path.** Rules are deterministic and Bangla explanations are pre-written, reviewed templates. AI tools may help you write code, and every use goes into `AI_USAGE.md`.
- **Right of reply:** a wrongly flagged owner or seller needs a way to ask for review. Findings cite their source so errors can be traced and corrected at the source office (roadmap).

## B12. UX plan

**Screens**
1. **Home:** language toggle (বাংলা default), one-line promise, “Start a check”, “Try a sample plot” chips, “Verify a report”.
2. **Guided form, three steps:** where (district → upazila → mouza and JL no.) → which plot (survey type, khatian no., dag no.; Bangla or English digits) → who is selling (name; father's or husband's name optional).
3. **Checking:** six source chips fill in live (✓ OK, … waiting, ! unavailable). This visualises the fragmentation problem and hides latency.
4. **Result:** verdict banner (icon, words and colour) → six-question scorecard (✓ ⚠ ✗ ?) → findings sorted by severity (plain sentence, **what to do next**, expandable “why we say this” with rule ID, source and record reference) → ownership timeline → coverage and “What we did not check” → validity and disclaimer → actions: Download PDF · Share summary as text · Show QR.
5. **Verify page:** scan or type the code → state card (B9.4) and the “what changed” diff when superseded.
6. **Demo console** (demo instance only): tamper · add event · reset.

**Microcopy rules:** short sentences; define terms in a tap-to-explain glossary (নামজারি কী?); one action per finding; never alarmist, never reassuring beyond the evidence.

**Accessibility and low bandwidth:** status never by colour alone; tap targets of at least 44 px; font size of at least 16 px; works at 360 px width; no heavy images; print-friendly report page.

## B13. Synthetic data and evaluation

### B13.1 Generator spec

- **Seeded:** one integer seed produces an identical database every run.
- **Scale:** 3 districts, about 12 mouzas, about 600 plots, 2–4 survey generations each, with dag lineage (renumber, split, merge).
- **Events:** sales, gifts, inheritance with realistic share fractions, partitions, acquisitions, mortgages and releases, mutation cases with lag, LT notices.
- **Names:** assembled from synthetic Bangla name parts. Never real people, real NIDs, phone numbers or real parcel identifiers.
- **Noise injection:** spelling variants, honorific prefixes, mixed units, Bangla and ASCII digits, missing LT notices, stale sources, unavailable sources.
- **Defect injector:** for each Must rule, inject N defective plots and write a ground-truth label file (plot → expected rules and verdict). Because you inject the defects, the ground truth is exact.
- **Golden plots:** 10 fixed plots with fixed IDs (B14.1).

### B13.2 Metrics

| Metric | Target | How measured |
|---|---|---|
| Detection rate per rule on injected defects | ≥ 95% | Label file vs findings |
| False-positive rate on clean plots | ≤ 5% | Clean subset |
| End-to-end verdict agreement | ≥ 95% | Expected verdict per plot |
| Name matching: positives matched at PROBABLE or better, negatives not matched | ≥ 90% and ≥ 95% | Gold set of at least 60 pairs |
| Tamper detection | 6 of 6 types | Ledger tests |
| GREEN honesty | 0 GREEN verdicts with a non-COVERED question | Property test across all plots |
| Latency | Report p50 and p95 | Benchmark script |
| Bangla PDF | 0 broken conjuncts on the test page | Visual check plus a stored screenshot |
| Comprehension | At least 4 of 5 non-technical readers state verdict and next step within 20 s | Informal test |

**Caveat to state on the slide:** synthetic evaluation tests the *logic*, not real-world data quality. Saying so makes the numbers more credible, not less.

## B14. Demo plan

### B14.1 Golden plots (write these first)

| ID | Scenario | Expected | Demonstrates |
|---|---|---|---|
| P-001 | Clean plot, all sources OK (court TEXT_MATCH, bank with consent) | GREEN | An honest green: 6/6 coverage, “not checked” list, validity date |
| P-002 | Seller is not the recorded holder | RED (R-OWN-01) | Q1 |
| P-003 | Active mortgage plus pending mutation | RED (R-LIEN-01, R-DISP-03) | Q3 and Q5 together |
| P-004 | Open title suit linked to the plot | RED (R-DISP-01) | Q3 |
| P-005 | Khas or vested record | RED (R-RES-01 / R-RES-02) | Q4 |
| P-006 | Same share sold twice, overlapping dates | RED (R-SALE-01) | Q5 |
| P-007 | Area drift RS→BS plus class change, unexplained | AMBER (R-CHAIN-03, R-CHAIN-04) | Q2 |
| P-008 | Name variant (মোঃ আব্দুল করিম vs মোহাম্মদ আবদুল করিম) | AMBER without father's name (R-OWN-02); GREEN with it | Name-match tiers |
| P-009 | Court source returns only PARTY_NAME_ONLY; bank source unavailable | GREY | Unknown is not safe |
| P-010 | P-001 reused: once after the tamper simulator, once after add-event | INTEGRITY ALERT / 🔄 superseded | Tamper vs legitimate update |

### B14.2 90-second video storyboard

| Time | On screen | Voice-over |
|---|---|---|
| 0:00–0:10 | Six office icons collapse into one question mark, then the logo | “Before you pay for land, five questions decide if it's safe, and the answers sit in six different offices.” |
| 0:10–0:30 | P-001: enter the plot, six source chips fill, GREEN banner, 6/6 coverage, “What we did not check”, valid-until date | “Here's a clean plot. Green doesn't mean safe. It means no red flags in what we checked, and we show exactly what we didn't.” |
| 0:30–0:55 | P-003 **in Bangla**: RED banner, three findings with rule, source and next step | “This plot has an active mortgage and a pending mutation. Each warning says which rule fired, which record it came from, and what to do next.” |
| 0:55–1:15 | Tamper simulator edits a record → verify page shows the integrity alert with the broken link highlighted; then add-event → the older report shows 🔄 superseded | “We can tell a forged change from a legitimate update.” |
| 1:15–1:30 | Phone scans the QR → ✅ genuine and current; closing card: adapters ↔ real systems; tagline | “Every report is signed, time-limited and verifiable. Our adapters map to real systems, from e-Mutation to e-registration. কেনার আগে যাচাই করুন।” |

About 150 words of narration, which leaves room for pauses. Narrate in the language the judges use and subtitle in the other. Keep Bangla UI visible in at least the RED beat.

### B14.3 Live demo

- Same four beats as the video. Let a judge pick one of the sample plots; you know all ten outcomes.
- **Pre-flight checklist:** seed reset · `DEMO_MODE` on · fonts load offline · phone on the same network or hotspot · a pre-generated PDF on hand · backup video open in a second window · browser zoom set · laptop charged.
- **Rule:** if any step fails live, switch to the recorded video immediately. Do not debug on stage.

## B15. Pitch and Q&A

### B15.1 Ten slides, five minutes

| # | Slide | Time | Notes |
|---|---|---|---|
| 1 | Hook: one buyer, one question (a fictional, labelled story) | 0:15 | |
| 2 | Problem: five questions, six offices, one evidence number (B2) | 0:25 | |
| 3 | Why it's hard: fragmentation, name variants, fake paper, false comfort | 0:20 | |
| 4 | Solution: the Land Safety Report, four verdict states, coverage | 0:20 | |
| 5 | **Live demo:** clean → risky in Bangla → tamper vs update → QR | 1:30 | One drives, the other narrates |
| 6 | How it works: adapters → ledger → rules → report | 0:30 | |
| 7 | Trust: what the signature proves and doesn't (B4.2) | 0:30 | Say the limits first |
| 8 | Evidence: benchmark, tests, comprehension test | 0:10 | One chart or three numbers |
| 9 | Rollout: mock → real mapping, maturity tiers, pilot, registrar-side check | 0:30 | |
| 10 | Limitations, roadmap, ask | 0:30 | Top three limitations, honestly |

Total 5:00. Each of you presents the part you built, because both of you must be able to explain every line. Rehearse three times with a timer. When you don't know, say “we don't know yet; here's how we'd find out”.

### B15.2 Expected questions

| # | Question | Short answer |
|---|---|---|
| 1 | Why rule-based and not ML? | Every flag must be explainable to a buyer and defensible to a lawyer, we have no labelled real data, and rules are deterministic and testable. ML could later help where rules can't (OCR, candidate name matches), never the verdict. |
| 2 | What if a data source is wrong? | We can't fix the truth, but we show provenance and freshness, flag cross-source conflicts (R-INT-04) and never treat silence as safety. Corrections go through the source office; our ledger proves what the source said at that moment. |
| 3 | How would you get real data? | Through official data-sharing agreements using the adapter contract (Land Ministry, Registration Department, judiciary, banks), starting with a one-upazila pilot. Never by scraping. The mocks mirror real systems (B7.4). |
| 4 | How do you protect privacy? | Synthetic data now. In production: data minimisation, match-based disclosure, consent-gated bank data, rate limits, audit logs, retention limits, and legal review of what buyers may see. |
| 5 | What if an admin re-hashes the whole chain? | The chain alone wouldn't stop that. The signed checkpoint does, because the signing key sits outside the database. The honest limit is key compromise; in production the key sits under government custody. |
| 6 | Who signs the reports, and why trust them? | Prototype: a demo key. Production: a government-controlled key or a CCA-licensed certificate. The design separates data custody from signing authority. |
| 7 | Isn't this legal advice? | No. It's advisory, coverage-aware and time-limited, and every finding ends with a next step that includes legal review. |
| 8 | How do you handle Bangla spelling variants? | Normalisation, optional prefixes, phonetic keys and the father's name produce tiers. It never auto-clears, and it's measured on a gold set with lookalike negatives (করিম / রহিম). |
| 9 | How is this different from e-Porcha and e-Mutation? | They publish one office's records. We aggregate across offices, cross-check them, say what we could not see, and return a signed, time-limited answer. They are our sources. |
| 10 | How does it scale nationally? | One adapter contract, parallel fan-out with timeouts, caching, per-district partitioning, rollout upazila by upazila. |
| 11 | What about false positives and negatives? | Rules are conservative: unknown never becomes safe. We measure detection and false-positive rates on a synthetic benchmark and would calibrate with validated real data in a pilot. |
| 12 | What if data changes after the report? | Reports expire; any later change marks the report superseded and shows a diff; we advise re-checking on registration day. |
| 13 | Couldn't fraudsters misuse the tool? | That's why there's a threat model (B11): rate limits, match-based disclosure instead of owner dumps, audit logs, and login in production. |
| 14 | Why mocks instead of real integrations? | The rulebook forbids live data. The adapter contract makes the swap mechanical, and contract tests keep mock and real adapters aligned. |
| 15 | What did you build, what did you reuse, how did AI help? | Name the modules, libraries and AI tools (`AI_USAGE.md`). Each of you explains every module; you ran teach-back sessions. |
| 16 | What would you do with six more months? | Lawyer-reviewed rules, a one-upazila pilot, the document check, and a registrar-side pre-registration view. |
| 17 | What if the system wrongly flags an honest owner? | Findings cite their source so the error can be traced and corrected there; a right-of-reply workflow is on the roadmap. |
| 18 | How would this sustain itself? | One possible model: a free basic citizen check with paid professional access for banks and lawyers, ideally government-hosted. |

## B16. Concept note (up to 3 pages)

| Section | Words | Include |
|---|---|---|
| 1. Problem and why it matters in Bangladesh | ~200 | Two evidence numbers (B2); the six questions |
| 2. Solution and how it works | ~250 | Architecture figure; adapters → ledger → rules → signed report |
| 3. Trust and integrity | ~150 | What the signature proves and doesn't (B4.2); tamper vs update |
| 4. Key features | ~150 | Three screenshots: green, red in Bangla, verify page |
| 5. Rollout via adapters and maturity tiers | ~150 | Short mock → real table; pilot path |
| 6. Limitations and roadmap | ~100 | Top three limitations; next steps |
| 7. Team, mentors, AI tools | ~50 | |

About 1,050 words plus two figures. Confirm the required language and template with the organizers.

## B17. Work plan

### B17.1 Roles (swap to match your strengths)

- **Person A — Data and trust:** generator and golden plots; adapters; title graph; rules; name matching; ledger and signing; tests.
- **Person B — Experience and story:** React UI (bn/en); report and PDF templates; verify page; Bangla copy review; demo, video and slides; concept note.
- **Shared:** mentor interviews, rule-catalogue review, evaluation, rehearsals.

Whatever the split, each of you must be able to explain every module. That is what the teach-back sessions are for.

### B17.2 Gates (as a share of the time you have; convert to dates once deadlines are known)

| Gate | By | Exit criteria |
|---|---|---|
| G0 | first 10% | Repo, CI and `AI_USAGE.md` live; three spikes done; organizer and mentor questions sent; golden plots written; adapter contract and stubs |
| G1 | 30% | **Vertical slice:** one golden plot goes UI → API → adapters → rules → verdict → signed JSON → verify page (ugly is fine) |
| G2 | 55% | All six adapters; 18 Must rules; generator and 10 golden plots; ledger plus tamper and legitimate-update demo; Bangla UI strings; PDF with QR; teach-back #1 |
| G3 | 70% | **Feature freeze.** Should-items done or dropped; Docker/hosted demo; metrics run; video script locked |
| G4 | 85% | Video recorded; concept note, slides and README done; all tests green; teach-back #2 |
| G5 | last 15% | Three timed rehearsals; fallback ready; submission checklist (B21); bug fixes only |

### B17.3 If you fall behind

**Cut in this order:** Could items → Merkle checkpoints and ledger visual → evaluation-harness polish → Should rules → PDF visual polish → name matching level 2 → offline-verifiable QR payload.

**Never cut:** the vertical slice; Bangla in the RED beat; the tamper-vs-update demo; the “not checked” section; tests for the Must rules.

### B17.4 Working agreements

- **Commits:** each of you commits at least daily with meaningful messages. Use feature branches and pull requests reviewed by the other person. Use merge commits. **No force-push and no history rewriting**, so the real history stays intact (rulebook).
- **`AI_USAGE.md` from day 1:** date, tool, purpose, files touched, who reviewed. Update it when you use a tool, not at the end.
- **Teach-back at G2 and G4:** each person walks the other through their modules for 20 minutes, and the listener keeps asking “why” until the answer holds. If you can't explain it, rewrite it or delete it.
- **Definition of done:** code, tests, bn/en strings, and reachable in the demo path.
- **15-minute daily sync:** yesterday, today, blockers, “what can we cut?”.
- **Time-boxes:** no task over half a day without a check-in. UI polish is capped at three screens: Home, Result, Verify.
- Write the demo script before the polish.

## B18. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Scope creep leaves features unfinished | High | High | MoSCoW; vertical slice by G1; cut order (B17.3) |
| 2 | Bangla PDF breaks | Medium | High | Day-1 spike; WeasyPrint in Docker; printable-HTML fallback |
| 3 | Domain mistakes (wrong legal or process detail) | High | Medium | Tag assumptions; mentor questions; `legal_basis` blank until validated; conservative wording |
| 4 | Live demo fails (network or hosting) | Medium | High | Local build plus recorded video; offline-verifiable QR |
| 5 | You can't explain AI-assisted code | Medium | High | AI log; teach-back; module ownership; read code aloud |
| 6 | Name matching embarrasses you live | Medium | Medium | Demo only tested cases; show tiers; gold-set metrics |
| 7 | Time sink in UI polish | Medium | Medium | Cap at three screens; Tailwind defaults |
| 8 | Synthetic data looks fake | Medium | Medium | Realistic name and mouza patterns; noise; mentor review of samples |
| 9 | Rulebook breach (real data, scraping) | Low | Critical | No automated requests; watermark; checklist (B21) |
| 10 | A teammate becomes unavailable | Medium | High | Pair on core modules; written docs; daily sync |
| 11 | Unknown rubric misaligns priorities | Medium | Medium | Ask now; map rubric to features |
| 12 | Overlap with P3 and document-verification entries makes you look generic | Medium | Medium | Lead with buyer-facing aggregation, coverage honesty and verifiability |
| 13 | Crypto misimplementation | Low | High | Library primitives only; six tamper tests; no custom crypto |

## B19. Assumptions and validation plan

### B19.1 Assumptions

| ID | Assumption | Why it matters | How to validate |
|---|---|---|---|
| A1 | Lawyers and banks check, roughly in this order: seller identity and authority, mother deed and chain of deeds, khatian chain plus latest mutated khatian, land-tax receipts, registry deed-index search, mutation status, case search, khas/vested/acquisition at the DC office, bank release, physical inspection | Rule priorities; the “not checked” list | Interview a lawyer and a bank officer |
| A2 | Mouza + JL no. + khatian + dag identify a plot; same-named mouzas exist | Search form; ID model | Mentor or land-office staff |
| A3 | Dag lineage between surveys is recorded somewhere, and splits and merges are common | Title-graph feasibility | Surveyor or land-office mentor |
| A4 | Restrictions beyond khas, vested, abandoned and acquisition: waqf/debottar, forest, water bodies and flood-flow zones, hill tracts, cantonment, allotted plots, agricultural-land conversion limits | R-RES-04; restriction taxonomy | Lawyer |
| A5 | Court data cannot be searched by plot; only by case number, party or advocate; the plot appears in the plaint's property schedule | Court adapter linkage design | Lawyer and court staff |
| A6 | Registered mortgages appear at the Sub-Registry; equitable mortgages may be unrecorded; bank data needs consent | Bank adapter; “not checked” list | Banker |
| A7 | Deed-to-mutation lag is about 8 days where integrated, longer elsewhere | Threshold N in R-DISP-05 | Land-office staff |
| A8 | A signed digital report carries practical weight if signed under a recognised authority (for example a CCA-licensed certificate) | Production trust story | Lawyer or ICT-division mentor |
| A9 | Area units and regional conversion factors; typical tolerance across surveys | R-CHAIN-03 tolerance | Surveyor |
| A10 | Seven days is a sensible validity window | B9.2 | Lawyer or bank |
| A11 | Rules on what a buyer may see about owners and cases; current status of data-protection legislation | Privacy design | Lawyer; check current law |
| A12 | Records carry the father's or husband's name; prefix and spelling conventions as in B8.4 | Name matching | Land-office staff; sample documents from mentors |
| A13 | Which upazilas already have registry–land-office integration, and the status of e-registration and Smart Mutation | Accuracy of the rollout story | Ministry sources or a mentor |

### B19.2 Questions for mentors

1. Walk me through due diligence for a plot purchase. What do you check, in what order, and which check catches the most fraud? (A1)
2. Which identifiers make a plot unique across surveys? Is the JL number needed? (A2)
3. How are dag numbers linked between CS, SA, RS and BS when plots split or merge? (A3)
4. Which record do you treat as the current owner evidence when the mutated khatian, the tax receipt and the deed disagree? (A1)
5. What restrictions beyond khas, vested/abandoned and acquisition must a buyer check? (A4)
6. How are cases linked to plots? Is there a structured plot reference, or only text in the plaint? (A5)
7. How do you discover a mortgage: registered, equitable, bank NOC? What would a bank share, and under what consent? (A6)
8. What is a normal gap, and what is a suspicious gap, between deed registration and mutation? (A7)
9. What do you trust as proof today: stamp, seal, QR, certified copy? Would a signed digital report be accepted by a bank or sub-registrar, and under which framework? (A8)
10. Which fraud patterns have you actually seen that this plan doesn't model? (all)
11. Which area units and regional conversions apply, and what tolerance is acceptable across surveys? (A9)
12. What should a buyer be allowed to see about owners and cases? (A11)

### B19.3 Process

Tag each validated item in this document, update the rule YAML and this table, and keep unresolved assumptions visible on the limitations slide. An honest “not yet validated” is better than a confident guess.

## B20. Roadmap

- **First three months after the hackathon:** lawyer review of rules and wording; pilot design with one upazila and the registry and land offices; adapter prototypes against official test data; name matching on anonymised samples; the document-check (OCR) module.
- **Three to twelve months:** integrate with e-Mutation and e-registration data under formal agreements; a consent-gated bank-lien consortium; “watch this plot” alerts; a registrar-side pre-registration view so the same flags appear at the registration desk; the right-of-reply workflow.
- **Beyond a year:** rollout by division; government-controlled signing (CCA); public anchoring of checkpoints; an open API for banks and lawyers; voice, IVR and call-centre channels for low-literacy users.

## B21. Rulebook and submission checklist

### B21.1 Constraints and how this plan complies

| Rulebook constraint | How we comply |
|---|---|
| Dummy data only | Synthetic generator; watermark on UI and PDF; no real names, NIDs, phone numbers or parcels |
| No scraping or bulk downloads; no testing against live systems | No automated requests to government sites. Learn record formats from mentors' samples or documentation. If you want to view public pages manually, ask the organizers first **[DECISION]** |
| Keep the real commit history | Daily commits from both of you; no force-push or history rewriting |
| List all AI tools in the README | `AI_USAGE.md` from day 1, summarised in the README |
| Only the two students present at the final | Both rehearse every section |

### B21.2 Deliverables

- [ ] Concept note PDF, up to 3 pages (B16)
- [ ] Public GitHub repo: README (run steps, data used and how it is generated, AI tools used), tests, CI, real history, licence
- [ ] Demo video, up to 90 seconds (B14.2)
- [ ] Final pitch: up to 10 slides, 5 minutes plus 3 minutes Q&A (B15)

### B21.3 Ask the organizers today

1. The judging rubric and its weights.
2. The stages and the deadline for each deliverable. Public repos from other teams mention a “Round 1”, so confirm what is due when.
3. Submission format: links or uploads; video size, format and language; concept-note template and language.
4. Whether a hosted live URL is expected or a local demo is fine; what internet and equipment the final provides; whether a pre-recorded fallback is allowed.
5. Whether synthetic data may use real administrative names (districts, upazilas, mouzas) and real legal terms. Our default: real administrative names, invented plot and person data, watermark.
6. The format of the AI-tools disclosure, and whether AI-assisted code is judged differently.
7. Mentor access: who, how often, and whether mentor input may be cited.
8. Whether manually viewing public government pages to learn record formats is acceptable.
9. Licence requirements for the repo, fonts and libraries.

---

# Appendices

## Appendix A — Glossary

| Bangla | Transliteration | English | Note |
|---|---|---|---|
| খতিয়ান | khatian | Record of rights | One per survey; also the mutated khatian |
| পর্চা | porcha | Certified copy of a khatian | |
| দাগ | dag | Plot number | Changes between surveys |
| মৌজা | mouza | Revenue village; lowest cadastral unit | Pinned by JL no. **[A2]** |
| জেএল নম্বর | JL no. | Jurisdiction-list number of a mouza | **[A2]** |
| নামজারি / খারিজ | namjari / kharij | Mutation: updating the record of rights after transfer or inheritance | |
| দলিল | dolil | Deed | |
| মূল দলিল (মাদার ডিড) | mul dolil / mother deed | The root deed in a chain of title | |
| সিএস / এসএ / আরএস / বিএস | CS / SA / RS / BS | Cadastral / State Acquisition / Revisional / Bangladesh Survey | |
| খাস জমি | khas jomi | Government-owned land | |
| অর্পিত সম্পত্তি | orpito shompotti | Vested property (Ka/Kha lists in the Gazette) | |
| পরিত্যক্ত সম্পত্তি | poritokto shompotti | Abandoned property | |
| ভূমি উন্নয়ন কর (খাজনা) | bhumi unnayan kor (khajna) | Land development tax | |
| এলটি নোটিশ | LT notice | Land Transfer notice from the Sub-Registry to AC (Land) | |
| এসি (ল্যান্ড) | AC (Land) | Assistant Commissioner (Land); handles mutation | |
| সাব-রেজিস্ট্রার | sub-registrar | Registers deeds | |
| ডিসিআর | DCR | Duplicate carbon receipt issued after mutation | |
| শতাংশ | shotangsho (decimal) | One hundredth of an acre | |
| বন্ধক | bondhok | Mortgage | |
| যাচাই | jachai | Verification, checking | Working product name |

## Appendix B — Example report (abridged)

```json
{
  "report_id": "RPT-2026-000123",
  "short_code": "K7M2-9QXA",
  "issued_at": "2026-10-20T10:15:00+06:00",
  "valid_until": "2026-10-27T10:15:00+06:00",
  "synthetic": true,
  "plot": { "district": "…", "upazila": "…", "mouza": "…", "khatian_no": "…", "dag_no": "…" },
  "seller_input": { "name": "…", "match": { "tier": "PROBABLE", "score": 0.88 } },
  "verdict": "AMBER",
  "coverage": { "Q1": "COVERED", "Q2": "COVERED", "Q3": "PARTIAL", "Q4": "COVERED", "Q5": "NOT_COVERED", "Q6": "COVERED" },
  "findings": [
    { "rule_id": "R-DISP-03", "severity": "Medium", "confidence": "High",
      "message_key": "disp.mutation_pending", "evidence": ["MUT-0042"],
      "next_step_key": "next.check_mutation" }
  ],
  "sources": [
    { "source": "land_records", "status": "OK", "as_of": "…", "maturity": "M3" },
    { "source": "bank", "status": "UNAVAILABLE", "reason": "consent_required" }
  ],
  "not_checked": ["Bank liens (consent not given)", "Physical possession and boundaries", "…"],
  "ledger": { "height": 1842, "head": "sha256:…", "checkpoint_sig": "ed25519:…" },
  "key_id": "demo-2026-01",
  "signature": "ed25519:…"
}
```

## Appendix C — Example rule, ledger entry and checkpoint

```yaml
id: R-LIEN-01
question: Q5
title:
  en: "Active mortgage on this plot"
  bn: "এই জমিতে সক্রিয় বন্ধক আছে"
severity: Critical
fires_when: "any lien with status == ACTIVE and linkage in (EXACT, TEXT_MATCH)"
requires_sources: [bank, registry]
next_step:
  en: "Ask the seller for the bank's written release (NOC) before paying anything."
  bn: "টাকা দেওয়ার আগে বিক্রেতার কাছে ব্যাংকের লিখিত ছাড়পত্র (NOC) চান।"
legal_basis: ""   # fill only after a lawyer confirms; never invent
tests: [lien_active_fires, lien_released_clean, lien_two_active_escalates]
```

```json
{ "seq": 1842, "ts": "2026-10-20T10:14:58+06:00", "source": "registry",
  "record_id": "REG-0001", "record_hash": "sha256:…",
  "prev_hash": "sha256:…", "entry_hash": "sha256:…" }
```

```json
{ "height": 1842, "head_hash": "sha256:…", "ts": "2026-10-20T10:15:00+06:00",
  "key_id": "demo-2026-01", "signature": "ed25519:…" }
```

## Appendix D — Sources consulted

These come from search results and snippets. Open each source and confirm the date and wording before citing it in the concept note. A search did not turn up an official LandTech 2026 page or the judging rubric, so ask the organizers.

**Evidence on land disputes**
- Dhaka Tribune op-ed, “Whose land is it anyway” (pending cases, the Ministry of Land secretary's 80% statement): https://www.dhakatribune.com/opinion/op-ed/396001/whose-land-is-it-anyway
- The Observer, “Land case backlog weighs on our legal system”: https://www.observerbd.com/news/552680
- The Observer, “Why civil cases delayed for many years” (a 2019 government report, about 70%): https://observerbd.com/news/513536
- UCA News (ALRD figure, about 75%): https://www.ucanews.com/amp/land-grabbing-drives-lawlessness-and-deaths-in-bangladesh/71660
- The Daily Star, “One in 7 households facing land disputes”: https://www.thedailystar.net/one-in-7-households-facing-land-disputes-36783

**Existing systems and reforms**
- UN Public Service Awards, e-Mutation: https://publicadministration.un.org/unpsa/database/Winners/2020-winners/e-mutation
- The Financial Express / bdnews24, online mutation fees and QR-code-based DCR: https://thefinancialexpress.com.bd/home/bangladesh-mandates-online-payment-of-land-mutation-fees-1664697255
- The Observer, Cabinet decision on automatic mutation after registration (Nov 2020): https://www.observerbd.com/news.php?id=283723
- TBS News, coordinated registration and mutation: https://www.tbsnews.net/bangladesh/coordinated-land-registration-mutation-benefit-over-1-crore-people-land-secretary-156184
- TBS News, mutation without an application, LT notice: https://www.tbsnews.net/bangladesh/mutation-application-no-longer-needed-land-office-171619
- The Observer, “Smart Mutation in offing” (report appears to date from about 2024; check status): https://observerbd.com/news/453122
- Ministry of Land, “Land Services by 2026” presentation (2023): https://bdplatform4sdgs.net/wp-content/uploads/2023/03/Land-Services-by-2026_Secretarys-Presentation.pdf
- The Daily Star, “Reforming land registration in Bangladesh” (Registration (Amendment) Ordinance 2026): https://www.thedailystar.net/law-our-rights/news/reforming-land-registration-bangladesh-4093841
- JICA report, land property system in Dhaka (LT notice, mutation flow): https://openjicareport.jica.go.jp/pdf/12324018_05.pdf

**How buyers check, restrictions, courts**
- The Daily Star, “Steps to follow before purchasing land in Bangladesh”: https://online91.thedailystar.net/law-our-rights/news/steps-follow-purchasing-land-bangladesh-1856956
- The Financial Express, “Concluding clean deal in purchasing land”: https://thefinancialexpress.com.bd/views/concluding-clean-deal-in-purchasing-land-1572444815
- Supreme Court of Bangladesh, writ judgments on vested-property “Ka” list entries (examples): https://supremecourt.gov.bd/resources/documents/1_W_P_No13546of2015.pdf
- UNDP, online cause list and Amar Adalat app (2022): https://www.undp.org/bangladesh/press-releases/online-caselist-judicial-monitoring-dashboard-and-amar-adalat-mycourt-app-launched
- Dhaka Tribune, “Justice going digital” (case search by case number, party, advocate): https://www.dhakatribune.com/opinion/op-ed/13177/justice-going-digital

**Landscape awareness only (do not reuse their code or ideas)**
- Public README of another LandTech 2026 entry on P3: https://github.com/RafiulKabir0/landtrace
- Public README of an AI-based document-verification entry: https://github.com/mohammademon10/LandGuard-AI-LandTech-Innovation-Hackathon-2026

*End of plan v2.*
