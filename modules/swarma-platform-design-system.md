# Дизайн-система Swarma

Репозиторий содержит правила оформления, семантические токены и утверждённые изображения для веб-интерфейсов. Начало работы описано в [скилле][skill], инструменты проверки перечислены в [README][readme].

## Установка и запуск

Самостоятельного приложения или службы нет. Для проверок нужны Node 22.23.4 или новее, Python 3.12 или новее и Chromium через Playwright. Точные Node-зависимости закреплены в `package.json` и `package-lock.json`.

README задаёт подготовку из корня:

```sh
npm ci
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.temp/playwright-browsers"
npx playwright install chromium
```

Переменная сохраняется для следующих проверок. Альтернативный установленный Chromium выбирается только через явный `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` с записью его версии. Команды проверок запускаются через `node scripts/run.mjs`; точные формы перечислены в таблице README.

## Ограничения

Дизайн-система задаёт оформление и проверочные условия; контракт конкретного продукта определяет допустимость рисунков и показа состояния. Знаки и изображения копируются из утверждённых закреплённых ресурсов, без перерисовки. Автоматические браузерные проверки не заменяют ручную матрицу доступности. PR из форков пропускают CI с секретами и остаются непроверенными на этом маршруте.

[К справочнику](README.md).

[readme]: https://github.com/relux-works/swarma-platform-design-system/blob/fa2ae72e6f90cb15cfca2a55e4c93fbcff46b74c/README.md
[skill]: https://github.com/relux-works/swarma-platform-design-system/blob/fa2ae72e6f90cb15cfca2a55e4c93fbcff46b74c/SKILL.md
