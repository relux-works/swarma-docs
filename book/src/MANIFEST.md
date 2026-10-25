# Рисунки книги: манифест

Каждый рисунок книги рисуется генератором `scripts/diagram-kit/render.py` из исходника TOML в этом каталоге по правилам `editorial/diagram-style.ru.md`; рендер — `book/diagrams/<имя>.svg`:

```
python3 scripts/diagram-kit/render.py book/src/<имя>.toml book/diagrams/<имя>.svg --report --require-fit <поле>
```

Поле `tall` (167 × 168 мм) получает рисунок, чья ссылка в главе несёт класс `{.tall}`; остальные стоят в обычном поле 167 × 98 мм. Раскладка `graph` требует Graphviz 14.0.4, генератор при другой версии отказывает.

Перед сборкой запускается `bash book/check-figures.sh`: у каждой картинки из глав есть исходник и строка здесь, у каждой копии хэш совпадает с записанным, в `diagrams/` нет картинок без исходника, каждый SVG совпадает со свежим рендером своего исходника и проходит `--require-fit` для своего поля.

**Происхождение.** «книга» — исходник ведёт эта книга. «копия» — байт в байт копия исходника из снимка в `sources/` на записанной ревизии; править её здесь нельзя. Сейчас копий нет.

| Рисунок | Исходник | Происхождение | SHA-256 копии | Поле | Главы |
| --- | --- | --- | --- | --- | --- |
| three-layers | `three-layers.toml` | книга | — | обычное | Swarma целиком |
| keeper-sign-1 | `keeper-sign-1.toml` | книга | — | обычное | Ключи и ключник |
| keeper-sign-2 | `keeper-sign-2.toml` | книга | — | tall | Ключи и ключник |
| grant-issue-and-check | `grant-issue-and-check.toml` | книга | — | tall | Гранты и полномочия |
| action-namespace-registration | `action-namespace-registration.toml` | книга | — | tall | Гранты и полномочия |
| mailbox-delivery-1 | `mailbox-delivery-1.toml` | книга | — | tall | Путь сообщения и мост |
| mailbox-delivery-2 | `mailbox-delivery-2.toml` | книга | — | tall | Путь сообщения и мост |
| bridge-components | `bridge-components.toml` | книга | — | tall | Путь сообщения и мост |
| carrier-admission-1 | `carrier-admission-1.toml` | книга | — | обычное | Допуск к носителю |
| carrier-admission-2 | `carrier-admission-2.toml` | книга | — | tall | Допуск к носителю |
| one-shot-agent-1 | `one-shot-agent-1.toml` | книга | — | обычное | Запуск агента и хост сессий |
| one-shot-agent-2 | `one-shot-agent-2.toml` | книга | — | tall | Запуск агента и хост сессий |
| long-session-goals-1 | `long-session-goals-1.toml` | книга | — | обычное | Запуск агента и хост сессий |
| long-session-goals-2 | `long-session-goals-2.toml` | книга | — | tall | Запуск агента и хост сессий |
| controlled-restart | `controlled-restart.toml` | книга | — | tall | Запуск агента и хост сессий |
| goal-loop | `goal-loop.toml` | книга | — | tall | Запуск агента и хост сессий |
| custody-states | `custody-states.toml` | книга | — | обычное | Swarma Keeper |
| escalation-chain | `escalation-chain.toml` | книга | — | tall | Swarma Keeper |
| ledger-append-fold-replay | `ledger-append-fold-replay.toml` | книга | — | tall | Swarma Keeper |
| profile-prepare | `profile-prepare.toml` | книга | — | tall | Swarma Curator |
| resolution-order | `resolution-order.toml` | книга | — | tall | Учётные данные и логины |
| setup-token-1 | `setup-token-1.toml` | книга | — | обычное | Учётные данные и логины |
| setup-token-2 | `setup-token-2.toml` | книга | — | tall | Учётные данные и логины |
| credential-lease-revocation-1 | `credential-lease-revocation-1.toml` | книга | — | обычное | Учётные данные и логины |
| credential-lease-revocation-2 | `credential-lease-revocation-2.toml` | книга | — | tall | Учётные данные и логины |
| credential-lease-revocation-3 | `credential-lease-revocation-3.toml` | книга | — | обычное | Учётные данные и логины |
| donor-variants | `donor-variants.toml` | книга | — | обычное | Удалённое рабочее место |
| join-handshake-1 | `join-handshake-1.toml` | книга | — | tall | Удалённое рабочее место |
| join-handshake-2 | `join-handshake-2.toml` | книга | — | tall | Удалённое рабочее место |
| remote-worker-turn-donor | `remote-worker-turn-donor.toml` | книга | — | tall | Удалённое рабочее место |
| remote-worker-turn-ours | `remote-worker-turn-ours.toml` | книга | — | tall | Удалённое рабочее место |
| worker-code-path-1 | `worker-code-path-1.toml` | книга | — | tall | Удалённое рабочее место |
| worker-code-path-2 | `worker-code-path-2.toml` | книга | — | tall | Удалённое рабочее место |
| board-components | `board-components.toml` | книга | — | tall | Доска задач и процесс |
| board-transition-spawn-1 | `board-transition-spawn-1.toml` | книга | — | tall | Доска задач и процесс |
| board-transition-spawn-2 | `board-transition-spawn-2.toml` | книга | — | обычное | Доска задач и процесс |
| decision-pipeline | `decision-pipeline.toml` | книга | — | tall | Модели и деньги |
| local-weights | `local-weights.toml` | книга | — | tall | Модели и деньги |
| memory-data-delivery | `memory-data-delivery.toml` | книга | — | tall | Память агентов |
| operator-phone-1 | `operator-phone-1.toml` | книга | — | tall | Оператор и интерфейсы |
| operator-phone-2 | `operator-phone-2.toml` | книга | — | обычное | Оператор и интерфейсы |
| protocol-topology | `protocol-topology.toml` | книга | — | tall | Модель протокола |
| authority-ladder | `authority-ladder.toml` | книга | — | обычное | Контракт задачи и правила валидаторов |
| candidate-integration | `candidate-integration.toml` | книга | — | tall | Оркестратор по аренде и цикл задачи |
| portable-attestations-1 | `portable-attestations-1.toml` | книга | — | tall | Аттестации и переносимая репутация |
| portable-attestations-2 | `portable-attestations-2.toml` | книга | — | tall | Аттестации и переносимая репутация |
| sublayers | `sublayers.toml` | книга | — | tall | Цепочка: устройство |
| block-anatomy | `block-anatomy.toml` | книга | — | обычное | Цепочка: устройство |
| history-holders | `history-holders.toml` | книга | — | обычное | Цепочка: устройство |
| publish-flow-1 | `publish-flow-1.toml` | книга | — | обычное | Социальный слой, память сети и экономика |
| publish-flow-2 | `publish-flow-2.toml` | книга | — | tall | Социальный слой, память сети и экономика |
| curation | `curation.toml` | книга | — | tall | Социальный слой, память сети и экономика |
| economy | `economy.toml` | книга | — | обычное | Социальный слой, память сети и экономика |

`block-anatomy` и `history-holders` были копиями из `sources/`. При финализации дизайна книга взяла их на себя: в теле блока появились события личностей, в заголовке — корень состояния, лёгкий клиент читает заголовки от checkpoint. `decision-pipeline` и `curation` были копиями PlantUML из `sources/` до перерисовки генератором; теперь это рисунки книги, их содержание сверено с прежними копиями и главами (`editorial/notes/diagram-book-wave-notes.ru.md`).

Рисунки с суффиксом части (`-1`, `-2`, `-3`, `-donor`, `-ours`) — части одной прежней последовательности или схемы, поделённой по правилу деления гайда; номера шагов в частях сквозные. Раскладка хранения Swarma Runtime (`platform-storage-layout`) стала блоком кода в главе «Пользователь ОС на агента и сеть агента».
