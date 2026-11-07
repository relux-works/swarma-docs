# Доска Swarma

Доска хранит факты задач и предоставляет планы через явно выбранную службу. Корневого README в этой ревизии нет. Точки входа описаны в [скилле клиента][skill], [справочнике соединений][connection] и [README поставщика данных][readme].

## Установка и запуск

Общая команда установки в этих источниках не задана. Нужны отдельно предоставленный клиент `swarma-board`, уже работающая служба и разрешённая проекция соединения с проектом и ожидаемой учётной записью. Клиент не ищет конфигурацию в домашнем каталоге или окружении.

Локальная проверка возможностей из справочника:

```sh
swarma-board --deployment-profile=single-trust-unit --deployment-status
```

Это статический отчёт, а не готовность службы. Чтение `q 'count()'` требует явной `--deployment-projection` с каноническим абсолютным путём. Полная форма дана в справочнике соединений.

## Ограничения

Профиль `single-trust-unit` использует Unix-сокет и общий UID без изоляции агентов. Профиль `production` отклоняется. Клиент не запускает службу, не повторяет запись и не переходит к локальному хранилищу. Неизвестный результат записи требует чтения и сверки. Миграция и переключение хранилища из этих команд не следуют. [Скилл поставщика данных][provider] описывает отдельный интерфейс хранения.

[К справочнику](README.md).

[skill]: https://github.com/relux-works/swarma-board/blob/521822000c76ebcb8c94f2817810bb83784c097b/agents/skills/swarma-board/SKILL.md
[connection]: https://github.com/relux-works/swarma-board/blob/521822000c76ebcb8c94f2817810bb83784c097b/agents/skills/swarma-board/references/client.md
[readme]: https://github.com/relux-works/swarma-board/blob/521822000c76ebcb8c94f2817810bb83784c097b/docs/data-provider/README.md
[provider]: https://github.com/relux-works/swarma-board/blob/521822000c76ebcb8c94f2817810bb83784c097b/agents/skills/swarma-board-dataprovider/SKILL.md
