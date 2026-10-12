import importlib.util
import array
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('speechy1', Path(__file__).parents[1] / 'speechy1.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class CleanupTests(unittest.TestCase):
    def test_microphone_meter_tracks_signal_strength_and_silence(self):
        silence = array.array('h', [0] * 1600).tobytes()
        quiet = array.array('h', [1000, -1000] * 800).tobytes()
        loud = array.array('h', [10000, -10000] * 800).tobytes()
        self.assertEqual(s.microphone_level(silence), 0)
        self.assertGreater(s.microphone_level(loud), s.microphone_level(quiet))
        self.assertGreater(s.microphone_level(loud), 0.9)

    def test_processing_and_idle_clear_meter_without_text_payload(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s, 'RUNTIME', Path(tmp)), patch.object(s, 'VISUAL', {'phase': 'Idle', 'level': 0, 'screen': ''}):
            s.visual('Recording', level=0.8, screen='test-screen')
            self.assertEqual(json.loads((Path(tmp) / 'visual.json').read_text())['level'], 0.8)
            for phase in ('Cleaning', 'Idle'):
                s.visual(phase)
                payload = json.loads((Path(tmp) / 'visual.json').read_text())
                self.assertEqual(payload['level'], 0)
                self.assertEqual(set(payload), {'phase', 'level', 'screen', 'updated_ms'})

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
