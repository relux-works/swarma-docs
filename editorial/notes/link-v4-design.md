# Grant v4 and grant-gated services: editorial boundaries

This map covers the new design text, not a new implementation baseline.

| Text | Design authority and boundary |
| --- | --- |
| Link grant-gated service definition and seven examples | Owner design decisions dated 2026-11-10; examples grant no action. LIP-0006 wallet v1 retains its exact closed actions and bytes. |
| Delegated issuance | Decided capability with explicit issuance authority; attenuation, parent closure and delegation profile remain open. It is outside the current rental rehearsal. |
| Grant v4 limits and contract mirror | Draft LIP-0008; directly signed kinds include coin spending, model requests/input/output/cost, per-request maximum and signed default output. New kinds use separate LIPs. No canonical v4 wire is asserted. |
| Name-mode grantee | Owner input dated 2026-11-10: any Namecoin name plus its owner public key, checked before current channel keys; no exact recipient-output pin. Same-owner renewal/rotation preserve grants. Exact issuer output remains a separate closure rule. Current-owner equality alone gives no permanent grantee transfer-history proof. Unsupported owner proofs refuse. |
| Service self-declaration | Draft LIP-0007; logical type/actions/receipt key/endpoint only. Unknown member path and strict-parser upgrade remain open. Discovery cannot create receipt trust or action authority. |
| Model proxy | Independent chain observation is follow-on direction; current implementation trusts gateway binding and expiry. No MP3 or v4 implementation result is inferred. |

The chain-level diagram is conceptual and intentionally assigns no new JSON,
script or signature-domain bytes. V3 field diagrams and historical byte domains
remain intact. State rows retain decided/Draft/open boundaries.

## External-review triage refinements

Issuer-output binding makes issuer renewal/channel updates require reissuance.
The grantee retains the owner-name rule, allowing same-owner renewal/rotation.
Same validated state gives the same issuer spent-outpoint verdict; unavailable
reads refuse without permanent closure. Reorg
handling is profile work and completed-effect journals remain intact.

The executor is a concrete service name plus key; budgets are partitioned by
executor, single-use requests commit it and replicas share one authoritative
journal. Type discovery and old wallet-v1 bytes gain no such guarantee.

The reported 20000-block/137.2-day sample supports reviewing freshness policy.
The lead's 60/90-minute cutoffs await Ivan; the decided 30-minute stop remains
current. The reported 30-minute cost is 70.7 min/day over 137.2 days on one node.
No future availability bound or tested replacement behaviour is asserted.
LIP-0003's corrected seal-time paragraph is acceptance-only; the v4 recent-block
reference is a construction bound, not a wall-clock signing timestamp.

## W/L construction and confirmed namespace

Any Namecoin name is confirmed; no pending namespace choice applies to v4.
The 2026-11-10 follow-up selects construction through the authenticated chain
pin: W uses native P2WPKH/SIGHASH_ALL inputs, confirmed ordinary funding and
explicit validated unconfirmed linkage/payment dependencies. L references
confirmed outpoints and builds the anchor after the seal confirms; no
unconfirmed chains. The two share grant checks, with fail-closed reissuance
after a changed parent and no automatic fallback. Account-based chains need
a separate seal design. The input rule does not set the seal output script.
Current P2PKH funding meets neither W nor L qualification by script alone.

BIP141 supports txid/witness separation; BIP143 specifies the standard witness
preimage. BIP66's strict DER narrows encoding malleability, without guaranteeing
a stable legacy txid. Exact chain pins, dependency validation and migration
remain Draft profile work. W targets Namecoin first; L remains spec-only until
a non-SegWit chain is pinned. No latency or implementation result is asserted.

The lead's immutable-config decision assigns files to the administrator with service-
group read-only access (0640, directory0750), a pre-start hash check against
the sealed manifest and new reviewed packages for ceiling changes. The state
chapter records accepted design, with no implementation or host qualification.

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
| Issuance construction | W explicitly allows validated unconfirmed linkage/payment dependencies; T and A may share a block. Legacy waits for T confirmation before grant signing and A construction. Namecoin anchors spend NMC only; BTC/LTC retain separate proofs. Control, fees, consent, exact dependency validation and historical name-anchor migration remain open. An anchor name update still requires a non-circular, unspent signed name pin. No code/test or speed claim. |
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

## Follow-up authority and review corrections

Owner input of 2026-11-10: "принимаем любой ключ, который это имя перечисляет";
"только в рамках текущего владельца имени" and "всегда публ ключ на котором имя и само имя".
These retain the grantee owner-key rule; the issuer instance remains separate.
The same date's owner input asks for two protocols so chains without SegWit can
use the design. Profile details and config hardening are the lead's directions.
The config facts are the lead's 10 November decision, item4, also reconciled
against the immutable-boundaries proposal; accepted design is not deployed code.
General agent child grants remain open for both owners; the signer capability
does not resolve them. The two untraced booking/room examples are removed.
