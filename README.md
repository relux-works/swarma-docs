# swarma-docs

Пейпер и книга о платформе Swarma: рантайм роя агентов на машинах владельца (Swarma Runtime), протокол совместной разработки агентами независимых владельцев (Swarma Protocol) и цепочка идентичностей, аттестаций и репутации (Swarma Chain).

Авторы: Алексей Григорьев, Иван Опарин. Relux Works, 2026.

Версия на русском — источник правды; английская делается позже переводом с неё. Где тексты расходятся со спецификациями модулей, расхождение поднимается к владельцам и решается в каждом случае отдельно; до решения права книга Swarma (решение 86 в `editorial/decisions.ru.md`; у книги об a2a своё правило, см. `editorial/sources.ru.md`).

## Текущие версии

| Документ | Версия | PDF | Объём |
| --- | --- | --- | --- |
| Пейпер «Swarma: платформа для роёв автономных агентов» | 7.1.0 | `dist/swarma-platform-7.1.0.ru.pdf` | 22 страницы |
| Пейпер «Swarma: проверяемые границы доверия для роёв автономных агентов» | 6.2.0 | `dist/swarma-trust-6.2.0.ru.pdf` | 13 страниц |
| Пейпер «Swarma Chain: личности, имена и ценность для роёв автономных агентов на одних хэш-функциях» | 1.1 | `dist/swarma-chain-1.1.ru.pdf` | 19 страниц |
| Приложение «Swarma: состояние реализации» | 6.2.0 | `dist/swarma-status-appendix.ru.pdf` | 2 страницы |
| Книга «Swarma» | 1.7.1 | `dist/swarma-book-1.7.1.ru.pdf` | 32 главы в пяти частях, 54 рисунка, 305 страниц |

Оба PDF собраны из `main` после ревью каждой главы и раздела и редакторского прохода.

## Состав

