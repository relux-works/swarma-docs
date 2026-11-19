# Open decisions for the Swarma Link, Talk and Forum books

| Question | Current text | Owner of the decision |
| --- | --- | --- |
| Binding of a Nostr key to an identity | The laboratory landlord/agent profile defines optional root Nostr metadata and a separate discovery mirror. The complete client identity document and general resolver remain open; transport selection still requires its own qualification | Owners; profile maintainers |
| An agent issuing a child grant | A separate scheme; the current verification contract does not allow it. Owner position: an agent must not differ from a human at the cryptographic level | Both owners |
| Sender name in the first-contact notification | Owner scheme decided 2026-11-07; whether the name fits depends on the measured `OP_RETURN` limit, fallback is names registered to the sender address | Owner, after the measurement |
| Contract amendment, late-anchored offers, early-end settlements, organization's first administrators and rule versions, display of a room mode change | Named as open in the state chapters; the contract-seal termination rule and framework cascade are decided, not open | Owners |
| Exhaustion and continuation: period accounting versus a new grant per period | LIP-0031 section 5 at specification v0.1.61 requires a new grant per period for long-lived agents. Its relation to both LIP-0008 section 2.1 sentences on the whole term and periods without a new grant remains open. The proposed reconciliation has no interim force; report recipients, carrier and form are also open | Specification owners |
| Scope and exact forms of contract seals | LIP-0017 at specification v0.1.61 requires confirmed seals for every framework and every contract a v4 grant binds. Whether C12 also reaches v3, whether C11 removes the seal choice for a non-framework contract without grants, the scripts, termination-statement bytes, framework-document presentation and resolution, node reads and spent-seal step, code and closure remain open | Specification owners |
| Own zone and its namespace rule | `.bit` for experiments; own zone after 2026-11-17, proposal written in parallel | Owners, after ICANN string confirmation |
| Chain-only revocation profile against the agreed keyvault contract | Target profile in the book; the agreed contract stays until both owners change it | Both owners |
| Autonomous agent entities running nodes | Named as open in the state chapters | Owner's message is pending |
| Adoption of the landlord-grant and locator profiles | Specification 0.1.4 reconciled the LIP-0004/0005 drafts with the landed framed writer and the optional root Nostr metadata; both remain Draft and are not normatively adopted | Specification owners |
| General grant-gated service specification | LIP-0006 is published as a Draft since specification 0.1.4 and describes the wallet service v1 profile only; a common action vocabulary, a registry of service types and real host qualification remain open | Specification and host owners |
| Signing of release tags | Draft RCs: GitHub pre-release, unsigned tag on a signed commit; final releases signed by the owner | Decided |
