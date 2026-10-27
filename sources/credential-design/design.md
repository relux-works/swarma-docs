# Credential design: a secret-free agent mode for service and model credentials

Design note, revision 3. Revision 2 was accepted as a design proposal by an independent review; revision 3 records the owner's dispositions of the six open questions (section 9) and changes nothing else. Status: owner-approved proposal. It turns the owner direction of 2026-10-26/27 into responsibilities and invariants for the book, the broker specification and the papers. Sections 2–7 use the target-state voice; status appears only in sections 1 and 8. Harness behaviour in the proposed mode is marked **to qualify** unless a cited source shows it. No format, field, action name, refusal code or number is introduced; the owning specification names what is needed, and its absence gates activation.

Citations: `NN-*.md:line` is the Russian book on current `main`; `paper.tex`, `platform.tex` and `status-appendix.tex` are under `paper/`; "broker §N" is `spec/broker.md` of the public broker repository; "runtime draft v0.12" is the earlier runtime book kept as a source snapshot (not published).

## 1. Problem and the current honest state

An agent needs credentials for two reasons: to reach its **model provider** (subscription or API key) and to reach **external services** (code hosting, issue trackers, release channels, search, any HTTP API). Today the design gives the harness a readable provider token. Service credentials stay outside agents in three named cases: the repository-action executor (`04-polzovatel-i-set.md:197`), the platform search key (broker §5.5, custody open, §18 item 18) and the carrier credentials of the messaging service (`07-soobscheniya-i-most.md:205-207`). Nothing generalises these cases.

- **The model token is readable by design.** "среда может прочитать токен в своём окружении" (`11-uchetnye-dannye.md:5`; `02-swarma-celikom.md:71`; `platform.tex:289`). The broker does not "make a credential non-extractable" or "intercept model traffic" (broker §1.1); proxy injection is "a separate design" (§12.1).
- **Channels differ by harness.** Claude: `setup-token` through `CLAUDE_CODE_OAUTH_TOKEN` (`11-uchetnye-dannye.md:19,63`). Codex personal plans: short-lived access tokens through a private app-server in external-token mode, never env (`:103-107`; broker §9.3). Muse: a minted key through env or stdin, proposed and unqualified (`:33`; broker §10.2). The native per-home lane remains in the source policy (`:35-57`).
- **What exists is limited.** Chapter 11's harness observations are bounded to the versions and conditions it names (`11-uchetnye-dannye.md:3-9`). The Codex single-refresher result is a pinned historical observation, not qualification (broker §9.6). The public broker is an experimental core that issues nothing: "the shipped owner adapter refuses issuance and the production qualified release set is empty" (broker README). Its v0 contract admits lease methods only for bound agent principals, its leaf grants carry only `credential.lease` (broker §6.3, §8.1), `lease.release` ends one lease's renewal without barring a fresh lease, and a client report changes only its own lease record (§8.5). No secret-free path exists in any form.
- **Revocation does not recall a delivered token.** It stops new leases and renewals; the token lives until expiry or vendor revocation, hence three containment states (`06-granty.md:94-104`). Revocation reaches each check no later than max(S + A, F), counted from signed publication, and nothing is promised before publication; completion is a separate condition (`06-granty.md:110-114`; `paper.tex:182,228`).
- **Consequences already priced in.** Home deletion without archive exists because the agent may have hidden a copy and scanning cannot prove absence (`04-polzovatel-i-set.md:93`). The proxy does not decrypt TLS, so an allowed destination remains an exfiltration channel (`:163-165`).
- **Placeholder injection was considered and parked.** Runtime draft v0.12, «Чего мы не делаем», decided: the harness would start with a placeholder and a TLS-decrypting proxy would substitute the real authorization header, "но провайдеры могут распознавать перехваченный трафик и закрывать аккаунты … Поэтому подстановка на прокси — только исследование". Still open as research (`29-gde-my.md:279`; broker §5.2, §18 item 6).
- **Existing contradictions** are listed under "repair now" in section 8.

Owner direction: no hard dependency on GitHub ("может быть гитлаб а может еще миллион разных сервисов"); service tokens never reach agents; per-service adapters; the model provider only through a proxy; a leased token in an outgoing body blocks the request and revokes the lease.

