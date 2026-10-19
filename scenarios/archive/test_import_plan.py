import json
from pathlib import Path
from django.test import SimpleTestCase
from .codec import encode_archive, decode_archive
from .import_plan import plan_import

FIXTURE = Path(__file__).parent / "fixtures" / "reference_v1.json"
DOC_ID = "00000000-0000-4000-8000-000000009999"


class ImportPlanTests(SimpleTestCase):
    def test_remaps_all_identities_and_transitions(self):
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        manifest, decoded = decode_archive(encode_archive(document, document_id=DOC_ID))
        original = json.dumps(decoded, sort_keys=True)
        plan = plan_import(manifest, decoded)
        scene_ids = {s["id"] for s in plan["scenes"]}
        self.assertEqual(len(scene_ids), len(decoded["scenes"]))
        self.assertFalse(scene_ids.intersection(s["id"] for s in decoded["scenes"]))
        self.assertFalse({b["id"] for b in plan["blocks"]}.intersection(b["id"] for b in decoded["blocks"]))
        self.assertTrue(all(b["target_scene_id"] in scene_ids for b in plan["blocks"] if b["kind"] == "transition"))
        self.assertEqual(len(plan["unresolved_encounters"]), 1)
        self.assertEqual(json.dumps(decoded, sort_keys=True), original)

    def test_separate_plans_get_distinct_ids(self):
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        manifest, decoded = decode_archive(encode_archive(document, document_id=DOC_ID))
        first = plan_import(manifest, decoded)
        second = plan_import(manifest, decoded)
        self.assertNotEqual(first["scenes"][0]["id"], second["scenes"][0]["id"])
