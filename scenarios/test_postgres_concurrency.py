"""PostgreSQL-only concurrency checks for the scenario editor.

Use a dedicated disposable PostgreSQL TEST database. Never point DATABASE_URL at
production. SQLite tests skip because select_for_update behaves differently.
"""
import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, close_old_connections
from django.test import Client, TransactionTestCase
from django.urls import reverse

from .archive.codec import encode_archive
from .models import Scenario, Scene, ScenarioImportReceipt


class PostgreSQLConcurrencyTests(TransactionTestCase):
    def setUp(self):
        if connection.vendor != "postgresql":
            self.skipTest("Nécessite PostgreSQL ; SQLite ne valide pas les verrous.")
        self.user = get_user_model().objects.create_user(
            username="pg_scenario_concurrency", password="test-password-123"
        )

    def _parallel(self, work):
        barrier = threading.Barrier(2, timeout=15)
        def worker(index):
            close_old_connections()
            try:
                client = Client()
                client.force_login(self.user)
                barrier.wait()
                return work(client, index)
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker, i) for i in range(2)]
            return [f.result(timeout=30) for f in futures]

    def test_simultaneous_document_saves_only_one_wins(self):
        scenario = Scenario.objects.create(owner=self.user, title="Concurrent")
        scene = Scene.objects.create(scenario=scenario, title="Before")
        url = reverse("scenarios:document", args=[scenario.pk])
        def work(client, index):
            payload = {
                "mode": "content", "content_revision": 0, "layout_revision": 0,
                "scenes": [{"id": str(scene.pk), "title": "Writer " + str(index),
                            "position": {"x": 0, "y": 0}, "blocks": []}],
            }
            return client.post(url, data=json.dumps(payload), content_type="application/json").status_code
        statuses = sorted(self._parallel(work))
        self.assertEqual(statuses, [200, 409])
        scenario.refresh_from_db()
        self.assertEqual(scenario.content_revision, 1)
        self.assertIn(Scene.objects.get(pk=scene.pk).title, ("Writer 0", "Writer 1"))

    def test_simultaneous_import_same_key_creates_one_copy(self):
        doc = {
            "schema_version": "1.0",
            "metadata": {"title": "Concurrent import", "summary": ""},
            "scenes": [], "blocks": [],
            "resources": {"media": [], "encounters": []},
        }
        archive = encode_archive(doc, document_id=str(uuid.uuid4()))
        key = str(uuid.uuid4())
        url = reverse("scenarios:import")
        def work(client, index):
            response = client.post(url, {
                "import_key": key,
                "archive": SimpleUploadedFile("test.tmps", archive),
            })
            return response.status_code, response.json()
        results = self._parallel(work)
        self.assertEqual(sorted(status for status, _ in results), [200, 201])
        self.assertEqual(results[0][1]["scenario_id"], results[1][1]["scenario_id"])
        self.assertEqual(Scenario.objects.filter(owner=self.user).count(), 1)
        self.assertEqual(ScenarioImportReceipt.objects.filter(owner=self.user, key=key).count(), 1)
