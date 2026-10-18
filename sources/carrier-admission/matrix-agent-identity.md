# Matrix accounts for agents by public key (proposal, 2026-10-15)

Goal: agents get Matrix accounts on relux.works without a shared registration token. Trust rests on public keys, so the same scheme later becomes part of Swarma (book v0.10, chapter 4 "Ключи и ключник": owner root, keymaster, admission records).

## What tuwunel v1.9.3 already supports (tuwunel-example.toml)

- `[global.jwt]`: JWT login (`org.matrix.login.jwt`). `format = "EDDSA"` (Ed25519 public key, PEM) or `ECDSA`; `register_user = true` creates the account on the first valid token; `issuer` and `audience` lists; `require_exp`, `require_nbf`. One verification key per server.
- `[[global.identity_provider]]`: built-in SSO (GitHub, Google, Keycloak, MAS ...). `registration = false` lets only accounts that an admin associated (`!admin query oauth associate`) log in.
- `[global.appservice.<ID>]`: inline appservices with exclusive user namespaces.
- `access_token_ttl`, `refresh_token_ttl`: short-lived access tokens with refresh.

## Proposal: a registrar with host keys

```
agent ──(1) "sign registration for ivmbp_curator_orch" ──> host key helper (root, Unix socket, SO_PEERCRED)
agent <──(2) signed request ──────────────────────────────── helper   (agent never sees the host key)
agent ──(3) signed request ──> registrar (in the cluster, HTTPS)
          checks: host key enrolled (git, PR-reviewed), name has the host's prefix, nonce fresh, exp <= 2 min
agent <──(4) JWT {iss: relux-registrar, aud: relux.works, sub: ivmbp_curator_orch, exp: +120 s} (signed Ed25519)
agent ──(5) POST /login type org.matrix.login.jwt ──> tuwunel (trusts only the registrar public key)
agent <──(6) access token + refresh token (no password stored anywhere)
```

- tuwunel: `allow_registration = false`; JWT with the registrar public key, `issuer = ["relux-registrar"]`, `audience = ["relux.works"]`, `require_exp = true`, `register_user = true`; access tokens of about a day plus refresh tokens.
- Registrar: a small HTTPS service next to the Matrix server (today that is our cluster; it runs equally on a VM or a Mac), signing key as a SOPS secret. Nothing in the scheme depends on Kubernetes. The enrollment registry is in git: one file per host with its public key and allowed name prefix (`ivmbp_`, `m1max_`). Adding a host is a reviewed PR; later a record signed by the owner key from the phone (book 4.5). Every issued token is logged.
- Host key: Mac, Secure Enclave key (P-256, non-exportable; the registrar verifies ECDSA P-256 too); Linux, TPM or a 0600 file behind a root helper. This is the phase-0 keymaster: agents ask it over a Unix socket and never hold the key.
- a2a CLI: `identity ensure` and re-login use steps 1-6 instead of the registration token and the stored password.
- Revocation: remove the host from the registry (no new logins), deactivate single users through the admin, short token TTL.

Result: no shared secret on any host; a compromised host can only mint names with its own prefix, and only until it is removed.

## Path to Swarma

- Replace host keys with Swarma identities: the keymaster derives the agent key (purpose'/product'/project'/agent'), the owner root signs it, and the registrar verifies the chain to the owner public root. The Matrix side does not change: it still trusts one registrar key.
- Swarma's bridge (agents do not read the carrier, chapter 6.2) can use one appservice per host with an exclusive namespace instead of per-agent logins.

## Humans

tuwunel's built-in GitHub SSO with `registration = false`: the admin creates @ivan, @alexis, @timur and associates their GitHub identities; nobody else can log in. Element shows "Sign in with GitHub". MAS is not needed for this.

## Where SOPS fits

SOPS keeps secrets in git encrypted to public keys: the registrar signing key and any appservice tokens (cluster key), and per-host secrets encrypted to that host's age key. The registration proof itself is a signature, not SOPS.

## Alternatives

