"""Exercise the distributed CLI against copied and intentionally broken bundles."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


BUNDLE = Path(__file__).resolve().parents[1]
SCRIPT = BUNDLE / 'tools' / 'validate-docs.py'


class DocumentBundle(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / 'CAD guide có khoảng trắng'
        shutil.copytree(BUNDLE, self.root, ignore=shutil.ignore_patterns('__pycache__'))
        for path in self.root.rglob('*.md'):
            path.write_text('# Page\n', encoding='utf-8')

    def run_cli(self, *arguments):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--root', str(self.root), *arguments],
            cwd=self.parent, text=True, capture_output=True, encoding='utf-8')
        self.assertTrue(result.stdout.lstrip().startswith('{'), result.stderr)
        return result, json.loads(result.stdout)

    def test_copy_runs_from_unrelated_cwd_and_keeps_unicode_paths(self):
        (self.root / 'tệp có dấu.md').write_text('# Title\n', encoding='utf-8')
        (self.root / 'README.md').write_text(
            '[unicode](<tệp có dấu.md>)\n[encoded](t%E1%BB%87p%20c%C3%B3%20d%E1%BA%A5u.md)',
            encoding='utf-8')
        result, report = self.run_cli()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report['local_links'], 2)
        copied = subprocess.run(
            [sys.executable, str(self.root / 'tools' / 'validate-docs.py')],
            cwd=self.parent, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(copied.returncode, 0, copied.stdout + copied.stderr)

    def test_missing_file_and_missing_required_document_fail(self):
        (self.root / 'README.md').write_text('[missing](gone.md)', encoding='utf-8')
        (self.root / 'START-HERE.md').unlink()
        result, report = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual({issue['check'] for issue in report['issues']},
                         {'missing_target', 'missing_required'})

    def test_existing_external_file_and_absolute_path_are_not_portable(self):
        outside = self.parent / 'private.md'
        outside.write_text('# Private\n', encoding='utf-8')
        (self.root / 'README.md').write_text(
            '[escape](../private.md)\n[absolute](' + outside.as_posix() + ')',
            encoding='utf-8')
        result, report = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(report['issues']), 2, report)
        self.assertEqual({issue['check'] for issue in report['issues']},
                         {'outside_bundle', 'absolute_path'})

    def test_local_and_cross_file_fragments_are_checked(self):
        (self.root / 'README.md').write_text(
            '# First\n[local](#first)\n[other](sources.md#claim)\n[bad](sources.md#absent)',
            encoding='utf-8')
        (self.root / 'sources.md').write_text('<a id="claim"></a>\n', encoding='utf-8')
        result, report = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([issue['check'] for issue in report['issues']], ['missing_anchor'])

    def test_required_document_through_external_symlink_or_junction_fails(self):
        outside = self.parent / 'external'
        outside.mkdir()
        (outside / 'readiness-scenarios.md').write_text('# Private\n', encoding='utf-8')
        link = self.root / 'examples'
        link.rename(self.root / 'saved-examples')
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            if sys.platform != 'win32':
                self.skipTest(str(error))
            result = subprocess.run(
                ['cmd', '/c', 'mklink', '/J', str(link), str(outside)],
                capture_output=True, text=True)
            if result.returncode:
                self.skipTest(result.stderr)
        self.addCleanup(lambda: link.unlink() if link.is_symlink() else link.rmdir())
        result, report = self.run_cli()
        self.assertNotEqual(result.returncode, 0, report)
        self.assertIn('outside_bundle', [issue['check'] for issue in report['issues']])

    def test_code_examples_are_ignored_and_unsafe_schemes_fail(self):
        fence = chr(96) * 3
        inline = chr(96)
        (self.root / 'README.md').write_text(
            '[web](https://example.org)\n' + fence +
            '\n[example](not-a-file.md)\n' + fence + '\n'
            '~~~md\n[another](not-real.md)\n~~~\n' +
            inline + '[inline](not-real.md)' + inline + '\n[bad](javascript:alert)\n',
            encoding='utf-8')
        result, report = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['local_links'], 0)
        self.assertEqual([issue['check'] for issue in report['issues']], ['unsupported_scheme'])


if __name__ == '__main__':
    unittest.main()
