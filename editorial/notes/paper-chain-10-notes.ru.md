# Работа "Swarma Chain", версия 1.0: заметки автора

Ветка `paper/chain-10-261025` от origin/main 02f82dd. Файлы: `paper/chain/chain.tex`, `paper/chain/references.bib`, `paper/chain/Makefile` (`make -C paper/chain` собирает `paper/chain/chain.pdf` через tectonic), минимальное расширение `scripts/check.sh` и тест к нему в `scripts/check-self-test.py`, строка `paper/chain/chain.pdf` в `.gitignore`. `paper/paper.tex`, `paper/Makefile` и `paper/platform/` не тронуты.

Решение владельца (Иван, 2026-10-25): у Swarma три работы; эта описывает Swarma Chain целиком по последним итерациям дизайна. Голос финальной платформы, статусов поставки в тексте нет. Где точка дизайна остаётся открытой, текст называет пространство дизайна и выбранное направление нейтрально.

## Источники и ревизии

Старшинство: новее решения выигрывают. Ревизии ниже взяты как последний коммит файла на origin/main 02f82dd.

| Источник | Ревизия | Что взято |
| --- | --- | --- |
| `editorial/decisions.ru.md`, разделы "Решения по Swarm Chain" (17 и 18 октября), "Рантайм и цепочка", правки текста по ревью | fd35d89 (2026-10-25) | решения 27-34, 35-40, 41-48, 49-52, социальный слой в генезисе, 53-56 |
| `editorial/chain-post-ai.ru.md` | e98c1b8 (2026-10-18) | хэш-профиль, отказ от 256s, WOTS/XMSS/LMS и 384-битных хэшей, ячейка, штраф поздней ветки с таблицей, слабая субъективность, рой как майнеры, билеты, остаточный риск, резерв, размер блока, следствия 49-51 |
| `editorial/decisions-pending.ru.md` | 078e155 (2026-10-18) | формулировки пунктов 27-40, принятых по рекомендациям |
| `editorial/identity-reputation.ru.md` | 5b34191 (2026-10-17) | исходное направление "ключ есть личность", "чего не обещает" (уточнено решениями 27-34 и 42) |
| `editorial/names.ru.md` | 8241377 (2026-10-17) | термины; имя слоя взято как в книге 1.4.1 и в брифе: Swarma Chain (карта имён пишет Swarm Chain) |
| `editorial/style.ru.md` | a9ada4d (2026-10-25) | голос, чёрный список, термины |
| `book/ru/26-cepochka.md` | ba9fc37 | подслои, граница консенсуса, профиль, корни вне консенсуса и план миграции, блок и сегмент, размер блока, сложность и ASERT, метки времени, RandomX, штраф, рой и билеты, имена, эмиссия, сервисные узлы, фильтры и индексатор |
| `book/ru/24-identichnost.md` | fd35d89 | ячейка, пути траты, идентификатор, журнал до цепочки, предел реестра одного владельца, владелец и восстановление, доказательство идентичности, отзыв и записи, вывод учётки против отзыва |
| `book/ru/25-attestacii-i-reputaciya.md` | 859a796 | состав аттестации, пачки и цена, четыре шага проверки, обязательства, формула репутации, споры, деньги и репутация, допуск |
| `book/ru/27-socialnyj-sloj.md` | ba9fc37 | спам и минимальная плата, потоки оплаты, спонсор, отвергнутые модели |
| `book/ru/05-klyuchi.md` | eb5583a | деривация ключей ячейки SHAKE256 от пути и номера ротации, SLIP-0010 для каналов, смена и компрометация мастер-секрета |
| `book/ru/15-pamyat.md` | eb5583a | ячейки как издатель, субъект, отправитель; грант в реестре; недоступный реестр не грант |
| `book/ru/17-model-protokola.md`, `18-zhurnal.md`, `19-kontrakt.md` | 948e2d0, e1d58ca, e1d58ca | личность ноды, ключи нод, корни пачек аттестаций исхода в цепочке |
| `book/ru/20-orkestrator-i-cikl.md` | 948e2d0 | выбор ревьювера: заморозка множества, луковица хэшей кор-нод и хэш блока |
| `book/ru/22-effekty-ostanovka-federaciya.md` | fd35d89 | PoW-билет на публичной точке, очередь, нет ключа подписи допуска; подписант манифеста |
| `book/ru/23-ugrozy.md` | 859a796 | криптографический противник, Sybil |
| `book/ru/29-gde-my.md` | eb5583a | список открытых вопросов цепочки (только для раздела "открытые точки" ниже, в текст статусы не переносились) |
| `book/ru/30-slovar.md` | 859a796 | определения терминов |
| работа 5.2, раздел цепочки: `git show b85e8c7:paper/paper.tex` | b85e8c7 (2026-10-18) | структура разделов "Идентичность" и "Swarma Chain", набор ссылок |
| работа 6.0.1: `paper/paper.tex`, `paper/references.bib` | 02f82dd, 2c1a17d | преамбула и стиль вёрстки; проверенные записи литературы (см. ниже) |
| `~/Developer/ReluxWorks/swarm-platform-architecture` (только чтение) | 567b077 | поиск по `randomx`, `slopcore`, `ASERT`, `Swarm Chain` пуст: материала о цепочке там нет, ничего не взято |

