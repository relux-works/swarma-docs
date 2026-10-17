# Рецепты для человека и spawned agents

## macOS desktop: Claude сегодня

Запустите из того же вида сессии, из которого будет работать launcher:

```bash
eval "$(curator env resolve claude_code --profile P --format shell)"
claude auth login
claude auth status --json
```

Это документированный путь rc.6. Desktop login относится к выбранному `CLAUDE_CONFIG_DIR`; проверяйте `loggedIn` и `authMethod` в том же окружении. Не прикладывайте credential files к отчёту. ⟦работает сегодня⟧

## ssh: не переносите desktop-предположение

Для Claude сегодня используйте те же resolve и login внутри ssh-сессии с доступным native file path. Desktop login не подтверждает готовность ssh. Если у OS user вообще нет login Keychain, измеренный native login не сохранялся: повтор команды не создаёт file fallback. Для такого случая нужен иной поддержанный источник; setup-token через executor пока предложен. ⟦работает сегодня⟧ ⟦предложено⟧

Не нужно менять selector Claude на `file`: force-file interface у Curator не квалифицирован. Это решённый отказ, а не обход проблемы ssh. ⟦решено⟧

## Linux server

Claude использует `<home>/.credentials.json`, так что `shared` может связать его с native file. Для Codex сначала проверьте native store: если ключ отсутствует и используется file, shared link — обычный рабочий путь. Переносить выводы macOS Keychain на Linux нельзя. ⟦работает сегодня⟧

## Codex: отдельный login после rc.7

При `isolated` для пары профиля и среды после rc.7:

```bash
curator env config set credential_store.P.codex_cli file
curator env login codex_cli --profile P
```

Это задаёт store, но не переключает isolation. Пара должна уже быть настроена как `isolated`; shared login команда отвергает. Для native file login в shared ничего дополнительно не нужно. ⟦решено⟧ ⟦работает сегодня⟧

## Muse

Измеренный путь использует `TBH_CREDENTIAL_BACKEND=file` и `$XDG_CONFIG_HOME/muse/auth.json`. Для shared home его `auth.json` связывается с native file; для isolated login отдельный. D10 допускает оба режима; rc.7 должен применять backend и при login, и при launch. Не полагайтесь на default global Keychain для изоляции homes. ⟦работает сегодня⟧ ⟦решено⟧

## Spawned agents

Человек заранее готовит профиль через `curator profile prepare P` после rc.7 и читает readiness для всех сред. Run получает session snapshot, а не live managed home, по D4–D6. Это решения для интеграции, а не уже подтверждённый end-to-end запуск. ⟦решено⟧

Для Claude желаемый путь — enroll setup-token один раз и передача env token final executor каждому spawned agent. Он снимает per-home login и годится для inference без Remote Control. Enrollment CLI и весь delivery path ещё не реализованы в описанном срезе. ⟦предложено⟧

## Если появилось «Not logged in»

1. Сверьте версию и фактические config variables выбранного home. Случайный запуск в native home не проверяет managed home.
2. Для Claude сопоставьте происхождение login и запуска: desktop-потомок или ssh-потомок. Проверьте `loggedIn` и `authMethod` через `claude auth status --json`.
3. Для Codex проверьте `cli_auth_credentials_store` и launch override. Для Muse — `TBH_CREDENTIAL_BACKEND` и наличие ожидаемого file/link без чтения credential bytes.
4. Сверьте `shared`/`isolated` и source. Не лечите shared отсутствием отдельного login: войдите в native среде. При inherited source проверяйте доставку source, а не создавайте per-home login.
5. Если selector недавно изменён, учитывайте: миграции не было. Возвращайтесь к login в нужном store и нужном виде сессии, не удаляя старый login вслепую.

Первые проверки опираются на измеренные свойства инструментов. Автоматические подсказки `env login` и prepare относятся к решённому rc.7; inherited setup-token path остаётся Draft. ⟦работает сегодня⟧ ⟦решено⟧ ⟦предложено⟧
