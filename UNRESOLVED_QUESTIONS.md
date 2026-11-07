# Open decisions for the identity and Talk books

The Russian chapters describe the current reading of the direction chosen on 7 November 2026. Implementation status belongs to each book's own "Где мы" chapter.

| Question | Current reading | Where a decision changes the text |
| --- | --- | --- |
| Public name of the identity layer | Use the descriptive "слой личности и полномочий"; Keybase is prior art only. | `editorial/names.ru.md`, identity book introduction. |
| New naming zones | Use `.bit` for experiments; consider a new zone after 17 November 2026. Community-specific zones remain a reading awaiting confirmation. | Identity book state chapter; no new zone or consensus semantics are asserted. |
| Chain-only privileged revocation | Target profile uses first-block acceptance, a mempool hold, a 30-minute no-progress stop and optional authenticated denial. Changing the existing authority-verification contract requires separate agreement. | Identity book "Доверенности и отзыв" and state chapter. |
| Optional chain contact notification | Default contact is off chain. A notification may represent a message request with optional tips; payment does not establish consent. | Talk book "Найти человека и установить контакт". |
| Encrypted contact-log recovery | Retained encrypted replicas plus a checkpoint in the name value; seed alone cannot recreate missing data. Wire formats, concurrent updates and recovery selection need a defined protocol. | Talk book "Зашифрованный журнал контактов" and state chapter. |
| Autonomous agent entities | Do not assign independent legal status, custody or operating authority before the promised separate account of this subject. | Both state chapters; future service-market description. |
| Organization and contract interoperability | Exact signed-object formats, complete-state proofs, administrative conflict rules and room-epoch binding require specification and qualification. | Identity book contract/organization chapters; Talk group/work chapters. |

The older research recommendation for mandatory fast revocation and the later chain-only decision are reconciled by following the later decision. A sponsor's first year of payment remains distinct from name expiry and includes timely renewals. Partial mainnet reading and unsuccessful testnet connection are observations separate from the unrun real-network grant experiment.
