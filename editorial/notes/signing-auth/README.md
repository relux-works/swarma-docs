# Подписи и аутентификация в Swarma

Короткая русская записка для оператора и команды: утверждённая архитектура
Swarm Signer, а не заявление о готовности всех компонентов.
Готовый документ: [signing-auth.ru.pdf](signing-auth.ru.pdf).

## План и основания

Порядок глав: зачем подписывать → ключи и роли корней → телефон → Element →
агент → новое и потерянное устройство → реестр владельца и свежесть → отказы →
конверт → два сервера и два владельца → уверенность и гранты → устройство
Signer и открытые вопросы.

| Основание | Ревизия | Что из него взято |
| --- | --- | --- |
| Книга Swarma 1.3, этот репозиторий | `861725c` | голос завершённой платформы и правила прозы (`editorial/style.ru.md`); главы о ключах, грантах, пути сообщения, допуске к носителю |
| Спецификация подписанных записей `swarm-envelope/2` (relux-works/waggle, main) | `f76a400ebeb599b95a9bf9b2c59b522bef0392d8` | конверт, `message/1`, `operator-act/1`, `attestation/1`, `revocation/1`, журнал и контрольные точки, роли корней, восстановление корня, A0-A3, завершение отзыва, `freshness/1` и проверка свежести (§2.9), явное восстановление свежести, граница состава проверок (§7) |
| Дизайн службы реестра владельца (relux-works/swarma-owner-registry) | `e94675751da6073c6a9ab4ea865c0a80445d2a77` | узел доверия, изолированный процесс подписи, публикация свежести раз в 20 секунд, доказательство публикации, завершение отзыва |
| Спецификация ключника (relux-works/swarma-keymaker) | `595d6a6430d9e01f00fb3b887c108c4e4afc6f6b` | аттестация агента до 24 часов, обновление и доказательство публикации, свидетель отката |
| Схема Signer от 23-24 октября 2026 года (внутренний документ, в тексте записки не упоминается) | — | аппаратный корень, Secure Enclave, цепочка Matrix до аттестации владельца, ядро и приложения |

Подробности по главам и дословный вывод проверок лежат в
[prose-update-notes.ru.md](prose-update-notes.ru.md). Учебный JSON в главе
о конверте использует синтетический ключ и аттестацию из векторов формата;
`body_sha256` и `id` вычислены пакетом `record` спецификации, подпись остаётся
заглушкой. Открытые решения перечислены в [UNRESOLVED_QUESTIONS.md](UNRESOLVED_QUESTIONS.md)
и в последней главе PDF.

## Сборка

Используется исходный checkout публичного скилла `relux-works/skill-platform-book`
на **`1c75fdf4a09960e41ea153645da7c48800b7a82b`**. В переменную `BOOK_SKILL`
передаётся каталог этого checkout. Перед запуском проверить:

```sh
test "$(git -C "$BOOK_SKILL" rev-parse HEAD)" = 1c75fdf4a09960e41ea153645da7c48800b7a82b
```

Команды выполняются из корня документационного репозитория в обычном
активированном venv Python 3.12.15 с пакетами из
`$BOOK_SKILL/requirements-lock.txt`. Pandoc 3.11 и нативные библиотеки WeasyPrint
должны быть подготовлены отдельно, по README скилла. На macOS с Homebrew
задаётся `PLATFORM_BOOK_LIBRARY_PATH=/opt/homebrew/lib`.
Сборщик не устанавливает зависимости. PDF основной книги эти команды не меняют.

```sh
NOTE=editorial/notes/signing-auth
"$BOOK_SKILL/scripts/platform-book" ready
"$BOOK_SKILL/scripts/platform-book" figures "$NOTE"
"$BOOK_SKILL/scripts/platform-book" build "$NOTE" "$NOTE/signing-auth.ru.pdf"
"$BOOK_SKILL/scripts/platform-book" check-pdf "$NOTE/signing-auth.ru.pdf" \
  --expected-pages 14 --fonts "PT Serif" "PT Sans" "PT Mono"
sh scripts/check.sh
python3 -I scripts/check-self-test.py
```

Для записки принят предел **8-14 страниц**, включая обложку и оглавление.
Каждая глава начинается с новой страницы, поэтому при двенадцати главах каждая
должна уместиться на одной странице. Текущая сборка: **14 страниц**. Число
страниц и встраивание шрифтов не заменяют визуального ревью рисунков, таблиц,
кода и переносов.

## Инструменты и артефакты

| Инструмент | Назначение и команда | Результат |
| --- | --- | --- |
| platform-book на закреплённой ревизии | `ready`, `figures`, `build`, `check-pdf` выше; Pandoc + Python WeasyPrint 70.0, pypdf 5.9.0, встроенные PT-шрифты | PDF рядом с исходниками; JSON вердикта в stdout |
| PlantUML 1.2026.6 и Graphviz | `plantuml -tsvg -nometadata -o ../diagrams editorial/notes/signing-auth/src/*.puml` | самодостаточные SVG в `diagrams/` |
| Python 3.12.15, `hashlib` | `hashlib.sha256(path.read_bytes()).hexdigest()` для каждой пары | `src/figures.json`: исходник, SVG и оба хэша; обновить после ревью рисунка |
| Poppler: `pdfinfo`, `pdffonts`, `pdftotext` | независимо проверить страницы, шрифты и извлечение текста | stdout или временные файлы в `.temp/` |
| Poppler: `pdftoppm` | `pdftoppm -scale-to 1400 -png editorial/notes/signing-auth/signing-auth.ru.pdf .temp/signing-auth-page` | временные страницы для визуального ревью в `.temp/` |
| `sh scripts/check.sh` | гигиена книги и пейпера; чёрный список прозы блокирует и `editorial/notes/signing-auth/ru/*.md`; `python3 scripts/check-self-test.py` проверяет это на подложенных нарушениях | stdout |

В `src/` лежат редактируемые PlantUML-исходники. SVG в `diagrams/` — их
рендеры, объявленные в `src/figures.json`. Хэши обнаруживают дрейф, но не
доказывают семантическую верность рисунка: её проверяют вместе с текстом.
Записка не вводит продуктовых проверок и не меняет исполняемого поведения.
Коды отказов взяты из спецификации подписанных записей; интеграционным тестом
криптографии записка не служит.