## Карта разделов

| Раздел работы | Источники | Решения |
| --- | --- | --- |
| Аннотация | всё ниже; число 87 % из табл. 6 (расчёт) | 41, 42, 43, 44, 49 |
| 1. Введение | гл. 24 "С чем агент приходит", гл. 02, работа 6.0.1 (рантайм, протокол), записка о хэш-профиле (повод) | 53, 54 |
| 2. Модель системы и угроз | гл. 26 (нотариус, остаточный риск), гл. 24, 25, 23; допущения и противники собраны автором из механизмов этих глав | 44, 47, 55 |
| 3. Подслои и граница консенсуса | гл. 26 "Три подслоя", "Где заканчивается консенсус", "Блок и сегмент данных" | 42, 49, социальный слой в генезисе (18 октября) |
| 4. Криптографический профиль | записка, раздел 2 и 4; гл. 26 "Криптографический профиль", "Корни доверия вне консенсуса"; гл. 05 | 41, 46, 55 |
| 5. Личность как ячейка | гл. 24 целиком; гл. 05 о смене мастер-секрета | 27, 42, 49, 54, пункт 6 листа 1-26 (смена мастер-секрета) |
| 6. Имена | гл. 26 "Имена", гл. 27 "За что платят" | 39, 45 |
| 7. Аттестации и репутация | гл. 25 целиком; записка, раздел 1 | 28-34, 43 |
| 8. Ценность | гл. 26 "Размер блока", "Эмиссия", "Сервисные узлы"; гл. 27 | 36, 37, 39, 52 |
| 9. Консенсус и майнинг | гл. 26 "Сложность", "Чистый майнинг", "Рой и есть майнеры"; гл. 22 | 35, 37, 47 |
| 10. Финальность | записка "Время нельзя арендовать"; гл. 26 | 44, 48, 50 |
| 11. Лёгкие клиенты и индексаторы | гл. 26 "Блок и сегмент", "Лёгкое чтение"; гл. 25 | 38, 40, 49, 51 |
| 12. Рантайм и протокол | гл. 05, 15, 17-20, 22, 24 | 53, 54, 55 |
| 13. Анализ безопасности | аргументы автора из механизмов разделов 3-12; пределы из гл. 24-27 и записки ("честный остаточный риск") | все выше |
| 14. Анализ параметров | расчёты автора по числам источников (см. ниже) | 37, 44, 52 |
| 15. Смежные работы | литература ниже | |
| 16. Заключение | гл. 29 "Нерешённые вопросы" (только как открытые точки дизайна) | 37, 34 |

## Что выведено расчётом, а не взято из источника

Все входные числа взяты из источников; производные посчитаны здесь и воспроизводятся.

- Формула штрафа $P(\Delta)=\min(32, 2^{(\Delta-10\,мин)/1\,ч})$ при $10\,мин<\Delta<24\,ч$: формализация правила "P = 1 первые 10 минут, дальше удвоение каждый час, потолок 32, после 24 часов реорганизаций нет". Она воспроизводит таблицу записки: $2^{50/60}=1{,}78$, $2^{170/60}=7{,}13$, потолок 32 при 5 ч 10 мин. Строка 2 ч ($3{,}56$, $78{,}1\,\%$) добавлена тем же расчётом. Доля $\alpha=P/(1+P)$: 64,1 %, 87,7 %, 97,0 %. Книга округляет 87,7 % до "> 88 %"; аннотация пишет "больше 87 %".
- Пропускная способность: $512\cdot1024/15712\approx33$ объекта на блок по цели, 66 на блок $2T_0$, около 16 при полном сегменте. Записка: "мегабайт тела вмещает около 60".
- Таблица пачки: $15712/N$ и $64\lceil\log_2N\rceil$.
- Цена записи: $f_{\min}=R/(16T)$; 1 КБ стоит $R/8192$, при $R=64$ это 0,0078; парная подпись $15712/(16\cdot524288)\approx R/534$, в тексте "около $R/530$", 0,12 при $R=64$. Размер записи 1 КБ выбран для примера и так и назван.
- Рост цели: $0{,}5\cdot2^y = 4\cdot2^{y/4}$ при $y=4$, 8 МБ; затем $2^{1/4}-1\approx19\,\%$ в год.
- Заголовки: $525600\cdot350$ байт $\approx184$ МБ в год (книга: "порядка 180 МБ").
- Эмиссия: $64\cdot525600\cdot3/\ln2\cdot(1-2^{-5})\approx141{,}0$ млн; доля за 3 года $0{,}5/0{,}96875=51{,}6\,\%$, за 10 лет $93{,}0\,\%$ (в тексте "больше 90 %", книга пишет "около 90 %"); хвост $2\cdot525600=1051200$ в год, $0{,}745\,\%$ от 141 млн; халвинги $50\cdot4\cdot525600\cdot1{,}875\approx197{,}1$ млн. Число 150 млн для быстрого спада взято из книги без пересчёта.
- ASERT: формула приведена в идеализированном виде по спецификации aserti3-2d; порядок величины $\tau\log_2 10\approx6{,}6$ ч согласуется с оценками книги (4 ч, 6,5 ч), сами оценки названы предварительными, как в книге.

