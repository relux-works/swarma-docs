# Интерфейсы: CLI, каналы, приложение

## Что есть сегодня

- **`task-board`** — около тридцати команд: данные борды (`q`, `m`, `grep`, `tree`, `plan`, `resource`, `goal`), run'ы (`spawn …`), доставка (`worktree`, `board commit|publish`), сессии (`claude`, `codex`, `session …`), сервер (`admin`, `login`), `limits`, `self-update`. ⟦работает сегодня⟧
- **`curator`**: `init`, `add`, `install`, `status`, `profile …`, `env …`, `global …`, `audit` и `run`, который вызывает провайдер `curator-run`. Плюс обёртки `anthropic-board` и `openai-board` вокруг `task-board claude|codex`. ⟦работает сегодня⟧
- **В спеках запланированы** `keeper …`, `memory …`, `curator models|runtimes|…`, `task-board playbook confirm`, `trust init`, `tick`, `event post`, `mail …`, `session park` и `emergency-stop`. Сами возможности частью решены, а форма команд пересматривается. ⟦предложено⟧

## Взгляд со стороны на CLI

25 сентября внешний рецензент прочитал все команды из спек и установленных бинарников. Вердикт: направление верное, но черновики ему пока не следуют. ⟦предложено⟧

- **Дубли**: две аварийные остановки (`task-board emergency-stop` с фразой `STOP` и `keeper estop` с «EMERGENCY STOP»), парковка в двух местах, управление сессиями в трёх (`task-board session`, `keeper` и зарезервированный `curator session`).
- **Перегруженные слова**: у `profile` семь значений, и существующий флаг `--context-profile full|lite` занимает имя, которое черновики приберегли для профиля Curator. Harness пишется шестью способами: `--agent`, `--runtime`, `--harness`, `claude_code`, `claude-code`, `claude`.
- **У главных команд человека нет имён**: выдать и отозвать право, выключить инструмент, yolo, ключи.
- **Сантехника**: провайдеры не названы по существительному, которое набирает человек (`curator inference` ищет `curator-inference`, а планируется `curator-inference-manager`), и нет команды, которая ставит провайдера.

## Предлагаемая форма

Это предложение рецензента, оно ждёт решения оператора. ⟦предложено⟧

1. **Три входа по аудитории**: `keeper` — для человека на пасеке; `curator` — для установки и настройки машины, а незнакомое существительное уходит провайдеру `curator-<существительное>`; `task-board` — ядро для агентов, таймера, мостов и самого Кипера.
2. **Сначала существительное, потом глагол** (`keeper hive add`, `curator models set`, `task-board mail read`) и один словарь глаголов: `list`, `show`, `status`, `add`/`remove`, `set`/`unset`, `check`, `explain`, `confirm` (присутственное «да» версии конфигурации), `approve`/`reject` (один ожидающий пункт), `grant`/`revoke` (постоянное разрешение), `init`, `install`/`upgrade`. У Кипера свой жизненный цикл: `up`, `down`, `wake`, `park`, `stop`, `estop`, `chat`, `watch`.
3. **Пасечные слова — только в существительных `keeper` и папках пасеки** (`keeper hive`, `~/apiary/hives/`, профиль `apiary`), везде остальное — технические термины.
4. **Одно слово — одно значение**: `profile` — только профиль Curator, поэтому `--context-profile full|lite` в task-board становится `--prompt`; harness везде задаётся id runtime'а.
5. **Сессиями управляет `curator session`**, CLI хоста, а `keeper` его оборачивает. Аварийная остановка одна — `keeper estop [<улей>]` с присутствием и одной фразой, а ядро даёт ей примитивы `board snapshot` и директиву `park`.
6. **Акты доверия — под `task-board trust`** (`init`, `status`, `confirm`, `grant`, `revoke`, `disable`, `enable`, `keys`), и у человека один ящик в `keeper`: `inbox`, `approve|reject`, `confirm`, `grant|revoke`, `review`.
7. **Файлы оператора — `~/.curator/*.toml`**, по одному существительному на файл (`models`, `runtimes`, `engines`, `network`), провайдеры названы так же и ставятся отдельной командой.

| Человек набирает | Что вызывается |
| ------------ | ------------------------ |
| `keeper`, `keeper chat <улей>` | `curator session attach` с управлением |
| `keeper watch <цель>` | `curator session watch` |
| `keeper up` | для каждого улья `curator run <runtime> --profile <роль>` → контракт ax → хост |
| `keeper park`, `keeper down` | `curator session park`, ядро пишет цель с `handoff_ref` |
| `keeper estop` | `curator session estop`: снимки борд, потом run'ы, потом сессии |
| `keeper confirm`, `grant`, `revoke` | `task-board trust confirm`, `grant`, `revoke` в каждом улье |
| `task-board claude`, `task-board codex` | алиасы `curator run claude` и `curator run codex` |

Ядро task-board остаётся как есть; `claude|codex` на один релиз становятся алиасами, `session …` переезжает в `curator session` вместе с хостом на машину (SH3), `limits` — в `curator runtimes`, обёртки `*-board` уходят. Фаза 1 session host команд не меняет. ⟦предложено⟧

## Каналы, приложение, конструктор

- **Терминал первым**: `keeper`, `keeper chat` и `keeper watch` показывают harness ровно таким, какой он есть, а если выйти, сессия продолжает работать. Мессенджеры подключаются через провайдеров waggle: там можно спросить и ответить, но нельзя одобрить. ⟦предложено⟧
- **Приложение-компаньон** показывает, что человек одобряет, и подписывает ключом в защищённом чипе: одобрения, доверенности, подтверждения и запросы прав. Отдельный трек, iOS первым, ещё не начат. ⟦решено⟧ Позже — shell по SSH и настольная версия как пульт. ⟦предложено⟧
- **Схема `Playbook.json` готова для визуального конструктора**: блоки `ui`, запись и чтение без потерь, `playbook validate` на каждой правке; самого конструктора пока нет. ⟦решено⟧
- **Вики станет публичным сайтом на Quartz** (`apiary.relux.works`) после заморозки спеки процессов, без заметок для юристов. ⟦решено⟧ Что ещё публиковать, не решено. ⟦открыто⟧
