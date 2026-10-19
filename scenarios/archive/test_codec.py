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

    def test_unknown_encounter_reference_rejected(self):
        document = copy.deepcopy(self.document)
        encounter = next(b for b in document["blocks"] if b["kind"] == "encounter")
        encounter["payload"]["resource_key"] = "missing"
        with self.assertRaises(ArchiveError):
            encode_archive(document, document_id=DOC_ID)

    def test_unknown_payload_key_rejected(self):
        document = copy.deepcopy(self.document)
        document["blocks"][0]["payload"]["unexpected"] = True
        with self.assertRaises(ArchiveError):
            encode_archive(document, document_id=DOC_ID)

    def test_excessive_json_depth_rejected(self):
        document = copy.deepcopy(self.document)
        deep = {}
        node = deep
        for _ in range(45):
            node["nested"] = {}
            node = node["nested"]
        document["blocks"][0]["payload"] = deep
        with self.assertRaises(ArchiveError):
            encode_archive(document, document_id=DOC_ID)

    def test_duplicate_zip_entry_rejected(self):
        import io
        import zipfile
        import warnings
        raw = encode_archive(self.document, document_id=DOC_ID)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            manifest = archive.read("manifest.json")
            document = archive.read("scenario.json")
        stream = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(stream, "w") as archive:
                archive.writestr("manifest.json", manifest)
                archive.writestr("scenario.json", document)
                archive.writestr("scenario.json", document)
        with self.assertRaises(ArchiveError):
            decode_archive(stream.getvalue())

    def test_zip_path_traversal_rejected(self):
        import io
        import zipfile
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("manifest.json", b"{}")
            archive.writestr("../scenario.json", b"{}")
        with self.assertRaises(ArchiveError):
            decode_archive(stream.getvalue())

    def test_zip_symlink_rejected(self):
        import io
        import zipfile
        raw = encode_archive(self.document, document_id=DOC_ID)
        with zipfile.ZipFile(io.BytesIO(raw)) as source:
            manifest = source.read("manifest.json")
            document = source.read("scenario.json")
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            link = zipfile.ZipInfo("scenario.json")
            link.create_system = 3
            link.external_attr = (0o120777 << 16)
            archive.writestr("manifest.json", manifest)
            archive.writestr(link, document)
        with self.assertRaises(ArchiveError):
            decode_archive(stream.getvalue())

    def test_zip_oversized_decompressed_member_rejected(self):
        import io
        import zipfile
        from .codec import MAX_UNCOMPRESSED
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", b"{}")
            archive.writestr("scenario.json", b"x" * (MAX_UNCOMPRESSED + 1))
        with self.assertRaises(ArchiveError):
            decode_archive(stream.getvalue())

    def test_corrupt_json_rejected(self):
        import io
        import zipfile
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("manifest.json", b'{"format": "tmps", "format": "tmps"}')
            archive.writestr("scenario.json", b"not json")
        with self.assertRaises(ArchiveError):
            decode_archive(stream.getvalue())
