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

## D-009. R7-055: issuer-local canonical order (2026-10-17)

- **Question put:** owner question R7-055 (`conformance/OWNER-QUESTIONS.md`). Two decisions d1 and d3 of issuer H1 are connected only through a predecessor event of H2 (`r1(H1) <- r2(H2) <- r3(H1)`). Kernel §5.3 did not say whether a foreign event on the predecessor path orders H1's decisions; the two evaluators split (`ambiguous_current` vs current d3). Options: only H1 events order H1's decisions (judge and lane recommendation), or H1's edge adopts the global predecessor order. The forwarded review `inputs/REVIEW-R7-055.ru.md` recommends the first, with refinements.
- **Decision (Ivan, in session):** «Давай, утверждаю.» (to the issuer-local option in the reviewer's formulation, as put by the lane)
- **Rule:**
  - Currentness and the strict-replacement-succession check use one relation: the canonical order of the deciding issuer H. A qualifying predecessor path consists entirely of events whose protected policy authority-event issuer is H, including intermediate events with no assertion attached.
  - Formally, with `V_H` the events issued by H and `E_H = E ∩ (V_H × V_H)`: `a ≺_H b` iff `(b, a) ∈ E_H⁺`. Not `E⁺` restricted to H endpoints.
  - One such path suffices. Cross-issuer edges create no transitive order for H; removing a foreign event never creates a bypass edge; foreign branches do not cancel an existing all-H path.
  - Mixed states are not refused merely for mixing issuers; existing integrity rules stay. A missing qualifying path means "required order not established", not an invalid state; write outcomes follow the existing refusal contract, with no new error code.
  - For the separating input (single path through H2) the order of H1 is not established: d1 and d3 stay `ambiguous_current` candidates; neither becomes historical on that path.
  - Invariant: on admissible states with an unchanged H subgraph, changes confined to foreign parts of the graph never change `≺_H`.
- **Scope:** R7-055 only. D-001…D-008, single-issuer fixes, protected event attribution and all other checks stand. No cross-authority order adoption, no authority transfer, no new delegation, no local/global switch; a shared multi-authority register would be a separately versioned extension.

## D-010. Identities and delegation bind to the platform identity design (2026-10-18)

- **Question put:** close the open question "concrete bindings of identities, delegation and authority in the adapter" by binding memory to the platform identity design (`notes/identity-binding-proposal.md`): issuer, subject and submitter are identity cells resolved through the owner registry; the representation basis is a registry grant; rotation and revocation follow the cell's spending rules. Taken as a direction for the adapter and the book chapter.
- **Decision (Ivan, in session):** «да».
- **Scope:** the Swarma adapter contract only (`spec/adapters/swarma.md`, package 0.2.7-draft); the kernel and its vectors are unchanged. It rests on the recorded owner decisions on identity cells (2026-10-17) and the owner registry (2026-10-18), cited in the note. The derivation of the cell id, including the self-certifying ID, is not part of this decision and stays with its own pending question.

## Proposed next steps (not decisions)

- **Done 2026-10-17:** the R7 package (`memory/spec/` 0.2.5-draft) and the adversarial collective (seven astra-max seats instead of a triad, by Ivan's order); both evaluators pass 57/57 canonical semantic vectors. R7-055 resolved by D-009; package 0.2.6-draft, both evaluators 66/66. Next: the platform book ch. 09 correction (D-001), then the documentary pilot on 10–30 Swarma decisions.

- **R7 package** first, from `designs/kernel.md`: closed schemas for the envelope and the five records, the view disclosure contract, the 17 + 27 vectors as executable fixtures, plus the review-1 gaps (`notes/review-1-gaps.md`: corpus coverage, incompatibility rules, S28/S29, `premise_quality`, source availability states).
- **Adversarial triad** after the package, under the Codex-only spawn policy: an independent evaluator implementer (`gpt-6.1-sol`, high) that reads only the package, and a divergence-case writer (`gpt-6-astra`, medium); every divergence becomes a package fix or a new vector. The evaluator becomes the core of the pilot's read-only adapter.
- **Pilot metrics** added to the collective's list: corpus maintenance cost, actualization latency, and a working-task check (does a fresh agent bring back a superseded decision; does it notice the real dependents).
- **Platform book ch. 09** correction for D-001, through the wiki's PR flow.
