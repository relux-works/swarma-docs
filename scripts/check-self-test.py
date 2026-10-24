#!/usr/bin/env python3
"""Exercise check.sh on disposable fixtures, never on publication sources."""
import argparse
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

    def run_check(self):
        return subprocess.run(['sh', str(self.root / 'scripts/check.sh')],
                              capture_output=True, text=True)

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

    # Only the exact state chapter is exempt; other hygiene checks still apply there.
    def test_state_chapter(self):
        p = self.root / 'book/ru/29-gde-my.md'
        p.write_text('# State\n\n⟦решено⟧ пока не реализовано\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0)
        self.assertNotIn('== delivery hedge', r.stdout)
        p.write_text(p.read_text() + '\n/home/example/project\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('== local path', r.stdout)

    # Every requested hedge is reported without failing the pilot; a nearby
    # precise design sentence has no report. This is lexical, not semantic proof.
    def test_hedges(self):
        for phrase in ('пока', 'ещё не', 'в v0', 'не реализовано', 'Пока', 'В v0'):
            with self.subTest(phrase=phrase):
                self.chapter.write_text('# Example\n\n' + phrase + '\n')
                r = self.run_check()
                self.assertEqual(r.returncode, 0)
                self.assertIn('== delivery hedge', r.stdout, 'planted hedge must be flagged')
        self.chapter.write_text('# Example\n\nПроверка отклоняет отозванный грант.\n')
        self.assertNotIn('== delivery hedge', self.run_check().stdout)

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


unittest.main(argv=[__file__])