## 2. The contract, scoped by mode and topology

**Secret-free mode.** In this mode an agent account never receives secret material that is valid outside the platform's credential-spending services. Material is enrolled in the broker and leased only to those services, which run under their own OS accounts and spend it on the agent's behalf (sections 4–6). The guarantee holds only for launches admitted in this mode and only where its boundaries are qualified.

**Exposed-token lanes.** The existing channels stay as explicit exceptions: Claude env, Codex external-token, the proposed Muse key channel and the native per-home lane. The machine's owner selects each per profile and harness (`11-uchetnye-dannye.md:47`); each is qualified on its own, and the launch states that the harness can read and copy the token and revocation does not recall it. Failure to qualify secret-free mode never qualifies an exposed lane by implication. If neither the selected mode nor the selected lane is qualified, the launch refuses. A change of mode never migrates homes silently, never copies a native login, keeps the provider, account and billing identity, and never substitutes API billing for a subscription (`14-modeli.md:71-73`).

**Topology.** The separate-UID guarantee applies to local stations under enforced network rules (`04-polzovatel-i-set.md:143-155`) and to donor variant B. Donor variant C runs the harness under the donor's UID inside an OS sandbox (`12-udalennoe-mesto.md:23-27`). There it needs its own qualified sandbox, store and IPC boundary: the harness must not reach the holder's store, private pipes, interception trust material or another launch's placeholder. Variant A has no OS boundary and stays outside the guarantee. The project host's kernel cannot identify a donor process, so donor credentials, their holder and consent stay with the donor (`11-uchetnye-dannye.md:119`; `12-udalennoe-mesto.md:47-51`). A project workplace never receives a broker lease and keeps zero egress (`04-polzovatel-i-set.md:179`). Placing the credential holder and any interception trust material on a donor is a publication and qualification gate, not part of this design. The first delivery is local-only; donor variants B and C are closed gates, each a separate later step (disposition 6, section 9).

**Who may hold plaintext.**

| Holder | Material | Note |
| --- | --- | --- |
| Broker | every enrolled credential; single refresh owner | unchanged; no provider HTTP forwarding (section 5) |
| Gateway (paths b, c) | leased material for the requests it forwards | new trusted-base member |
| Action service (path a) | leased material for the actions it executes | generalises the repository-action executor |
| Leak matcher | see section 7 | custody is an owner gate |
| Messaging service | its existing carrier credentials only | never model or service credentials |
| Harness | a placeholder (secret-free mode) or the real token (exposed lane) | |

Each new holder joins the trusted base with a stated compromise scope: a compromised gateway or action service exposes every credential it leases. Separate-UID custody does not withstand a captured host root (`paper.tex:242`).

## 3. Two authorities for every use

A credential-spending service authenticates to the broker as itself, not as the requesting agent. Every use therefore needs two separately verified authorities:

1. **Service authority to obtain material**: the service is an admitted, kernel-identified principal of the current generation, with a service lease for the account.
2. **Caller authority for this exact use**: the original caller chain (account owner, delegation chain, agent generation, launch, profile, account), the permitted target and the semantic operation, checked by the service at the boundary of the use, with the narrowing rules of `06-granty.md:78-90`.

Invariants:

- The service's own grant, the request, an account selector or a placeholder never supply missing caller authority. A service that holds credentials for two projects never lets a caller authorised for one reach the other.
- Unknown operations and target predicates that the grant language cannot express refuse; nothing is translated silently (broker §6.6).
- The caller dependency persists through renewal and every use. Binding replacement or a new service generation ends the old leases and requires fresh authority (broker §8.5).
- Secret-free mode is gated on a versioned broker and grant extension that publishes service principals, service leases and use-through-service authority, because the v0 contract has none of them (section 1). Bindings, lease requests and records, and method permissions change with it (broker §4.1-4.2, §7, §8.1-8.3, §13).

**Current authority at every use.** Each use or effect boundary checks current authority under the existing bounds: snapshot freshness, the max(S + A, F) propagation bound, "unavailable" meaning refusal (`06-granty.md:106-114`). The gateway and the action service are named consumers of revocation. Revocation completes only when each has durably acknowledged it or every earlier authority has expired; an intake acknowledgement proves nothing (`06-granty.md:114`). Queued requests, open streams and cached leases are inside the fence:

- on revocation, generation freeze, retirement, all-stop and operator reopening, the gateway closes that generation's listener sessions, open streams and queue, and the action service closes its queued actions, each with a durable closure record, as network freeze already does (`04-polzovatel-i-set.md:157-159`);
- an action already started follows `22-effekty-ostanovka-federaciya.md:33-37`: interrupted where safe, otherwise completed and its outcome recorded;
- after a crash or a restore, a service resumes only through the same closed reopening as the broker (`06-granty.md:116`).

The third containment state ("credentials still usable at the provider") remains for exposed-lane launches, actual leaks and compromise of a credential-holding service.

## 4. Path a: service actions

A non-LLM **action service** under its own OS account performs actions that change shared state: push and landing, change requests, releases, issues or comments as the project. It leases the service credential (section 3) and reaches each service through an adapter (section 5); GitHub, GitLab or any other host is one adapter among many. This is the repository-action executor (`04-polzovatel-i-set.md:197`) without its single target.

What it keeps:

- **Acceptance.** Repository publication and landing still require a board-signed request for the accepted exact candidate, with compare-and-swap of the head (`04-polzovatel-i-set.md:197`; `12-udalennoe-mesto.md:152`). An agent signature plus a grant never replaces that acceptance (`paper.tex:238`).
- **External-effect contract for every mutating adapter operation** (`22-effekty-ostanovka-federaciya.md:7-37`; `platform.tex:437`): current authority, epoch and stop checks at execution, a stable operation identity with fixed parameters and an idempotency key where the recipient supports one, a recorded outcome of done, rejected or unknown, and no blind retry after an unknown outcome. Recovery reconciles with the recipient or asks a person. These rules hold whatever route carries the action, including any write that policy allows through path b.
- **Separation from verification.** Build and test runners stay secret-free (`04-polzovatel-i-set.md:187-193`). The Protocol's trusted runner for project secrets (`17-model-protokola.md:43`; `platform.tex:410`) keeps its semantics; the action service is the trusted effect executor of the Protocol (owner disposition 3, section 9).

## 5. Path b: an injecting gateway with per-service adapters

The agent talks to an **injecting gateway** under its own service account, which terminates the agent's connection, checks both authorities, attaches the credential and opens its own connection to the destination.

**Network policy is preserved, not relaxed.** The gateway adds a mediated capability for model providers and code hosting only, and carries no writes to external services (disposition 4, section 9); existing restrictions stay as they are. Local agents reach only provider endpoints by default, web stays off by default with opt-in per trusted-circle identity, workplaces keep zero egress, R-UNTRUSTED admission still refuses, and publication to code hosting and dependency fetching stay with the action service and the runner's fetch phase (`04-polzovatel-i-set.md:173-193`; `12-udalennoe-mesto.md:138-152`). Operations on code hosting without an effect on shared state reach the gateway only where the admitted profile's machine policy grants that class (disposition 4, section 9). Which service classes an identity may use through the gateway is machine policy selected by the admitted profile, as network profiles are (`04-polzovatel-i-set.md:145`); the caller cannot select it. The plain `CONNECT` path is not widened: credential-free destinations stay on the existing allowlist.

**Caller identity.** The per-generation listener identifies the caller only through the qualified kernel rule; the listener itself does not know the UID (`04-polzovatel-i-set.md:149`). The gateway checks listener owner, generation and served policy generation, as the proxy manager does (`:177`).

**Upstream obligations.** The upstream connection inherits the existing proxy rules: dial-guard on the address actually dialled, resolution by the gateway and no agent resolver path, per-generation budgets that survive restarts, logs without bodies, headers, tokens or URLs (`04-polzovatel-i-set.md:165-169`). It adds server TLS authentication of the destination. Credential recipients come only from the adapter's declarations: client Host or SNI, an alternate auth source or an unchecked URL never selects one. Every redirect or reroute is validated as a new destination before a credential is attached; otherwise it refuses. Credentials supplied by the agent are refused.

**Service adapter: responsibilities, not wire formats.**

