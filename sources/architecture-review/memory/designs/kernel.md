# Bounded evidence memory: kernel contract

Owner: the memory lane (`ivmbp_swarma-memory_orch`). Status: **draft v0.2, 2026-10-17** (v0.2 adds review 3: snapshot applicability, lineage completeness, declassification evidence, three distinct conflict outcomes, projection exclusion, the normalized input tuple), normative direction for the R7 package (D-007); not a released specification and not implemented. This document consolidates the collective's design and the later inputs into one kernel contract. It changes no meaning of the collective's assembly except where a section says "amends".

Sources, in precedence order where they differ:

1. Owner decisions `memory/DECISIONS.md` (D-001…D-008).
2. This document.
3. `designs/bounded-support-semantics-astra-03.md` @ 9bafff8 (the companion; its §§3–6 and vectors S01–S27 stay normative unless amended here).
4. `designs/bounded-evidence.md` @ 5d96e70 (stores and authority table, profiles, APIs, boundary vectors).
5. Inputs and reconciliations: `inputs/REVIEW-1.ru.md` with `notes/review-1-gaps.md`; `inputs/USECASE-PROFILES.ru.md` with `notes/usecase-profiles-gaps.md`; `inputs/REVIEW-3.ru.md` with `notes/review-3-gaps.md`.

## 1. Scope

The kernel answers one question: **which admitted sources and explicitly registered reasoning support or oppose a precisely scoped assertion, from whose perspective, at a named cut, under a named projection rule?** It never answers what is true, who may act, or which decision to adopt. An empty result never proves falsity.

The kernel is domain-free (D-002). It knows records, schemas by reference, projection rules, lineage and disclosure constraints. It does not know decisions, people, agents, profiles, intents, catalogs or matching. Those are **domain packages** above the kernel: a domain package supplies schemas and projection rules, and its own services (a publisher, a catalog, a matching layer) consume views. A domain package never widens the kernel's authority: knowledge grants nothing, starts nothing, wakes nothing and sends nothing.

Portability is a conformance requirement: the same **normalized input tuple** — admitted corpus, exact schema and projection-rule versions, perspective, authorized projection, evaluation cut and logical budget — yields an equivalent semantic result with or without Swarma's dispatcher, board and session host. Equivalence is modulo the declared normalization of fresh opaque handles; implementations given different cuts or rights are not expected to agree. Profiles (documentary, protected service, embedded) differ in authentication and isolation guarantees, never in the meaning of any output field.

## 2. The record envelope (amends: attribution roles)

Every record of every kind carries one envelope. Fields marked *intake* are set by authenticated admission, never by the client.