## Решения, использованные по номерам

27 (вывод учётки и отзыв различаются; уточнено 42), 28 (открытые аттестации, обязательства для приватных), 29 (выдаёт любой рантайм с личностью), 30 (оси, затухание, формула с индексатором), 31 ("не установлено" нейтрально), 32 (споры без арбитража), 33 (канонический состав, цена = тариф), 34 (деньги и репутация не связаны), 35 (только собственный RandomX), 36 (фонд разработки 0), 37 (ASERT, блок 60 с, числа по моделированию), 38 (GraphQL с подписками), 39 (цена имён по длине и спросу, плата пополам), 40 (iOS тонкий режим), 41 (хэш-профиль), 42 (ячейка), 43 (пачки, доказательство у субъекта), 44 (штраф, 24 ч, checkpoint), 45 (commit-reveal, 24 ч), 46 (случайность без VRF и BLS), 47 (майнинг на хостах, билеты как шары, пул), 48 (резерв), 49 (корень состояния в заголовке), 50 (ChainLocks исключены), 51 (лёгкий клиент от checkpoint), 52 (размер блока), социальный слой в генезисе (18 октября), 53 (рантайм в расчёте на цепочку), 54 (самосертифицирующий идентификатор, журнал в реестре), 55 (корни на кривых и план миграции); из листа 1-26: пункт 6 (смена и компрометация мастер-секрета), пункт 8 (реестр: один писатель, git, снимки не старше 60 с).

Не использованы: юридический вопрос монеты (это не дизайн; в работе нет), 56 (план перехода: статус поставки), 57-61 (подпись и человеческий вход, к цепочке не относятся).

## Открытые точки дизайна и как текст их называет

| Точка | Где в работе | Формулировка |
| --- | --- | --- |
| Числа генезиса: цель и темпы размера блока, минимальная плата, полупериод ASERT, параметры штрафа, график эмиссии | табл. 3, разделы 8-10, 14, заключение | "Числа служат кандидатами"; "окончательные значения генезиса задаёт моделирование" |
| Константы формулы репутации | раздел 7, заключение | "Формула и её константы публикуются вместе с индексатором, и конкретные значения затухания и начальных весов классов задаёт эта публикация" |
| Сервисные узлы: доля награды, залог, частота проверок, ответственность | раздел 8 | "Параметры этого механизма составляют открытое пространство дизайна" |
| Связь денег и репутации | раздел 7, заключение | "Связь между ними допустима только там, где понятны её цена и последствия, и это открытый вопрос дизайна" |
| Резерв: композиция PoW, отметка в Bitcoin, STARK | раздел 10 | "Три усиления ядро не включает, и дизайн держит их в резерве" |
| Точные форматы ячейки, записей, индексатора | разделы 3, 11 | "Точный формат записей задаёт спецификация цепочки"; "Точную схему задаёт спецификация индексатора" |

Чего в тексте нет намеренно: строк статуса, таблицы готовности, слов "работает сегодня", "спроектировано и не построено", "пока", "в первой версии" (версии первой реализации заменены формулировкой дизайна: "Дизайн не связывает деньги и репутацию", "Арбитра в цепочке нет").

## Термины, определённые при первом появлении

