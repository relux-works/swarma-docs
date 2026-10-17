# Agent memory for the platform: synthesis of the parked collective

Written by the convener from the files under `memory/` at PARK (2026-10-14T03:01Z): ten verdicts, the designs, the findings and the parked records. No subagent was used. Seats by five: five 1 = astra-01..03, wonder-01..02; five 2 = astra-04..06, wonder-03..04. Five 3 (the mini) never started. All four Muse seats ended at 01:30Z on a provider quota error, so their files are their last states and predate the Codex seats' final convergence. All scores are design scores; nobody built, ran or measured anything.

## 1. Verdict

The base is **admissible and directionally right, but beaten**. Its second half already draws the hard boundaries (no grants, no acceptance, no session input, no wake, no secret hoarding, no global log of record). The seats find that its weakness is not a wrong idea but an **unclosed contract**: eight primitives plus several engines, a full ATMS commitment without bounded semantics, an "observe everything" intake without an admission and erasure contract, and a `KnowledgeView` whose disclosure rules are not specified. Two implementations could follow the base and disagree on conflict, missing evidence, revision, scope and erasure.

The winning design is **bounded evidence memory** (`designs/bounded-evidence.md` at `5d96e70`, with its normative companion `designs/bounded-support-semantics-astra-03.md` at `9bafff8`). It keeps the base's knowledge semantics and its Swarma half, and shrinks the core:

- **Five record shapes**: Assertion, Source reference, Justification, Assessment, Revision. View is a derived, bounded response, not a stored primitive. Principal and Knowledge Space become references to the platform's existing identities and policy scopes, not parallel registries.
- **No own log of record.** Memory keeps only its own assertion/revision history and cites the authoritative journals (user manager, broker, dispatcher, session host, board, keeper, a2a, Curator) by exact revision.
- **Two profiles.** A *documentary profile* first: a reviewed, git-versioned register of explicitly persistable records plus a read-only retrieval adapter; writes go through ordinary repository review; no daemon. A *protected service profile* later: one unprivileged single-writer service with an owned admission contract, only when private material, autonomous proposers or measured load need it.
- **TMS, bounded.** First release: explicit source links, documentary basis, review-on-change edges and supersession. Next slice: finite acyclic rules over signed literals (AND within a premise list, alternatives across rules) with a bounded affected closure and an explicit evaluation-completeness field. A full ATMS is not a commitment.
- **First use case:** architecture decision continuity on Swarma's own decisions (the base's F-1 example: "retirement deletes the home" superseding "archive by default", with the registered assumptions that still depend on the old rule).

Every Codex seat's final recommendation is this family; the Muse seats independently reached close relatives (wonder-01 "D★", wonder-02 "base-minus", wonder-03 "refs, not copies", wonder-04 "D1: trimmed decision-and-evidence ledger"), each scoring 14–15.

## 2. Score table

Rubric R1–R8 from `MISSION-MEMORY.md`. "Initial" is each seat's frozen independent table; "final" is its verdict at PARK where it changed.

| Design | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | Total | Seats |
|---|---|---|---|---|---|---|---|---|---|---|
| Base, both halves | 1 | 2 (1–2) | 2 (1–2) | 1 (1–2) | 2 | 1 (1–2) | 1 | 2 | **12 (9–13)** | all 10; Codex 12–13, Muse 9–11 |
| **Bounded evidence, protected service profile** | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | **15** | astra-01..06 (astra-01: 14 initial, 15 final) |
| **Bounded evidence, documentary profile (first slice)** | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | **14** | astra-02, astra-04, astra-05, astra-06 final |
| Muse relatives (D★, base-minus, refs-not-copies, D1) | — | — | — | — | — | — | — | — | 14–15 | wonder-01 14 (15 with an R7 profile), wonder-02 14, wonder-03 15, wonder-04 15 |
| Typed decision documents + existing board decisions | 2 | 2 | 2 | 1 | 2 | 1 (1–2) | 1 | 2 | 13 (12–15) | astra-01, -03, -04, -05, -06; wonder-03 "docs-board" 12 |
| Projection over existing journals only, no own log | 2 | 2 | 2 | 1 (1–2) | 2 (1–2) | 1 | 1 | 1 (1–2) | 12–13 | astra-01, -03, -05, -06; wonder-03 |
| Memory as compiler (no persistent knowledge) | | | | | | | | | 13 | wonder-01 only |

Ranges in parentheses where seats differ. The row-level values for the Muse relatives are in their verdict files; they score related but not identical artifacts, so they support the family, not the exact vector.

**R7 is 1 everywhere.** No design has a published closed grammar with exact expected-output conformance vectors yet. "Optimal" therefore holds at design-contract fidelity only, as in the MCP collective.

## 3. Proof status

