# Proposal: binding memory's identities and delegation to the platform identity design

Status: **accepted as D-010 on 2026-10-18** (binding only; the self-certifying ID stays a separate pending question). Raised by the swarma-docs editorial lane on 2026-10-18; written down by the memory lane. If accepted, it closes the open question "concrete bindings of identities, delegation and authority in the adapter" (book chapter 1.0, «Нерешённые вопросы»). The kernel does not change; only the Swarma adapter contract (`memory/spec/adapters/swarma.md`) does.

## Cited sources

All in the private repository `relux-works/swarma-docs`, branch `orch/editorial-opus`, commit `078e155c935df7bf6a20f001f9c37c7335654443`. The branch is not merged to main.

| Item | Where | Status |
| --- | --- | --- |
| Identity is a spendable cell: current keys, a hash of the next keys, a parent reference. Rotation spends the cell with the next keys; the external parent is a second spending path; revocation spends into a terminal cell; a rotation is effective from publication; identity state is part of consensus | `editorial/decisions.ru.md`, «Решения по Swarm Chain (17 октября 2026)», item 42 | Owner decision, 2026-10-17 |
| One owner registry service as the sole authoritative writer, a git journal for audit, signed snapshots no older than 60 s | same file, «Решения по листу 1–26 (18 октября 2026)», runtime bullet, item 8 | Owner decision, 2026-10-18 |
| Design rationale | `editorial/chain-post-ai.ru.md`, «Личность как расходуемая ячейка» | Rationale |
| Self-certifying identity (ID = hash of the first record); before the chain launches, its key event log lives in the owner registry with the same records, and IDs stay unchanged when published to the chain | — | **Not an owner decision**; proposed to Ivan, answer pending |

## Proposed binding

| Kernel field | Binding in the Swarma adapter |
| --- | --- |
| `issuer`, `subject` (principals) | Identity cell id |
| `submitter` | The authenticated identity cell of the caller, from the registry's current state |
| `representation_ref` | A grant record in the owner registry, checked at admission against the registry snapshot (no older than the snapshot bound) |
| Revocation of a representative | Spending the grant or the identity cell; later admissions refuse; existing records keep their history |
| Key rotation | No effect on record identity; signatures verify against the keys current at the record's admission |
| Policy authority events (decision order) | Events whose protected issuer is the deciding identity cell; issuer-local order applies unchanged |

Open points if accepted: snapshot staleness at admission versus at delivery; what memory records when the registry is unavailable (`unavailable`, never an implied grant); how a terminal (revoked) cell affects the current-state projections of its past self-declarations.
