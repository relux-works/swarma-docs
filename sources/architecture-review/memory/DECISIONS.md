# Memory design: decision log

Owner decisions on the agent-memory design, as Ivan states them in the lane orchestrator's session. Each entry quotes the decision, names its scope and the follow-up. Proposals that are not yet decided stay in `SYNTHESIS.md` §6 and `notes/`.

## D-001. Memory snapshot travels as a data block, not as an overlay (2026-10-14)

- **Question put:** platform book ch. 09 «Память» places the session-start memory snapshot in the operator overlay with a weight below every role module, and calls that "not instructions". Curator weights only order chapters; they do not turn instruction text into data (`findings/memory-data-channel.md`). Should the snapshot reach the session as a separate data block instead, and should ch. 09 be corrected to say so?
- **Decision (Ivan, in session):** «да».
- **Meaning:** the snapshot idea survives (fixed for the session, keeps the prompt cache warm), but its channel is a data-only block with per-item provenance and the `data` classification, never a Curator overlay, `AGENTS.md`, skill root or machine base context. Memory content gets no overlay weight at all.
- **Follow-up:** a change to `wiki/book/ru/09-pamyat.md` (the overlay paragraph and the "это не инструкции" line of the ladder section), through the wiki's normal PR flow; the exact delivery contract of the data block belongs to the R7 package.

## D-002…D-007. The six owner questions (2026-10-17)

- **Question put:** accept as decisions the six answers in the final form of the comparison table (lane recommendation reconciled with `inputs/REVIEW-1.ru.md`), with the review's variant on question 3.
- **Decision (Ivan, in session):** «Да, я хотел бы, чтобы вот уже было как решение, все сделано, чтобы мы получили 0.2 версию.»
- **Source of each answer:** `SYNTHESIS.md` §6 (questions), the lane's recommendations of 2026-10-14, and `inputs/REVIEW-1.ru.md` §6.

### D-002. Product shape

A portable semantic contract and kernel; the first implementation and the value check run inside Swarma. Swarma is the first full consumer and the first security adapter. The kernel holds assertions, source references, justifications, assessments, revisions and the view evaluation rules; the Swarma adapter binds identities, account generations, source owners and admission. Portability is a conformance requirement: the same admitted corpus yields the same semantic result without the dispatcher, the board and the session host; profiles differ in authentication and isolation guarantees, never in the meaning of `incomplete`. A standalone repository and release come when the kernel has a second real consumer. The first use case stays architecture decision continuity; personal memory, extraction, consolidation and models of other agents come later on top of the kernel without widening its authority.

### D-003. Content of the documentary register (erasure promise)

Only explicitly admitted non-sensitive content goes into the git register. Admitted non-sensitive excerpts are allowed under their separate retention admission. Sensitive paraphrases never go into git; sensitive content waits for the protected service with erasable payloads. Working rule: if it would not go into the repository's README, it is not a register record. The goal is reproducible justification within explicitly chosen custody boundaries, not the fewest stored bytes at any price.

### D-004. Review capacity

In the pilot a human accepts records through ordinary repository review; agents prepare proposals. A board role with a review grant for low-sensitivity classes is considered after the pilot, on its measured maintenance cost. Facts from external sources stay in quarantine until human review (platform book ch. 09). No reviewer mints adopted status: an assertion about an adopted decision resolves to the deciding authority's receipt.

### D-005. Automatic extraction

No automatic intake of raw session journals in v1. A separate tool may generate proposals from already admitted documents; its output enters memory only through D-004 review. The deterministic log distiller (ch. 10) and model extraction from journals come later, and only if the pilot shows value without weakening the boundary vectors.

### D-006. The protected service

Built only on a concrete need: an admitted private or personal data class, autonomous writers without per-change review, or measured load. It is tied to the platform milestone of a separate OS user and mediator (ch. 09 names that the real protection) and must pass its own admission contract (`findings/memory-service-admission.md`) before deployment. Not built for architectural status alone.

### D-007. Where the specification lives, and who owns R7

One canonical package: normative prose, closed schemas and executable conformance vectors, owned by the memory lane. The kernel package carries no Swarma terms; the Swarma adapter contract lives in `swarm-platform-architecture` next to `handoff-package`; the book explains the package and integration documents reference it. The package is drafted in this repository under `memory/spec/` and moves to its own repository together with D-002's standalone release. Semantic vectors and protected-deployment checks are reported separately; passing the first is never presented as passing the second.

## D-008. Profiles use case enters the design; one kernel for both scenarios (2026-10-17)

- **Question put:** add to the R7 scope an addendum for subjects and derived views, built from the profiles use case (`inputs/USECASE-PROFILES.ru.md`, reconciled in `notes/usecase-profiles-gaps.md`): attribution roles and current-state projection with freshness in the kernel, derived disclosure and the publication handoff as boundary contracts, vectors on a synthetic profile corpus; the pilot stays on architecture decisions and no real personal data is admitted.
- **Decision (Ivan, in session):** «Да, вот надо бы, давай все то, что нам прислали сейчас по этому use case, давай оформим это, возьмем это к себе в дизайн, чтобы у нас было ядро, а, в общем, как надо, абстрактное, а, но удовлетворяло конкретным сценарием.»
- **Meaning:** the kernel stays domain-free with five records; profiles, intents, discovery cards, matching, catalogs and introductions are a domain package and services above it. The kernel gains the envelope roles (subject, issuer, submitter, representation reference, perspective, admission class), domain-schema cardinality and incompatibility rules, revision authority per issuer sequence with expected-version concurrency, named projection rules, freshness, lineage-inherited disclosure with declassification by the policy owner, and the boundary to publication. Real profiles still wait for D-003 and D-006.
- **Artifact:** `designs/kernel.md` (the consolidated kernel contract, draft v0.1), with vectors S28–S33 and P01–P11.

## Proposed next steps (not decisions)

- **R7 package** first, from `designs/kernel.md`: closed schemas for the envelope and the five records, the view disclosure contract, the 17 + 27 vectors as executable fixtures, plus the review-1 gaps (`notes/review-1-gaps.md`: corpus coverage, incompatibility rules, S28/S29, `premise_quality`, source availability states).
- **Adversarial triad** after the package, under the Codex-only spawn policy: an independent evaluator implementer (`gpt-6.1-sol`, high) that reads only the package, and a divergence-case writer (`gpt-6-astra`, medium); every divergence becomes a package fix or a new vector. The evaluator becomes the core of the pilot's read-only adapter.
- **Pilot metrics** added to the collective's list: corpus maintenance cost, actualization latency, and a working-task check (does a fresh agent bring back a superseded decision; does it notice the real dependents).
- **Platform book ch. 09** correction for D-001, through the wiki's PR flow.
