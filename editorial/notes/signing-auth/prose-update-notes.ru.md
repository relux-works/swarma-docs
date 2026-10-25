# Записка о подписях: проход по правилам прозы и решениям S0-S4

Задача TASK-261025-acvljn. Ветка `notes/signing-auth-prose-261025` от `origin/main` (`861725c`, книга 1.3).
Рабочие клоны спецификаций, логи и рендеры страниц лежат в `.temp/TASK-261025-acvljn/` и в коммит не входят.

## Источники и закреплённые ревизии

| Источник | Ревизия | Что взято |
| --- | --- | --- |
| swarma-docs, книга 1.3 и `editorial/style.ru.md` | `861725c` | голос завершённой платформы, правила прозы, чёрный список, главы о ключах, грантах, пути сообщения, допуске |
| relux-works/waggle main, `spec/swarm-envelope-2.md`, `UNRESOLVED_QUESTIONS.md` (S0-S3) | `9b42338b8a57d12a21da4db4375b269deacdd6bf` | конверт и `message/1` (§2.1-2.2), криптография (§2.3), закрытый список меток и профили (§2.4), подпись ключника (§2.5), `attestation/1`, `revocation/1`, роли D30, восстановление D31, D32 узел доверия (§1, §2.6), журнал и контрольные точки D34-D37 (§2.7), `operator-act/1` и A3 (§4, R6, D2), A0-A3 и Matrix (§5), коды отказов (§6), завершение отзыва D29 и онлайн-проверка (§7), D26 отказ от WebAuthn, R4 устройства только P-256 |
| relux-works/waggle, ветка `spec/s4-freshness`, PR #13 (ревью ACCEPT, не влита) | `66bbd8a3d35ef2684bc2ce20396249ece4e977ab` | решение владельца D38=B, `freshness/1`, метка `swarma-registry freshness/1`, поля `publication_seq`, `prev`, `issued_at`, проверка свежести (§2.9). В тексте записки это только решение владельца и формат со статусом "предложено" |
| relux-works/swarma-owner-registry, `design/owner-registry.md` | `e94675751da6073c6a9ab4ea865c0a80445d2a77` | узел доверия, роли ключей (§2), изолированный процесс подписи Q3, записи реестра (§4), свежесть раз в 20 секунд (§5.1), граница скрытого хвоста (§5.3), завершение отзыва Q7, доказательство публикации ключника (§5.5), свидетель на узле и контрольная точка вне узла (§6.2) |
| relux-works/swarma-keymaker, `spec/keymaker-msg.md`, `spec/keymaker-msg-state.md`, `spec/keymaker-witness.md`, `UNRESOLVED_QUESTIONS.md` | `595d6a6430d9e01f00fb3b887c108c4e4afc6f6b` | MSG3: корень purpose 5, аттестация агента не дольше 86400 секунд; обновление по истечению, активация только с доказательством публикации (запись журнала, контрольная точка, подтверждение WC1), `key_not_enrolled` без возврата к T1; WC1 размещение решено, развёртывание открыто |
| Пакет `record` waggle на той же ревизии main | `9b42338` | вычисление `id` и `body_sha256` учебного конверта (`.temp/TASK-261025-acvljn/tools/exampleid`) |

Не найдено ни в одной ветке трёх спецификаций: решение D41 и "квитанция свежести". Вопрос оркестратору отправлен
в `#curator` (событие `$uQxmTNaEymzRtN__Cel-ASRXAvXSn3lPlOH-6hKDA54`); ответ (`$K8cNf1wGr0rhZNpdP2dvu0mtilrN6cb0Rlewdj-OKQM`):
S0-S3 из main, D38=B как решение владельца по PR S4, D41 и квитанция свежести одной строкой в "Открытых вопросах".
Так и сделано.

Цепочка Matrix device → self-signing → master → аттестация владельца и FIDO-корень взяты из схемы Signer
(23-24 октября) и прежней записки; в формате v0 аттестации Matrix master и OMEMO отложены (R3, §2.6), это вынесено
в открытые вопросы. Межвладельческое доверие описано через закрепление корней вне полосы (дизайн реестра §2:
"Neither requests nor repository metadata select roots"; §5.3 закрепление root/owner/scope); обмен реестрами между
владельцами исключён из рамок дизайна реестра (Non-goals: registry exchange) и стоит в открытых вопросах.