| Responsibility | What the adapter declares or does |
| --- | --- |
| Destinations | The names and ports that may receive its credential; nothing else ever does. |
| Authentication scheme | How the credential is presented, so the gateway attaches it unseen. |
| Credential lifecycle (broker side) | Enrolment through the vendor's own flow, completed by a person (`11-uchetnye-dannye.md:79`); minting, single-owner refresh, expiry and vendor-side revocation. |
| Operations and targets | The semantic operations and resources a grant can name, mapped to the narrowest vendor scope. One endpoint carrying several targets or operations is resolved to the actual ones; unknown ones refuse. Endpoints that create, list or reveal credentials refuse. |
| Effect class | Whether an operation mutates shared state; mutating operations inherit section 4. |
| Responses | Whether a response may reflect credential material; an adapter that cannot handle reflection safely stays closed. |
| Leak-match forms | The encodings of its credential that section 7 must recognise. |
| Qualification | Adapter version, service API version and negative controls (section 8). |

**Placement.** Adapters split by concern: the credential-lifecycle half is broker-side and extends the single-refresh-owner pattern (broker §9); the request half runs in the gateway. The broker keeps no network listener and no plugins (broker §12.3) and serves only its Unix-socket protocol. "No provider HTTP forwarding in the broker" is the separation the owner chose (disposition 3, section 9), not an existing non-goal of the published broker specification. Broker §1.1's ban on intercepting traffic stays true of the broker itself.

**MCP.** MCP servers that need service tokens (`10-curator.md:107-139`) get a gateway endpoint chosen by machine policy, never a token; consent stays. A named server or operator-declared connector does not prove routing through the gateway (`:119-123`), so each client and auth mode is qualified.

## 6. Path c: model providers and the login problem

The harness reaches its provider only through a **provider gateway**: a section 5 gateway whose adapter is a model provider. The broker leases the subscription or API credential to the gateway, not to the launch. There are two connection modes, and each harness release is qualified for at most one:

- **endpoint mode**: the harness is configured to use the gateway as its provider endpoint, with no TLS interception (**to qualify** per harness and credential type);
- **interception mode**: the gateway terminates TLS with platform trust material scoped to the launch. This is the parked mode. **Closed gate**: the owner does not admit it (disposition 2, section 9); a harness that cannot use a configured endpoint stays on an approved exposed lane or is refused.

**The concern** is that a harness may need to recognise a login to work properly; whether and how each harness checks is **to qualify**. **What the sources decided.** (1) Harness login is handled by leasing into a supported channel instead of a per-home login. For Claude, a `CLAUDE_CODE_OAUTH_TOKEN` value took precedence over the home login and was written neither to the home nor to Keychain, and Remote Control rejected that channel. That was observed on the versions in `11-uchetnye-dannye.md:9`; the contract is published but not operating (section 1). (2) The placeholder plus substituting proxy was designed and parked in runtime draft v0.12. The reason was the account-closure risk and the rule that the platform never authenticates instead of a person, not harness login. (3) The local provider proxy of donor variants B and C (`12-udalennoe-mesto.md:27`) constrains the route only; the harness still receives the donor's token.

**Proposal: a placeholder that works only through the gateway.**

- The harness receives a placeholder through the channel it accepts (env, stdin or external-token). The value is random per lease, bound by the gateway to one generation, one launch and one account, and accepted only on that generation's listener. Whether the harness's local checks accept it as a login is **to qualify**.
- The gateway refuses any request whose credential is not that placeholder, and replaces the placeholder only after both authority checks.
- **Codex responsibility split (to qualify as a whole).** The broker stays the single refresh owner. Only the gateway holds the real token, so only it sees the real upstream rejection; it asks for renewal with the rejected real token's identity and checks that the account is unchanged. A placeholder digest never substitutes without a specified mapping (broker §9.3). Qualification settles whether the app-server still sees a rejection and what its local refresh callback then means, whether account, status and policy calls pass the gateway, and renewal failure. The gateway never retries a request whose upstream outcome is uncertain or whose stream has begun.
- **Per-harness qualification, each item to qualify:** the placeholder is accepted without local validation; every credentialed provider call, including startup, status and account calls, goes through the gateway; features needing provider-side identity work or are knowingly lost; child processes (MCP servers, hooks, tools) get nothing beyond the placeholder; Codex app-server accepts a placeholder in external-token mode; Muse accepts a placeholder key, for local agents only (`12-udalennoe-mesto.md:45`).
- Qualified combinations are pinned; an unknown release refuses, and there is no "try with a warning" mode (`12-udalennoe-mesto.md:43`).

