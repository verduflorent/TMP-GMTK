from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from catalogue.models import MobProfile
from .models import BestiaryMob, Encounter, EncounterMob, GameTable, TableInstance
from .services import save_validated

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="florent", password="secret-pass")

    def test_private_home_requires_authentication(self):
        response = self.client.get(reverse("table"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('table')}")

    def test_login_creates_private_game_table(self):
        self.client.login(username="florent", password="secret-pass")
        response = self.client.get(reverse("table"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(GameTable.objects.filter(owner=self.user).exists())


class DomainIntegrityTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pwd")
        self.bob = User.objects.create_user(username="bob", password="pwd")
        self.alice_table = GameTable.objects.create(owner=self.alice)

    def test_encounter_mob_cannot_use_other_users_bestiary_source(self):
        source = BestiaryMob.objects.create(
            owner=self.bob, name="Intrus", profile=MobProfile.COMBATANT, level=4
        )
        encounter = Encounter.objects.create(owner=self.alice, name="Parking")
        mob = EncounterMob(
            encounter=encounter,
            source=source,
            name="Intrus",
            profile=MobProfile.COMBATANT,
            level=4,
            current_hp=340,
            max_hp=340,
        )
        with self.assertRaises(ValidationError):
            save_validated(mob)

    def test_table_instance_cannot_use_other_users_encounter_mob(self):
        encounter = Encounter.objects.create(owner=self.bob, name="Intrusion")
        source = EncounterMob.objects.create(
            encounter=encounter,
            name="Intrus",
            profile=MobProfile.COMBATANT,
            level=4,
            current_hp=340,
            max_hp=340,
        )
        instance = TableInstance(
            game_table=self.alice_table,
            source=source,
            name="Intrus",
            profile=MobProfile.COMBATANT,
            level=4,
            current_hp=340,
            max_hp=340,
        )
        with self.assertRaises(ValidationError):
            save_validated(instance)