## Что изменилось по файлам

| Файл | Изменение |
| --- | --- |
| `ru/00-why.md` | Дата 25 октября. A0-A3 по §5 S0 (A2: ключ человека и текущее полномочие; A3: квалифицированный провайдер). Основания: книга 1.3 и три спецификации модулей; убраны тире и ёлочки. |
| `ru/01-keys.md` | Таблица ролей по D30: корень оператора, ключ устройства (только P-256 low-S), корень аттестаций ключника (только агенты, до 24 ч), ключ агента, корень и сервис грантов (D33), ключ реестра (снимки, контрольные точки, свежесть; изолированный процесс Q3). Попарная различимость ролей, ограничение компрометации ролью, восстановление корня (D31, два из трёх). Убрана поддержка Ed25519 FIDO для устройств (R4). Новый рисунок. |
| `ru/02-phone.md` | Критическая команда как `operator-act/1` с полями §4.1; сырая подпись P-256 low-S, отказ WebAuthn (D26); резерв `action_id` и `act_replay`; сужение и расширение; квалификация A3 (решение владельца 2026-10-24) и `act_a3_inactive`. Списки заменены прозой. |
| `ru/03-element.md` | Цепочка device ← self-signing ← master ← аттестация корня оператора; проза вместо нумерованного списка; убраны тире и "пока". |
| `ru/04-agent.md` | Подпись `swarma-msg/2` + `0x0a` + CCJ-1, три пути сверки ключника (§2.5); аттестация агента с привязкой и пределом 86400 с; обновление и доказательство публикации (keymaker-msg-state §1); проверка получателя по `author_attestation`. |
| `ru/05-devices.md` | Аттестация устройства с классом, ролями и действиями §2.6; журнал реестра; накопительные снимки, граница S+A и max(S+A, from); завершение отзыва D29/Q7 и онлайн-проверка критических действий. |
| `ru/06-registry.md` (новый) | Реестр владельца на узле доверия (D32), ключ реестра и его три вида записей, журнал и контрольные точки (D34), свидетель отката и домен отказа, свежесть `freshness/1` раз в 20 секунд и граница гарантии. Главы 06-10 переименованы в 07-11. |
| `ru/07-failures.md` (был 06) | Таблица условий с точными кодами §6; экстренная остановка не зависит от реестра (§7). |
| `ru/08-envelope.md` (был 07) | Конверт S0 `{version, body, id, signatures}` вместо прежней плоской схемы с `signer`, `key_id`, `ts`; поля `message/1`; новый учебный JSON с вычисленными `id` и `body_sha256`; построение `id` и подписи; метки 1-96 байт, ключи и подписи, пределы. Прежние открытые вопросы о кодировке подписи и выводе `key_id` закрыты спецификацией. |
| `ru/09-federation.md` (был 08) | Новый раздел о доверии к другому владельцу; окно `iat`/`exp` 120 секунд вместо `ts`; журналы идентификаторов и `action_id`. |
| `ru/10-assurance.md` (был 09) | Таблица A0-A3 по §5; закрытый `grant/1`, `min_assurance`, цепочка до 4 звеньев, словарь действий, запрет агентским ключам выдавать гранты, сервис грантов под родительским грантом. |
| `ru/11-decisions.md` (был 10) | Устройство ядра и приложений; раздел "Открытые вопросы" с таблицей "Часть / Что осталось / Статус", включая строку о квитанции свежести. Состояния перенесены сюда из абзацев. |
| `src/*.puml`, `diagrams/*.svg`, `src/figures.json` | Обновлены trust-chain (роли корней), phone-command, device-lifecycle, agent-message, federated-command, failure-cases (убрано тире); element-message без изменений. Хэши пересчитаны. |
| `README.md`, `UNRESOLVED_QUESTIONS.md` | Таблица оснований с ревизиями; путь библиотек Homebrew; предел страниц; строка о `check.sh`; открытые решения по S0-S4. |
| `scripts/check.sh` | Чёрный список прозы блокирует и `editorial/notes/signing-auth/ru/*.md`; остальные записки остаются рекомендательными. |
| `scripts/check-self-test.py` | `test_signing_note_blacklist`: пять подложенных нарушений проваливают проверку с меткой книги, при `STRICT_PROSE=0` становятся отчётом; чистая записка проходит; нарушения в другой записке, в `README.md` и в `en/` блокирующими не считаются. |
| `signing-auth.ru.pdf` | Пересобран: 14 страниц. |

