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

## D-011…D-014. The first working version (2026-10-18)

- **Question put:** the architecture draft `notes/v1-architecture-draft.md`, decisions 1, 2 and 6, plus revising D-006.
- **Decisions (Ivan, in session, voice transcript):** «Продолжить запись. Да.» (autonomous writing); «D006, тогда надо пересмотреть, да, нам нужно, чтобы память работала автономно»; «Пространство агента, проекты и платформа. Ну, если это про то, что это у нас гид, то да» (it is git); «Про Go один репозиторий … ядро CLI и Skill, э, да, утверждаю».

### D-011. Memory is written autonomously

Agents write memory themselves, from the evidence they see and read; no approval gate. Humans write through the same path under their own identity, or ask an agent to. This replaces the human review gate of D-004 for every space. The epistemic limits stay: attribution to issuer and perspective, no replacement of another issuer's sequence, no adopted decision without the deciding authority's receipt, delivery as data only, and no raw journal intake (D-005).

### D-012. Autonomy does not require the protected service

D-006 no longer counts autonomous writers as a trigger for the protected service. What the service remains for is tied to the v1 trust model (proposed: sensitive data, guaranteed erasure, enforcement before write).

### D-013. Spaces: agent, project, platform, each a git repository

Each space is a git repository with a policy file. Where an agent space is hosted and what happens to it at retirement are proposed separately (`notes/v1-architecture-draft.md`).

### D-014. Go, one repository

One new repository `swarma-memory` in Go: kernel module, the `memory` CLI and the skill. Curator installs the CLI through the skill. Separate modules can be split out later.

## D-015…D-021. Agent memory, session excerpts, keys, sync, trust, conflicts, v1 scope (2026-10-18)

- **Question put:** the second design round in `notes/v1-architecture-draft.md` (agent memory class, promotion, signatures, archive, sync, shared memory, trust model).
- **Decisions (Ivan, in session, voice transcript):** «ок» (agent memory class); «только кусочек который был записан в сессии должен стать дискретной сущностью … но в идеале сохранять референс на нее в виде идентификатора сессии и индекса сообщения»; «временно, пока вся сварм не готова, да, мы можем агенту выдавать свой ключ. Точнее, агент сам себе генерирует ключ»; «синхронизацию берем»; «Если напираемся на конфликт … выводится на эскалацию, и ответственные за конфликты … разрешают конфликт, дальше работа происходит»; «Про модель доверия … Берем»; on scope: «Пока склоняюсь к тому, что агенты, которые наши, доверенные, имеют память, и мы ей управляем. Агенты приходят, которые со стороны. Наверное, они как бы эфемерные сущности без памяти» with the request to record the questions and risks.

### D-015. Agent memory is its own class

The agent's own working knowledge (observations, choices made in its work, rejected hypotheses) is the class "agent memory", held in the agent space (owner, issuer and perspective = the agent). It is not personal data about people.

### D-016. What comes from a session is a discrete record with a session locator

