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

    def test_cannot_attach_another_users_folder(self):
        self.client.force_login(self.alice)
        response = self.client.post(reverse("scenarios:library"), {"title": "Intrusion", "folder": str(self.bob_folder.pk)})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Scenario.objects.filter(title="Intrusion").exists())

    def test_get_does_not_create(self):
        self.client.force_login(self.alice)
        self.client.get(reverse("scenarios:library"))
        self.assertEqual(Scenario.objects.count(), 1)
