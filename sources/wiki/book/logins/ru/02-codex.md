# Codex CLI: store выбирается настройкой

В Codex CLI 0.153.2 store задаётся ключом `cli_auth_credentials_store` в `config.toml`. Если ключ отсутствует, используется `file`: `$CODEX_HOME/auth.json`. Значения `keyring` и `auto` используют OS keyring. Поэтому утверждение «Codex всегда читает auth.json» неверно: сначала нужно выяснить native настройку. ⟦работает сегодня⟧

Командный override `-c cli_auth_credentials_store='"file"'` выбирает file для одного invocation и имеет приоритет над файлом конфигурации. Кавычки вокруг `file` внутри shell-аргумента сохраняют строковое значение TOML. Curator применяет этот механизм в launcher; переписывать принадлежащий Codex `config.toml` не требуется. ⟦работает сегодня⟧

Для `shared` Curator связывает credential file managed home с native файлом. Это подходит к обычному native file login. Если native использует keyring, наличие или отсутствие соседнего `auth.json` само по себе ничего не доказывает. Выбор store должен предшествовать решению о link. ⟦работает сегодня⟧ ⟦решено⟧

В rc.7 typed `-c` overrides будут общим транспортом profile-level Codex settings с наследованием (CIP-0018, D13). Но значение credential store приходит из machine selector по D14. Профиль не получает права отправлять токены в file только потому, что умеет передавать другие Codex settings. ⟦решено⟧