| Field | Meaning |
| --- | --- |
| `id`, `version` | Opaque within a typed issuer namespace; immutable |
| `kind` | `assertion`, `source`, `justification`, `assessment`, `revision` |
| `schema` | Exact domain schema id and version (§4); required for `assertion` |
| `subject` | What or whom the record is about: an opaque subject handle in the record's space (§9.4) |
| `issuer` | Who answers for the content: the principal whose statement this is |
| `submitter` *intake* | Who technically entered it, from authenticated intake |
| `representation_ref` | When `submitter` ≠ `issuer`: a reference to the delegation record held by the deployment's policy owner, checked at admission; memory stores the reference and the check result, never a delegation registry of its own |
| `perspective` | Whose model of the world this expresses (the issuer's own, an observer's, a team's) |
| `admission_class` *intake* | One of §8's classes |
| `space` | The policy scope; a reference to the deployment's policy owner, not a registry |
| `valid` | Half-open `[from, to)` in the domain, explicit precision; `unknown` is a value, never an invented time |
| `confirmed_at` | When the issuer last stated or confirmed it (§6.3) |
| `recorded` *intake* | Writer-assigned admission sequence and UTC time; protected metadata |
| `lineage` | Content-derivation inputs (§7.1); separate from justification edges |
| `disclosure` | Constraints inherited from inputs plus any admitted declassification (§7) |

Three cases that must stay distinguishable through every summary, index, export and publication:

- the issuer states something about itself (`subject` = `issuer`, perspective = own);
- a representative relays the issuer's statement (`submitter` ≠ `issuer`, valid `representation_ref`);
- an observer records its own hypothesis about the subject (`issuer` = observer, perspective = observer).

A `representation_ref` that fails its check is a refusal, not a downgrade into the observer's own statement.

## 3. The five records

The collective's five shapes stay; this section fixes their fields on top of the envelope. (The companion calls `assertion` "claim" and `source` "SourceRef".)

1. **Assertion**: a schema-typed proposition about `subject` with `statement_kind` taken from the schema (§4): `fact`, `self_declaration`, `proposal`, `decision_record`, `intent`, `assessment_summary`. A claim that an authority decided something is a `decision_record` assertion and resolves to that authority's receipt (§5.3).
2. **Source**: owning system and kind, object id, exact revision or committed sequence, digest where available, provenance class, availability (`resolvable`, `unavailable`, `erased`). A reference grants no access to its target. Retaining an excerpt needs its own retention admission. One source class is new: **direct declaration** — "the issuer stated X through an admitted channel" — a first-class source with no document behind it.
3. **Justification**: signed polarity, target assertion version, premises (source references or registered assertion versions), rule id and version, edge role (`documentary_basis`, `review_on_change`, `sufficient_support`). Unchanged from the companion.
4. **Assessment**: an immutable result of a named check or reviewer with exact subject, rule, policy and environment pins. Kinds: `source_binding`, `signature`, `test_result`, `formal_entailment`, `semantic_review`, plus two used by domain packages without kernel meaning: `account_control` and `declassification` (§7.2). An LLM assessment is `semantic_review` and cannot mint any other kind.
5. **Revision**: names an exact prior version and one relation: `replace`, `withdraw`, `correct`, `challenge`, `availability`. It never rewrites old bytes. Who may issue which relation is §5.

`View` remains a derived response, not a sixth record. `Publication` is not a kernel record at all (§9).

## 4. Domain schemas (amends: closes review 1 §2.2 and profiles A1)

The kernel's record format is fixed; an assertion's content is governed by a named, versioned domain schema. A schema declares:

- exact field types and equality; natural-language sameness is never identity;
- `statement_kind` and what the kind may and may not imply (an `intent` is not a commitment; a `self_declaration` of competence is self-assessment, not established competence);
- **cardinality** per subject and perspective: `single` (a new value is a candidate replacement) or `multi` (values coexist: two interests never conflict);
- **incompatibility rules**: when two assertions under this schema oppose each other — same subject, overlapping valid time, same perspective, and a named field relation. Without such a rule two assertions never form a conflict; a model's "these may conflict" is a `semantic_review` assessment, never a deterministic opposition;
- **freshness default**: the `usable_until` horizon consumers start from (§6.3), or `none`;
- disclosure defaults per field class (for example "exact location: never public").

A schema is data, never executable code. An unknown schema or version is refused with a typed error (companion S18). Schema governance is the domain package's; the kernel only checks admission against the exact version.

## 5. Revision authority and ordering (amends: closes review 1 §2.3 and profiles A2/A3)

### 5.1 Sequences

An **assertion sequence** is the chain of versions issued by one issuer for one subject, schema and perspective (and, for `single` cardinality, one slot). `replace`, `withdraw` and `correct` are valid only from the sequence's issuer or a submitter with a valid `representation_ref` for that issuer. Anyone else may `challenge` or issue an assertion in their own sequence. Consequences: another agent's later record never replaces my self-description; an agent never supersedes an owner's decision record.

### 5.2 Concurrency

`revise` carries `expected_version`. If the sequence head is not that version, the result is a typed `version_conflict` and nothing commits. Two representatives editing from one version: the first commits, the second gets the conflict (vector P10). There is no last-writer-wins, and recorded time never orders authority.

### 5.4 Three outcomes that are never the same thing

| Outcome | Where it appears | Means | Never implies |
| --- | --- | --- | --- |
| `version_conflict` | Refusal of a write | The write was based on a version that is no longer the head; nothing committed | That the knowledge is contradictory; it creates no record about the subject (P14) |
| `ambiguous_current` | A projection result | The authority's record gives no order between two current candidates | A write error, or opposition between the candidates |
| Evidence conflict | Per-polarity result: `witness: present` on both polarities | Admissible support and opposition both exist | That either record should have been refused; both stay stored |

APIs and renderings keep these three distinct; a client may not map one onto another.

### 5.3 Decision currentness

For a `decision_record`, the current decision is a projection of the deciding authority's own ordered record (the commit order of a reviewed decision register, the board's revision), cited by exact revision. Memory-side replacements without that authority's receipt stay `proposal`s. Two receipted replacements of one decision with no order between them in the authority's record yield `ambiguous_current`, listing both; neither wins by learned-at time. A decision learned late keeps its authority order, not its arrival order (vectors S28, S29).

## 6. Evaluation and views (amends: corpus coverage, premise quality, freshness, availability)

### 6.1 Per-polarity result

The companion's per-polarity record becomes:

