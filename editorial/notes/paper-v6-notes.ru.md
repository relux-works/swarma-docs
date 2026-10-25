# Пейпер 6.0: записка автора

Задача TASK-261025-ds4mge, ветка `paper/v6-261025` от origin/main cedd7bb (книга 1.4). Коммит текста пейпера: bc473f2. Файлы: `paper/paper.tex`, `paper/references.bib`, `paper/Makefile` (цель `paper.pdf` теперь зависит и от `references.bib`; BibTeX запускает tectonic).

## Итог

| Показатель | Значение |
| --- | --- |
| Страниц A4 вместе с литературой | 12 (`pdfinfo`: Pages 12, A4) |
| Слов в теле документа (`wc -w` от `\begin{document}` до конца, с разметкой) | 6099 |
| Источников в списке литературы | 42, все процитированы в тексте |
| Таблиц / рисунков | 3 / 1 |
| Сборка `make -B -C paper` | exit 0, без overfull и undefined (вывод ниже) |
| `make -C paper model` | 1090 состояний без нарушения, четыре контрпримера (вывод ниже) |
| `sh scripts/check.sh` | `check.sh: ok (38 files)`, exit 0 |

Шрифт 10pt вместо 11pt, поля 22 мм: при 11pt тот же текст занимал 13 страниц. Все 12 страниц PDF просмотрены глазами (рендер `pdftoppm` 60-80 dpi). Найдено и исправлено: наложение подписей на схеме рис. 1 (перерисована на явных координатах), строки шире поля в 4.1 и в двух таблицах, слишком узкая таблица 2.

Проза проверена правилами `style.ru.md` вручную, потому что `check.sh` гоняет чёрный список только по главам книги: тот же набор регулярных выражений (тире, ёлочки, антитезы, пустые зачины, рекламные прилагательные) по `paper/paper.tex` даёт ноль срабатываний, кроме слова "надёжно" в "инъекцию надёжно не распознаёт" (оговорка о пределе, не реклама). В тексте нет кодовых имён, машин, путей, задач и решений: `grep -iE "waggle|seraph|agents1|ivmbp|rise|CIP-|D-0[0-9]|TASK-|/home/|/Users/|keymaker"` по `paper.tex` и `references.bib` пуст.

## Карта разделов: 5.2 и 6.0

| 5.2 | 6.0 | Что сделано |
| --- | --- | --- |
| Аннотация | Аннотация | Один абзац: проблема, подход, что проверено, главный результат и чего нет. |
| 1. Введение | 1. Введение | Добавлен нумерованный список вклада; фраза о старшинстве спецификаций сохранена. |
| 2. Модель: три слоя и участники | 2. Постановка задачи и модель системы | Принципалы, хосты и станции, носители, узел доверия, протокол (пороги L0-L2), рис. 1, формулировка задачи. |
| 3. Сквозные принципы | 4 и 5 | Принципы разошлись по механизмам раздела 4 и гарантиям раздела 5. |
| 4. Swarma Runtime | 4.1-4.6 | Переписано по книге 1.4: ключ сообщений и `attestation/1`, роли корней, реестр владельца на узле доверия, свидетель отката, свежесть, граница отзыва `max(S+A,F)`, уровни A0-A3, люди других владельцев, станции и контракт изоляции исполнения, самоквалификация, допуск к носителю, память как потребитель реестра. |
| 5. Swarma Protocol | 2 (абзац "Протокол"), 4.7, G8 | Оставлены кандидат `(M,I)`, выбор ревьювера после фиксации, адрес аттестации, исходы, привилегированный класс, аренда и fencing. |
| 6. Идентичность, аттестации и репутация | 4.1 (абзац о KERI), 3 "Вне рамок" | Ячейка и журнал ключевых событий оставлены; репутация вынесена за рамки работы. |
| 7. Swarma Chain | упоминания в 1, 4.1, G4, П6 | Майнинг, эмиссия, имена, блок убраны: вне предмета пейпера и бюджета страниц. |
| — | 3. Модель угроз | Новый раздел: противники П1-П6, допущения, вне рамок. |
| — | 5. Анализ безопасности | Новый раздел: G1-G9 и криптографический противник, у каждой гарантии допущения и предел. |
| 8. Что проверено | 6. Проверка | Таблица состояния реализации, таблица свидетельств "утверждение, метод, результат, чего не показывает", подразделы 6.1-6.5, раздел "Ограничения". Модель 1090 сохранена (6.3). |
| 9. Чего платформа не обещает | 3 "Вне рамок", пределы в G1-G9, 6.6 | Пределы стоят рядом с гарантиями. |
| 10. Смежные работы | 7. Смежные работы | Переписано по семи темам брифа, литература проверена (ниже). |
| 11. Заключение | 8. Заключение и дальнейшая работа | Дальнейшая работа следует ограничениям раздела 6. |