When an agent records something from a session, the record carries that piece itself (the statement or an admitted non-sensitive excerpt), because the session may be deleted. It also keeps a source reference to the session: runtime, session id and message position (the message id where the runtime has one, otherwise the message index in the session's stored sequence) plus a digest of the message. If the session is later deleted, the record stays and its source becomes unavailable. This is an agent-authored record, not raw journal intake (D-005 stands).

### D-017. Temporary per-agent keys until the key holder exists

Until the platform key holder exists, each agent generates its own signing key and signs its records with it. The key holder replaces this when it arrives.

### D-018. Sync protocol

The engine provides `memory sync`, per-space cursors and `memory changes --since`; the skill tells the agent when to use them: sync and recall at task start, sync before every write, changes at checkpoints and before finishing, write what was learned at the end. A space directory in the platform space maps identities and projects to space locations and access.

### D-019. Trust model of the first version

Every record is signed by its submitter; every reader verifies signature, schema, the space policy and revision authority, and ignores (but reports) records that fail. The protected service stays for sensitive data, guaranteed erasure and enforcement before write.

### D-020. Conflicts that affect further work go to escalation

A conflict between decisions that the current work depends on is not left standing as two parallel views. The work step that depends on it stops and the conflict is escalated to those responsible for resolving it, when they are part of the trusted system; they resolve it with a new decision, and work continues. Memory itself still escalates and wakes no one: the agent or orchestrator that meets the conflict raises it through the platform's escalation path. The resolution supersedes the conflicting decisions under the existing order rules.

### D-021. Scope of the first version (owner's leaning, open questions recorded)

Our own trusted agents have memory, and the owners manage it. Agents that come from outside are ephemeral and have no memory of their own in the first version. The questions and risks this leaves are recorded in `OPEN-QUESTIONS.md`.

## D-022. Memory of external agents follows their identity (2026-10-18)

- **Question put:** a five-step scheme for external agents' memory: identity verified at admission; a local identity; guest writes in the project space; a returning agent sees its earlier records; knowledge stays with the project unless the project owner exports it.
- **Decision (Ivan, in session):** «Это мне нравится, берем.»
- **Correction (confirmed below):** steps 2 and 3 as first put (a one-off local identity from our key holder; signatures with that local key) contradict the decided platform design: an external worker does not use our key holder, brings its own keys and signs on the donor side in its bridge (book «Ключи и ключник», «Внешняя личность»), and nothing is signed blind (platform decision 57). The decision is therefore recorded in the platform-compatible form:
  1. Admission into the project verifies the agent's external identity: public keys and the attestation chain to its owner's root. We never hold its private keys; on our side it has only an authorization context.
  2. It writes into the project space as a guest; its records are attributed to its identity cell id.
  3. It signs with its own key on its own side, in the donor bridge, never through a model tool; the bridge receives what it signs in full. First path: memory records inside the signed result export; a bridge message type for mid-task writes is a possible extension.
  4. A returning agent that proves it is the same identity sees its own earlier records in the project space again (the owner's default grant); memory follows the identity, not the key. Anything beyond that is a policy decision.
  5. Knowledge about the project stays with the project; giving it to the agent's owner needs a separate export by the project owner's decision.
- **Scope:** design direction. In the first version external agents still have no memory of their own (D-021).
- **Correction confirmed (Ivan, in session, 2026-10-18):** «подтверждаю от curator-14» — confirming his «да» given in the swarma-docs lane to the corrected form (the external agent signs with its own key in the donor bridge; its first memory records travel inside the signed result export). D-022 stands in the form above.

## D-023. Memory design is decided design, not implemented (2026-10-18)

- **Question put:** the swarma-docs book counts every former «предложено» item as decided design (owner's rule of 2026-10-18). Does this extend to memory?
- **Decision (Ivan, in session):** «Решено, не реализовано.» and «если вдруг у нас по результатам наших обсуждений какие-то будут дополнения, мы их внесем в книгу».
- **Meaning:** every element of the memory design that was marked as proposed (the kernel's data model and semantics, the normative package, the deployment profiles, the delivery and disclosure rules) is decided design, not implemented. Items that are open stay open (`OPEN-QUESTIONS.md`). Further additions from the design discussions go into the book as they are decided.
- **Next step held by the owner:** the architecture document of the first working version starts only on Ivan's separate go («Дождись моего отдельного Go на архитектуру первой рабочей версии»).

## Proposed next steps (not decisions)

- **2026-10-18, on Ivan's order** («можно сразу публичный. доска в отдельном репо - в приватном»): public code repository [relux-works/swarma-memory](https://github.com/relux-works/swarma-memory) created with the cleaned package 0.2.7 (c2627bf); private board repository relux-works/swarma-memory-board created with EPIC-261018-sjk2i0 memory-v1, STORY-261018-qlwnsw v1-architecture and STORY-261018-mcdun6 public-repo-bootstrap. The architecture document waits for Ivan's go.

- **Done 2026-10-17:** the R7 package (`memory/spec/` 0.2.5-draft) and the adversarial collective (seven astra-max seats instead of a triad, by Ivan's order); both evaluators pass 57/57 canonical semantic vectors. R7-055 resolved by D-009; package 0.2.6-draft, both evaluators 66/66. Next: the platform book ch. 09 correction (D-001), then the documentary pilot on 10–30 Swarma decisions.

- **R7 package** first, from `designs/kernel.md`: closed schemas for the envelope and the five records, the view disclosure contract, the 17 + 27 vectors as executable fixtures, plus the review-1 gaps (`notes/review-1-gaps.md`: corpus coverage, incompatibility rules, S28/S29, `premise_quality`, source availability states).
- **Adversarial triad** after the package, under the Codex-only spawn policy: an independent evaluator implementer (`gpt-6.1-sol`, high) that reads only the package, and a divergence-case writer (`gpt-6-astra`, medium); every divergence becomes a package fix or a new vector. The evaluator becomes the core of the pilot's read-only adapter.
- **Pilot metrics** added to the collective's list: corpus maintenance cost, actualization latency, and a working-task check (does a fresh agent bring back a superseded decision; does it notice the real dependents).
- **Platform book ch. 09** correction for D-001, through the wiki's PR flow.