```text
{ witness:            present | not_found,
  evaluation:         complete | incomplete,          -- over the registered authorized graph
  corpus_coverage:    unknown | declared(ref),        -- how fully records represent their sources
  premise_quality:    clean_path | conflicted_premises_only | not_fully_checked,
  evidence_qualification,
  source_state:       resolvable_now | prior_assessment_only | independent_attestation,
  freshness:          fresh | stale | not_applicable,
  authorized_snapshot_handle,
  dependency_coverage: registered_only }
```

- `evaluation: complete` is a promise about computation over registered, authorized records at the cut. It never implies `corpus_coverage`: three registered grounds evaluated completely do not exclude a fourth unregistered one in the document (S30). Candidate retrieval (search, top-k) and witness evaluation are separate operations with separate promises.
- `premise_quality` must survive every rendering. A compact view that drops it is non-conforming (S03 extended, S31).
- `source_state` says what can still be presented: the source resolves now; only a prior immutable assessment survives; or an independent sufficient attestation exists (S32).
- **Witness roots.** A witness is identified by its root origin. Copies of one root (reimports, mirrors, catalog copies, paraphrases) are one witness for any qualification that claims independence (P07).

### 6.2 Projection rules

A view is computed under a **named, versioned projection rule**, supplied by the kernel or a domain package. A rule fixes which issuers and perspectives count, the time cut, how sequences resolve (§5) and the freshness policy. The kernel defines three rule families; domain packages instantiate them:

- `issuer_current`: the issuer's current statements about a subject (self-description; a decision authority's current decisions);
- `observer_model`: one observer's own assertions and assessments about a subject;
- `audience_projection`: the subset of an `issuer_current` view admitted for a named audience and purpose under §7.

The kernel never picks a "true profile" or "real decision" by counting witnesses or by model confidence.

### 6.3 Freshness

Three times stay distinct: when the proposition holds (`valid`), when the issuer last stated or confirmed it (`confirmed_at`), and until when a consumer will use it without refresh (`usable_until`, from the schema default or the query). Past `usable_until` an item is `stale`: refresh needed, never false, never negative evidence (P04). Intents and availability normally carry a horizon; architecture decisions normally carry none.

### 6.4 Frozen views and snapshots

A frozen view (including a session-start snapshot) is immutable **as a historical artifact bound to its cut**. Its bytes never change; its applicability does. Two cases stay separate:

- **Knowledge moved on** (a decision replaced, a new assessment, `usable_until` passed): the snapshot stays valid history; current state comes from a fresh view. A snapshot item is always rendered with its cut, never as "now".
- **Use or disclosure was revoked** (an intent closed, onward disclosure revoked, content erased): the component that performs the next delivery or external effect applies current policy and either refuses that operation or rebuilds an admitted context. Memory only reports the change; it never restarts, re-prompts or stops an agent. A cache or prompt-cache optimisation never extends a permission (P12). Bytes already delivered to a model are not recalled.

## 7. Disclosure and derived information (amends: profiles A4)

### 7.1 Lineage taint

Every derived record (summary, excerpt, paraphrase, embedding, index entry, cached view, match result) carries its content lineage and **inherits the disclosure constraints of all its inputs**. A label cannot lift them: an agent that read a private record and wrote a paraphrase marked public produces a record that is still private (P11). The same lineage drives erasure (unchanged from the collective).

**Declared lineage is not complete lineage.** The evidence an agent cites is not a list of the content it used. Lineage is computed by the integration from the inputs it controls: for a deterministic transformation, the exact inputs it read; for model output, everything the adapter supplied to that model call (context, tool results, recalled views) as declared by the integration profile. A derived record whose lineage the integration cannot establish carries `lineage: unknown` and is treated as inheriting the most restrictive constraints of the inputs the adapter did supply; it is never publishable by default (P13). The kernel promises lineage only within the integration profile's declared tracking; it makes no claim about what a model knew otherwise.

The first publishing path assembles a card only from admitted structured fields of an `audience_projection`. Free text written by an agent enters only as a `semantic_inference` proposal with its own admission.

### 7.2 Declassification

Releasing a result computed over private inputs (a city from private coordinates; "will consider the offer" from private preferences) requires a **declassification decision** by the policy owner of each constrained input. A `declassification` assessment is **evidence of that owner's decision**, pinned to the exact inputs, the transformation, the output schema, the audience and the purpose. It is not an authority and does not replace the check before each new disclosure that the decision still applies. A model's judgement that a paraphrase is safe is a `semantic_review`, which can only propose a declassification. When inputs carry constraints of several owners, each owner's decision lifts only that owner's constraint. The released output is a new assertion whose lineage is protected; the audience can verify the issuer's statement, not the hidden derivation (P05). Memory records the decision; it never makes it.