Убраны из 5.2 целиком: варианты донора A/B/C и удалённое рабочее место, маршрутизатор моделей, Swarma Keeper, Swarma Curator как модуль, механизмы цепочки. Они есть в книге и не входят в перечень брифа для раздела "Устройство".

## Числа и их источники

### Свидетельства раздела 6

| Число в пейпере | Где | Источник | Как проверено |
| --- | --- | --- | --- |
| 2632 случая, 2499 отрицательных, 133 положительных | аннотация, табл. 2, 6.1 | публичный репозиторий `relux-works/waggle`, main f76a400: `README.md` (строка 7: "Its 2632 vectors (2499 negative, 133 positive) have a Go generator and independent Python checker"), `vectors/swarm-envelope-2/README.md` ("Only 944 named cases are tracked. All 1688 T/B/Z/U cases remain in the generator ... complete 2632-case check") | Свой подсчёт: `0-negative` 811 JSON, `1-positive` 133 JSON, итого 944; `sweeps.tsv` 1688 строк, 1688 уникальных id; 944 + 1688 = 2632. Тест библиотеки повторён на f76a400 (`go test ./verifier -run '^TestConformance$' -count=1 -v`, Go 1.26.0 darwin/arm64 через `GOTOOLCHAIN=auto`): вывод ниже. Проверку на Python локально не запускали: модуля `cryptography` нет, и проверка по своему контракту дала бы PENDING. |
| 944 именованных, 1688 развёрток | 6.1 | то же | то же |
| 66 смысловых векторов, два независимых вычислителя | аннотация, табл. 2, 6.1 | публичный `relux-works/swarma-memory`, main 763e024: `README.md` строка 13 ("independent cross-evaluator agreement was established for the earlier 66-vector corpus"); `.scripts/packaging.patch` строка 35 (формулировка 0.2.7: "Two independent evaluators agree with the expected results on all 66 semantic vectors"); книга, главы 15 и 29 | Сверено чтением файлов на 763e024. |
| 77 смысловых векторов, черновик 0.3.0 | 6.1 | `swarma-memory` main 763e024, `README.md` строка 13 | Сверено чтением. |
| 8 векторов развёртывания не исполняются | табл. 2 | книга, глава 15; `swarma-memory` README | Сверено. |
| r1: применение, проверка, откат примитивов учёток | аннотация, табл. 2, 6.2 | публичный `relux-works/swarma-user-manager`, `docs/root-qualification-evidence.md`, добавлен коммитом fe4a0b7, есть на main a71d15a; r1 на сборке 4639d69 | Формулировки взяты из документа: "TestRootQualification passed its apply, verify and rollback modes"; область: "disposable account/group commands, root:S home protection, ACL/capability refusal, one child's unlinked handle, root pidfd stop/absence and bounded home/account/group rollback". |
| r2: 11 из 11 проверок при применении и при проверке | аннотация, табл. 2, 6.2 | тот же документ; набор на сборке a5e99c4 | "boot-mode qualification inside the unit with 11/11 checks", "Verify: 11/11 checks", "Admission was left unconfigured", "does not establish ... rollback of the installation". |
| 1090; 84, 82, 71, 490 | табл. 2, 6.3, G8 | `paper/model/integration-fragment-model.py` на этой ветке | `make -C paper model`, вывод ниже. |
| Медианы и размахи замеров, память, выделения, размеры входов | аннотация, табл. 2, табл. 3, 6.4 | неопубликованный отчёт о замерах (`../.tmp/paper-evidence/report.md`, разделы "Headline single-processor measurements" и "Exact received-byte sizes") | Перенесено из таблиц отчёта; медиана сверена с третьим значением из пяти в сыром выводе отчёта. Время в мс = ns/op / 10^6, округление до 0,01; память в 10^6 байт = B/op / 10^6. |
| AMD Ryzen 7 9700X, 8 логических CPU гостя KVM, ядро 7.0.0-38-generic, Go 1.26.10 linux/amd64, GOMAXPROCS=1, 5 повторов, нагрузка 1,73 и 1,95 | 6.4 | тот же отчёт, раздел "Revision and environment" и вывод `uptime` | Имя машины из строки `uname` в пейпер не перенесено. |
| Ревизия библиотеки 9b42338 | 6.4 | отчёт; 9b42338 есть в истории публичного main (предок f76a400, проверено `git merge-base --is-ancestor`) | Замеренный коммит 155c129 и бенчмарк-файл локальные и не опубликованы; публична только сама библиотека. |
| 140 задач, 318 записей, 104 вердикта (55/49), первые раунды 17/18, медиана 2, максимум 13, P0 0, P1 73, P2 49, второй разборщик 58/51/209 | табл. 2, 6.5 | неопубликованный отчёт `../.tmp/paper-evidence/review-stats-curator.md`, сформирован 2026-10-24T23:18:58Z | Перенесено из отчёта; метод и нижняя граница описаны в 6.5. |

