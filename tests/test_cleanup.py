import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('speechy1', Path(__file__).parents[1] / 'speechy1.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class CleanupTests(unittest.TestCase):
    def test_overlapping_aliases_and_canonical_phrase_are_not_rewritten_twice(self):
        aliases = {'astro': 'GPT Astra', 'astro max': 'GPT Astra Max', 'omarchy': 'Omarchy Linux'}
        self.assertEqual(s.substitutions('ASTRO MAX; Omarchy Linux; Omarchy; omnarchy', aliases),
                         'GPT Astra Max; Omarchy Linux; Omarchy Linux; omnarchy')

    def test_snippet_marker_loss_refuses_pasteable_output(self):
        cfg = s.DEFAULTS | {'snippets': {'my signature': 'VERBATIM'}}
        response = {'usage': {'total_tokens': 20}, 'choices': [{'finish_reason': 'stop', 'message': {'content': 'Rewritten signature'}}]}
        with patch.object(s, 'update'), patch.object(s, 'budget'), patch.object(s, 'request', return_value=response):
            with self.assertRaisesRegex(RuntimeError, 'snippet marker'):
                s.cleanup('my signature', cfg)

    def test_snippet_expands_after_cleanup_verbatim(self):
        cfg = s.DEFAULTS | {'snippets': {'my signature': 'Verbatim\nLine two.'}}
        response = {'usage': {'total_tokens': 20}, 'choices': [{'finish_reason': 'stop', 'message': {'content': 'Hello. SPEECHYPLACEHOLDER0END'}}]}
        with patch.object(s, 'update'), patch.object(s, 'budget'), patch.object(s, 'request', return_value=response):
            self.assertEqual(s.cleanup('Hello my signature', cfg), 'Hello. Verbatim\nLine two.')