агент (1), владелец (1), рантайм / Swarma Runtime (1), ключник (1), Swarma Protocol (1), Swarma Chain (1), личность (1), ячейка личности (1, точно в 5), аттестация (1, точно в 7), выдавший (1), субъект (7), реестр владельца (1, 5), полный узел, лёгкий клиент, индексатор, майнер (табл. 1), нотариус как модель цепочки (3), p2p-память, социальный граф (3), тело блока, сегмент данных, корень состояния личностей и имён, типизированный конверт (3), обязательство (4), луковица хэшей (4), текущие и следующие ключи, предротация, трата, ротация, трата родителем, отзыв, терминальная ячейка (5), ячейка владельца, внешний ключ восстановления, мастер-секрет (5), журнал ключевых событий (5), доказательство идентичности, валидатор (5), имя (6), пачка (7), тариф записи (7), репутация, затравка (7), спор, возражение (7), сервисный узел (8), шар (9), PoW-билет допуска (9), полупериод ASERT (9), штраф поздней ветки (10), слабая субъективность, checkpoint (10), кор-нода (12).

## Литература

`paper/chain/references.bib`: 56 записей, все процитированы (сверка ключей `\cite` и `.bib` в обе стороны пуста). Двенадцать перенесены из `paper/references.bib` работы 6.0, где их метаданные проверены по первичным записям (таблица в `editorial/notes/paper-v6-notes.ru.md`): `fips205`, `eigentrust`, `sybil`, `sybilproof`, `keri`, `ct`, `ct2`, `coniks`, `sigstore`, `slip10`, `bip32`, `swarmabook` (версия поправлена на 1.4.1 по `dist/swarma-book-1.4.1.ru.pdf`). `swarmapaper` описывает нашу работу 6.0.1 по титулу `paper/paper.tex`. Ещё 44 записи проверил отдельный агент по первичным записям (Crossref, RFC Editor, arXiv API, NIST CSRC, IACR ePrint, страницы USENIX, репозитории EIP/BIP/ECIP/DIP, официальные страницы проектов); неподтверждённых нет. Запись `smt` проверена, но не процитирована и в `references.bib` не вошла, поэтому из 44 вошли 43. Вместе с `swarmapaper` это 56.

Что изменилось в тексте после проверки: ECIP-1100 (MESS) имеет статус Replaced, а ECIP-1110 (2023) отключил MESS. Текст говорит: MESS Ethereum Classic ввёл после атак 2020 года и позднее отключил (`mess`, `messoff`). Документ Horizen назван предложением (оригинальный адрес не отвечает, ссылка на копию в Wayback Machine). Формула ASERT в тексте помечена как идеализированная запись: спецификация aserti3-2d считает `time_delta` от родителя якорного блока и берёт `height_delta + 1`.

Протокол проверки агента (из `.temp/chain-refs/verification.md`, дословно):

Entries: 44 in `new.bib`. That covers 42 requested keys (including the late addition `joux`) plus two extra entries: `ethyellow` (the second Ethereum document that was requested) and `messoff` (the ECIP that deactivated MESS). Nothing is UNVERIFIED.

The test compile (tectonic, `abbrv`, `\nocite{*}`) rendered all 44 entries, and the `.blg` had 0 BibTeX warnings.

Crossref calls take the form `https://api.crossref.org/works/<DOI>` (full record) or `https://api.crossref.org/works?query.bibliographic=...` (lookup). Raw responses are in `raw/`.

How the LNCS volumes were checked: Crossref Springer chapter records carry no series volume. Direct fetches of link.springer.com (JS challenge or IdP redirect), dblp.org (Anubis bot wall) and IACR cryptodb (Cloudflare) were blocked. The volume numbers therefore come from Springer book/chapter listings surfaced through web search restricted to link.springer.com and springer.com, and from the Open Library ISBN API where it had a series note (`https://openlibrary.org/api/books?bibkeys=ISBN:<isbn>&format=json&jscmd=data`). These are marked "vol via Springer listing" below. They are well-known numbers, but nobody opened the Springer page itself.

