# Muse: глобальный Keychain и явный file backend

В Muse 1.4.8 на macOS default login — один глобальный Keychain item `ai.meta.dev.credentials`. `auth.json` служит fallback. В метаданных сессий встречаются `credential_backend=keychain`, `keychain_fallback_file` и `file`. Разные homes при таком default ещё не означают разные Keychain logins. ⟦работает сегодня⟧

Без Keychain OAuth проходил, но сохранить login не удавалось: «keychain write failed (os status -60006)», exit 1. Название fallback не доказывает, что отсутствие Keychain автоматически приводит к file login: в этом опыте fallback не было. ⟦работает сегодня⟧

## Что меняет `TBH_CREDENTIAL_BACKEND=file`

При явном `TBH_CREDENTIAL_BACKEND=file` login сохраняется в `$XDG_CONFIG_HOME/muse/auth.json`, mode 0600. Следующие запуски используют backend `file` без обращений к Keychain. После скрытия файла credentials отсутствуют. Home, чей `auth.json` является link на файл другого home, работает. Именно на этом основан `shared`. ⟦работает сегодня⟧

D10 допускает Muse `isolated` и `shared` через file backend, не дожидаясь опыта с token refresh. Применение backend при login и launch входит в rc.7. Проверенная возможность Muse и готовность интеграции Curator — разные статусы. ⟦решено⟧

## API keys

Minted API key, переданный через `exec --api-key-stdin`, расходует subscription. `META_API_KEY` оставляет credential store нетронутым. D11 принимает долгоживущие credentials, включая minted key Muse, для swarm v0. Здесь нет примеров ключей и нет инструкции записывать их в профиль. ⟦работает сегодня⟧ ⟦решено⟧

Записи при token refresh не измерены. Успешное первое чтение через link не доказывает, что обновление токена сохранит link, права файла и согласованность при нескольких процессах. ⟦открыто⟧
