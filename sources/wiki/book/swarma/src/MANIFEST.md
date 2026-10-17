# Рисунки книги Swarma: манифест

> Редакция: v0.12 (2026-10-13). Главы перенумерованы после добавления «Сети агента»; ссылки в источниках книги обновлены. Копии закреплённых upstream-рисунков не изменены.

Каждый рисунок книги собирается из исходника PlantUML в этом каталоге. Рендер — `diagrams/<имя>.png`, его делает CI (`.github/workflows/swarma-book.yml`):

```
java -DPLANTUML_LIMIT_SIZE=16384 -jar plantuml-1.2025.4.jar -tpng -o "$PWD/book/swarma/diagrams" book/swarma/src/*.puml
```

Перед рендером CI запускает `book/swarma/check-figures.sh`: у каждой картинки из глав есть исходник и строка здесь, у каждой копии хэш совпадает с записанным, в `diagrams/` нет картинок без исходника.

**Свежесть копий.** За свежесть копий отвечает автор книги: на каждом выпуске книги копии сверяются с текущей основной веткой исходника и обновляются вместе с пином и хэшем в этой таблице. Копия, отставшая от исходника, — дефект выпуска, а не допустимое расхождение.

**Происхождение.** «книга» — исходник ведёт книга; он следует спецификациям модулей, ссылки на разделы — в комментариях в начале файла. «копия» — байт в байт копия файла из другого репозитория на записанной ревизии; править её здесь нельзя: исправление делается в источнике, потом копия обновляется вместе с ревизией и хэшем в этой таблице.

**Статус** повторяет пометки книги: «спецификация» — рисунок описывает черновик спецификации модуля, «архитектура» — общий дизайн без модуля, «черновик CIP» — предложение Curator, ещё не принятое, «концепция» — замысел.

| Рисунок | Исходник | Происхождение | SHA-256 копии | Главы | Статус |
| --- | --- | --- | --- | --- | --- |
| action-namespace-registration | src/action-namespace-registration.puml | копия: swarm-platform-architecture @ 08c3b1e00e7284e0e1bc99029cb9ff8c6ce98ce1, diagrams/plantuml/sequence/action-namespace-registration.puml | a11464a97975d47e7b828350c527add2a18e92e0102e313cf75785ffdd981714 | 06 | архитектура |
| agent-wake | src/agent-wake.puml | книга | — | 08 | спецификация, SH2+ |
| board-components | src/board-components.puml | книга | — | 13 | архитектура |
| board-transition-spawn | src/board-transition-spawn.puml | книга | — | 13 | архитектура |
| bridge-components | src/bridge-components.puml | книга | — | 09 | архитектура |
| controlled-restart | src/controlled-restart.puml | книга | — | 08 | спецификация, SH2+ |
| credential-lease-revocation | src/credential-lease-revocation.puml | книга | — | 11 | спецификация |
| delegated-action-handler | src/delegated-action-handler.puml | копия: swarm-platform-architecture @ 567b07701bdf32cdebc516e38e6f0321fc5253a0, diagrams/plantuml/sequence/delegated-action-handler.puml | 4097c5102ca22fcc9d8ff600483dc20d485327f693732a0e86a57f0b61b117eb | 07 | архитектура |
| donor-first-deployment | src/donor-first-deployment.puml | копия: curator-spec @ b14aeebfa2bf51afd7a39e423d07e89bf590c534, cips/diagrams/donor-first-deployment.puml | 27dca9274151365642c6b231512ec275006ce0f6482d65b80b748b1891e63086 | 12 | черновик CIP |
| donor-variants | src/donor-variants.puml | копия: curator-spec @ b14aeebfa2bf51afd7a39e423d07e89bf590c534, cips/diagrams/donor-variants.puml | 4b1f28bc87a7f371fd111ed3530bb8fca257f435da111e33acc9169527b7a086 | 12 | черновик CIP |
| goal-loop | src/goal-loop.puml | книга | — | 09 | архитектура, D-GOALS |
| grant-issue-and-check | src/grant-issue-and-check.puml | копия: swarm-platform-architecture @ 567b07701bdf32cdebc516e38e6f0321fc5253a0, diagrams/plantuml/sequence/grant-issue-and-check.puml | 0e7280209cfc5b1d35ede54a5afdbeba741557edb94f16318dce13625220e732 | 06 | архитектура |
| join-handshake | src/join-handshake.puml | копия: curator-spec @ b14aeebfa2bf51afd7a39e423d07e89bf590c534, cips/diagrams/join-handshake.puml | d4a19b3cd573c3b121f2f29c229049700a1d9844b23cc5f83d193e7f7a0e16c1 | 12 | черновик CIP |
| keeper-sign | src/keeper-sign.puml | книга | — | 05 | архитектура |
| long-session-goals | src/long-session-goals.puml | книга | — | 08 | спецификация, SH2+ |
| mailbox-delivery | src/mailbox-delivery.puml | копия: swarm-platform-architecture @ 567b07701bdf32cdebc516e38e6f0321fc5253a0, diagrams/plantuml/sequence/mailbox-delivery.puml | 9d6ba8c41c22fb11726c1bab6a14962f95bd2d8176cbaeb5da6794926b2eb49a | 07 | архитектура |
| operator-phone | src/operator-phone.puml | книга | — | 05 | спецификация, решено 12.10 |
| one-shot-agent | src/one-shot-agent.puml | книга | — | 10 | решено 11.10, выключено |
| overview | src/overview.puml | книга | — | 02 | спецификация |
| platform-context | src/platform-context.puml | книга | — | 02 | спецификация |
| platform-storage-layout | src/platform-storage-layout.puml | книга | — | 03 | спецификация |
| remote-worker-retire | src/remote-worker-retire.puml | копия: curator-spec @ b14aeebfa2bf51afd7a39e423d07e89bf590c534, cips/diagrams/remote-worker-retire.puml | f9ba59035e3f3a3b259dbe1950adbb2b4705ff6a166a3e5c1cf1d567ace4d3a8 | 12 | черновик CIP |
| remote-worker-turn | src/remote-worker-turn.puml | копия: curator-spec @ 5b5efa200ba86da56098470cdbdaad449d473a14, cips/diagrams/remote-worker-turn.puml | 53341a74f00da1d28df8f66a55db13bc66a0f33c8b5f45c9ad809f3fbba4d68b | 12 | черновик CIP |
| standing-team-start | src/standing-team-start.puml | книга | — | 14 | спецификация, SH2+ |
| three-layers | src/three-layers.puml | книга | — | 16 | концепция |
| worker-code-path | src/worker-code-path.puml | книга | — | 12 | решено 13.10, спецификация в работе (волна 5) |
