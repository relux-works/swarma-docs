#!/usr/bin/env python3
"""Exercise check.sh on disposable fixtures, never on publication sources."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

parser = argparse.ArgumentParser()
parser.add_argument('--checker', type=Path, default=Path(__file__).with_name('check.sh'))
args = parser.parse_args()
checker = args.checker.resolve()


class HygieneTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[1] / '.temp'
        scratch.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix='check-fixture-', dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'scripts').mkdir()
        shutil.copyfile(checker, self.root / 'scripts/check.sh')
        (self.root / 'book/ru').mkdir(parents=True)
        (self.root / 'paper').mkdir()
        self.chapter = self.root / 'book/ru/06-example.md'
        self.chapter.write_text('# Example\n\nThe verifier checks the grant.\n')

    def run_check(self, **env):
        return subprocess.run(['sh', str(self.root / 'scripts/check.sh')],
                              capture_output=True, text=True, env=dict(os.environ, **env))

    # A valid chapter passes; each planted marker fails with the intended label,
    # including another chapter, paper, and split/unmatched delimiter cases.
    def test_marker_boundary(self):
        self.assertEqual(self.run_check().returncode, 0)
        for name in ('book/ru/06-example.md', 'book/ru/07-neighbor.md', 'paper/example.tex'):
            p = self.root / name
            old = p.read_text() if p.exists() else None
            for marker in ('⟦решено⟧', '⟦решено\n⟧', '⟦решено'):
                with self.subTest(name=name, marker=marker):
                    p.write_text('# Example\n\n' + marker + '\n')
                    r = self.run_check()
                    self.assertEqual(r.returncode, 1, 'planted marker must fail')
                    self.assertIn('== status marker', r.stdout)
            if old is None:
                p.unlink()
            else:
                p.write_text(old)
        self.assertEqual(self.run_check().returncode, 0)

    # Only the exact state chapter is exempt from markers and hedges; the other
    # hygiene checks and the prose blacklist still fail there.
    def test_state_chapter(self):
        p = self.root / 'book/ru/29-gde-my.md'
        p.write_text('# State\n\n⟦решено⟧ пока не реализовано\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== delivery hedge', r.stdout)
        for text, label in (('/home/example/project', 'local path'), ('Ключник — служба.', 'dash in prose')):
            with self.subTest(label=label):
                p.write_text('# State\n\nпока не реализовано\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1)
                self.assertIn('== ' + label, r.stdout)

    # The a2a book is held to the book's rules: a planted marker, hedge, dash,
    # guillemet or missing heading fails an a2a chapter; only the exact a2a
    # state chapter 09-gde-my.md may carry markers and hedges, and the book's
    # state chapter name gives no exemption there. A clean a2a chapter passes.
    def test_a2a_book(self):
        d = self.root / 'a2a-book/ru'
        d.mkdir(parents=True)
        ch = d / '05-pochta.md'
        ch.write_text('# Почта\n\nПотребитель сохраняет событие до курсора.\n')
        self.assertEqual(self.run_check().returncode, 0)
        for text, label in (('⟦решено⟧', 'status marker'), ('пока', 'delivery hedge'),
                            ('Ящик — файл.', 'dash in prose'), ('Поле «to».', 'guillemets'),
                            ('/home/example/project', 'local path')):
            with self.subTest(label=label):
                ch.write_text('# Почта\n\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn('== ' + label, r.stdout)
        ch.write_text('Без заголовка\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('chapter without a level-1 heading: a2a-book/ru/05-pochta.md', r.stdout)
        ch.write_text('# Почта\n')
        state = d / '09-gde-my.md'
        state.write_text('# Где мы\n\n⟦решено⟧ пока не реализовано\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        state.write_text('# Где мы\n\nпока\nЯщик — файл.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('== dash in prose', r.stdout)
        self.assertNotIn('== delivery hedge', r.stdout)
        state.unlink()
        other = d / '29-gde-my.md'
        other.write_text('# Где мы\n\nпока\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('== delivery hedge', r.stdout)

    # The installation book is held to the book's rules: a planted marker,
    # hedge, dash, guillemet, local path or missing heading fails an
    # install-book chapter; only the exact state chapter 06-gde-my.md may carry
    # markers and hedges, and the other books' state chapter names give no
    # exemption there. A clean chapter passes.
    def test_install_book(self):
        d = self.root / 'install-book/ru'
        d.mkdir(parents=True)
        ch = d / '03-shagi.md'
        ch.write_text('# Шаги\n\nУстановщик проверяет подпись манифеста.\n')
        self.assertEqual(self.run_check().returncode, 0)
        for text, label in (('⟦решено⟧', 'status marker'), ('пока', 'delivery hedge'),
                            ('Ключник — служба.', 'dash in prose'), ('Поле «to».', 'guillemets'),
                            ('/home/example/project', 'local path')):
            with self.subTest(label=label):
                ch.write_text('# Шаги\n\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn('== ' + label, r.stdout)
        ch.write_text('Без заголовка\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('chapter without a level-1 heading: install-book/ru/03-shagi.md', r.stdout)
        ch.write_text('# Шаги\n')
        state = d / '06-gde-my.md'
        state.write_text('# Где мы\n\n⟦решено⟧ пока не реализовано\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        state.write_text('# Где мы\n\nпока\nКлючник — служба.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('== dash in prose', r.stdout)
        self.assertNotIn('== delivery hedge', r.stdout)
        state.unlink()
        for name in ('09-gde-my.md', '29-gde-my.md'):
            with self.subTest(name=name):
                other = d / name
                other.write_text('# Где мы\n\nпока\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1)
                self.assertIn('== delivery hedge', r.stdout)
                other.unlink()

    # Every hedge form, in either case, fails a chapter other than the state
    # chapter; a precise design sentence nearby passes. Lexical, not semantic.
    def test_hedges(self):
        for phrase in ('пока', 'ещё не', 'еще не', 'Еще не', 'в v0', 'не реализовано', 'Пока', 'В v0'):
            with self.subTest(phrase=phrase):
                self.chapter.write_text('# Example\n\n' + phrase + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, 'planted hedge must fail')
                self.assertIn('== delivery hedge', r.stdout)
        self.chapter.write_text('# Example\n\nПроверка отклоняет отозванный грант; покажем v0.3; размещение запрещено.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== delivery hedge', r.stdout)

    # Existing heading, identifier, retired-name, and TeX checks keep rejecting
    # their specific violations, with a clean positive control after each plant.
    def test_existing_checks(self):
        for text, label in (
            ('RUN-260101-abcdef', 'board, run or review identifier'),
            ('F-123', 'review finding number'), ('D-001', 'decision number'),
            ('/home/example/project', 'local path'), ('orch-example', 'machine or seat name'),
            ('Slopcore', 'retired name'), ('\\status{example}', 'TeX status label')):
            with self.subTest(label=label):
                self.chapter.write_text('# Example\n\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1)
                self.assertIn('== ' + label, r.stdout)
                self.chapter.write_text('# Example\n')
                self.assertEqual(self.run_check().returncode, 0)
        self.chapter.write_text('No heading\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('chapter without a level-1 heading', r.stdout)

    # Arbiter ruling ids of the a2a ruling log fail a chapter; words that only
    # contain the same letters pass. Lexical, not semantic.
    def test_ruling_identifier(self):
        for text in ('Постановление ac-R11 и правило.', 'tb-R108'):
            with self.subTest(text=text):
                self.chapter.write_text('# Example\n\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn('== arbiter ruling identifier', r.stdout)
        for text in ('Флаг `-R` и постановление арбитра.', 'fac-R11', 'ac-Rx'):
            with self.subTest(text=text):
                self.chapter.write_text('# Example\n\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 0, r.stdout)


    # Each prose blacklist pattern fails a book chapter by default and is only
    # reported under STRICT_PROSE=0; a clean sentence with a hyphenated word and
    # a numeric range passes both ways.
    def test_prose_blacklist(self):
        cases = (('Ключник — служба.', 'dash in prose'), ('Ключник–служба.', 'dash in prose'),
                 ('Поле `aud`— аудитория.', 'dash in prose'), ('Ключ (агента)— подпись.', 'dash in prose'),
                 ('— Ключник подписывает.', 'dash in prose'), ('– Ключник подписывает.', 'dash in prose'),
                 ('Шаги 10—12.', 'dash in prose'), ('Ключник —служба.', 'dash in prose'),
                 ('Поле `aud`–x.', 'dash in prose'), ('Шаги 10 – 12.', 'dash in prose'),
                 ('Поле «aud».', 'guillemets'),
                 ('Это не очередь, а журнал.', 'antithesis'), ('Стоит отметить, что ключ один.', 'filler opener'),
                 ('Мощная проверка.', 'marketing adjective'))
        for text, label in cases:
            with self.subTest(text=text):
                self.chapter.write_text('# Example\n\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, 'default mode must fail on ' + label)
                self.assertIn('== ' + label + '\n', r.stdout)
                r = self.run_check(STRICT_PROSE='0')
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertIn('== ' + label + ' (advisory)', r.stdout)
        self.chapter.write_text('# Example\n\nКлючник подписывает запись; кросс-подпись проверяется в 10-12 шагов.\n'
                                'Диапазоны 0–2, L0–L2, 09–21 и 30000–59999 остаются.\n')
        for env in ({}, {'STRICT_PROSE': '0'}, {'STRICT_PROSE': '1'}):
            with self.subTest(env=env):
                r = self.run_check(**env)
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertNotIn('== ', r.stdout)

    # The chain paper paper/chain/*.tex is held to the book voice: a planted
    # dash, guillemet, antithesis or delivery hedge fails with its label, and
    # so does a TeX dash (---, spaced --) or \guillemot quote; a clean sentence
    # with a numeric range and a TikZ path passes, and the same text in another
    # paper file stays outside these checks. Limit: an unspaced word--word dash
    # and babel shorthands other than "< and "> are not detected.
    def test_chain_paper(self):
        chain = self.root / 'paper/chain/chain.tex'
        chain.parent.mkdir(parents=True)
        cases = (('Ключник — служба.', 'dash in prose'), ('Поле «aud».', 'guillemets'),
                 ('Это не очередь, а журнал.', 'antithesis'), ('Пока цепочки нет.', 'delivery hedge'),
                 ('Узел ещё не проверяет.', 'delivery hedge'), ('Ключник --- служба.', 'TeX dash or quote'),
                 ('Ключник -- служба.', 'TeX dash or quote'), ('Поле \\guillemotleft aud.', 'TeX dash or quote'))
        for text, label in cases:
            with self.subTest(text=text):
                chain.write_text('\\section{Пример}\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, 'chain paper must fail on ' + label)
                self.assertIn('== ' + label + '\n', r.stdout)
                self.assertIn('paper/chain/chain.tex:2:', r.stdout)
        chain.write_text('\\section{Пример}\nУзел проверяет пачку; шаги 0–2, страницы 136--163, кросс-подпись.\n'
                         '\\draw[arr] (a) -- (b);\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== ', r.stdout)
        other = self.root / 'paper/other.tex'
        other.write_text('\\section{Пример}\nПока ключник — служба «aud» --- да.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== ', r.stdout)
        other.unlink()

    # Editorial notes under editorial/notes/*/ru/ get an advisory blacklist
    # report that never fails; other editorial files are not scanned at all.
    def test_note_blacklist(self):
        note = self.root / 'editorial/notes/example/ru/01-note.md'
        note.parent.mkdir(parents=True)
        note.write_text('# Note\n\nПоле «aud» — подпись.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('== guillemets in editorial notes (advisory)', r.stdout)
        self.assertIn('== dash in prose in editorial notes (advisory)', r.stdout)
        note.write_text('# Note\n\nКлючник подписывает запись.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0)
        self.assertNotIn('editorial notes', r.stdout)
        for name in ('editorial/notes/top.ru.md', 'editorial/notes/example/en/01-note.md'):
            with self.subTest(name=name):
                other = self.root / name
                other.parent.mkdir(parents=True, exist_ok=True)
                other.write_text('# Other\n\nПоле «aud» — подпись.\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 0)
                self.assertNotIn('editorial notes', r.stdout)
                other.unlink()

    # The signing note in editorial/notes/signing-auth/ru/ is blocking: each
    # planted blacklist pattern fails with the book label and is only reported
    # under STRICT_PROSE=0, a clean note passes, and a hit in another note or
    # outside that ru/ directory stays advisory or unscanned.
    def test_signing_note_blacklist(self):
        note = self.root / 'editorial/notes/signing-auth/ru/01-note.md'
        note.parent.mkdir(parents=True)
        cases = (('Ключник — служба.', 'dash in prose'), ('Поле «aud».', 'guillemets'),
                 ('Это не очередь, а журнал.', 'antithesis'), ('Стоит отметить, что ключ один.', 'filler opener'),
                 ('Мощная проверка.', 'marketing adjective'))
        for text, label in cases:
            with self.subTest(text=text):
                note.write_text('# Note\n\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, 'signing note must fail on ' + label)
                self.assertIn('== ' + label + '\n', r.stdout)
                self.assertIn('editorial/notes/signing-auth/ru/01-note.md:3:', r.stdout)
                self.assertNotIn('in editorial notes', r.stdout)
                r = self.run_check(STRICT_PROSE='0')
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertIn('== ' + label + ' (advisory)', r.stdout)
        note.write_text('# Note\n\nКлючник подписывает запись; шаги 0–2, кросс-подпись.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== ', r.stdout)
        for name in ('editorial/notes/other/ru/01-note.md', 'editorial/notes/signing-auth/README.md',
                     'editorial/notes/signing-auth/en/01-note.md'):
            with self.subTest(name=name):
                other = self.root / name
                other.parent.mkdir(parents=True, exist_ok=True)
                other.write_text('# Other\n\nПоле «aud» — подпись.\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertNotIn('== guillemets\n', r.stdout)
                other.unlink()

    # Each platform-paper rule fails a planted TeX line in paper/platform/ with
    # its own label and file:line, and is only reported under STRICT_PROSE=0; a
    # clean TeX line with digit ranges, П1--П8, L0--L2, hyphenated words, the
    # verb "планирует" and a TikZ "to" path passes. Limit: lexical; the same hits in other TeX under
    # paper/ or in a non-.tex file under paper/platform/ are not scanned by it.
    def test_platform_paper(self):
        doc = self.root / 'paper/platform/platform.tex'
        doc.parent.mkdir(parents=True)
        cases = (('Ключник --- служба.', 'dash in prose'), ('Ключник -- служба.', 'dash in prose'),
                 ('Поле~--- аудитория.', 'dash in prose'), ('Ключник — служба.', 'dash in prose'),
                 ('Шаги a--b.', 'dash in prose'), ('Поле «aud».', 'guillemets'), ('Поле <<aud>>.', 'guillemets'),
                 ('Поле \\guillemotleft aud.', 'guillemets'),
                 ('Это не очередь, а журнал.', 'antithesis'), ('Стоит отметить, что ключ один.', 'filler opener'),
                 ('Мощная проверка.', 'marketing adjective'), ('Пока ключника нет.', 'delivery hedge'),
                 ('Кода ещё не написано.', 'delivery hedge'), ('Ключник работает сегодня.', 'readiness wording'),
                 ('Ключник в планах.', 'readiness wording'), ('Цепочка не построена.', 'readiness wording'),
                 ('Брокер в разработке.', 'readiness wording'))
        for text, label in cases:
            with self.subTest(text=text):
                doc.write_text('\\section{Пример}\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, 'platform paper must fail on ' + label)
                self.assertIn('== platform paper: ' + label + '\n', r.stdout)
                self.assertIn('paper/platform/platform.tex:2:', r.stdout)
                r = self.run_check(STRICT_PROSE='0')
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertIn('== platform paper: ' + label + ' (advisory)', r.stdout)
        doc.write_text('\\section{Пример}\nОркестратор планирует работу; шаги 2--18, П1--П8, L0--L2 и [5,70--7,22]; '
                       'кросс-подпись.\n\\draw[arr] (a) to node{UID} (b);\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== ', r.stdout)
        doc.unlink()
        for name in ('paper/other.tex', 'paper/platform/notes.md'):
            with self.subTest(name=name):
                other = self.root / name
                other.write_text('# Other\n\\section{Пример}\nКлючник --- служба; поле <<aud>>; работает сегодня.\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertNotIn('platform paper', r.stdout)
                other.unlink()

    # The broadened readiness rule fails each planted status form in
    # paper/platform/ with its label and file:line, in either case; the same
    # phrase wrapped in \\measured{...} passes, while an unwrapped readiness
    # form on the same line still fails, and \\measured{...} does not exempt
    # its argument from the dash, guillemet or delivery-hedge rules. Verbs and
    # limits that only look similar ("планирует", "не позже", "будто",
    # "готовность") pass. Limit: lexical; other wordings of a readiness claim
    # pass, and nested braces inside \\measured{...} are not stripped.
    def test_platform_readiness_measured(self):
        doc = self.root / 'paper/platform/platform.tex'
        doc.parent.mkdir(parents=True)
        forms = ('Допуск не настроен.', 'Допуск не настраивался.', 'Формат не опубликован.',
                 'Формат не публикуется.', 'Служба не развёрнута.', 'Мост не готов.',
                 'Выпуск планируется.', 'Мы планируем выпуск.', 'Цепочка запланирована.',
                 'Мост будет проверять.', 'Службы будут работать.', 'В будущем мост проверит.',
                 'Есть прототип моста.', 'Предстоит написать мост.', 'Мост появится.',
                 'НЕ ОПУБЛИКОВАН формат.')
        for text in forms:
            with self.subTest(text=text):
                doc.write_text('\\section{Пример}\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, 'planted readiness form must fail: ' + text)
                self.assertIn('== platform paper: readiness wording\n', r.stdout)
                self.assertIn('paper/platform/platform.tex:2:', r.stdout)
        doc.write_text('\\section{Пример}\nЗаписи \\measured{не опубликованы}; допуск \\measured{не настраивался}.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== ', r.stdout)
        for text, label in (('Записи \\measured{не опубликованы}, а мост будет готов.', 'readiness wording'),
                            ('Записи \\measured{не опубликованы --- журнал}.', 'dash in prose'),
                            ('Записи \\measured{не опубликованы <<aud>>}.', 'guillemets'),
                            ('Записи \\measured{пока не опубликованы}.', 'delivery hedge')):
            with self.subTest(text=text):
                doc.write_text('\\section{Пример}\n' + text + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn('== platform paper: ' + label + '\n', r.stdout)
        doc.write_text('\\section{Пример}\nОркестратор планирует работу не позже 300~с, будто сам; '
                       'готовность логина проверена.\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('== ', r.stdout)

    # The verdict does not depend on the caller's locale: under C and POSIX
    # settings a clean chapter still passes, and a capitalised Cyrillic hedge
    # and a guillemet still fail with their labels. Limit: the refusal path for
    # a host without any UTF-8 locale is not exercised here.
    def test_caller_locale(self):
        for env in ({'LC_ALL': 'C'}, {'LC_ALL': '', 'LC_CTYPE': 'C', 'LANG': 'C'}, {'LC_ALL': 'POSIX'}):
            with self.subTest(env=env):
                self.chapter.write_text('# Пример\n\nКлючник подписывает запись; шаги 0–2.\n')
                r = self.run_check(**env)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertNotIn('== ', r.stdout)
                for text, label in (('Пока ключника нет.', 'delivery hedge'), ('Поле «aud».', 'guillemets'),
                                    ('Ключник — служба.', 'dash in prose')):
                    self.chapter.write_text('# Пример\n\n' + text + '\n')
                    r = self.run_check(**env)
                    self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                    self.assertIn('== ' + label + '\n', r.stdout)


unittest.main(argv=[__file__])