- **Rule:** two seats from two different fives score the winning design within one point on every row.
- **Met on one host.** astra-04 (five 2) ratified the exact assembly `5d96e70` + `9bafff8` and matches astra-01 (five 1) on every row (`verdicts/astra-04.md`, final position). astra-05 (five 2) and astra-02 (five 1) hold identical current vectors for both profiles, 15 and 14 (`verdicts/astra-05.md`, `verdicts/astra-02.md`). astra-06 × astra-03 also agree (15, `verdicts/astra-06.md`).
- **Independence:** each five-2 seat froze its initial table in a signed commit before reading any five-1 verdict.
- **Not met cross-host.** The mini five never started: its executor was unavailable, and Muse seats could not run after the quota ran out. The proof is two fives on one host.
- **Muse seats** stopped before the Codex convergence; their families agree in direction but their files do not ratify the exact assembly.

## 4. Smallest change set from the base

1. Replace the eight primitives with five record shapes and a derived View; make Principal and Knowledge Space foreign references (astra-01, -03, -04, -06; wonder-02).
2. Drop the single append-only event log; keep only memory's own assertion/revision history and cite authoritative journals by exact revision (all seats; the base's own Part 2 already says so).
3. Replace the ATMS commitment with the bounded support semantics: signed polarity, versioned rules, bounded affected closure, and an evaluation-completeness field so incomplete search is never reported as support or refutation (`findings/bounded-inference-completeness.md`, `findings/closed-conflict-and-rule-semantics.md`).
4. Put the admission and erasure contract into the first slice, not P3: explicit admitted sources, separation of reasoning dependencies from content derivation and custody, erasure through every derived index, cache and replica, and honest reporting of deleted evidence (`findings/erasure-closure.md`).
5. Authorize what a view reveals, including status, provenance and explanations, which can leak restricted facts by inference (`findings/view-inference.md`).
6. Deliver memory to agents only as data through a data-only context channel, never as instructions or through Curator overlays (`findings/memory-data-channel.md`).
7. Give the protected service an owned admission contract before deployment: private state, sole write API, socket permissions and peer identity checks, admitted client roles, its own egress rules (`findings/memory-service-admission.md`).
8. Start without a daemon: documentary register plus read-only adapter (astra-01..06).
9. Treat Graphiti or any off-the-shelf store only as a replaceable projection, and only after its deletion behaviour is validated against exact versions (`findings/graphiti-erasure-contract.md`).
10. Treat a signed or attributed mirror as evidence of the mirror, not of the original record (`findings/mirror-origin-astra-06.md`).
11. Engage the platform's own memory chapters (platform book ch. 09 «Память», ch. 10 «Сны») and mark which platform seams are still proposals (`findings/platform-memory-chapters.md`, `findings/platform-memory-omitted.md`, `findings/status-blind-seams.md`).

## 5. Mechanical check of the base's platform claims

wonder-02 and wonder-04 checked the base's factual claims against book v0.12, the architecture repository and curator-spec. Most are **confirmed**. Corrections:
- "Session is a cache" is chapter 8 in v0.12, not 7 (drift only).
- The one-writer-per-store rule is marked *proposed* in the book; the base leans on it as established (status inflation).
- The book marks CIP-0002 (project content never becomes instruction without approval) as decided, while curator-spec still holds it as Draft; the base inherits the book's stronger status.
- The base's two halves describe different systems (a standalone runtime vs a Swarma module); scoring must name which (`findings/two-bases.md`). Every seat scored both halves together.

## 6. Questions for the operator

1. **Product shape.** Is the goal a Swarma-internal memory module, or a standalone open-source Knowledge Runtime that other ecosystems adopt, with Swarma as one adapter? The sketch wants both; they pull R5 against R2/R8 (wonder-01 Q1).
2. **Erasure promise.** May reviewed records ever contain summarised sensitive content, accepting git-history retention, or are they references only, even if less readable offline (wonder-01 Q2, astra-02)?
3. **Review capacity.** Who accepts records at steady state: humans only, or a board role with a review grant for low-sensitivity records? This bounds memory poisoning more than any schema (wonder-01 Q3).
4. **Automatic extraction.** Is model-driven extraction from session journals (the platform book's "dreams") in scope for v1, or only agent-authored records with review? Most seats recommend the latter: extraction is where secrets enter (wonder-01 Q4).
5. **When to build the protected service**, and under which owner and admission contract (astra-04, astra-05 parked records).
6. **Where the RFC lives** (curator-spec, the architecture repository, or a new repository) and who owns R7: the grammar and the conformance vectors.

## 7. Open threads

- R7 work shared by every seat: closed schemas for the five shapes, the view disclosure contract, exact conformance vectors, and the governance home. See `parked/astra-01.md` and `parked/astra-03.md`.
- A pilot plan for the documentary register on Swarma's own decisions, with its value metric (fewer repeated investigations and fewer text-versus-decision drifts; the base cites that almost half of 44 confirmed review-cycle findings were such drifts).
- Muse seats left no parked records; wonder-02's findings file was never confirmed by a peer in the room.
- The cross-host five can still run later as an independent addendum on Codex seats.