Qualification uses dedicated test accounts, as Muse qualification already requires (broker §10.2). Account classes follow disposition 1 (section 9): API keys and dedicated test subscriptions first; personal subscriptions only after qualification on the test ones.

## 7. Second line: the leak tripwire

**Matching.** Where the gateway terminates the agent's connection it inspects agent-originated plaintext (request line, headers, body) **before** it attaches legitimate authentication, so its own injected credential never triggers a match. It recognises the forms the adapter declares: raw, base64 and base64url, hex, percent-encoding, JSON escaping, scheme-specific forms. Matching spans chunk boundaries within a bounded window over request and response streams. A response that reflects credential material is not delivered to the agent.

**Matchable set.** Every issued credential version stays matchable until it is expired at the vendor or confirmed invalidated, not only the versions currently leased. The broker's inventory of credential versions per generation defines the set (`06-granty.md:104`); the existing runner likewise retains initial and renewed values for output protection. Missing or stale matcher state blocks rather than passes.

**Custody (owner gate).** The gateway already holds its leased values and can match its own traffic. The bridge's outbound detector (`07-soobscheniya-i-most.md:225-229`) must not receive raw values: exporting them to the messaging account would enlarge the secret-holding trusted base. Values never reach an LLM classifier. One candidate is a broker-local matching service that answers match or no-match for given bytes and never returns values; another narrowly scoped mechanism may replace it. Until one is approved, the bridge claims no leased-value matching. The bridge blocks and never rewrites signed bytes, and a detector failure stops the post, as today (`:227`).

**Response to a match (owner-decided: block and revoke).**

1. The gateway blocks the request immediately and records a verdict without body or value.
2. Local revocation is a **proposed narrow authority**; releasing a lease or reporting on it is not enough (section 1). The broker specification publishes an authenticated trigger that places a durable, protected hold on the affected account; the hold covers the whole account, every generation and launch (disposition 5, section 9). The hold is checked under the broker's lock at every lease and renewal, so reconnects and restarts obtain nothing. The trigger gives the gateway no general operator authority.
3. The gateway and the action service close in-flight uses in that scope (section 3).
4. The session stops through the existing authorised path for credential failures (`11-uchetnye-dannye.md:123`).
5. A durable acknowledgement records each step. If the broker or the alert recipient cannot be reached, forwarding stays closed and nothing reports the revocation as done. Only the owner lifts the hold.
6. An owner-visible event reports the match through a separately gated alert route (broker §18 item 22). A confirmed leak additionally requires rotation at the provider; a possible leak gets the block and the hold only (disposition 5, section 9).