### 7.3 Non-interference

Unchanged and not weakened: hidden records must not change disclosed statuses, counts, ranking, cursors, coverage or change notices; logical budgets count authorized work only (companion §4, S13, S24, S27). An answer to a private compatibility query is a separately authorized disclosure (§7.2), never hidden influence on a public view. Rate limits on repeated probes belong to the domain layer that answers them.

## 8. Admission classes (amends: profiles A6)

| Class | Example | Default acceptance in the pilot (D-004) |
| --- | --- | --- |
| `self_declaration` | Issuer states a fact about itself through an admitted channel | Human review |
| `imported_publication` | A card or record from another issuer's publication, via a catalog | Quarantine until human review; attributed to the catalog and to the original issuer |
| `machine_observation` | A deterministic check, a tool result, a distiller output | Human review; no raw journals (D-005) |
| `semantic_inference` | A model's proposal or hypothesis | Proposal only, human review; never promoted to another class |

The acceptance path per class is policy, not kernel; the class itself is kernel and survives every derivative. Steady-state automation per class is decided after the pilot (D-004).

## 9. Boundary with publication (amends: profiles A5)

### 9.1 Roles

Memory computes an admitted `audience_projection`. A **publisher** (domain service) issues a publication from it. A **catalog** stores and indexes publications. Another participant's memory imports a publication as an `imported_publication` source. Memory never owns publications, catalogs or ledgers.

### 9.2 What the boundary fixes

- A publication has its own id and revision and exposes no memory ids, hidden links or global cuts.
- Memory keeps a protected link from each publication to the view it came from, for refresh and erasure.
- Reimport never raises confidence (§6.1 witness roots).
- A stale publication never returns as current: an importer uses known replacements, `usable_until` and current-version checks with the issuer; without them it knows only the last state it received.

### 9.3 Four distinct operations

| Operation | Effect | Does not imply |
| --- | --- | --- |
| Revise the assertion | New version in the issuer's sequence (§5) | That the old one was false |
| Revoke onward disclosure | Future views and sends for that audience refuse; send-time recheck (P06) | Unpublishing copies already sent |
| Unpublish | Publisher withdraws its publication | Erasure of stored content |
| Erase stored content | Custody-lineage erasure inside the controlled boundary (collective §6) | Deletion at independent recipients |

A space or audience owner may also **exclude** another issuer's record from its own projections (a person drops an organisation's attestation from their public card) and erase its locally stored copy under its policy. Exclusion is a projection-rule choice, not a revision: the issuer's record and its sequence stay as they were (P15).

### 9.4 Subject handles

A subject's internal id is never its public id. Each space and audience projection gets its own subject handle; linking two handles of one subject (a professional and a personal profile) is itself a disclosure under §7.2, never a side effect of a shared store (P09).

## 10. Platform boundaries (unchanged)

The stores and authority table of `designs/bounded-evidence.md` stands: memory cites user manager, broker, dispatcher, session host, board, keeper, a2a/bridge and Curator by exact revision and replaces none of them. Memory reaches an agent only as data, never as a Curator overlay, `AGENTS.md`, skill root or machine base context. **In the first slice it reaches an agent only as an explicit tool result** (pull); there is no automatic seeding and no change to `swarm-handoff/2`. The session-start snapshot is a later adapter mechanism: D-001 fixes its channel (a separate data block with per-item provenance), not its arrival in the first slice, and §6.4 governs its applicability. Stop, park, revocation, recovery and acceptance never wait for memory.

## 11. Two scenarios on one kernel

### 11.1 Architecture decision continuity (the pilot)

Domain package `decisions`: schemas `decision` (`decision_record`, cardinality `single` per decision slot, no freshness horizon), `rule` (`fact` about a platform rule, valid intervals), `assumption` (`fact` registered by a document, multi). Sources: reviewed documents at exact git revisions; the decision register's commit order is the authority order (§5.3).

- "Archive the home by default" and "retirement deletes the home" are two versions in one `decision` sequence issued by the owner; `issuer_current` returns the delete-home decision with its receipt, and the old version stays traceable.
- Documents that registered the archive-home rule as an assumption carry `review_on_change` edges and come back as stale dependents.
- An agent's later note claiming the old rule is current is an observer assertion or a `challenge`; it cannot replace the owner's sequence (§5.1).
- A late-arriving earlier decision keeps its place in the register's order (S29).

### 11.2 Profiles and discovery (the second consumer, synthetic corpus first)