### Что снято и почему

- **180 обычных и 50 состояний восстановления порядка блокировок активации.** Публичного документа с этими числами нет. Проверены `spec/activation-order.md` и `UNRESOLVED_QUESTIONS.md` в `swarma-user-manager` (main a71d15a), `spec/keymaker-pc2.md` в `swarma-keymaker` (main 219ca90) и `git grep` по всем коммитам обоих репозиториев на "180 ordinary", "50 recovery", "180 states", "ordinary states": совпадений нет. По указанию оркестратора строка убрана из таблицы свидетельств и из аннотации. Правило дизайна "граф ожиданий каждой службы не содержит циклов" (книга, глава "Пользователь ОС на агента и сеть агента") осталось в 4.4 как утверждение дизайна, без свидетельства.
- **68 состязательных случаев памяти.** Публичного источника нет. Замороженная копия `sources/architecture-review/memory/conformance/R7-SCORE.md` называет 68 числом случаев исторического смыслового корпуса 0.2.5 ("Historical semantic 0.2.5: 68 pass / 0 fail"), а не состязательными случаями, как пишут главы 15 и 29 книги. В пейпере осталось только 66. Расхождение книги с источником передано оркестратору; книгу эта задача не меняет.
- **"11 из 11 проверок с проверенным откатом".** Формулировка брифа сводит два разных запуска. Откат проверен в r1 для примитивов учёток; 11 из 11 относится к r2, где откат установки прямо не установлен. Пейпер называет их раздельно.
- **"Открытая доска" в статистике ревью.** В публичном дереве `relux-works/curator` на 0e1670b7 отслеживаются только 17 файлов `*review-r<N>.md`, так что 318 записей из публичного git не воспроизводятся: отчёт считал рабочее состояние доски. Слово "открытой" убрано, пейпер пишет "доска задач проекта Swarma Curator".

### Расхождение статуса, которое пейпер не повышает

Глава 29 книги ставит контрактам менеджера пользователей, запускателя и диспетчера статус "спецификация" с пояснением "кода нет", а в публичном `swarma-user-manager` есть бэкенд Linux и записаны квалификационные запуски r1/r2. Табл. 1 сохраняет статус книги "спецификация" и в столбце границы пишет "станции не допускаются; квалификационные запуски на одной машине", без слов о наличии или отсутствии кода. Главу 29 стоит сверить отдельно.

### Числа дизайна из книги 1.4

| Число | Где в пейпере | Глава книги |
| --- | --- | --- |
| Снимок не старше 60 с, запись свежести каждые 20 с, `max(S+A,F)`, A не больше 60 с | аннотация, 4.2, G3 | "Ключи и ключник", "Гранты и полномочия" |
| Аттестация ключа сообщений не длиннее 86 400 с | 4.1 | "Ключи и ключник" |
| Прообраз `swarma-msg/2` не длиннее 24 576 байт, путь `m/4'/...` | 4.1 | "Ключи и ключник" |
| Поколение 128 бит | 4.1 | "Пользователь ОС на агента и сеть агента" |
| Не больше четырёх конвертов, лист с глубиной 0, `grant_unconstructible`, `grant_root_unknown`, глубина родителя не меньше 1 | 4.2 | "Гранты и полномочия" |
| Снимок не больше 64 записей и 8192 байт | G3 | "Где мы и что дальше" |
| 10 минут по монотонным часам | 4.2 | "Гранты и полномочия" |
| 42 гарантии, четыре статуса, 300 с | 4.4, G7 | "Пользователь ОС на агента и сеть агента" |
| Пропуск 120 с, токен 86 400 с, HR1-HR9, допуск по времени 60 с | 4.5, G6 | "Допуск к носителю" |
| 52 пункта, 14 схем, 74 вектора, пакет 0.2.7 | 4.6 | "Память агентов" |
| Пороги L0-L2 | 2 | "Журнал, кворум и инварианты" |

