# Хранилище ключей Swarma

Модуль содержит нативное хранение ключей на macOS, узкие интерфейсы подписи и KEK и отдельные типизированные доверенности. [README][readme] описывает сборку, [скилл][skill] задаёт границу операций владельца.

## Установка и запуск

Для нативного хранения нужны macOS, Go 1.26.0 или новее с закреплённым toolchain Go 1.26.10, cgo, Apple Command Line Tools и Swift CryptoKit. Раздел `Tools and local build` README задаёт сборку `mac-keyvault`, `mac-keyvault-kek` и парного `mac-keyvault-enclave`. Помощник остаётся рядом со своим CLI. Сборка не заменяет установленные программы и не переносит ACL Keychain.

`cmd/swarma-keyvault` предоставляет семейства `grants`; `cmd/mac-keyvault` предоставляет управление записями, `signer serve` и `ssh-agent`. Подкоманд `keys` и `kek` у него нет. Для KEK используется отдельный `cmd/mac-keyvault-kek` и пакет `pkg/kekclient`. Выбор интерфейса и точные команды находятся в тематических ссылках скилла.

## Ограничения

Создание ключей, запуск подписанта, чтение хранилища и операции присутствия выполняются только на отдельно разрешённой встрече с владельцем. Даже `list`, `describe` и vault-backed `pub` могут обращаться к Keychain. Отказ подтверждения завершает попытку. Переносимая проверка и Linux-библиотеки не означают переносимого хранения или полной Linux-службы. Типизированного подписанта релизов и публичного SDK подписанта нет.

[К справочнику](README.md).

[readme]: https://github.com/relux-works/swarma-keyvault/blob/d9e5b2143f2cf1808558231b10b34c2dc0731390/README.md
[skill]: https://github.com/relux-works/swarma-keyvault/blob/d9e5b2143f2cf1808558231b10b34c2dc0731390/agents/skills/swarma-keyvault/SKILL.md
