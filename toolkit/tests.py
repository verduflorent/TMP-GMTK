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


class MonsterBuilderViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="builder", password="pwd")
        self.client.login(username="builder", password="pwd")

    def test_builder_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("monster_builder"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('monster_builder')}",
        )

    def test_builder_get_displays_generation_form(self):
        response = self.client.get(reverse("monster_builder"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monster Builder")
        self.assertContains(response, "Nombre de Mobs")
        self.assertContains(response, "Niveau")

    def test_builder_post_generates_requested_number_of_cards(self):
        from django.core.management import call_command

        call_command("seed_monster_catalogue", verbosity=0)
        response = self.client.post(
            reverse("monster_builder"),
            {"action": "generate", "quantity": 3, "level": 5},
        )
        self.assertEqual(response.status_code, 200)
        mobs = response.context["generated_mobs"]
        self.assertEqual(len(mobs), 3)
        self.assertTrue(all(mob["level"] == 5 for mob in mobs))
        self.assertTrue(
            all(mob["current_hp"] == mob["max_hp"] for mob in mobs)
        )

    def test_builder_rejects_invalid_quantity(self):
        response = self.client.post(
            reverse("monster_builder"),
            {"quantity": 0, "level": 5},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["generated_mobs"], [])
        self.assertContains(response, "Assurez-vous que cette valeur est supérieure ou égale à 1")


    def test_role_switch_rerolls_only_selected_mob_and_keeps_level(self):
        from django.core.management import call_command

        call_command("seed_monster_catalogue", verbosity=0)
        response = self.client.post(
            reverse("monster_builder"),
            {"action": "generate", "quantity": 3, "level": 5},
        )
        before = self.client.session["monster_builder_mobs"]
        untouched = [before[0].copy(), before[2].copy()]

        response = self.client.post(
            reverse("monster_builder_role"),
            {"index": 1, "profile": "S"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        after = self.client.session["monster_builder_mobs"]
        self.assertEqual(after[0], untouched[0])
        self.assertEqual(after[2], untouched[1])
        self.assertEqual(after[1]["profile"], "S")
        self.assertEqual(after[1]["level"], 5)
        self.assertEqual(len(response.context["generated_mobs"]), 3)


    def test_weapon_switch_changes_only_selected_mob_weapon(self):
        from django.core.management import call_command
        from catalogue.models import MobWeapon

        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(
            reverse("monster_builder"),
            {"action": "generate", "quantity": 3, "level": 5},
        )
        before = self.client.session["monster_builder_mobs"]
        untouched = [before[1].copy(), before[2].copy()]
        target = before[0]
        profile = target["profile"]
        replacement = next(
            weapon
            for weapon in MobWeapon.objects.all()
            if weapon.id != target["weapon_ids"][0] and weapon.supports_profile(profile)
        )

        response = self.client.post(
            reverse("monster_builder_weapon"),
            {"index": 0, "slot": "primary", "weapon_id": replacement.id},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        after = self.client.session["monster_builder_mobs"]
        self.assertEqual(after[1], untouched[0])
        self.assertEqual(after[2], untouched[1])
        self.assertEqual(after[0]["weapon_ids"][0], replacement.id)

    def test_weapon_switch_allows_mj_profile_override(self):
        from django.core.management import call_command
        from catalogue.models import MobWeapon

        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(
            reverse("monster_builder"),
            {"action": "generate", "quantity": 1, "level": 5},
        )
        saved = self.client.session["monster_builder_mobs"]
        profile = saved[0]["profile"]
        override = next(
            weapon for weapon in MobWeapon.objects.all()
            if not weapon.supports_profile(profile)
        )

        self.client.post(
            reverse("monster_builder_weapon"),
            {"index": 0, "slot": "primary", "weapon_id": override.id},
        )
        self.assertEqual(
            self.client.session["monster_builder_mobs"][0]["weapon_ids"][0],
            override.id,
        )

    def test_weapon_groups_are_family_then_tier_sorted(self):
        from django.core.management import call_command

        call_command("seed_monster_catalogue", verbosity=0)
        response = self.client.get(reverse("monster_builder"))
        groups = response.context["weapon_groups"]
        self.assertEqual([name for name, _ in groups][:3], ["Commun", "Combattant", "Assassin"])
        for _name, weapons in groups:
            keys = [(weapon.tier, weapon.name) for weapon in weapons]
            self.assertEqual(keys, sorted(keys))


    def test_generated_draft_uses_equipment_lists(self):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        draft = self.client.session["monster_builder_mobs"][0]
        self.assertIsInstance(draft["weapon_ids"], list)
        self.assertIsInstance(draft["implant_ids"], list)
        self.assertEqual(draft["abilities"], [])
        self.assertEqual(draft["overrides"], {})


    def test_manual_perception_override_recalculates_weapon_aim(self):
        from django.core.management import call_command

        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        response = self.client.post(
            reverse("monster_builder_field"),
            {"index": 0, "field": "perception", "value": 18},
            follow=True,
        )
        mob = response.context["generated_mobs"][0]
        self.assertEqual(mob["stats"].perception, 18)
        self.assertEqual(mob["stat_modifiers"]["perception"], 4)
        self.assertEqual(
            mob["weapon_cards"][0].effective_aim,
            mob["weapons"][0].aim + 4,
        )

    def test_manual_constitution_override_recalculates_hp_until_hp_is_overridden(self):
        from django.core.management import call_command
        from rules.engine import max_hp

        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        response = self.client.post(
            reverse("monster_builder_field"),
            {"index": 0, "field": "constitution", "value": 16},
            follow=True,
        )
        mob = response.context["generated_mobs"][0]
        self.assertEqual(mob["max_hp"], max_hp(5, 16))

        response = self.client.post(
            reverse("monster_builder_field"),
            {"index": 0, "field": "max_hp", "value": 999},
            follow=True,
        )
        self.assertEqual(response.context["generated_mobs"][0]["max_hp"], 999)

    def test_manual_armor_override_does_not_change_modifiers(self):
        from django.core.management import call_command

        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        response = self.client.post(
            reverse("monster_builder_field"),
            {"index": 0, "field": "armor", "value": 35},
            follow=True,
        )
        mob = response.context["generated_mobs"][0]
        self.assertEqual(mob["armor"], 35)