| key | final citation (one line) | verified how | status |
| --- | --- | --- | --- |
| bitcoin | S. Nakamoto, Bitcoin: A Peer-to-Peer Electronic Cash System, 2008, bitcoin.org/bitcoin.pdf | Downloaded https://bitcoin.org/bitcoin.pdf (title and author on p.1; the PDF carries no date). Year from the announcement post https://www.metzdowd.com/pipermail/cryptography/2008-October/014810.html (Fri Oct 31 2008) | VERIFIED |
| ethereum | V. Buterin, Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform, 2014 | https://ethereum.org/en/whitepaper/ ("published in 2014", link to original PDF). Original PDF https://ethereum.org/content/whitepaper/whitepaper-pdf/Ethereum_Whitepaper_-_Buterin_2014.pdf, p.1: "By Vitalik Buterin (2014)" | CORRECTED: full title added. Year 2014 per the PDF and visible page text; the page's schema.org metadata says 2013 |
| ethyellow | G. Wood, Ethereum: A Secure Decentralised Generalised Transaction Ledger, Shanghai version efc5f9a, 2025-02-04 | https://ethereum.github.io/yellowpaper/paper.pdf p.1 | VERIFIED (new key `ethyellow`; it is a living document, so the version is pinned in the note) |
| backbone | J. Garay, A. Kiayias, N. Leonardos, The Bitcoin Backbone Protocol: Analysis and Applications, EUROCRYPT 2015 Part II, LNCS 9057, pp. 281-310, doi 10.1007/978-3-662-46803-6_10 | Crossref works/10.1007/978-3-662-46803-6_10. Vol 9057 from Open Library ISBN 9783662468029 ("Lecture Notes in Computer Science (9057)") and the Springer listing. Note: a journal version exists, J. ACM 71 (2024), doi 10.1145/3653445 | VERIFIED |
| selfish | I. Eyal, E. G. Sirer, Majority Is Not Enough: Bitcoin Mining Is Vulnerable, FC 2014, LNCS 8437, pp. 436-454, doi 10.1007/978-3-662-45472-5_28 | Crossref works/10.1007/978-3-662-45472-5_28; vol via Springer listing (corroborated by a DBLP record snippet). CACM 2018 version: doi 10.1145/3212998 | VERIFIED |
| eclipse | E. Heilman, A. Kendler, A. Zohar, S. Goldberg, Eclipse Attacks on Bitcoin's Peer-to-Peer Network, 24th USENIX Security Symposium, pp. 129-144, 2015 | https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/heilman (citation_firstpage 129, lastpage 144) | VERIFIED |
| rosenfeld | M. Rosenfeld, Analysis of Hashrate-Based Double Spending, arXiv:1402.2009, Feb 2014 | https://arxiv.org/abs/1402.2009 meta tags (the export API was rate-limited). DataCite https://api.datacite.org/dois/10.48550/arXiv.1402.2009 | VERIFIED (DOI 10.48550/arXiv.1402.2009 confirmed registered) |
| weaksubj | V. Buterin, Proof of Stake: How I Learned to Love Weak Subjectivity, Ethereum Foundation Blog, 25 Nov 2014 | https://blog.ethereum.org/2014/11/25/proof-stake-learned-love-weak-subjectivity (datePublished 2014-11-25, author Vitalik Buterin) | VERIFIED |
| merkle89 | R. C. Merkle, A Certified Digital Signature, CRYPTO '89 Proceedings, LNCS 435, pp. 218-238, Springer 1990, doi 10.1007/0-387-34805-0_21 | Crossref works/10.1007/0-387-34805-0_21 (no issue date in Crossref). Vol 435 and 1990 publication year via Springer listing | VERIFIED (year 1990 = publication year of the proceedings, not the 1989 conference) |
| lamport79 | L. Lamport, Constructing Digital Signatures from a One Way Function, SRI International Technical Report CSL-98, Oct 1979 | https://lamport.azurewebsites.net/pubs/pubs.html (author's own publication list) | VERIFIED (month October added) |
| sphincs | D. J. Bernstein, D. Hopwood, A. Hülsing, T. Lange, R. Niederhagen, L. Papachristodoulou, M. Schneider, P. Schwabe, Z. Wilcox-O'Hearn, SPHINCS, EUROCRYPT 2015 Part I, LNCS 9056, pp. 368-397, doi 10.1007/978-3-662-46800-5_15 | Crossref works/10.1007/978-3-662-46800-5_15; vol 9056 via Springer listing ("LNCS 9056 + 9057") | VERIFIED (full 9-author list from Crossref) |
| sphincsplus | D. J. Bernstein, A. Hülsing, S. Kölbl, R. Niederhagen, J. Rijneveld, P. Schwabe, The SPHINCS+ Signature Framework, ACM CCS 2019, pp. 2129-2146, doi 10.1145/3319535.3363229 | Crossref works/10.1145/3319535.3363229 | VERIFIED |
| xmss | J. Buchmann, E. Dahmen, A. Hülsing, XMSS - A Practical Forward Secure Signature Scheme Based on Minimal Security Assumptions, PQCrypto 2011, LNCS 7071, pp. 117-129, doi 10.1007/978-3-642-25405-5_8 | Crossref works/10.1007/978-3-642-25405-5_8; vol via Springer listing | VERIFIED |
| rfc8391 | A. Hülsing, D. Butin, S. Gazdag, J. Rijneveld, A. Mohaisen, XMSS: eXtended Merkle Signature Scheme, RFC 8391, May 2018, doi 10.17487/RFC8391 | https://www.rfc-editor.org/rfc/rfc8391.json (status INFORMATIONAL, source "Crypto Forum") | VERIFIED (institution IRTF because it is the CFRG stream, not IETF) |
| rfc8554 | D. McGrew, M. Curcio, S. Fluhrer, Leighton-Micali Hash-Based Signatures, RFC 8554, Apr 2019, doi 10.17487/RFC8554 | https://www.rfc-editor.org/rfc/rfc8554.json (INFORMATIONAL, "Crypto Forum") | VERIFIED |
| sp800208 | D. A. Cooper, D. C. Apon, Q. H. Dang, M. S. Davidson, M. J. Dworkin, C. A. Miller, Recommendation for Stateful Hash-Based Signature Schemes, NIST SP 800-208, Oct 2020, doi 10.6028/NIST.SP.800-208 | Crossref works/10.6028/NIST.SP.800-208; https://csrc.nist.gov/pubs/sp/800/208/final (Date Published: October 2020) | VERIFIED (authors added) |
| fips203 | NIST, Module-Lattice-Based Key-Encapsulation Mechanism Standard, FIPS 203, Aug 2024, doi 10.6028/NIST.FIPS.203 | Crossref works/10.6028/NIST.FIPS.203; https://csrc.nist.gov/pubs/fips/203/final (August 13, 2024) | VERIFIED |
| fips180 | NIST, Secure Hash Standard (SHS), FIPS 180-4, Aug 2015, doi 10.6028/NIST.FIPS.180-4 | Crossref works/10.6028/NIST.FIPS.180-4; https://csrc.nist.gov/pubs/fips/180-4/upd1/final (Date Published: August 2015) | VERIFIED |
| fips202 | NIST, SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions, FIPS 202, Aug 2015, doi 10.6028/NIST.FIPS.202 | Crossref works/10.6028/NIST.FIPS.202 (title truncated there); https://csrc.nist.gov/pubs/fips/202/final (full title, August 2015) | VERIFIED |
| shor | P. W. Shor, Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer, SIAM J. Comput. 26(5):1484-1509, Oct 1997, doi 10.1137/S0097539795293172 | Crossref works/10.1137/s0097539795293172 | VERIFIED |
| grover | L. K. Grover, A Fast Quantum Mechanical Algorithm for Database Search, STOC '96, ACM, pp. 212-219, doi 10.1145/237814.237866 | Crossref works/10.1145/237814.237866 | VERIFIED |
| dworknaor | C. Dwork, M. Naor, Pricing via Processing or Combatting Junk Mail, CRYPTO '92, LNCS 740, pp. 139-147, Springer 1993, doi 10.1007/3-540-48071-4_10 | Crossref works/10.1007/3-540-48071-4_10 (no issue date). Vol 740 and print year 1993 via the Springer book listing for 10.1007/3-540-48071-4 | VERIFIED (year 1993 = publication year) |
| hashcash | A. Back, Hashcash - A Denial of Service Counter-Measure, 1 Aug 2002 | http://www.hashcash.org/papers/hashcash.pdf p.1 ("1st August 2002") | VERIFIED |
| mergedmining | A. Judmayer, A. Zamyatin, N. Stifter, A. G. Voyiatzis, E. Weippl, Merged Mining: Curse or Cure?, DPM/CBT 2017 (ESORICS 2017 workshops), LNCS 10436, pp. 316-333, doi 10.1007/978-3-319-67816-0_18 | Crossref works/10.1007/978-3-319-67816-0_18. Vol 10436 from Open Library ISBN 9783319678153 | VERIFIED (booktitle is the joint volume title; which of DPM or CBT hosted the paper was not confirmed, so neither is named) |
| flyclient | B. Bünz, L. Kiffer, L. Luu, M. Zamani, FlyClient: Super-Light Clients for Cryptocurrencies, IEEE S&P 2020, pp. 928-946, doi 10.1109/SP40000.2020.00049 | Crossref works/10.1109/sp40000.2020.00049 (Crossref spells "Bunz"); umlaut from https://eprint.iacr.org/2019/226 meta tags | VERIFIED |
| stark | E. Ben-Sasson, I. Bentov, Y. Horesh, M. Riabzev, Scalable, Transparent, and Post-Quantum Secure Computational Integrity, Cryptology ePrint Archive 2018/046 | https://eprint.iacr.org/2018/046 (received 2018-01-10, last revised 2018-03-06) | VERIFIED |
| qrl | P. Waterland, Quantum Resistant Ledger (QRL), white paper, revised edition dated October 2016 | https://theqrl.org/whitepaper/QRL_whitepaper.pdf redirects to https://github.com/theQRL/Whitepaper/blob/master/QRL_whitepaper.pdf. The current PDF lists only info@theqrl.org, "October 2016 (revised)". The earliest committed version (commit 554d75e, 2017-10-26) lists peterwaterland@gmail.com, "November 2016" | VERIFIED with caveat: the author is inferred from the contact e-mail on the earliest revision; the current revision names no person |
| ens | N. Johnson, ERC-137: Ethereum Domain Name Service - Specification, Apr 2016, status Final | https://eips.ethereum.org/EIPS/eip-137; raw https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-137.md (created 2016-04-04, status Final); the EIPs repo file now reads "status: Moved" to the ERCs repo | CORRECTED: now labelled ERC-137 (moved to the ERC repository) rather than EIP-137 |
| namecoinstudy | H. Kalodner, M. Carlsten, P. Ellenbogen, J. Bonneau, A. Narayanan, An Empirical Study of Namecoin and Lessons for Decentralized Namespace Design, WEIS 2015, Delft, June 2015 | https://econinfosec.org/archive/weis2015/program.html (listed with [paper] link); PDF https://econinfosec.org/archive/weis2015/papers/WEIS_2015_kalodner.pdf | VERIFIED (no DOI or pages; it is a workshop) |
| namecoin | Namecoin project, https://www.namecoin.org/ | Fetched the home page (HTTP 200, title "Namecoin") | VERIFIED (no date) |
| eip1559 | V. Buterin, E. Conner, R. Dudley, M. Slipper, I. Norden, A. Bakhta, EIP-1559: Fee market change for ETH 1.0 chain, Apr 2019, status Final | https://eips.ethereum.org/EIPS/eip-1559; raw https://raw.githubusercontent.com/ethereum/EIPS/master/EIPS/eip-1559.md (created 2019-04-13) | VERIFIED |
| bip157 | O. Osuntokun, A. Akselrod, J. Posen, BIP 157: Client Side Block Filtering, 2017, status Deployed | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0157.mediawiki (Authors: Osuntokun, Akselrod, Posen; Assigned 2017-05-24) | VERIFIED (Posen is an author of 157) |
| bip158 | O. Osuntokun, A. Akselrod, BIP 158: Compact Block Filters for Light Clients, 2017, status Deployed | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0158.mediawiki (Authors: Osuntokun, Akselrod; Assigned 2017-05-24) | VERIFIED (Posen is not an author of 158) |
| horizen | A. Garoffolo, P. Stabilini, R. Viglione, U. Stav, Proposal to Modify Satoshi Consensus to Enhance Protection Against 51% Attacks: A Penalty System for Delayed Block Submission, Horizen, 14 June 2018 | The URL https://www.horizen.global/assets/files/A-Penalty-System-for-Delayed-Block-Submission-by-Horizen.pdf (taken from a third-party repo README) now redirects to a 404 on horizen.io. Archived copy https://web.archive.org/web/20200217015049/https://www.horizen.global/assets/files/A-Penalty-System-for-Delayed-Block-Submission-by-Horizen.pdf, title page read visually | CORRECTED: full title; four authors (Stabilini and Stav added); date 14 June 2018; URL is the archive copy because the official file is gone |
| mess | Isaac, ECIP-1100: MESS (Modified Exponential Subjective Scoring), created 2020-09-09, status Replaced | https://ecips.ethereumclassic.org/ECIPs/ecip-1100; raw https://raw.githubusercontent.com/ethereumclassic/ECIPs/master/_specs/ecip-1100.md ("author: Isaac"; "Update (January 2024): Replaced with ECBP-1110") | CORRECTED (status): MESS is no longer active. The author is listed as just "Isaac" |
| messoff | Isaac, ECIP-1110: Deactivate MESS, created 2023-09-17, status Active | raw https://raw.githubusercontent.com/ethereumclassic/ECIPs/master/_specs/ecip-1110.md | VERIFIED (extra entry; cite it if the text says MESS was turned off) |
| asert | freetrader, J. Toomim, C. Culianu, M. Lundeberg, 2020-NOV-15 ASERT Difficulty Adjustment Algorithm (aserti3-2d), v0.6, 2020-08-12 | https://upgradespecs.bitcoincashnode.org/2020-11-15-asert/ (author line and "Version 0.6, 2020-08-12"). The mirror https://documentation.cash/protocol/forks/2020-11-15-asert (v0.6.3, 2020-08-17) also lists Tobias Ruck | CORRECTED: four authors (freetrader and Calin Culianu added to Lundeberg and Toomim) |
| randomx | tevador, RandomX design, repository document, first committed Jan 2019 | https://raw.githubusercontent.com/tevador/RandomX/master/doc/design.md (no author line in the file); GitHub API repos/tevador/RandomX (owner tevador) and commits?path=doc/design.md (earliest 2019-01-13 by tevador, latest 2026-02-17) | VERIFIED (living document; author = repository owner handle) |
| p2pool | SChernykh, P2Pool: Decentralized pool for Monero mining, GitHub, 2021 | https://github.com/SChernykh/p2pool; GitHub API repos/SChernykh/p2pool (created 2021-08-22, description, top contributor SChernykh) | VERIFIED (author is the GitHub handle; no real name was confirmed, so none is given) |
| tail | The Monero Project, Tail Emission, Moneropedia | https://www.getmonero.org/resources/moneropedia/tail-emission.html (tail emission began at the end of May 2022, 0.6 XMR per block) | VERIFIED (undated page) |
| chainlocks | A. Block, DIP 0008: ChainLocks, Nov 2018, status Final | https://raw.githubusercontent.com/dashpay/dips/master/dip-0008.md (Author(s): Alexander Block; Created 2018-11-16; Status Final) | VERIFIED |
| vrf | S. Micali, M. Rabin, S. Vadhan, Verifiable Random Functions, FOCS '99, IEEE CS, pp. 120-130, doi 10.1109/SFFCS.1999.814584 | Crossref works/10.1109/sffcs.1999.814584 (IEEE record gives initials only, no issued date; year from the 40th FOCS = 1999) | VERIFIED |
| smt | R. Dahlberg, T. Pulls, R. Peeters, Efficient Sparse Merkle Trees: Caching Strategies and Secure (Non-)Membership Proofs, NordSec 2016, LNCS 10014, pp. 199-215, doi 10.1007/978-3-319-47560-8_13 | Crossref works/10.1007/978-3-319-47560-8_13 (Crossref title is just "Efficient Sparse Merkle Trees", no subtitle); vol 10014 via the Springer book listing | VERIFIED (the full title with subtitle is confirmed by the authors' ePrint version https://eprint.iacr.org/2016/683; Springer/Crossref store only the main title) |
| joux | A. Joux, Multicollisions in Iterated Hash Functions. Application to Cascaded Constructions, CRYPTO 2004, LNCS 3152, pp. 306-316, doi 10.1007/978-3-540-28628-8_19 | Crossref query.bibliographic, then works/10.1007/978-3-540-28628-8_19; vol 3152 via Springer listing (book doi 10.1007/b99099) | VERIFIED |


## Вывод проверок

Сборка `make -C paper/chain` (tectonic, лог `.temp/chain-10/build-02.log`), код возврата 0, `pdfinfo paper/chain/chain.pdf`: 15 страниц вместе со списком литературы. Overfull-боксов нет:

```
make: `chain.pdf' is up to date.
```

`sh scripts/check.sh` (код 0):

```
check.sh: ok (39 files)
```

`python3 -I scripts/check-self-test.py` (код 0):

```
.........
----------------------------------------------------------------------
Ran 9 tests in 8.077s

OK
```

Изменение `check.sh`: проверка оговорок о поставке и чёрный список прозы теперь читают и `paper/chain/*.tex`; остальные файлы `paper/` эти две проверки по-прежнему не читают (другие авторы). Новый тест `test_chain_paper` сажает тире, ёлочки, антитезу и две оговорки в `paper/chain/chain.tex` (каждая валит проверку со своей меткой), проверяет чистый положительный контроль и то, что тот же текст в `paper/other.tex` проверку не валит. Предел теста: TeX-тире `--` и `---` проверка не видит; в `chain.tex` они встречаются только в числовых диапазонах и путях TikZ, это проверено вручную (`grep -n -e '---' -e '[^0-9 ]--[^0-9]'` вне `\draw` пуст).

Контроль инструмента: тот же набор тестов против `check.sh` с origin/main (`.temp/chain-10/check-old.sh`) падает именно на новом тесте (код 1):

```
FAIL: test_chain_paper (__main__.HygieneTests.test_chain_paper) (text='Ключник — служба.')
FAIL: test_chain_paper (__main__.HygieneTests.test_chain_paper) (text='Поле «aud».')
FAIL: test_chain_paper (__main__.HygieneTests.test_chain_paper) (text='Это не очередь, а журнал.')
FAIL: test_chain_paper (__main__.HygieneTests.test_chain_paper) (text='Пока цепочки нет.')
FAIL: test_chain_paper (__main__.HygieneTests.test_chain_paper) (text='Узел ещё не проверяет.')
Ran 9 tests in 8.109s
FAILED (failures=5)
```

Первый прогон `check.sh` по черновику нашёл три слова "пока" в значении союза (`chain.tex`, строки про споры, eclipse и расхождение взглядов узлов); фразы переписаны без него.