## Литература

42 источника, все процитированы. Метаданные проверял отдельный агент по первичным записям (Crossref, RFC Editor, arXiv API, страницы USENIX, поисковый API OpenReview, NIST, GitHub, официальные страницы проектов); DBLP не отвечал автоматическим запросам. Итог: 39 подтверждены как есть, 3 исправлены, неподтверждённых нет. После проверки в `references.bib` изменены две вещи: у `matrix` из URL убран фрагмент `#cross-signing` (символ `#` ломает `\url` в `.bbl`), раздел назван в заглавии; у `kata` защищён регистр заглавия.

Слабые места: `autogen` цитируется как препринт arXiv (площадку COLM 2024 не удалось открыть на первичной странице); у `sybil` номер тома LNCS 2429 подтверждён только вторичными записями; у `kata` и `ucan` нет даты публикации, год взят по дате обращения или ревизии; у `pbft` и `eigentrust` нет диапазона страниц.

| key | final citation (one line) | verified how (exact URL(s) checked) | status |
| --- | --- | --- | --- |
| macaroons | A. Birgisson, J. G. Politz, Ú. Erlingsson, A. Taly, M. Vrable, M. Lentczner. Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud. NDSS 2014. doi:10.14722/ndss.2014.23212 | https://api.crossref.org/works/10.14722/ndss.2014.23212 | VERIFIED |
| biscuit | Eclipse Biscuit project. Biscuit, a bearer token with offline attenuation and decentralized verification. Specification v3.3, 2024. | https://raw.githubusercontent.com/eclipse-biscuit/biscuit/v3.3/SPECIFICATIONS.md ; https://raw.githubusercontent.com/eclipse-biscuit/biscuit/main/SPECIFICATIONS.md ; GitHub API repos/eclipse-biscuit/biscuit/releases (v3.3 published 2024-12-17) ; https://www.biscuitsec.org/ | VERIFIED. The title is the H1 of SPECIFICATIONS.md, and the year is the v3.3 release. No personal authors are listed, so the author is the project. The main branch file was last changed 2025-10-21; the entry pins the v3.3 tag. |
| spki | C. M. Ellison, B. Frantz, B. Lampson, R. Rivest, B. Thomas, T. Ylonen. SPKI Certificate Theory. RFC 2693, Sept. 1999. | https://www.rfc-editor.org/rfc/rfc2693.json ; https://www.rfc-editor.org/rfc/rfc2693.txt (Authors' Addresses) | VERIFIED |
| ucan | I. Gozalishvili, D. Holmgren, P. Krüger, B. Zelenka. User Controlled Authorization Network (UCAN) Specification, Version 1.0.0. github.com/ucan-wg/spec, 2026. | https://raw.githubusercontent.com/ucan-wg/spec/main/README.md ; GitHub API (last commit to README 2026-10-22; latest tag v1.0-rc.1) | VERIFIED. The title, version and authors come from the README (Brooklyn Zelenka is also listed as editor). There is no release date: year 2026 is the date of the fetched revision, and no git tag named 1.0.0 exists. |
| dennis1966 | J. B. Dennis, E. C. Van Horn. Programming Semantics for Multiprogrammed Computations. CACM 9(3):143–155, March 1966. doi:10.1145/365230.365252 | https://api.crossref.org/works/10.1145/365230.365252 | VERIFIED. Crossref also lists a 1983 CACM reprint, 26(1):29–35; the 1966 original is the one cited. |
| miller2006 | M. S. Miller. Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control. PhD thesis, Johns Hopkins University, May 2006. | http://www.erights.org/talks/thesis/ | VERIFIED |
| ct | B. Laurie, A. Langley, E. Kasper. Certificate Transparency. RFC 6962, June 2013. | https://www.rfc-editor.org/rfc/rfc6962.json ; https://www.rfc-editor.org/rfc/rfc6962.txt | VERIFIED |
| ct2 | B. Laurie, E. Messeri, R. Stradling. Certificate Transparency Version 2.0. RFC 9162, Dec. 2021. | https://www.rfc-editor.org/rfc/rfc9162.json ; https://www.rfc-editor.org/rfc/rfc9162.txt | VERIFIED (authors filled in) |
| coniks | M. S. Melara, A. Blankstein, J. Bonneau, E. W. Felten, M. J. Freedman. CONIKS: Bringing Key Transparency to End Users. 24th USENIX Security Symposium, 2015, pp. 383–398. | https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/melara | VERIFIED |
| keri | S. M. Smith. Key Event Receipt Infrastructure (KERI). arXiv:1907.02143, 2019. | https://export.arxiv.org/api/query?id_list=1907.02143 (first submitted 2019-07-03) | VERIFIED |
| mls | R. Barnes, B. Beurdouche, R. Robert, J. Millican, E. Omara, K. Cohn-Gordon. The Messaging Layer Security (MLS) Protocol. RFC 9420, July 2023. | https://www.rfc-editor.org/rfc/rfc9420.json ; https://www.rfc-editor.org/rfc/rfc9420.txt | VERIFIED |
| matrix | The Matrix.org Foundation. Matrix Specification v1.19, Client-Server API, Cross-signing. https://spec.matrix.org/v1.19/client-server-api/#cross-signing (v1.19 released 2026-07-08). | https://spec.matrix.org/latest/ (shows "version v1.19") ; https://spec.matrix.org/v1.19/client-server-api/ (has `<h5 id="cross-signing">`) ; https://spec.matrix.org/v1.19/changelog/v1.19/ (release date July 8, 2026) | VERIFIED. The current version is v1.19. |
| gvisor | E. G. Young, P. Zhu, T. Caraza-Harter, A. C. Arpaci-Dusseau, R. H. Arpaci-Dusseau. The True Cost of Containing: A gVisor Case Study. HotCloud 2019. | https://www.usenix.org/conference/hotcloud19/presentation/young | VERIFIED |
| firecracker | A. Agache, M. Brooker, A. Florescu, A. Iordache, A. Liguori, R. Neugebauer, P. Piwonka, D.-M. Popa. Firecracker: Lightweight Virtualization for Serverless Applications. NSDI 2020, pp. 419–434. | https://www.usenix.org/conference/nsdi20/presentation/agache ; https://www.usenix.org/system/files/nsdi20-paper-agache.pdf (title page) | VERIFIED. The USENIX page meta tags omit Andreea Florescu, but the paper's title page and the page's own byline list all 8 authors. |
| kata | Kata Containers project. Kata Containers: An OpenInfra Foundation Project. https://katacontainers.io/ (accessed 2026-10-25). | https://katacontainers.io/ | VERIFIED as a web citation. The page carries no publication date, so year 2026 is the access year. The page states that the community is stewarded by the Open Infrastructure Foundation. |
| react | S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, Y. Cao. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023. | https://iclr.cc/virtual/2023/poster/11003 ; https://export.arxiv.org/api/query?id_list=2210.03629 | VERIFIED |
| autogen | Q. Wu, G. Bansal, J. Zhang, et al. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. arXiv:2308.08155, 2023. | https://export.arxiv.org/api/query?id_list=2308.08155 ; OpenReview search API (record BAakY1hNKS, venue "COLM") ; web search hits for Microsoft Research publication pages listing "COLM 2024" | CORRECTED: cited as the arXiv preprint only. COLM 2024 is indicated by the OpenReview index and Microsoft Research listings, but the primary COLM/OpenReview page could not be fetched (browser challenge). The OpenReview index also gives the COLM title as "...via Multi-Agent Conversations", which differs from arXiv. Add the COLM venue only after a manual check. |
| metagpt | S. Hong, M. Zhuge, J. Chen, et al. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework. ICLR 2024. | OpenReview search API (records J92dSse52q, VtmBAGCN7o: venue "ICLR 2024" / "ICLR 2024 oral", 15 authors) ; https://export.arxiv.org/api/query?id_list=2308.00352 | VERIFIED. The third author is "Jonathan Chen" in the ICLR record and "Jiaqi Chen" on arXiv; the entry follows the ICLR record. |
| chatdev | C. Qian, W. Liu, H. Liu, et al. ChatDev: Communicative Agents for Software Development. ACL 2024 (Vol. 1: Long Papers), pp. 15174–15186. doi:10.18653/v1/2024.acl-long.810 | https://api.crossref.org/works/10.18653/v1/2024.acl-long.810 | VERIFIED |
| sweagent | J. Yang, C. E. Jimenez, A. Wettig, et al. SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. NeurIPS 2024. | OpenReview search API (records 30hggYAY0Z "NeurIPS 2024", mXpq6ut8J3 "NeurIPS 2024 poster") ; https://export.arxiv.org/api/query?id_list=2405.15793 | VERIFIED |
| swebench | C. E. Jimenez, J. Yang, A. Wettig, et al. SWE-bench: Can Language Models Resolve Real-World GitHub Issues? ICLR 2024. | OpenReview search API (VTF8yNQM66 "ICLR 2024 oral") ; https://export.arxiv.org/api/query?id_list=2310.06770 (comment cites ICLR 2024, openreview id VTF8yNQM66) | VERIFIED. The title capitalization follows arXiv; OpenReview has "Real-world Github". |
| greshake | K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, M. Fritz. Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. AISec 2023 (16th ACM Workshop on AI and Security, with CCS '23), pp. 79–90. doi:10.1145/3605764.3623985 | https://api.crossref.org/works?query.bibliographic=Greshake... (DOI record 10.1145/3605764.3623985) | VERIFIED |
| agentdojo | E. Debenedetti, J. Zhang, M. Balunović, L. Beurer-Kellner, M. Fischer, F. Tramèr. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. NeurIPS 2024 Datasets and Benchmarks Track. | OpenReview search API (m1YYAQjO3w "NeurIPS 2024 Track Datasets and Benchmarks Poster") ; https://export.arxiv.org/api/query?id_list=2406.13352 | VERIFIED |
| codereviewer | Z. Li, S. Lu, D. Guo, et al. (11 authors). Automating Code Review Activities by Large-Scale Pre-training. ESEC/FSE 2022, pp. 1035–1047. doi:10.1145/3540250.3549081 | https://api.crossref.org/works/10.1145/3540250.3549081 | VERIFIED |
| tufano2021 | R. Tufano, L. Pascarella, M. Tufano, D. Poshyvanyk, G. Bavota. Towards Automating Code Review Activities. ICSE 2021, pp. 163–174. doi:10.1109/ICSE43902.2021.00027 | Crossref record 10.1109/icse43902.2021.00027 (via https://api.crossref.org/works?query.bibliographic=...) | VERIFIED |
| frommgen2024 | A. Froemmgen, J. Austin, P. Choy, et al. (16 authors). Resolving Code Review Comments with Machine Learning. ICSE-SEIP 2024, pp. 204–215. doi:10.1145/3639477.3639746 | https://api.crossref.org/works/10.1145/3639477.3639746 | CORRECTED: the publisher metadata spells the first author's surname "Froemmgen", not "Frömmgen"; the entry follows the publisher. |
| llmjudge | L. Zheng, W.-L. Chiang, Y. Sheng, et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023 Datasets and Benchmarks Track. | OpenReview search API (uccHPGDlao "NeurIPS 2023 Datasets and Benchmarks Poster") ; https://export.arxiv.org/api/query?id_list=2306.05685 | VERIFIED |
| selfpref | A. Panickssery, S. R. Bowman, S. Feng. LLM Evaluators Recognize and Favor Their Own Generations. NeurIPS 2024. | OpenReview search API (4NJBV6Wp0h "NeurIPS 2024 oral") ; https://export.arxiv.org/api/query?id_list=2404.13076 | VERIFIED |
| pbft | M. Castro, B. Liskov. Practical Byzantine Fault Tolerance. OSDI 1999 (3rd Symposium on Operating Systems Design and Implementation). | https://www.usenix.org/conference/osdi-99/practical-byzantine-fault-tolerance | VERIFIED. No page numbers are given because the source does not list them. |
| hotstuff | M. Yin, D. Malkhi, M. K. Reiter, G. Golan Gueta, I. Abraham. HotStuff: BFT Consensus with Linearity and Responsiveness. PODC 2019, pp. 347–356. doi:10.1145/3293611.3331591 | https://api.crossref.org/works/10.1145/3293611.3331591 | CORRECTED: the publisher record gives the fourth author as "Guy Golan Gueta" (given "Guy Golan", family "Gueta"), not "Golan-Gueta". |
| fips205 | NIST. Stateless Hash-Based Digital Signature Standard. FIPS 205, August 13, 2024. doi:10.6028/NIST.FIPS.205 | https://csrc.nist.gov/pubs/fips/205/final | VERIFIED |
| eigentrust | S. D. Kamvar, M. T. Schlosser, H. Garcia-Molina. The EigenTrust Algorithm for Reputation Management in P2P Networks. WWW 2003. doi:10.1145/775152.775242 | https://api.crossref.org/works/10.1145/775152.775242 | VERIFIED. No page range is given because Crossref lists only the first page, 640. |
| sybil | J. R. Douceur. The Sybil Attack. IPTPS 2002, LNCS 2429, Springer, pp. 251–260. doi:10.1007/3-540-45748-8_24 | https://api.crossref.org/works/10.1007/3-540-45748-8_24 ; https://api.crossref.org/works/10.1007/3-540-45748-8 (book, editors) ; web search (Microsoft Research / Springer-derived records) for the volume number | VERIFIED. The title, pages, DOI, book and editors come from Crossref. The LNCS volume 2429 is confirmed only by secondary listings, because the Springer page redirected to a login. |
| sybilproof | A. Cheng, E. Friedman. Sybilproof Reputation Mechanisms. P2PECON '05 (ACM SIGCOMM Workshop on Economics of Peer-to-Peer Systems), 2005. doi:10.1145/1080192.1080202 | https://api.crossref.org/works/10.1145/1080192.1080202 | VERIFIED |
| tla | L. Lamport. Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers. Addison-Wesley, 2002. | https://lamport.azurewebsites.net/tla/book.html (copyright 2002 Pearson Education / Addison-Wesley) | VERIFIED |
| slip10 | J. Hoenicke, P. Rusnak. SLIP-0010: Universal private key derivation from master private key. SatoshiLabs, 2016. | https://raw.githubusercontent.com/satoshilabs/slips/master/slip-0010.md (Created 2016-04-26, Status Final) | VERIFIED (authors and year filled in) |
| bip32 | P. Wuille. BIP 32: Hierarchical Deterministic Wallets. 2012. | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0032.mediawiki (Assigned 2012-02-11) | VERIFIED |
| chubby | M. Burrows. The Chubby Lock Service for Loosely-Coupled Distributed Systems. OSDI 2006. | https://www.usenix.org/conference/osdi-06/chubby-lock-service-loosely-coupled-distributed-systems | VERIFIED |
| kleppmann-fencing | M. Kleppmann. How to do distributed locking. Blog post, 8 February 2016. | https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html ("Published by Martin Kleppmann on 08 Feb 2016") | VERIFIED |
| compiler | N. Carlini. Building a C compiler with a team of parallel Claudes. Anthropic Engineering blog, 5 February 2026. | https://www.anthropic.com/engineering/building-c-compiler (H1 title, "Written by Nicholas Carlini", "Published Feb 5, 2026") | VERIFIED. The og:title is the shorter "Building a C compiler with parallel Claudes"; the entry uses the H1. |
| prove2me | S. Chen, K. Marwaha, X. Lu, H. Yuen, T. Peng. Prove2Me: An Open Collaborative Platform for Scaling Math Formalization. arXiv:2608.28433, 2026. | https://arxiv.org/abs/2608.28433 (citation_date 2026/08/28) | VERIFIED (all five authors listed) |
| sigstore | Z. Newman, J. S. Meyers, S. Torres-Arias. Sigstore: Software Signing for Everybody. ACM CCS 2022, pp. 2353–2367. doi:10.1145/3548606.3560596 | https://api.crossref.org/works/10.1145/3548606.3560596 | VERIFIED |

## Дословный вывод

### `make -B -C paper`

```text
tectonic -X compile paper.tex
note: "version 2" Tectonic command-line interface activated
note: Running TeX ...
warning: accessing absolute path `/System/Library/Fonts/Supplemental/PTSerif.ttc`; build may not be reproducible in other environments
warning: accessing absolute path `/System/Library/Fonts/Supplemental/PTSans.ttc`; build may not be reproducible in other environments
warning: accessing absolute path `/System/Library/Fonts/Supplemental/PTMono.ttc`; build may not be reproducible in other environments
warning: paper.tex:156: Underfull \hbox (badness 7796) in paragraph at lines 155--156
warning: paper.tex:156: Underfull \hbox (badness 2932) in paragraph at lines 155--156
warning: paper.tex:156: Underfull \hbox (badness 1237) in paragraph at lines 155--156
warning: paper.tex:160: Underfull \hbox (badness 1253) in paragraph at lines 159--160
warning: paper.tex:184: Underfull \hbox (badness 3098) in paragraph at lines 183--184
warning: paper.tex:184: Underfull \hbox (badness 4303) in paragraph at lines 183--184
warning: paper.tex:184: Underfull \hbox (badness 2393) in paragraph at lines 183--184
warning: paper.tex:320: Underfull \hbox (badness 1571) in paragraph at lines 319--320
note: Running BibTeX on paper.aux ...
note: Rerunning TeX because bibtex was run ...
warning: paper.tex:156: Underfull \hbox (badness 7796) in paragraph at lines 155--156
warning: paper.tex:156: Underfull \hbox (badness 2932) in paragraph at lines 155--156
warning: paper.tex:156: Underfull \hbox (badness 1237) in paragraph at lines 155--156
warning: paper.tex:160: Underfull \hbox (badness 1253) in paragraph at lines 159--160
warning: paper.tex:184: Underfull \hbox (badness 3098) in paragraph at lines 183--184
warning: paper.tex:184: Underfull \hbox (badness 4303) in paragraph at lines 183--184
warning: paper.tex:184: Underfull \hbox (badness 2393) in paragraph at lines 183--184
warning: paper.tex:320: Underfull \hbox (badness 1571) in paragraph at lines 319--320
warning: paper.bbl:35: Underfull \hbox (badness 1168) in paragraph at lines 30--35
warning: paper.bbl:153: Underfull \hbox (badness 10000) in paragraph at lines 147--153
warning: paper.bbl:247: Underfull \hbox (badness 1348) in paragraph at lines 242--247
note: Rerunning TeX because "paper.aux" changed ...
warning: paper.tex:156: Underfull \hbox (badness 7796) in paragraph at lines 155--156
warning: paper.tex:156: Underfull \hbox (badness 2932) in paragraph at lines 155--156
warning: paper.tex:156: Underfull \hbox (badness 1237) in paragraph at lines 155--156
warning: paper.tex:160: Underfull \hbox (badness 1253) in paragraph at lines 159--160
warning: paper.tex:184: Underfull \hbox (badness 3098) in paragraph at lines 183--184
warning: paper.tex:184: Underfull \hbox (badness 4303) in paragraph at lines 183--184
warning: paper.tex:184: Underfull \hbox (badness 2393) in paragraph at lines 183--184
warning: paper.tex:320: Underfull \hbox (badness 1571) in paragraph at lines 319--320
warning: paper.bbl:35: Underfull \hbox (badness 1168) in paragraph at lines 30--35
warning: paper.bbl:153: Underfull \hbox (badness 10000) in paragraph at lines 147--153
warning: paper.bbl:247: Underfull \hbox (badness 1348) in paragraph at lines 242--247
warning: warnings were issued by the TeX engine; use --print and/or --keep-logs for details.
note: Running xdvipdfmx ...
note: Writing `paper.pdf` (163.33203125 KiB)
note: Skipped writing 3 intermediate files (use --keep-intermediates to keep them)
```

### `make -C paper model`

```text
python3 -I model/integration-fragment-model.py
full rules: reachable states=1090, violation=None
without cas     : states explored=84, violation=record applied twice
   trace: submit(A) -> build_candidate(A) -> attest(A) -> propose(A) -> deliver(A) -> deliver(A)
without epoch   : states explored=82, violation=record from a stale lease epoch advanced main
   trace: submit(A) -> build_candidate(A) -> attest(A) -> propose(A) -> epoch_change -> deliver(A)
without contract: states explored=71, violation=attestation references a superseded contract version
   trace: submit(A) -> build_candidate(A) -> attest(A) -> change_contract(A) -> propose(A) -> deliver(A)
without bind_I  : states explored=490, violation=attestation made on a different base than the integrated candidate
   trace: submit(A) -> build_candidate(A) -> attest(A) -> propose(A) -> submit(B) -> build_candidate(B) -> attest(B) -> deliver(A) -> build_candidate(B) -> propose(B) -> deliver(B)
```

### Тест соответствия библиотеки на f76a400 (`go test ./verifier -run '^TestConformance$' -count=1 -v`)

Число подтестов `--- PASS: TestConformance/`, число `--- FAIL`, последние две строки:

```text
2632
0
PASS
ok  	github.com/relux-works/waggle/verifier	11.445s
```

### `sh scripts/check.sh`

```text
check.sh: ok (38 files)
```

Выше этой строки `check.sh` печатает только отчётные (advisory) срабатывания в `editorial/notes/signing-auth/ru/`, чужих файлах, которые эта задача не трогает; код выхода 0.
