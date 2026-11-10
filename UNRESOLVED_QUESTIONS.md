# Open decisions for the Swarma Link, Talk and Forum books

| Question | Current text | Owner of the decision |
| --- | --- | --- |
| Binding of a Nostr key to an identity | The laboratory landlord/agent profile defines optional root Nostr metadata and a separate discovery mirror. The complete client identity document and general resolver remain open; transport selection still requires its own qualification | Owners; profile maintainers |
| An agent issuing a child grant | Open general sub-delegation mechanism. Owner position: an agent must not differ from a human at the cryptographic level. The signer-service capability is separate and does not decide the child-grant contract. | Both owners |
| Delegated grant issuance by a grant-gated signing service | Capability decided; explicit issuance authority, attenuation, parent closure, chain validation and byte format need a separate profile. The current v3 messaging key gains no issuance authority; the rental rehearsal does not exercise this capability | Specification owners |
| Sender name in the first-contact notification | Owner scheme decided 2026-11-07; whether the name fits depends on the measured `OP_RETURN` limit, fallback is names registered to the sender address | Owner, after the measurement |
| Contract amendment and termination, late-anchored offers, organization's first administrators and rule versions, display of a room mode change | Named as open in the state chapters | Owners |
| Own zone and its namespace rule | `.bit` for experiments; own zone after 2026-11-17, proposal written in parallel | Owners, after ICANN string confirmation |
| Chain-only revocation profile against the agreed keyvault contract | Target profile in the book; the agreed contract stays until both owners change it | Both owners |
| Autonomous agent entities running nodes | Named as open in the state chapters | Owner's message is pending |
| Reconciliation of landlord-grant and locator publication | Public LIP-0004/0005 text still describes bare output as the first implementation and predates optional root Nostr metadata; the landed rental profile writes framed output and supports that metadata | Specification owners |
| General grant-gated service specification | LIP-0006 is a published Draft with a wallet service v1 profile. Further service profiles, delegated issuance and real host qualification remain separate work | Specification and host owners |
| Signing of release tags | Draft RCs: GitHub pre-release, unsigned tag on a signed commit; final releases signed by the owner | Decided |

## Grant v4 and service declarations

The design requires signed per-rental limits mirrored by the contract, and
name recipients bound to an arbitrary Namecoin name plus its current owner key,
without an exact recipient-output pin. Same-owner recipient renewal/rotation
preserves the grant. The landlord name output is bound separately; every later
confirmed issuer-name operation closes authority, including renewal and return.
Current grantee-owner equality alone does not prove transfer-and-return history. Concrete executor name/key
bindings, per-executor partitions and shared replica journals bound the budget.
Draft LIP-0008 records these semantics without adopting bytes or code.

Open profile choices: exact grant/consent/signature/issuance encoding; owner-key
proof for supported scripts/current outputs and reorg handling; channel
profiles and reissuance after issuer updates; risk-tier freshness and node-health
criteria; recent-block construction bound; executor key/single-use encoding;
typed limit units,
bounds, prices and reservation/reconciliation rules. Draft LIP-0007 also leaves
service-member placement, receipt-key/endpoint encoding, action schemas and
strict-parser compatibility open. Current v3 and wallet v1 remain unchanged.

The lead's proposed 60/90-minute cutoffs await Ivan's decision; the decided
30-minute privileged-command stop remains current. The replacement remains under review. They do not change the
historical normative v0.1 STOP rule. The reported 137.2-day block-gap sample
is evidence about one observed chain history, not product availability.

Any Namecoin name is a confirmed recipient rule, with no namespace confirmation
pending. This is independent of the platform DNS-zone question. V4 selects W/L
construction through an authenticated chain pin. W permits only its validated
linkage/payment dependencies; L uses confirmed references and separate seal/anchor
stages. Exact pin/input/dependency validation, migration and vectors remain open.
A changed parent requires fail-closed reissuance. L is spec-only until a
non-SegWit chain is pinned; account-based chains need a separate seal design.

## Second external design review

| Open profile decision | Boundary |
| --- | --- |
| Issuer registration-instance and renewal rollout | Bind name/owner key/exact output across grant, agent pointer and independent verifier pins. Expiry/re-registration cannot inherit authority. Exact provisioning, update order and replacement consent remain open. |
| Typed signing and migration | Static audit at chain-lab 839bdcca found both issuer paths recompute authenticated contract hashes, with no demonstrated oracle. Landlord/provider/detached-v2 domains need matched producer/verifier migration under new versions and no legacy fallback; standard NIP-01/transaction preimages stay intact. Exact tags/bytes remain open. |
| Issuer mempool-spend evidence | A validated issuer-branch spend permanently closes for an observing executor across restart/replacement. Branch proof, replica propagation and anti-rollback recovery need a profile; grantee use and transient failure are distinct. |
| Value-dependent confirmation minimum | MAX of signed minimum and operator risk floor, with explicit chain/evidence classes. Numerical tiers and cross-chain payment risk policies remain open. |
| T/L/A under W and Legacy | W permits validated unconfirmed linkage/payment dependencies; Legacy requires confirmed inputs and separate stages. Namecoin anchors spend only NMC; BTC/LTC keep separate proofs. Name-output migration/self-reference, payment control, fees, consent and exact proofs remain open. No implementation result. |
| Topology and explicit no-block-wait mode | Chain evidence cannot constrain one operator against itself. A separate agreed profile needs signed mode selection; unavailable anchored evidence cannot trigger fallback. Data-operator trust remains external. |
| Per-seal derived keys and endorsement | Bind key/script/exact outpoint/context under issuer signature; derivation, custody and recovery remain open. Public funding/names/anchors can still link seals. |
| Next-format canonicalization and conformance | RFC8785 plan needs exact per-field integer ranges or decimal-string schemas, public canonical/signature/error/state vectors, runner and independent Swift implementation. No silent rounding or historical-byte migration. |

The next-build editorial queue preserves historical v0.1 while correcting its
book account, status/version references, size/order disagreements and vocabulary.
Core evidence precedes a 520-byte rule change. PDF layout/overflow checks belong
to the build owner. Delegation/UCAN research and journal implementation changes
are outside this writing unit.
