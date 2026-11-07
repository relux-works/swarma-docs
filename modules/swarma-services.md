# Службы Swarma

Репозиторий объединяет независимые подпроекты. У каждого свой Go-модуль, README и скилл. [Корневой README][readme] не задаёт общей команды установки или запуска.

## Установка и запуск

Выберите подпроект до выбора инструментов:

| Подпроект | Вход и ограничения |
| --- | --- |
| [signer][signer] | Нужен Go 1.24 или новее и точные зависимости своего модуля. [Скилл][skill] описывает внутренние Go-компоненты; CLI службы и команды установки нет. `RunNative` закрыт отказом. |
| [shell-out][shell] | Нужны Go 1.25 или новее и Git для работы в Git-проекте; сторонних Go-зависимостей нет. Его [скилл][shellskill] и README задают команды ручного частного сохранения вывода. Сборка выполняется из `shell-out/src/`. |
| [pktscan][packet] | Linux-инструмент ограниченного разбора пакетов с выводом только счётчиков. Его [скилл][packetskill] отделён от подписанта. |

Для pktscan README требует неизменённый Go 1.26.8. Сборка выполняется из каталога `pktscan/`:

```sh
GOTOOLCHAIN=local GOPROXY=off GOSUMDB=off go build ./cmd/pktscan
```

Запуск требует выбранного пакета и файла шаблонов. Точная форма, частные абсолютные HOME/TMP/кэш, автономная изоляция и внешний предел времени приведены в README pktscan. Сам инструмент не является песочницей. У signer и shell-out свои требования; версия компилятора pktscan на них не переносится.

## Ограничения

Проверка переданных байтов не подтверждает полномочия источника, полноту зависимостей или разрешение подписи. Нативные SDK, провайдеры и изоляция signer требуют отдельной квалификации. README pktscan сохраняет статус локального кандидата с обязательным независимым ревью перед установленным использованием.

[К справочнику](README.md).

[readme]: https://github.com/relux-works/swarma-services/blob/b87443e39a1965e9a7d968b72718df7f7e7f8a34/README.md
[skill]: https://github.com/relux-works/swarma-services/blob/b87443e39a1965e9a7d968b72718df7f7e7f8a34/agents/skills/swarma-services/SKILL.md
[signer]: https://github.com/relux-works/swarma-services/blob/b87443e39a1965e9a7d968b72718df7f7e7f8a34/signer/README.md
[shell]: https://github.com/relux-works/swarma-services/blob/b87443e39a1965e9a7d968b72718df7f7e7f8a34/shell-out/README.md
[packet]: https://github.com/relux-works/swarma-services/blob/b87443e39a1965e9a7d968b72718df7f7e7f8a34/pktscan/README.md
[shellskill]: https://github.com/relux-works/swarma-services/blob/b87443e39a1965e9a7d968b72718df7f7e7f8a34/shell-out/SKILL.md
[packetskill]: https://github.com/relux-works/swarma-services/blob/b87443e39a1965e9a7d968b72718df7f7e7f8a34/pktscan/SKILL.md
