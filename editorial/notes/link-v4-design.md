# Grant v4 and grant-gated services: editorial boundaries

This map covers the new design text, not a new implementation baseline.

| Text | Design authority and boundary |
| --- | --- |
| Link grant-gated service definition and nine examples | Owner design decisions dated 2026-11-10; examples grant no action. LIP-0006 wallet v1 retains its exact closed actions and bytes. |
| Delegated issuance | Decided capability with explicit issuance authority; attenuation, parent closure and delegation profile remain open. It is outside the current rental rehearsal. |
| Grant v4 limits and contract mirror | Draft LIP-0008; directly signed kinds include coin spending, model requests/input/output/cost, per-request maximum and signed default output. New kinds use separate LIPs. No canonical v4 wire is asserted. |
| Name-mode grantee | Any Namecoin name plus exact issuance-time name output and owner key; same binding for landlord output. Owner proof precedes channel keys; any confirmed operation closes, including renewal. Fresh observers need no private transition history. Unsupported proofs refuse. |
| Service self-declaration | Draft LIP-0007; logical type/actions/receipt key/endpoint only. Unknown member path and strict-parser upgrade remain open. Discovery cannot create receipt trust or action authority. |
| Model proxy | Independent chain observation is follow-on direction; current implementation trusts gateway binding and expiry. No MP3 or v4 implementation result is inferred. |

The chain-level diagram is conceptual and intentionally assigns no new JSON,
script or signature-domain bytes. V3 field diagrams and historical byte domains
remain intact. State rows retain decided/Draft/open boundaries.

## External-review triage refinements

Name-output binding supersedes the earlier owner-pin-only v4 draft: renewal and
channel updates require reissuance. Same validated state gives the same spent-
outpoint verdict; unavailable reads refuse without permanent closure. Reorg
handling is profile work and completed-effect journals remain intact.

The executor is a concrete service name plus key; budgets are partitioned by
executor, single-use requests commit it and replicas share one authoritative
journal. Type discovery and old wallet-v1 bytes gain no such guarantee.

The reported 20000-block/137.2-day sample supports reviewing freshness policy.
60/90-minute cutoffs are proposed, not accepted or tested product behaviour.
LIP-0003's corrected seal-time paragraph is acceptance-only; the v4 recent-block
reference is a construction bound, not a wall-clock signing timestamp.

## Witness funding and confirmed namespace

Any Namecoin name is confirmed; no pending namespace choice applies to v4.
The witness-only input requirement covers seal creation and issuance commitments,
not the seal output script. Third-party input signature malleability with legacy
funding can break the pre-signed txid reference and cause refusal, not unsafe
authority. Revocation tracks the consumed seal outpoint. Current P2PKH funding
is a compatibility gap, not an implemented migration. See BIP141 for txid/witness
separation and the pinned rental profile for current P2PKH funding policy.

## Second external review: successor design boundaries

Authority is the 2026-11-10 second-review triage, with all new rules kept in
Draft LIP-0008 and book target-state prose/status. The historical normative
protocol, decisions and conformance bytes retain their meaning.

| Item | Text and boundary |
| --- | --- |
| Registration-instance pin | Name/owner key/exact registration-update output in grant, agent landlord pointer and independent verifier pins. Expiry/re-registration cannot inherit authority. Renewal closes existing grants, then requires authorized pointer/pin updates, fresh consent and reissuance. The roughly 220-day key-access reminder is an operational proposal; chain block age is authoritative. |
| Signing | Distinct application tagged hashes and signing only digests recomputed from complete validated objects. Static audit at chain-lab 839bdcca found authenticated contract-hash recomputation in both issuer paths and no demonstrated oracle. Landlord/provider/detached-v2 domains need versioned matched producer/verifier migration without legacy fallback; standard NIP-01 and transaction preimages remain intact. Exact tag registry and bytes remain open. |
| Mempool revocation | Only a validated issuer-branch seal spend creates the new durable exception, including RBF/eviction/restart. Cryptographic branch classification and authoritative evidence/journal recovery remain open. A grantee use-spend alone does not create issuer closure; transient reads/tip changes retry/refuse. First observers cannot reconstruct an evicted spend. |
| Confirmation risk | Typed minimum uses MAX of signed requirement and operator floor. No invented tiers, amounts or cross-chain finality equivalence. BTC/LTC payments keep their separate proofs. |
| Issuance evaluation | T creates seal and L; A spends L, possibly in the same block. A spending the exact payment output is NMC-only. Control, fees, consent and proof remain open. SW1 native P2WPKH/SIGHASH_ALL candidate has an unresolved confirmed-input exception for L/payment and historical name-anchor migration. If A updates a name, signed name-pin/self-reference compatibility also requires a decision. No code/test or speed claim. |
| Threat/topology | One threat section and topology table distinguish publication gating, same-operator dispute evidence and explicit no-block-wait mode. No silent fallback; permission does not establish trust in a data operator. |
| Privacy | Per-seal derived key plus typed issuer endorsement of key/script/outpoint/context. KDF/path/custody/recovery remain open; funding, public names and anchor structure still link activity. |
| Historical profile | v0.1 frozen, including its false closures on seal-read failure/tip change. New working profile does not inherit them. Correcting the old book account remains in the next-build queue. |
| Conformance | Next-format RFC8785 plan with per-field exact-unit schemas, canonical/signature/error/state fixtures, runner and independent Swift implementation. These are deliverables to build, not results. Historical bytes are preserved. |

Primary references: [BIP340 tagged hashes](https://bips.dev/340/) and
[RFC8785](https://www.rfc-editor.org/rfc/rfc8785.html), read on 2026-11-10.
They support primitives and canonicalization constraints, not adoption of our
object tags or amount schemas. No new executable byte examples are supplied.
The triage's malformed Go ampersand statement is not copied.

LIP-0006 already labels the 32-record journal bound as laboratory-only. Wallet
implementation changes and delegation/UCAN research are separate work; no UCAN
adoption or delegation spike is part of this text.
