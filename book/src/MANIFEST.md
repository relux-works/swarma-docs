# Рисунки книги: манифест

Каждый рисунок книги собирается из исходника PlantUML в этом каталоге; рендер — `book/diagrams/<имя>.png`, его делает оркестратор после ревью:

```
PLANTUML_LIMIT_SIZE=16384 plantuml -tpng -o "$PWD/book/diagrams" book/src/*.puml
```

Перед рендером запускается `book/check-figures.sh`: у каждой картинки из глав есть исходник и строка здесь, у каждой копии хэш совпадает с записанным, в `diagrams/` нет картинок без исходника.

**Происхождение.** «книга» — исходник ведёт эта книга. «копия» — байт в байт копия исходника из снимка в `sources/` на записанной ревизии; править её здесь нельзя.

| Рисунок | Исходник | Происхождение | SHA-256 копии | Главы | Статус |
| --- | --- | --- | --- | --- | --- |
| three-layers | `three-layers.puml` | книга | — | «Swarma целиком» | архитектура |
| platform-storage-layout | `platform-storage-layout.puml` | книга | — | «Пользователь ОС на агента и сеть агента» | решено; экспорт — открыто |
| keeper-sign | `keeper-sign.puml` | книга | — | «Ключи и ключник» | предложено |
| grant-issue-and-check | `grant-issue-and-check.puml` | книга | — | «Гранты и полномочия» | предложено |
| action-namespace-registration | `action-namespace-registration.puml` | книга | — | «Гранты и полномочия» | предложено |
| bridge-components | `bridge-components.puml` | книга | — | «Путь сообщения и мост» | предложено |
| mailbox-delivery | `mailbox-delivery.puml` | книга | — | «Путь сообщения и мост» | предложено |
| one-shot-agent | `one-shot-agent.puml` | книга | — | «Запуск агента и хост сессий» | спецификация; включение — открыто |
| controlled-restart | `controlled-restart.puml` | книга | — | «Запуск агента и хост сессий» | предложено |
| goal-loop | `goal-loop.puml` | книга | — | «Запуск агента и хост сессий» | предложено |
| custody-states | `custody-states.puml` | книга | — | «Swarm Keeper» | предложено |
| escalation-chain | `escalation-chain.puml` | книга | — | «Swarm Keeper» | предложено |
| ledger-append-fold-replay | `ledger-append-fold-replay.puml` | книга | — | «Swarm Keeper» | предложено |
| long-session-goals | `long-session-goals.puml` | книга | — | «Запуск агента и хост сессий» | предложено |
| profile-prepare | `profile-prepare.puml` | книга | — | «Swarm Curator» | решено |
| resolution-order | `resolution-order.puml` | книга | — | «Учётные данные и логины» | решено; наследуемая доставка — предложено |
| setup-token | `setup-token.puml` | книга | — | «Учётные данные и логины» | предложено |
| credential-lease-revocation | `credential-lease-revocation.puml` | книга | — | «Учётные данные и логины» | спецификация |
| donor-variants | `donor-variants.puml` | книга | — | «Удалённое рабочее место» | предложено |
| join-handshake | `join-handshake.puml` | книга | — | «Удалённое рабочее место» | предложено |
| remote-worker-turn | `remote-worker-turn.puml` | книга | — | «Удалённое рабочее место» | предложено |
| worker-code-path | `worker-code-path.puml` | книга | — | «Удалённое рабочее место» | решено; контракты — открыто |
| board-components | `board-components.puml` | книга | — | «Доска задач и процесс» | предложено |
| board-transition-spawn | `board-transition-spawn.puml` | книга | — | «Доска задач и процесс» | предложено |
| decision-pipeline | `decision-pipeline.puml` | копия | 56c22c3be4c56293b61f33bc2e7cd7c2ab0fc050d28a0971a9aa88024b22769f | «Модели и деньги» | работает сегодня |
| local-weights | `local-weights.puml` | книга | — | «Модели и деньги» | предложено |
| operator-phone | `operator-phone.puml` | книга | — | «Оператор и интерфейсы» | решено; форматы — открыто |
| memory-data-delivery | `memory-data-delivery.puml` | книга | — | «Память агентов» | предложено |
| protocol-topology | `protocol-topology.puml` | книга | — | «Модель протокола» | спецификация |
| authority-ladder | `authority-ladder.puml` | книга | — | «Контракт задачи и правила валидаторов» | спецификация |
| candidate-integration | `candidate-integration.puml` | книга | — | «Оркестратор по аренде и цикл задачи» | спецификация |
| portable-attestations | `portable-attestations.puml` | книга | — | «Аттестации и переносимая репутация» | предложено |
| sublayers | `sublayers.puml` | книга | — | «Цепочка: устройство» | предложено |
| block-anatomy | `block-anatomy.puml` | копия | 6d359a493da88dfcc7d37e2a68096aa2ae2aafc4d82ab0e7c47c5901a0b2dc38 | «Цепочка: устройство» | предложено |
| history-holders | `history-holders.puml` | копия | 8eb334ecce82248d663612cc36d1d4cc03149bff755ce00911b68492a7b31a88 | «Цепочка: устройство» | предложено |
| publish-flow | `publish-flow.puml` | книга | — | «Социальный слой, память сети и экономика» | предложено |
| curation | `curation.puml` | копия | d203229fb5d2df6be141eab333fa5785418f86728168086fec77e76c89dc8a94 | «Социальный слой, память сети и экономика» | предложено |
| economy | `economy.puml` | книга | — | «Социальный слой, память сети и экономика» | предложено |