Local block, local hold, session stop and vendor invalidation are distinct outcomes. A local hold neither invalidates the token at the vendor nor requires re-enrolment; vendor invalidation may (for Claude only in the vendor's web interface, broker §10.1).

**Limits.** The boundary is that material never reaches the agent account; the tripwire is only an extra detector. It sees nothing inside opaque `CONNECT` tunnels. Splitting, compression, encryption or slow leakage defeat it. A finite matcher never proves a message, response or home secret-free (`04-polzovatel-i-set.md:93`; `07-soobscheniya-i-most.md:227`).

## 8. Qualification obligations and status

Nothing in sections 2–7 exists. Each row is a negative witness with a nearby positive control; activation requires all rows for the claimed mode, harness, adapter and topology. Existing synthetic, v0 or historical evidence does not count.

| Witness | Required outcome | Positive control |
| --- | --- | --- |
| Request queued before a freeze, forwarded afterwards with a still-valid service lease | refused; closure record exists | request admitted and completed before the fence |
| Caller authorised for project X sends the same permitted method for project Y; unknown operation or unexpressible target | refused | the declared call for X succeeds |
| Issue created, response lost, harness retries | no second effect; outcome "unknown" until reconciled | idempotent replay of the same operation |
| Correctly signed producer request to land an unreviewed candidate | refused | board-signed request for the accepted candidate |
| Adapter grants web or package access to an identity whose admission forbids it | refused | trusted-circle identity with opt-in |
| Allowed destination redirects authenticated request to an unchecked or private address | refused before attaching the credential | validated redirect |
| Variant C harness reads the holder's store or another launch's listener | blocked by the sandbox, else C stays outside the guarantee | own listener reachable |
| Old, still-valid token emitted after refresh; echo split across chunks; matcher unavailable | blocked; hold placed on a match | ordinary authenticated traffic; near-match without revocation |
| After a match, reconnect or restart under the same grant | no new lease until the owner lifts the hold | unrelated account unaffected |
| Placeholder used outside the gateway or on another generation's listener; reused listener port; changed policy generation | useless or refused | own current listener |

**Where the text changes.** The independent review's update map is the exhaustive list; adoption follows it as narrowed by the owner dispositions in section 9. Book: chapters 01, 02, 04–12, 16–18, 22, 23 and 28–30, at credential consumers; contracts independent of credentials, including `14-modeli.md:71-73`, stay. Papers: `paper.tex` and `platform.tex` at the system model, trusted base, grants, network, containment, launch, donor, execution plane and G2/G3/G7/G8; new rows in `status-appendix.tex`; `chain.tex` unchanged. Broker specification: a versioned new-mode section touching §§1–18, v0 and historical evidence keeping their scope. Editorial records and figure sources follow.

- **Repair now, independently of this design**: `22-effekty-ostanovka-federaciya.md:145` and `editorial/decisions.ru.md:154` (the broker does show provider keys today); `11-uchetnye-dannye.md:87`, where the dispatcher releases an env lease although broker §8.5/§13.2 accept release only from the lease's own principal (the repair grants no new dispatcher power); `29-gde-my.md:69,271` (broker code exists, as an experimental core that issues nothing).

## 9. Owner dispositions

The owner answered the six questions of revision 2 on 2026-10-27 (02:21:54Z), in the owner's channel, verbatim: «По 6 вопросам как рекомендует лид». The accepted recommendations, verbatim, and what each one closes:

1. «Какие учётки: начать с API-ключей и отдельных тестовых подписок; личные подписки в этом режиме только после проверки на тестовых. Разрешение M0 ходить к провайдеру под учётками владельца — отдельная история, там аренда.»
   Secret-free mode starts with API keys and dedicated test subscriptions. **Closed gate:** personal subscriptions in secret-free mode, until the mode is qualified on test subscriptions; the research-only rule for placeholder substitution on personal accounts stands until then. Use of the owner's own provider accounts by a given machine is a separate question governed by leases and is outside this design.
2. «Перехват TLS: не допускать. В первом объёме только харнесы, которые умеют работать через настроенный адрес. Остальные остаются на явном исключении или получают отказ.»
   Path c uses endpoint mode only. **Closed gate:** interception mode, with its platform trust material; it is not admitted. A harness that cannot use a configured endpoint stays on an approved, separately qualified exposed lane or is refused.
3. «Компоненты: жизненный цикл токенов остаётся в брокере, брокер минимален; запросы обрабатывает отдельный шлюз; спеки брокера, адаптеров и шлюза ведёт лейн брокера; служба действий — это доверенный исполнитель эффектов из протокола.»
   The credential lifecycle half of every adapter is broker-side; request handling runs in the separate gateway; the broker keeps no network listener, no plugins and no provider HTTP forwarding. The broker specification owners also own the adapter and gateway specifications. The action service is the Protocol's trusted effect executor in its Runtime form. **Closed gate:** request handling or forwarding inside the broker. The matcher specification's owner is not named; it stays with the matcher-custody gate below.
4. «Сервисы через прокси: сначала только провайдеры моделей и хостинг кода; любая запись во внешний сервис идёт только через службу действий, не через прокси.»
   The gateway serves model providers and code hosting only, and through the gateway only operations without an effect on shared state. **Closed gates:** every other service class through the gateway, until admitted by a later owner decision and qualified; any write to an external service through path b. Every write goes through path a with acceptance, current authority and effect recovery.
5. «Утечка: подтверждённая — ротация у провайдера; возможная — только блокировка; блокировка действует на весь аккаунт; снимает её только владелец.»
   A match blocks the request and places a hold on the whole account: every generation and launch on that account is contained. A confirmed leak additionally requires rotation at the provider; a possible leak gets the block and the hold only. Only the owner lifts the hold. **Closed gate:** automatic vendor-side action on a possible leak; any principal other than the owner lifting a hold. The rule that classifies a match as confirmed is published by the owning specification; this design does not define it, and until it exists no match counts as confirmed by default.
6. «Доноры: первая поставка только локальная; донор B и C — отдельными шагами потом (closed gates).»
   The first delivery covers local stations only. **Closed gates:** donor variant B and donor variant C, each a separate later step with its own publication and qualification; donor variant A stays outside the guarantee. Matcher custody beyond the gateway's own traffic is not decided by this disposition: the bridge receives no raw values and claims no leased-value matching until a matcher boundary is approved.

Locally blocking and revoking on a leak was decided before and is not changed. Preserving caller authority, refusing blind retries, closing on unknown state and reporting qualification truthfully remain engineering obligations. The dispositions approve the design as a proposal; they publish no contract, qualify no harness, adapter or topology, and authorise no live-account test outside dedicated test accounts.

**Closed gates at a glance.**

| Gate | Closed until |
| --- | --- |
| Personal subscriptions in secret-free mode | qualification on dedicated test subscriptions |
| Interception mode and its trust material | not admitted |
| Request handling or forwarding in the broker | not admitted |
| Service classes other than model providers and code hosting through the gateway | a later owner decision and qualification |
| Writes to external services through the gateway | not admitted; writes go through the action service |
| Vendor-side action on a possible leak; hold lifted by anyone but the owner | not admitted |
| Donor variant B; donor variant C | separate later steps, each published and qualified |
| Leased-value matching in the bridge or another matcher outside the gateway | an approved matcher boundary |

---

## Кратко для владельца (RU)

- **Что изменилось после ревью.** «Агент не держит токенов» теперь режим (secret-free mode), и действует он только там, где квалифицирован: в первой поставке только локальные станции; донор B и донор C (с отдельной квалификацией песочницы) идут позже отдельными шагами. Донор A и полосы с читаемым токеном (env у Claude, external-token у Codex, ключ Muse, нативный вход дома) остаются явными исключениями: их выбирает владелец машины, риск виден в статусе, неквалифицированное отказывает.
- **Логин.** Да, решали. Вход харнеса решили арендой в поддержанный канал, но это наблюдение на конкретных версиях и опубликованный контракт: в работе это сейчас не стоит, брокер экспериментальный и неактивный. Заглушку с подменой на прокси отложили из-за риска закрытия личных аккаунтов, а не из-за логина. Примет ли харнес заглушку как логин, пока «to qualify».
- **Новые инварианты.** На каждое использование две проверки: служба вправе взять материал, а вызывающий агент вправе на это действие с этой целью; широкий грант службы чужую дыру не закрывает. Отзыв действует в пределах max(S + A, F), очереди, стримы и закэшированные аренды закрываются забором. Действия сохраняют приёмку доской точного кандидата и правила внешних эффектов (идентификатор операции, записанный исход, без слепого повтора). Шлюз не ослабляет сетевую политику и наследует dial-guard, проверку редиректов и бюджеты.
- **Растяжка.** Блок плюс локальный отзыв (твоё решение) оформлены как новое узкое полномочие брокера: долговечный hold на весь аккаунт, который не обходят переподключение и рестарт. Сопоставлять нужно все выданные версии токена, а не только текущие. Сырые значения не уходят ни в учётку моста, ни в классификатор. Локальный отзыв не равен аннулированию у провайдера.
- **Решения по шести вопросам (r3, §9).** Принято как рекомендовал лид: сначала API-ключи и тестовые подписки; перехвата TLS нет, только харнесы с настраиваемым адресом; жизненный цикл токенов в брокере, запросы в отдельном шлюзе, служба действий — доверенный исполнитель эффектов протокола; через шлюз только провайдеры моделей и хостинг кода, любая запись только через службу действий; подтверждённая утечка — ротация у провайдера, возможная — только блок, блок на весь аккаунт и снимает его только владелец; первая поставка только локальная, доноры B и C закрыты отдельными воротами.
