from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from toolkit.models import UserFolder
from .models import Scenario


class ScenarioLibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.alice = User.objects.create_user(username="alice_scenario", password="test-password-123")
        cls.bob = User.objects.create_user(username="bob_scenario", password="test-password-123")
        cls.alice_folder = UserFolder.objects.create(owner=cls.alice, name="E1")
        cls.bob_folder = UserFolder.objects.create(owner=cls.bob, name="Privé")
        cls.bob_scenario = Scenario.objects.create(owner=cls.bob, title="Secret")

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("scenarios:library"))
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_read_other_users_scenario(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("scenarios:detail", args=[self.bob_scenario.pk]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("scenarios:library"))
        self.assertNotContains(response, "Secret")

    def test_create_scenario_for_authenticated_user(self):
        self.client.force_login(self.alice)
        response = self.client.post(reverse("scenarios:library"), {"title": "Épisode 3", "summary": "Essai", "folder": ""})
        self.assertEqual(response.status_code, 302)
        scenario = Scenario.objects.get(title="Épisode 3")
        self.assertEqual(scenario.owner, self.alice)
        self.assertEqual(response.url, reverse("scenarios:detail", args=[scenario.pk]))

    def test_create_scenario_in_own_folder(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            reverse("scenarios:library"),
            {"title": "Épisode 0", "summary": "", "folder": str(self.alice_folder.pk)},
        )
        self.assertEqual(response.status_code, 302)
        scenario = Scenario.objects.get(title="Épisode 0")
        self.assertEqual(scenario.owner, self.alice)
        self.assertEqual(scenario.folder, self.alice_folder)

    def test_cannot_attach_another_users_folder(self):
        self.client.force_login(self.alice)
        response = self.client.post(reverse("scenarios:library"), {"title": "Intrusion", "folder": str(self.bob_folder.pk)})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Scenario.objects.filter(title="Intrusion").exists())

    def test_get_does_not_create(self):
        self.client.force_login(self.alice)
        self.client.get(reverse("scenarios:library"))
        self.assertEqual(Scenario.objects.count(), 1)

    def test_document_roundtrip_and_revision_conflict(self):
        import json
        import uuid
        from .models import Scene, SceneBlock
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Épisode 0")
        a, b = str(uuid.uuid4()), str(uuid.uuid4())
        payload = {
            "content_revision": 0, "layout_revision": 0,
            "scenes": [
                {"id": a, "title": "Entrée", "position": {"x": 10, "y": 20}, "blocks": [
                    {"kind": "narration", "text": "Bienvenue", "target": None},
                    {"kind": "transition", "text": "Continuer", "target": b},
                ]},
                {"id": b, "title": "Bureau", "position": {"x": 80, "y": 100}, "blocks": []},
            ],
        }
        url = reverse("scenarios:document", args=[scenario.pk])
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(Scene.objects.filter(scenario=scenario).count(), 2)
        self.assertEqual(SceneBlock.objects.filter(scene__scenario=scenario).count(), 2)
        response = self.client.get(url)
        self.assertEqual(response.json()["scenes"][0]["blocks"][1]["target"], b)
        self.assertEqual(self.client.post(url, data=json.dumps(payload), content_type="application/json").status_code, 409)
        self.assertEqual(Scene.objects.filter(scenario=scenario).count(), 2)

    def test_document_rejects_other_owner_and_invalid_target(self):
        import json
        import uuid
        from .models import Scene
        self.client.force_login(self.alice)
        foreign = reverse("scenarios:document", args=[self.bob_scenario.pk])
        self.assertEqual(self.client.get(foreign).status_code, 404)
        self.assertEqual(self.client.post(foreign, data="{}", content_type="application/json").status_code, 404)
        own = Scenario.objects.create(owner=self.alice, title="Épisode 0")
        url = reverse("scenarios:document", args=[own.pk])
        payload = {"content_revision": 0, "layout_revision": 0, "scenes": [
            {"id": str(uuid.uuid4()), "title": "Départ", "position": {"x": 0, "y": 0},
             "blocks": [{"kind": "transition", "text": "Vers ailleurs", "target": str(uuid.uuid4())}]}
        ]}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Scene.objects.filter(scenario=own).exists())

    def test_repeated_save_preserves_scene_and_block_ids(self):
        import json
        import uuid
        from .models import Scene, SceneBlock
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Stable")
        scene_id = str(uuid.uuid4())
        block_id = str(uuid.uuid4())
        url = reverse("scenarios:document", args=[scenario.pk])
        payload = {
            "content_revision": 0, "layout_revision": 0,
            "scenes": [{
                "id": scene_id, "title": "Début", "position": {"x": 5, "y": 8},
                "blocks": [{"id": block_id, "kind": "narration", "text": "Version 1", "target": None}],
            }],
        }
        first = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(first.status_code, 200, first.content)
        payload["content_revision"] = 1
        payload["layout_revision"] = 1
        payload["scenes"][0]["blocks"][0]["text"] = "Version 2"
        second = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(Scene.objects.filter(scenario=scenario).count(), 1)
        self.assertEqual(SceneBlock.objects.filter(scene__scenario=scenario).count(), 1)
        self.assertEqual(str(SceneBlock.objects.get(scene__scenario=scenario).pk), block_id)
        self.assertEqual(SceneBlock.objects.get(pk=block_id).text, "Version 2")
        self.assertEqual(self.client.get(url).json()["scenes"][0]["blocks"][0]["id"], block_id)

    def test_invalid_update_does_not_erase_existing_scene(self):
        import json
        import uuid
        from .models import Scene
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Stable")
        scene = Scene.objects.create(scenario=scenario, title="À préserver")
        url = reverse("scenarios:document", args=[scenario.pk])
        payload = {"content_revision": 0, "layout_revision": 0, "scenes": [
            {"id": str(scene.pk), "title": "Erreur", "position": {"x": 0, "y": 0},
             "blocks": [{"kind": "transition", "target": str(uuid.uuid4())}]}
        ]}
        result = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(result.status_code, 400)
        scene.refresh_from_db()
        self.assertEqual(scene.title, "À préserver")

    def test_layout_save_preserves_narration_and_content_revision(self):
        import json
        from .models import Scene, SceneBlock
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Disposition")
        scene = Scene.objects.create(scenario=scenario, title="Début")
        block = SceneBlock.objects.create(scene=scene, kind="narration", text="Texte précieux")
        url = reverse("scenarios:layout", args=[scenario.pk])
        payload = {"layout_revision": 0, "positions": [{"id": str(scene.pk), "x": 45, "y": -20}]}
        result = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(result.status_code, 200, result.content)
        scenario.refresh_from_db()
        scene.refresh_from_db()
        block.refresh_from_db()
        self.assertEqual(scenario.content_revision, 0)
        self.assertEqual(scenario.layout_revision, 1)
        self.assertEqual((scene.x, scene.y), (45, -20))
        self.assertEqual(block.text, "Texte précieux")
        self.assertEqual(self.client.post(url, json.dumps(payload), content_type="application/json").status_code, 409)

    def test_layout_rejects_foreign_scene_without_partial_update(self):
        import json
        from .models import Scene
        self.client.force_login(self.alice)
        own = Scenario.objects.create(owner=self.alice, title="Disposition")
        own_scene = Scene.objects.create(scenario=own, title="Propre")
        foreign_scene = Scene.objects.create(scenario=self.bob_scenario, title="Privée")
        payload = {"layout_revision": 0, "positions": [
            {"id": str(own_scene.pk), "x": 80, "y": 90},
            {"id": str(foreign_scene.pk), "x": 10, "y": 20},
        ]}
        result = self.client.post(reverse("scenarios:layout", args=[own.pk]),
                                  json.dumps(payload), content_type="application/json")
        self.assertEqual(result.status_code, 400)
        own_scene.refresh_from_db()
        self.assertEqual((own_scene.x, own_scene.y), (0, 0))

    def test_content_only_does_not_revert_concurrent_layout(self):
        import json
        from .models import Scene, SceneBlock
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Séparation")
        scene = Scene.objects.create(scenario=scenario, title="Début")
        block = SceneBlock.objects.create(scene=scene, kind="narration", text="Ancien")
        layout_url = reverse("scenarios:layout", args=[scenario.pk])
        doc_url = reverse("scenarios:document", args=[scenario.pk])
        move = {"layout_revision": 0, "positions": [{"id": str(scene.pk), "x": 300, "y": 400}]}
        self.assertEqual(self.client.post(layout_url, json.dumps(move), content_type="application/json").status_code, 200)
        content = {"mode": "content", "content_revision": 0, "layout_revision": 0, "scenes": [
            {"id": str(scene.pk), "title": "Début modifié", "position": {"x": 0, "y": 0},
             "blocks": [{"id": str(block.pk), "kind": "narration", "text": "Nouveau", "target": None}]}
        ]}
        response = self.client.post(doc_url, json.dumps(content), content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        scenario.refresh_from_db()
        scene.refresh_from_db()
        block.refresh_from_db()
        self.assertEqual((scenario.content_revision, scenario.layout_revision), (1, 1))
        self.assertEqual((scene.x, scene.y), (300, 400))
        self.assertEqual(block.text, "Nouveau")

    def test_content_only_structural_change_checks_layout_revision(self):
        import json
        import uuid
        from .models import Scene
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Structure")
        scene = Scene.objects.create(scenario=scenario, title="Début")
        layout_url = reverse("scenarios:layout", args=[scenario.pk])
        self.client.post(layout_url, json.dumps({"layout_revision": 0, "positions": [
            {"id": str(scene.pk), "x": 2, "y": 3}]}), content_type="application/json")
        doc_url = reverse("scenarios:document", args=[scenario.pk])
        content = {"mode": "content", "content_revision": 0, "layout_revision": 0, "scenes": [
            {"id": str(scene.pk), "title": "Début", "position": {"x": 0, "y": 0}, "blocks": []},
            {"id": str(uuid.uuid4()), "title": "Ajout", "position": {"x": 4, "y": 5}, "blocks": []}
        ]}
        self.assertEqual(self.client.post(doc_url, json.dumps(content), content_type="application/json").status_code, 409)
        self.assertEqual(Scene.objects.filter(scenario=scenario).count(), 1)

    def test_encounter_reference_roundtrip_and_foreign_rejection(self):
        import json
        from .models import SceneBlock
        from toolkit.models import Encounter
        self.client.force_login(self.alice)
        own = Scenario.objects.create(owner=self.alice, title="Scénario lié")
        scene = own.scenes.create(title="Combat")
        encounter = Encounter.objects.create(owner=self.alice, name="Escarmouche")
        foreign = Encounter.objects.create(owner=self.bob, name="Secret combat")
        url = reverse("scenarios:document", args=[own.pk])
        base = {"mode": "content", "content_revision": 0, "layout_revision": 0,
                "scenes": [{"id": str(scene.pk), "title": "Combat",
                            "position": {"x": 0, "y": 0}, "blocks": [
                                {"kind": "encounter", "text": "Déclencheur",
                                 "payload": {"encounter_id": encounter.pk}}]}]}
        response = self.client.post(url, json.dumps(base), content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.client.get(url).json()["scenes"][0]["blocks"][0]["payload"],
                         {"encounter_id": encounter.pk})
        base["content_revision"] = 1
        base["scenes"][0]["blocks"][0]["payload"] = {"encounter_id": foreign.pk}
        denied = self.client.post(url, json.dumps(base), content_type="application/json")
        self.assertEqual(denied.status_code, 400)
        self.assertEqual(SceneBlock.objects.get(scene=scene).payload["encounter_id"], encounter.pk)

    def test_encounter_options_are_private(self):
        from toolkit.models import Encounter
        Encounter.objects.create(owner=self.alice, name="Escarmouche")
        Encounter.objects.create(owner=self.bob, name="Secret combat")
        own = Scenario.objects.create(owner=self.alice, title="Mes combats")
        self.client.force_login(self.alice)
        response = self.client.get(reverse("scenarios:detail", args=[own.pk]))
        self.assertContains(response, "Escarmouche")
        self.assertNotContains(response, "Secret combat")

    def test_cannot_reuse_foreign_block_uuid(self):
        import json
        from .models import Scene, SceneBlock
        self.client.force_login(self.alice)
        own = Scenario.objects.create(owner=self.alice, title="A")
        own_scene = Scene.objects.create(scenario=own, title="A1")
        foreign_scene = Scene.objects.create(scenario=self.bob_scenario, title="B1")
        foreign_block = SceneBlock.objects.create(scene=foreign_scene, kind="narration", text="Secret")
        payload = {"mode": "content", "content_revision": 0, "layout_revision": 0, "scenes": [
            {"id": str(own_scene.pk), "title": "A1", "position": {"x": 0, "y": 0},
             "blocks": [{"id": str(foreign_block.pk), "kind": "narration", "text": "Vol", "target": None}]}
        ]}
        response = self.client.post(reverse("scenarios:document", args=[own.pk]),
                                    json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400, response.content)
        foreign_block.refresh_from_db()
        self.assertEqual(foreign_block.text, "Secret")
        self.assertEqual(own_scene.blocks.count(), 0)

    def test_cannot_move_existing_block_to_other_scene(self):
        import json
        from .models import Scene, SceneBlock
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="A")
        first = Scene.objects.create(scenario=scenario, title="A1")
        second = Scene.objects.create(scenario=scenario, title="A2")
        block = SceneBlock.objects.create(scene=first, kind="narration", text="Original")
        payload = {"mode": "content", "content_revision": 0, "layout_revision": 0, "scenes": [
            {"id": str(first.pk), "title": "A1", "position": {"x": 0, "y": 0}, "blocks": []},
            {"id": str(second.pk), "title": "A2", "position": {"x": 0, "y": 0},
             "blocks": [{"id": str(block.pk), "kind": "narration", "text": "Déplacé", "target": None}]},
        ]}
        response = self.client.post(reverse("scenarios:document", args=[scenario.pk]),
                                    json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400, response.content)
        block.refresh_from_db()
        self.assertEqual(block.scene_id, first.pk)
        self.assertEqual(block.text, "Original")

    def test_csrf_enforced_for_document_layout_and_library(self):
        import json
        from django.test import Client
        from .models import Scene
        scenario = Scenario.objects.create(owner=self.alice, title="CSRF")
        scene = Scene.objects.create(scenario=scenario, title="Avant")
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.alice)
        document_url = reverse("scenarios:document", args=[scenario.pk])
        layout_url = reverse("scenarios:layout", args=[scenario.pk])
        payload = {"mode": "content", "content_revision": 0, "layout_revision": 0,
                   "scenes": [{"id": str(scene.pk), "title": "Après",
                               "position": {"x": 0, "y": 0}, "blocks": []}]}
        self.assertEqual(client.post(document_url, json.dumps(payload),
                                     content_type="application/json").status_code, 403)
        self.assertEqual(client.post(layout_url, json.dumps({"layout_revision": 0, "positions": []}),
                                     content_type="application/json").status_code, 403)
        self.assertEqual(client.post(reverse("scenarios:library"), {"title": "Sans jeton"}).status_code, 403)
        scene.refresh_from_db()
        self.assertEqual(scene.title, "Avant")

    def test_revisions_reject_booleans_floats_negative_and_strings(self):
        import json
        from .models import Scene
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Révisions")
        scene = Scene.objects.create(scenario=scenario, title="Intacte")
        url = reverse("scenarios:document", args=[scenario.pk])
        base = {"mode": "content", "content_revision": 0, "layout_revision": 0,
                "scenes": [{"id": str(scene.pk), "title": "Modifiée",
                            "position": {"x": 0, "y": 0}, "blocks": []}]}
        for invalid in (True, -1, 0.5, "0", None):
            for field in ("content_revision", "layout_revision"):
                payload = dict(base)
                payload[field] = invalid
                response = self.client.post(url, json.dumps(payload), content_type="application/json")
                self.assertEqual(response.status_code, 400, (field, invalid, response.content))
        scene.refresh_from_db()
        self.assertEqual(scene.title, "Intacte")

    def test_document_and_layout_require_json_content_type(self):
        import json
        self.client.force_login(self.alice)
        scenario = Scenario.objects.create(owner=self.alice, title="Format")
        document_url = reverse("scenarios:document", args=[scenario.pk])
        layout_url = reverse("scenarios:layout", args=[scenario.pk])
        self.assertEqual(self.client.post(document_url, "{}", content_type="text/plain").status_code, 415)
        self.assertEqual(self.client.post(layout_url, "{}", content_type="text/plain").status_code, 415)