| Путь | Что |
| --- | --- |
| [modules/](modules/README.md) | справочник модулей: опубликованные команды установки и запуска, требования и ограничения на закреплённых ревизиях |
| `paper/paper.tex` | пейпер «Swarma: платформа для роёв автономных агентов», 10–12 страниц; продолжает работу «Разработка программного обеспечения роем автономных агентов над единой средой исполнения» (редакции 1–3.3) |
| `paper/model/` | исполняемая модель фрагмента интеграции: исчерпывающий перебор состояний в заданных границах |
| `book/ru/` | книга «Swarma», по главе на файл |
| `a2a-book/ru/` | небольшая книга «a2a» об архитектуре модуля обмена сообщениями агентов, по главе на файл; план в `editorial/a2a-book-outline.ru.md`; исходники рисунков в `a2a-book/src/`, рендеры в `a2a-book/diagrams/` |
| `install-book/ru/` | небольшая книга «Установка Swarma»: от одной команды на чистой машине до кипера, который пишет владельцу, по главе на файл; состояние частей в `install-book/ru/07-gde-my.md` |
| `link-book/ru/` | книга Swarma Link, версия 0.4: личность, доверенности и договоры, сквозной пример аренды агента; [карта ключей](link-book/ru/03-klyuchi.md#карта-ключей) в главе о ключах; собственная глава "Где мы" в `10-gde-my.md`; сборка `link-book/build.sh` |
| `talk-book/ru/` | книга Swarma Talk, черновик 0.3-rc1: опирается на Swarma Link; собственная глава "Где мы" в `10-gde-my.md`; сборка `talk-book/build.sh` |
| `forum-book/ru/` | книга Swarma Forum, черновик 0.3-rc1: публичные записи memo на Namecoin; собственная глава "Где мы" в `06-gde-my.md`; сборка `forum-book/build.sh` |
| `link-book/src/`, `link-book/diagrams/` | исходники TOML рисунков книги Swarma Link для `scripts/diagram-kit/` и их SVG, которые рендерит оркестратор; раскладки `stack` и `sequence`, Graphviz им не нужен |
| `UNRESOLVED_QUESTIONS.md` | открытые решения новых книг; состояние реализации находится в главах «Где мы» |
| `install-book/src/`, `install-book/diagrams/` | исходники TOML рисунков книги установки для `scripts/diagram-kit/` и их SVG, которые рендерит оркестратор |
| `book/diagrams/`, `book/src/` | диаграммы книги (SVG) и их исходники TOML для `scripts/diagram-kit/` |
| `twopager/` | двухстраничник «Swarma: платформа для роёв ИИ-агентов» простым языком: русский исходник (источник правды), английская версия, стиль A4 и PDF обеих версий |
| `editorial/` | рабочие материалы авторов: имена, стиль, источники, планы пейпера и книги, направление об идентичности и репутации |
| `editorial/notes/signing-auth/` | отдельная записка «Подписи и аутентификация в Swarma»: русские исходники, объявленные SVG и PDF для ревью; сборка описана в её README |
| `editorial/research/` | исследования архитектурных вариантов; [язык ядра Swarma Signer](editorial/research/signer-core-language.md): Go, Rust и Swift, источники и границы проверки |
| `sources/` | снимки исходных документов на зафиксированных ревизиях; рабочий материал, перед публикацией удаляется |
| `dist/` | готовые PDF пейпера и книги, которые собирает оркестратор после ревью |
| `scripts/check.sh` | проверка гигиены текстов: пометки статуса, внутренние идентификаторы, локальные пути, выведенные из оборота имена |
| `editorial/diagram-style.ru.md`, `scripts/diagram-kit/` | единый стиль диаграмм: правила, тема и генератор SVG; все рисунки книги нарисованы им, пилоты записки о подписях носят суффикс `-v2` |

## Инструменты

| Инструмент | Зачем | Как запустить | Куда пишет |
| --- | --- | --- | --- |
| tectonic 0.17 (движок XeTeX) | сборка пейпера; пакеты подтягивает сам | `make -C paper` | `paper/paper.pdf` |
| Python 3.9+ | прогон модели фрагмента интеграции | `make -C paper model` | stdout |
| pandoc 3.x | книга: Markdown → HTML, оглавление, нумерация | через `book/build.sh` | временный каталог |
| WeasyPrint 69+ | книга: HTML → PDF; сборка сначала гоняет `book/check-figures.sh`, проход рендера без Graphviz 14.0.4 валит её (`BOOK_SKIP_FIGURE_RENDER=1` пропускает его для черновика) | `book/build.sh` | `book/swarma-book.ru.pdf` |
| `install-book/build.sh` (pandoc 3.x, WeasyPrint 69+, Graphviz 14.0.4 для прохода рендера) | книга установки: Markdown → HTML → PDF с шаблоном, стилем и фильтром книги «Swarma»; сначала структурная проверка рисунков (у ссылки исходник, у исходника SVG), затем проход рендера (рендер свежий и проходит `--require-fit` для своего поля; `INSTALL_BOOK_SKIP_FIGURE_RENDER=1` пропускает его для черновика) | `bash install-book/build.sh [ru [OUT]]` | `install-book/swarma-install.ru.pdf` |
| `link-book/build.sh`, `talk-book/build.sh`, `forum-book/build.sh` (pandoc 3.x, WeasyPrint 69+) | книги Swarma Link, Talk и Forum: Markdown → HTML → PDF с шаблоном и фильтром книги «Swarma»; `style.css` каждой книги меняет колонтитул | `bash link-book/build.sh [ru [OUT]]`, `bash talk-book/build.sh [ru [OUT]]`, `bash forum-book/build.sh [ru [OUT]]` | `link-book/swarma-link.ru.pdf`, `talk-book/swarma-talk.ru.pdf`, `forum-book/swarma-forum.ru.pdf` |
| `twopager/build.sh` (pandoc 3.x, WeasyPrint 69+, `pdfinfo`) | двухстраничник: Markdown → HTML → PDF тем же путём, что книга; сборка падает, если в PDF не ровно две страницы | `bash twopager/build.sh [ru\|en]` | `twopager/swarma-twopager.{ru,en}.pdf` |
| PlantUML | исходники рисунков записки о подписях (рендер через `platform-book figures`) и пробник стиля | см. `editorial/notes/signing-auth/README.md` | `editorial/notes/signing-auth/diagrams/` |
| `book/check-figures.sh` (Graphviz 14.0.4 для прохода рендера) | рисунки книги: структурный проход (у каждой ссылки исходник и строка манифеста, класс поля совпадает со столбцом «Поле») и проход рендера (рендер свежий и проходит `--require-fit` для своего поля); вызывается из `book/build.sh` | `bash book/check-figures.sh [--structural \| --render]` | stdout; ненулевой код при нарушении |
| `a2a-book/build.sh` (pandoc 3.x, WeasyPrint 69+, Graphviz 14.0.4 для прохода рендера) | книга «a2a»: обёртка над `book/build.sh` с `BOOK_ROOT=a2a-book`; рисунки проверяются по `a2a-book/src/MANIFEST.md`, `a2a-book/style.css` меняет колонтитул; сборка книги Swarma без `BOOK_ROOT` не меняется | `bash a2a-book/build.sh [ru [OUT]]`; рисунки отдельно `BOOK_ROOT=a2a-book bash book/check-figures.sh` | `a2a-book/a2a-book.ru.pdf` |
| шрифты PT Serif, PT Sans, PT Mono | текст, заголовки, код | системные | — |
| `scripts/check.sh` | гигиена текстов всех шести книг и пейпера; пометки и оговорки о поставке только в главах «Где мы» (`book/ru/32-gde-my.md`, `a2a-book/ru/09-gde-my.md`, `install-book/ru/07-gde-my.md`, `link-book/ru/10-gde-my.md`, `talk-book/ru/10-gde-my.md`, `forum-book/ru/06-gde-my.md`); знак переноса в `book/style.css` задан дефисом, который есть в шрифтах PT | `sh scripts/check.sh` | stdout; ненулевой код при блокирующем нарушении |
| Python 3, `scripts/check-self-test.py` | положительные и отрицательные проверки гигиены на изолированных примерах | `python3 scripts/check-self-test.py` | stdout/stderr; временные примеры в `.temp/` удаляются |
| `scripts/diagram-kit/render.py` (Python 3.11+, Graphviz 14.0.4 для раскладки `graph`, `rsvg-convert` для PNG) | диаграммы в едином стиле из TOML; проверяет исходник по схеме и геометрию рисунка; `--report` печатает самый мелкий кегль в поле рисунка книги, `--require-fit tall` завершает с кодом 3, если рисунок не помещается, `--draft` пишет SVG с нарушением для просмотра | `python3 scripts/diagram-kit/render.py book/src/имя.toml book/diagrams/имя.svg --report` | SVG рядом с исходником; PNG по `--png` |
| `scripts/diagram-kit/test_render.py` | положительные и отрицательные проверки генератора, контрольные закладки для lint, свежесть всех рисунков книги и пилотов `-v2` | `python3 scripts/diagram-kit/test_render.py` | stdout; временные файлы удаляются |
| `scripts/diagram-kit/probe/run.sh` (D2, PlantUML, Mermaid CLI, WeasyPrint, `pdftoppm`; чего нет, пропускается) | воспроизводит сравнение инструментов из `editorial/notes/diagram-style-notes.ru.md`; сбой рендера генератора даёт код 1 | `sh scripts/diagram-kit/probe/run.sh` | `.temp/diagram-probe/` |
| platform-book | сборка отдельной записки о подписях; закреплённая ревизия и команды в `editorial/notes/signing-auth/README.md` | `platform-book ready`, `figures`, `build`, `check-pdf` | `editorial/notes/signing-auth/signing-auth.ru.pdf` |

## Как идёт работа

Каждое изменение — задача на доске архитектуры платформы: продьюсер пишет, ревьювер проверяет по источникам и по `editorial/`, принятая ревизия приходит в `main` через pull request с подписанными коммитами. PDF собирает оркестратор после ревью.
