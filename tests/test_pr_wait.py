import contextlib
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


loader = importlib.machinery.SourceFileLoader(
    'pr_wait', str(Path(__file__).resolve().parents[1] / 'skills/babysit-pr/scripts/pr-wait')
)
spec = importlib.util.spec_from_loader(loader.name, loader)
pr_wait = importlib.util.module_from_spec(spec)
loader.exec_module(pr_wait)


class ReviewReadinessTests(unittest.TestCase):
    def poll(self, bot_bucket, *, until='ready', advisory=None):
        pr = {
            'state': 'OPEN', 'url': 'https://github.com/example/repo/pull/1',
            'baseRefName': 'main', 'headRefOid': 'a' * 40,
            'mergeStateStatus': 'CLEAN', 'viewer': 'owner',
            'author': {'login': 'author'},
            'comments': {'nodes': []}, 'reviews': {'nodes': []},
            'reviewThreads': {'nodes': []},
        }
        checks = {
            'CI': {'bucket': 'pass', 'link': 'https://example.test/ci', 'description': ''},
            'Greptile': {'bucket': bot_bucket, 'link': 'https://example.test/review', 'description': ''},
        }
        if advisory:
            checks['CodeRabbit'] = {'bucket': advisory, 'link': 'https://example.test/advisory', 'description': ''}
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as state, patch.object(pr_wait, 'STATE_DIR', Path(state)), \
                patch.object(pr_wait.Watcher, 'fetch_pr', return_value=pr), \
                patch.object(pr_wait.Watcher, 'fetch_checks', return_value=checks), \
                contextlib.redirect_stdout(output):
            watcher = pr_wait.Watcher('example/repo', 1, until, 5)
            watcher.required = {'CI'}
            watcher.baseline = False
            try:
                watcher.poll()
                watcher.poll()
            except SystemExit as stopped:
                return stopped.code, output.getvalue()
        return None, output.getvalue()

    def test_failed_or_cancelled_review_requires_action(self):
        for bucket in ('fail', 'cancel'):
            with self.subTest(bucket=bucket):
                code, output = self.poll(bucket)
                self.assertEqual(code, 1, output)
                self.assertNotIn('ready on ', output)

    def test_successful_review_can_report_ready(self):
        code, output = self.poll('pass')
        self.assertEqual(code, 0, output)
        self.assertIn('ready on ', output)

    def test_pending_review_keeps_waiting(self):
        code, output = self.poll('pending')
        self.assertIsNone(code, output)
        self.assertNotIn('ready on ', output)

    def test_skipped_review_is_not_a_successful_review(self):
        code, output = self.poll('skipping')
        self.assertEqual(code, 1, output)
        self.assertNotIn('ready on ', output)

    def test_advisory_failure_does_not_block_successful_gating_review(self):
        code, output = self.poll('pass', advisory='fail')
        self.assertEqual(code, 0, output)
        self.assertIn('ready on ', output)

    def test_green_mode_only_requires_ci(self):
        code, output = self.poll('fail', until='green')
        self.assertEqual(code, 0, output)
        self.assertIn('green on ', output)


if __name__ == '__main__':
    unittest.main()
