from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from catalogue.models import CatalogueEntry, EquipmentDefinition
from .models import (
    CharacterProfile,
    CharacterVersion,
    Encounter,
    EncounterEntry,
    EquipmentAssignment,
    Folder,
    GameTable,
    TableInstance,
)
from .services import save_validated

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="florent", password="secret-pass")

    def test_private_home_requires_authentication(self):
        response = self.client.get(reverse("table"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('table')}")

    def test_login_creates_and_displays_private_game_table(self):
        self.client.login(username="florent", password="secret-pass")
        response = self.client.get(reverse("table"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(GameTable.objects.filter(owner=self.user).exists())
        self.assertContains(response, "Table de jeu")


class DomainIntegrityTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pwd")
        self.bob = User.objects.create_user(username="bob", password="pwd")
        self.alice_table = GameTable.objects.create(owner=self.alice)
        self.bob_table = GameTable.objects.create(owner=self.bob)

    def create_version(self, owner, name="Garde"):
        profile = CharacterProfile.objects.create(
            owner=owner,
            name=name,
            character_type=CharacterProfile.CharacterType.NPC,
            mode=CharacterProfile.Mode.STANDARD,
        )
        return CharacterVersion.objects.create(profile=profile, level=4, is_validated=True)

    def test_profile_level_is_unique(self):
        version = self.create_version(self.alice)
        duplicate = CharacterVersion(profile=version.profile, level=version.level)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_standard_profile_can_have_single_version(self):
        version = self.create_version(self.alice)
        self.assertEqual(version.profile.versions.count(), 1)
        self.assertEqual(version.level, 4)

    def test_encounter_cannot_reference_other_users_version(self):
        bob_version = self.create_version(self.bob, "Intrus")
        encounter = Encounter.objects.create(owner=self.alice, name="Parking")
        entry = EncounterEntry(encounter=encounter, character_version=bob_version)
        with self.assertRaises(ValidationError):
            save_validated(entry)

    def test_table_instance_cannot_reference_other_users_version(self):
        bob_version = self.create_version(self.bob, "Intrus")
        instance = TableInstance(
            game_table=self.alice_table,
            source_version=bob_version,
            name="Intrus",
            character_type=CharacterProfile.CharacterType.NPC,
        )
        with self.assertRaises(ValidationError):
            save_validated(instance)

    def test_equipment_assignment_belongs_to_same_user(self):
        alice_version = self.create_version(self.alice)
        definition = EquipmentDefinition.objects.create(owner=self.bob, kind=EquipmentDefinition.Kind.WEAPON, name="Custom", is_native_reference=False)
        entry = CatalogueEntry(owner=self.bob, local_definition=definition)
        save_validated(entry)
        assignment = EquipmentAssignment(version=alice_version, catalogue_entry=entry, slot="MAIN")
        with self.assertRaises(ValidationError):
            save_validated(assignment)

    def test_live_version_reference_protects_deletion(self):
        version = self.create_version(self.alice)
        encounter = Encounter.objects.create(owner=self.alice, name="Parking")
        EncounterEntry.objects.create(encounter=encounter, character_version=version)
        with self.assertRaises(ProtectedError):
            version.delete()

    def test_live_catalogue_reference_protects_deletion(self):
        version = self.create_version(self.alice)
        definition = EquipmentDefinition.objects.create(owner=self.alice, kind=EquipmentDefinition.Kind.WEAPON, name="Custom", is_native_reference=False)
        entry = CatalogueEntry(owner=self.alice, local_definition=definition)
        save_validated(entry)
        EquipmentAssignment.objects.create(version=version, catalogue_entry=entry, slot="MAIN")
        with self.assertRaises(ProtectedError):
            entry.delete()

    def test_folder_rejects_cross_owner_parent(self):
        alice_root = Folder.objects.create(owner=self.alice, domain=Folder.Domain.BESTIARY, name="A")
        child = Folder(owner=self.bob, domain=Folder.Domain.BESTIARY, name="B", parent=alice_root)
        with self.assertRaises(ValidationError):
            save_validated(child)