Domain package `profiles`: schemas `interest` (multi), `competence` (multi; `self_declaration` vs evidence-backed assessments), `location` (`single` per kind: residence, current, work area; short freshness; exact values never public by default), `availability` (horizon), `intent` (`intent`; horizon; never a commitment), `account_link` (needs an `account_control` assessment to be more than claimed), `relationship_status` and `open_to_introductions` as separate schemas with no rule deriving one from the other.

- The owner's self-description is an `issuer_current` view; its agent relays updates only with a `representation_ref` (P02).
- The agent's guess about the owner's interest is an `observer_model` record (P01); another agent's later assessment stays in its own sequence (P03).
- A discovery card is an `audience_projection` handed to a publisher (§9); the city is released by declassification, the coordinates never (P05).
- Matching, contact policy, introductions, catalogs and any ledger role are the domain layer above the kernel, not kernel features.

Real personal profiles never go into the git register (D-003) and wait for the protected service (D-006) and its security qualification. Relationship, romantic intent and location are high-risk data: the domain layer defaults to no exact public location, explicit adult opt-in for romantic introductions, mutual consent before contact details, and mutually confirmed partner links only.

## 12. Vectors added by this document

Inherited: companion S01–S27 and the design's 17 boundary vectors. New:

| ID | Input | Expected | Forbidden |
| --- | --- | --- | --- |
| S28 | Two receipted replacements of decision A with no order between them in the authority record | `ambiguous_current` listing both | Later learned-at wins |
| S29 | Decision D1 learned after D2, though the register orders D1 first | D2 current, D1 historical in authority order | Arrival order decides |
| S30 | Three registered grounds evaluated completely; source holds a fourth | `complete` + `corpus_coverage: unknown` | "All grounds" claimed |
| S31 | S03 rendered as a compact view | `premise_quality: conflicted_premises_only` present | Compact view drops the qualification |
| S32 | Source erased; prior signature assessment retained | `source_state: prior_assessment_only` | Shown as freshly verified |
| S33 | Unknown schema version on an assertion | Typed refusal | Closest known schema applied |
| P01 | Agent records an inferred interest of its owner | Observer-perspective hypothesis issued by the agent | Owner self-description |
| P02 | Representative updates the owner's self-description without a valid `representation_ref` | Refusal | Assertion issued as the owner |
| P03 | Another agent's later assessment of the owner | Separate observer sequence; self-description unchanged | Replacement of the owner's sequence |
| P04 | Location confirmed 30 days ago, `usable_until` 7 days | `stale` | Shown as current; shown as false |
| P05 | City declassified for publication, coordinates private | Card carries the city as a released assertion | Coordinates or their lineage in the projection |
| P06 | Disclosure revoked after the card was prepared, before sending | Send-time recheck refuses | Earlier check reused as standing permission |
| P07 | One self-declaration imported through three catalogs | One root witness, three attributed copies | Three independent confirmations |
| P08 | Sensitive assertion erased | Derived summaries, caches, controlled exports found through lineage | Survives without a logical edge |
| P09 | Two subject handles linked in private space | Public projections stay unlinkable | Link leaks via ids, digests or shared references |
| P10 | Two representatives revise from the same `expected_version` | First commits, second `version_conflict` | Silent last-writer-wins |
| P11 | Agent paraphrases a private record and labels it public | Derived record inherits private constraints | Label lifts the constraint |
| P12 | Onward disclosure revoked after a snapshot was built, before the next delivery | Next delivery refuses or rebuilds; snapshot stays as history | Snapshot or prompt cache extends the permission |
| P13 | Agent used private input A and public card B, cites only B | Lineage from the adapter includes A; result not publishable | Cited evidence taken as complete lineage |
| P14 | Two representatives' updates collide on `expected_version` | Second write `version_conflict`; no record about the subject; no evidence conflict | Write conflict reported as contradictory knowledge |
| P15 | Owner excludes an organisation's attestation from their public card | Card omits it; the organisation's record and sequence unchanged | Exclusion recorded as revision or withdrawal of the issuer's record |

P09 explicitly includes the case of two cards that share no fields but would share one global subject id: the public handles must differ and the link stays private.

## 13. Left for the R7 package

Concrete closed JSON schemas for the envelope and the five records, including the three conflict outcomes as distinct codes; canonical bytes and digests; the projection-rule grammar; the `decisions` and synthetic `profiles` domain schemas; machine-readable fixtures for S01–S33, P01–P15 and the boundary vectors, with semantic and protected-deployment vectors reported separately; authorization and evidence-policy vocabulary; numeric resource envelopes as deployment inputs.
