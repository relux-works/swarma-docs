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

    # Every hedge form, in either case, fails a chapter other than the state
    # chapter; a precise design sentence nearby passes. Lexical, not semantic.
    def test_hedges(self):
        for phrase in ('пока', 'ещё не', 'в v0', 'не реализовано', 'Пока', 'В v0'):
            with self.subTest(phrase=phrase):
                self.chapter.write_text('# Example\n\n' + phrase + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 1, 'planted hedge must fail')
                self.assertIn('== delivery hedge', r.stdout)
        self.chapter.write_text('# Example\n\nПроверка отклоняет отозванный грант; покажем v0.3.\n')
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


    # Each prose blacklist pattern fails a book chapter by default and is only
    # reported under STRICT_PROSE=0; a clean sentence with a hyphenated word and
    # a numeric range passes both ways.
    def test_prose_blacklist(self):
        cases = (('Ключник — служба.', 'dash in prose'), ('Ключник–служба.', 'dash in prose'),
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
        self.chapter.write_text('# Example\n\nКлючник подписывает запись; кросс-подпись проверяется в 10-12 шагов.\n')
        for env in ({}, {'STRICT_PROSE': '0'}, {'STRICT_PROSE': '1'}):
            with self.subTest(env=env):
                r = self.run_check(**env)
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertNotIn('== ', r.stdout)

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

unittest.main(argv=[__file__])
