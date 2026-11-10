# Open decisions for the Swarma Link, Talk and Forum books

| Question | Current text | Owner of the decision |
| --- | --- | --- |
| Binding of a Nostr key to an identity | The laboratory landlord/agent profile defines optional root Nostr metadata and a separate discovery mirror. The complete client identity document and general resolver remain open; transport selection still requires its own qualification | Owners; profile maintainers |
| Delegated grant issuance by a grant-gated signing service | Capability decided; explicit issuance authority, attenuation, parent closure, chain validation and byte format need a separate profile. The current v3 messaging key gains no issuance authority; the rental rehearsal does not exercise this capability | Specification owners |
| Sender name in the first-contact notification | Owner scheme decided 2026-11-07; whether the name fits depends on the measured `OP_RETURN` limit, fallback is names registered to the sender address | Owner, after the measurement |
| Contract amendment and termination, late-anchored offers, organization's first administrators and rule versions, display of a room mode change | Named as open in the state chapters | Owners |
| Own zone and its namespace rule | `.bit` for experiments; own zone after 2026-11-17, proposal written in parallel | Owners, after ICANN string confirmation |
| Chain-only revocation profile against the agreed keyvault contract | Target profile in the book; the agreed contract stays until both owners change it | Both owners |
| Autonomous agent entities running nodes | Named as open in the state chapters | Owner's message is pending |
| Reconciliation of landlord-grant and locator publication | Public LIP-0004/0005 text still describes bare output as the first implementation and predates optional root Nostr metadata; the landed rental profile writes framed output and supports that metadata | Specification owners |
| General grant-gated service specification | LIP-0006 is a published Draft with a wallet service v1 profile. Further service profiles, delegated issuance and real host qualification remain separate work | Specification and host owners |
| Signing of release tags | Draft RCs: GitHub pre-release, unsigned tag on a signed commit; final releases signed by the owner | Decided |