Сверка литералов: каждый литерал в обратных кавычках из `ru/*.md` найден в корпусе источников, кроме учебного
текста `Отчёт готов, проверки пройдены.`, вымышленных `alpha.example` и `beta.example` и нотационных записей
`{body, key, role, version}`, `{kind, id, from}`, `{role, key, sig}`, `r || s`, `id = sha256(метка || 0x0a || CCJ-1(body))`,
которые пересказывают §2.2 и §2.6 с пробелами.

## Сборка и визуальная проверка

Сборка: platform-book `1c75fdf4a09960e41ea153645da7c48800b7a82b`, Python 3.12.15 venv с `requirements-lock.txt`,
Pandoc 3.11, PlantUML 1.2026.6, `PLATFORM_BOOK_LIBRARY_PATH=/opt/homebrew/lib`. Первая сборка дала 23 страницы,
потому что каждая глава начинается с новой страницы; главы сокращены до одной страницы каждая.
Все 14 страниц просмотрены при 1400 px; после последней правки страницы 1-13 пиксельно совпадают с просмотренными,
страница 14 просмотрена заново. Перенос в JSON на странице 11 исправлен.

## Вывод проверок (дословно)

```text
$ platform-book ready
toolchain and bundled fonts: ready
exit=0
$ platform-book figures
figures: ok
exit=0
$ platform-book check-pdf --expected-pages 14
{"pages": 14, "embedded_fonts": ["diqsfwstixtwotextbold", "gnqughptserif", "hbengdptsans", "hhanfltimesnewromanbold", "hhhhivarial", "nafeloptsansbold", "qnktfnptmonobold", "rlrwzbptmono", "vfnjslptserifbold", "zcesiwhelvetica", "zewkqustixtwotext"]}
exit=0
$ platform-book check-pdf --expected-pages 13 (control)
platform-book: PDF page count mismatch
exit=2
$ pdfinfo
Pages:           14
Page size:       595.276 x 841.89 pts (A4)
$ pdffonts (name, emb)
NAFELO+PT-Sans-Bold yes
GNQUGH+PT-Serif yes
HBENGD+PT-Sans yes
VFNJSL+PT-Serif-Bold yes
ZEWKQU+STIX-Two-Text yes
RLRWZB+PT-Mono yes
ZCESIW+Helvetica yes
HHHHIV+Arial yes
QNKTFN+PT-Mono-Bold yes
HHANFL+Times-New-Roman,-Bold yes
DIQSFW+STIX-Two-Text-Bold yes
$ pdftotext | head -5
S WA R M A
Подписи и аутентификация
в Swarma
От А до Я: путь команды, ключи и границы доверия
25 октября 2026 года
$ sh scripts/check.sh
check.sh: ok (38 files)
exit=0
$ python3 scripts/check-self-test.py
Ran 8 tests in 9.054s

OK
exit=0
$ check-self-test.py --checker <origin/main check.sh> (control)
FAIL: test_signing_note_blacklist (__main__.HygieneTests.test_signing_note_blacklist) (text='Ключник — служба.')
FAIL: test_signing_note_blacklist (__main__.HygieneTests.test_signing_note_blacklist) (text='Поле «aud».')
FAIL: test_signing_note_blacklist (__main__.HygieneTests.test_signing_note_blacklist) (text='Это не очередь, а журнал.')
FAIL: test_signing_note_blacklist (__main__.HygieneTests.test_signing_note_blacklist) (text='Стоит отметить, что ключ один.')
FAIL: test_signing_note_blacklist (__main__.HygieneTests.test_signing_note_blacklist) (text='Мощная проверка.')
Ran 8 tests in 7.837s
FAILED (failures=5)
$ shasum -a 256
41fcd426cc9f18489398332c0798f426ab54602b13b27da1ad08f4d72326ab4a  editorial/notes/signing-auth/signing-auth.ru.pdf
```
