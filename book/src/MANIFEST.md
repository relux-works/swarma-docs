# Рисунки книги: манифест

Каждый рисунок книги собирается из исходника PlantUML в этом каталоге; рендер — `book/diagrams/<имя>.png`, его делает оркестратор после ревью:

```
PLANTUML_LIMIT_SIZE=16384 plantuml -tpng -o "$PWD/book/diagrams" book/src/*.puml
```

Перед рендером запускается `book/check-figures.sh`: у каждой картинки из глав есть исходник и строка здесь, у каждой копии хэш совпадает с записанным, в `diagrams/` нет картинок без исходника.

**Происхождение.** «книга» — исходник ведёт эта книга. «копия» — байт в байт копия исходника из снимка в `sources/` на записанной ревизии; править её здесь нельзя.

| Рисунок | Исходник | Происхождение | SHA-256 копии | Главы |
| --- | --- | --- | --- | --- |
| three-layers | `three-layers.puml` | книга | — | «Swarma целиком» |
| platform-storage-layout | `platform-storage-layout.puml` | книга | — | «Пользователь ОС на агента и сеть агента» |
| keeper-sign | `keeper-sign.puml` | книга | — | «Ключи и ключник» |
| grant-issue-and-check | `grant-issue-and-check.puml` | книга | — | «Гранты и полномочия» |
| action-namespace-registration | `action-namespace-registration.puml` | книга | — | «Гранты и полномочия» |
| bridge-components | `bridge-components.puml` | книга | — | «Путь сообщения и мост» |
| mailbox-delivery | `mailbox-delivery.puml` | книга | — | «Путь сообщения и мост» |
| one-shot-agent | `one-shot-agent.puml` | книга | — | «Запуск агента и хост сессий» |
| controlled-restart | `controlled-restart.puml` | книга | — | «Запуск агента и хост сессий» |
| goal-loop | `goal-loop.puml` | книга | — | «Запуск агента и хост сессий» |
| custody-states | `custody-states.puml` | книга | — | «Swarm Keeper» |
| escalation-chain | `escalation-chain.puml` | книга | — | «Swarm Keeper» |
| ledger-append-fold-replay | `ledger-append-fold-replay.puml` | книга | — | «Swarm Keeper» |
| long-session-goals | `long-session-goals.puml` | книга | — | «Запуск агента и хост сессий» |
| profile-prepare | `profile-prepare.puml` | книга | — | «Swarm Curator» |
| resolution-order | `resolution-order.puml` | книга | — | «Учётные данные и логины» |
| setup-token | `setup-token.puml` | книга | — | «Учётные данные и логины» |
| credential-lease-revocation | `credential-lease-revocation.puml` | книга | — | «Учётные данные и логины» |
| donor-variants | `donor-variants.puml` | книга | — | «Удалённое рабочее место» |
| join-handshake | `join-handshake.puml` | книга | — | «Удалённое рабочее место» |
| remote-worker-turn | `remote-worker-turn.puml` | книга | — | «Удалённое рабочее место» |
| worker-code-path | `worker-code-path.puml` | книга | — | «Удалённое рабочее место» |
| board-components | `board-components.puml` | книга | — | «Доска задач и процесс» |
| board-transition-spawn | `board-transition-spawn.puml` | книга | — | «Доска задач и процесс» |
| decision-pipeline | `decision-pipeline.puml` | копия | 56c22c3be4c56293b61f33bc2e7cd7c2ab0fc050d28a0971a9aa88024b22769f | «Модели и деньги» |
| local-weights | `local-weights.puml` | книга | — | «Модели и деньги» |
| operator-phone | `operator-phone.puml` | книга | — | «Оператор и интерфейсы» |
| memory-data-delivery | `memory-data-delivery.puml` | книга | — | «Память агентов» |
| protocol-topology | `protocol-topology.puml` | книга | — | «Модель протокола» |
| authority-ladder | `authority-ladder.puml` | книга | — | «Контракт задачи и правила валидаторов» |
| candidate-integration | `candidate-integration.puml` | книга | — | «Оркестратор по аренде и цикл задачи» |
| portable-attestations | `portable-attestations.puml` | книга | — | «Аттестации и переносимая репутация» |
| sublayers | `sublayers.puml` | книга | — | «Цепочка: устройство» |
| block-anatomy | `block-anatomy.puml` | книга | — | «Цепочка: устройство» |
| history-holders | `history-holders.puml` | книга | — | «Цепочка: устройство» |
| publish-flow | `publish-flow.puml` | книга | — | «Социальный слой, память сети и экономика» |
| curation | `curation.puml` | копия | d203229fb5d2df6be141eab333fa5785418f86728168086fec77e76c89dc8a94 | «Социальный слой, память сети и экономика» |
| economy | `economy.puml` | книга | — | «Социальный слой, память сети и экономика» |

`block-anatomy` и `history-holders` были копиями из `sources/`. При финализации дизайна книга взяла их на себя: в теле блока появились события личностей, в заголовке — корень состояния, лёгкий клиент читает заголовки от checkpoint. Копией остаются `decision-pipeline` и `curation`.
