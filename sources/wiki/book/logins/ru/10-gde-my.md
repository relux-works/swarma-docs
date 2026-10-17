# Где мы сейчас

Статусы этой таблицы повторяют facts pack от 16 октября 2026: установлен Curator rc.6, main `205272e7`. Нормативное решение в curator-spec не равно выпущенной реализации.

| Возможность | Состояние на дату среза |
| --- | --- |
| `isolation.<profile>.<env-id>` shared/isolated | ⟦работает сегодня⟧ |
| Claude macOS per-home login через resolve shell и `claude auth login` | ⟦работает сегодня⟧ документированный путь |
| `credential_store.<profile>.<env-id>` | ⟦решено⟧ CIP-0015/D14, реализация в rc.7 |
| `curator env login`, `curator profile prepare`, login readiness row | ⟦решено⟧ CIP-0015, реализация в rc.7 |
| Codex profile settings через `-c` | ⟦решено⟧ CIP-0018, реализация в rc.7 |
| Muse `root_context` и `TBH_CREDENTIAL_BACKEND=file` в Curator | ⟦решено⟧ CIP-0017/D10, реализация в rc.7 |
| Claude setup-token env source (OAuth) | ⟦предложено⟧ CIP-0010 Draft, требуется поддержка и реализация |
| Managed home snapshots, `env materialize` | ⟦решено⟧ CIP-0014, реализация в rc.7 |

## Открытые границы

Refresh write behaviour остаётся неизмеренным. Для Muse file link нужно отдельно проверить обновление credentials, atomic replacement, права и конкуренцию. Доказательство начального login не закрывает эти вопросы. ⟦открыто⟧

Force-Keychain interface Muse пока не qualified. У Claude нет force-file или force-Keychain interface для machine selector. До qualification нельзя обещать эти принудительные stores. У Codex keyring override допустим только на qualified macOS backend. ⟦открыто⟧ ⟦решено⟧

CIP-0010 ещё требует нормативного текста и реализации enrollment, protected store и executor delivery. Желание поддержать OAuth path принято к работе, но не даёт оснований поставить «работает сегодня» всему пути. ⟦предложено⟧

После смены версии инструментов, OS или способа запуска прежние опыты стоит повторить в scratch users/homes. Сначала проверяется конкретный случай и его отрицательный контроль; только потом обновляются факты и badges. Книга фиксирует известные границы, а не сертификат authentication для произвольной машины. ⟦открыто⟧
