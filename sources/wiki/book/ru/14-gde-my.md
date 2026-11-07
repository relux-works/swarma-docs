# Где мы сейчас

## Что работает

Состояние на 25 сентября 2026 года. ⟦работает сегодня⟧

| Компонент | Состояние |
| --------- | -------------------------- |
| task-board, `tb-sessiond` | релиз `0.27.0`: борды, spawn, Change Request'ы, интеграция через compare-and-set, реестр целей, главные сессии Claude и Codex; на поддержке |
| skill-agents-management | `v0.5.22` (task-board закреплён на `v0.5.19`): реестр моделей, запуск, лимиты |
| Curator, curator-spec | `v0.15.0-rc.1` и `v1.0.0-rc.12`: скиллы, профили, оверлеи, аудит |
| curator-agent-launcher | `v0.1.0`: `curator run` без учёта сессий |
| curator-skill-registry | в реализации, без релизов |
| ax | только фундамент кода; спека `v0.7.0` |
| board-server | поддерживается, не возрождается |
| relux-agents-infra | устаревший остаток, в архив на вехе M6 |

В спеках: процессы v4.3 (`curator-playbook` PR #5), доверие v0.3 (`curator-trust` PR #1), Кипер v0.4 (`curator-keeper` PR #1), session host v0.2 (`agent-session-host` PR #1), waggle v5.1 с A1 (PR #7); launch profiles и agent selection лежат в `.specs/drafts/` task-board, model routing, network profiles и inference plane — в своих репозиториях, распределённая пасека — в `curator-agent-runtime`. ⟦предложено⟧

Обновление на 29 сентября: процессы v4.8 (`curator-playbook`), доверие v0.4, Кипер v0.5.1, session host v0.3, waggle v5.2; Curator `v0.15.0-rc.2`, curator-spec `v1.0.0-rc.13`, skill-agents-management `v0.5.27`; task-board ставится из `main` (8f9ec43). ⟦работает сегодня⟧

## Порядок работ

Порядок решён 24 сентября. ⟦решено⟧

1. **SH** — модуль session host, и на нём **CM1** — waggle на одной машине.
2. **PC0 и PC1** — спека процессов и модуль `curator-playbook`, первые демо и опровергатель.
3. Остаток **M0**, **M2** — дочерние run'ы на Curator, **M5a** — локальные модели, **M6** — agents-infra в архив, **M5b** — доступность.
4. **CM2** — два оператора через NATS, **M3** — сессии через `curator run`, **PC2** — скиллы ролей пакетами.
5. **M4** — launch profiles, **PC3** — модуль доставки и доверие на ключах.
6. Позже: **M7** — сеть, **M8** — маршрутизация, **KP** — Кипер, свой цикл агента, **AR** — распределённая пасека, формальные методы.

В работе, по плану на конец 24 сентября: session host (`EPIC-260924-3q1f1v`, `STORY-260924-2jwvbm`), waggle CM1 (`EPIC-260907-jj9f23`), процессы (`EPIC-260924-1byr1t`) и уход с agents-infra: исправление алиасов моделей, теги `vX.Y.Z`, теги Curator, перевод рабочего Mac на Curator. ⟦решено⟧

Ждут оператора: слово «замораживаем» для ядра спеки процессов, передача задания оркестратору Curator, окно для перевода рабочего Mac (перезапустятся все сессии), юридическая проверка лицензий, один хост на машину и форма CLI. ⟦открыто⟧

## Репозитории

Все репозитории — в организации `relux-works` на GitHub. ⟦работает сегодня⟧

| Репозиторий | Что в нём | Доступ |
| ---------------- | -------------- | ------- |
| [skill-agents-management](https://github.com/relux-works/skill-agents-management) | реестр моделей, запуск, лимиты | публичный |
| [skill-agent-facing-api](https://github.com/relux-works/skill-agent-facing-api) | паттерн CLI для агентов | публичный |
| [curator](https://github.com/relux-works/curator), [curator-spec](https://github.com/relux-works/curator-spec) | Curator и его протокол | публичные |
| [curator-skill-registry](https://github.com/relux-works/curator-skill-registry) | реестр аудитов | публичный |
| [curator-agent-launcher](https://github.com/relux-works/curator-agent-launcher) | `curator run` | публичный |
| [curator-playbook](https://github.com/relux-works/curator-playbook) | спека процессов, схема, примеры | приватный |
| [curator-trust](https://github.com/relux-works/curator-trust) | спека доверия | приватный |
| [curator-keeper](https://github.com/relux-works/curator-keeper) | спека Кипера | приватный |
| [agent-session-host](https://github.com/relux-works/agent-session-host) | спека session host | приватный |
| [agent-session-manager](https://github.com/relux-works/agent-session-manager), [agent-session-manager-spec](https://github.com/relux-works/agent-session-manager-spec) | ax и его спека | публичные |
| [curator-inference-manager](https://github.com/relux-works/curator-inference-manager) | локальные движки | приватный |
| [curator-network-profiles](https://github.com/relux-works/curator-network-profiles) | сетевые профили | приватный |
| [curator-model-router](https://github.com/relux-works/curator-model-router) | маршрутизация моделей | приватный |
| [curator-agent-runtime](https://github.com/relux-works/curator-agent-runtime) | распределённая пасека | приватный |
| [waggle](https://github.com/relux-works/waggle) | протокол общения агентов | публичный |
| [relux-agents-infra](https://github.com/relux-works/relux-agents-infra) | старая инфраструктура | публичный, устаревший |

`curator-inference-manager`, `curator-network-profiles`, `curator-model-router` и `curator-playbook` решено открыть под Relux Community License 1.0. ⟦решено⟧ Публикация ждёт юридической проверки. ⟦открыто⟧

## Главные открытые вопросы

Полные списки — в `open-questions.md` и в разделе «Open questions» каждой спеки. ⟦открыто⟧

- **Лицензии**: реализации по нашим спекам не покрыты Relux Community License 1.0; нужны лицензия на спеки, знак совместимости и проверка юристом.
- **Процессы**: профили ролей в пакете процесса, память и персона в оверлеях, словарь `properties`, границы сна, привязка слота процесса к чужой борде, общий бюджет делегирования, первый запуск без `models.toml`.
- **Доверие**: дизайн приложения, как процесс просит право, запечатывание, потолок yolo, глубина веба доверия, доверие к аудитам при восстановлении, пороги L1, устройство посредника.
- **Сессии**: один хост на машину, мост к ax, `steer` у Claude, приостановка run'ов, форма `handoff_ref` и аварийной остановки.
- **Кипер**: имена команд, создание и регистрация улья, пороги маршрутизации, содержимое и шифрование бэкапа, перенос секретов.
- **Остальное**: сроки федерации waggle, вывод board-server из эксплуатации, раннеры CI, состав публичной вики.