| Option | Verdict |
| --- | --- |
| Shared registration token (today) | migration window only |
| Admin creates every account | fine for humans, does not scale for agents |
| Appservice per host | good for a Swarma bridge; per-host secret, not public-key based |
| Matrix Authentication Service | full OIDC; heavier than tuwunel's built-in SSO, not needed now |

## Work

Registrar (Go, small), a2a CLI JWT login path, tuwunel config, enrollment registry, host helper for macOS (Secure Enclave) and Linux. About 1-2 days of agent work; a seed for Swarma's broker/keymaster.

## Owner direction (2026-10-15)

Ivan leans to a separate repository from the start, as the seed of a Swarma module, not code inside a2a-swarm. The proposal goes to the curator lane for architecture review first.

## Questions for the review

1. Module name and repository (for example `swarma-registrar` or `swarma-identity`), and where it sits among the Swarma modules (broker, keymaster, dispatcher, session host).
2. Request format: canonical bytes and signature domain for the registration request, so it matches the planned `grant/1` and keymaster formats instead of inventing a third one.
3. Key types: Secure Enclave keys are P-256 (ECDSA), the keymaster plan is Ed25519 (SLIP-0010). The registrar would accept both for host keys and sign JWTs with Ed25519 (tuwunel `format = "EDDSA"`).
4. Enrollment record: today a reviewed git file (host, public key, name prefix); later a record signed by the owner root from the phone (book 4.5). Same schema for both?
5. Name derivation: prefix check now (`<host>_*`); later the name comes from the keymaster derivation path. Is the a2a name scheme `<host>_<project>_<role>` the one to keep?
6. Token lifetime and refresh policy for agent sessions (access token TTL, refresh TTL, idle vs absolute).
7. Operations: nonce store, rate limits, audit log of every issued token, and how the registrar's own signing key rotates (two keys published during rotation; tuwunel accepts one key, so rotation needs a short overlap plan).
8. Scope boundary: humans via tuwunel GitHub SSO (`registration = false`) stay out of the registrar.

## Review result (curator, 2026-10-16): approve with changes

Full review: (review file, working material). Module `swarma-registrar` (separate repo; scope = carrier admission, holds no keys), design record CIP-0019 in curator-spec `cips/` (draft, owner decision Ivan).

Required before build:
- R1: phase-0 boundary is host + OS user (all ivmbp lanes share one UID); the helper gets a SO_PEERCRED UID (optionally exe) to names map hook now.
- R2: cut-over resets or disables passwords of token-window accounts, logs out their devices and closes the registration token.
- R3: revocation = registry removal + logout/deactivation of every `<host>_*` user + audit since the last known-good time.
- R4: agents get no refresh tokens; access TTL 12-24 h; re-login through the signed flow on 401 (if refresh stays: absolute cap <= 7 days).
- R5: request = domain tag `swarma-registrar registration/1` + "\n" + CCJ-1 body; id = sha256(preimage); signature over the preimage outside the body. Body: type, key (`ed25519:` or `p256:` SEC1 compressed), name, aud, 128-bit nonce, iat, exp (<= 120 s). P-256: ECDSA-SHA256 raw r||s, low-S. Not grant/1. Canonical and negative vectors.
- R6: host labels `[a-z0-9-]` (no underscore); validate the localpart before signing; existing non-prefixed names (ivan-*) need per-name enrollment or a rename before cut-over.

Answers adopted: Ed25519 + P-256 host keys, Ed25519 JWTs; helper as a dedicated service user (Secure Enclave from a launchd daemon needs a probe); enrollment schema `swarma-registrar enrollment/1` (keys with validity windows, names, optional uid_map, seq, tombstones, pinned signed revision); names `<host>_<project>_<role>[-q]`; JWT 60-120 s; in-memory nonces + refuse iat before process start; per-key and per-name rate limits; append-only audit shipped off-cluster; key rotation by switching registrar key and tuwunel config together; GitHub 2FA for SSO humans. Suggestions S1-S5: require_nbf, jti = request id, README note on the Swarma bridge end state, negative tests first, CLI never prints tokens and writes credentials 0600 atomically.
