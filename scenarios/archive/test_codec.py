import copy
import json
from pathlib import Path
from django.test import SimpleTestCase
from .codec import ArchiveError, decode_archive, encode_archive

FIXTURE = Path(__file__).parent / "fixtures" / "reference_v1.json"
DOC_ID = "00000000-0000-4000-8000-000000009999"


class ArchiveCodecTests(SimpleTestCase):
    def setUp(self):
        self.document = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_reference_roundtrip(self):
        raw = encode_archive(self.document, document_id=DOC_ID)
        manifest, restored = decode_archive(raw)
        self.assertEqual(manifest["format"], "tmps")
        self.assertEqual(restored, self.document)

    def test_missing_transition_target_is_rejected(self):
        document = copy.deepcopy(self.document)
        transition = next(b for b in document["blocks"] if b["kind"] == "transition")
        transition["target_scene_id"] = DOC_ID
        with self.assertRaises(ArchiveError):
            encode_archive(document, document_id=DOC_ID)

    def test_truncated_zip_rejected(self):
        raw = encode_archive(self.document, document_id=DOC_ID)
        with self.assertRaises(ArchiveError):
            decode_archive(raw[:50])

    def test_duplicate_scene_id_rejected(self):
        document = copy.deepcopy(self.document)
        document["scenes"].append(copy.deepcopy(document["scenes"][0]))
        with self.assertRaises(ArchiveError):
            encode_archive(document, document_id=DOC_ID)
