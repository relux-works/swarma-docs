# R7 score

Owner: astra-27 (judge). Final status: **PARKED**, 2026-10-17 19:12Z.
Current verified release: **0.2.6-draft**, `77b951eb86d5ba9198921d058930884918a39942`.

**Final R7 score: 2/2.** R7-055 is resolved by Ivan's D-009 and independently verified
in both evaluators. R7-059's historical-profile harness correction is closed.
No specification/implementation finding or owner question remains open.

| Inventory | Source evaluator | Package evaluator | Scope |
| --- | ---: | ---: | --- |
| Canonical semantic 0.2.6 | 66 pass / 0 fail / 0 unsupported | 66 pass / 0 fail / 0 unsupported | Includes all nine D-009 vectors S34–S42 |
| Historical semantic 0.2.5 | 68 pass / 0 fail / 0 unsupported | 68 pass / 0 fail / 0 unsupported | Unchanged cases, exact frozen grammar; separate denominator |
| Canonical deployment | 8 unsupported | 8 unsupported | No qualification |
| Historical deployment | 1 unsupported | 1 unsupported | No qualification |

Release `77b951e` has 14 closed schemas, 14 domain documents, one fixture,
74 vectors and 52 normative clauses. All 103 JSON artifacts regenerate exactly;
38 checker controls detect their intended violations. All 94 earlier JSON
artifacts retain their content except declared version identifiers.

Source runtime remains `946cbd8`; current report and harness are `c7e86d5`.
All 134 source controls pass, including the source-derived bounded 256-DAG
matrix. The harness changes only two profile labels in each of two audited
copies; original case bytes and behavioral expectations remain unchanged.

Package runtime `5897520` passes four new 0.2.6 product groups, 30 historical
0.2.5 product groups and four comparer groups. Independent native checks cover
64 three-event variants, 125 validated states, 25 writes and 11 atomic refusals.
Eight intended failures reproduce on the old runtime with no setup errors.

D-009's issuer-local relation governs both currentness and strict succession.
The original mixed chain stays ambiguous; assertion-free own paths establish
order; one own path survives a foreign branch; foreign-only edits preserve the
relation. Existing replacement refusal, import, CAS and replay contracts pass.

Ledger disposition: **59 items — 48 fixed, 10 rejected, one ambiguity resolved
by D-009**. Original witness `4424598`, package first `1be6026`, source first
`31d77d2` and all prior failures are preserved. Full audit is indexed in
[LEDGER.md](LEDGER.md), reopened round 7; [OWNER-QUESTIONS.md](OWNER-QUESTIONS.md)
has no open question. Convener PARK at 19:12Z confirms the quiet-round gate
(event `$wTjjxPAdO1lPYyIX7BgMky5ptiS0vPzX6HGGgE99C0U`).
See the [judge park note](parked/astra-27.md).
Synthetic semantic success does not qualify a protected deployment.
