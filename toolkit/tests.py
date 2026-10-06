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
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)

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
            {"index": 0, "action": "replace", "weapon_index": 0, "weapon_id": replacement.id},
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
            {"index": 0, "action": "replace", "weapon_index": 0, "weapon_id": override.id},
        )
        self.assertEqual(
            self.client.session["monster_builder_mobs"][0]["weapon_ids"][0],
            override.id,
        )

    def test_weapon_groups_are_family_then_tier_sorted(self):
        response = self.client.get(reverse("monster_builder"))
        groups = response.context["weapon_groups"]
        self.assertEqual([name for name, _ in groups][:3], ["Commun", "Combattant", "Assassin"])
        for _name, weapons in groups:
            keys = [(weapon.tier, weapon.name) for weapon in weapons]
            self.assertEqual(keys, sorted(keys))


    def test_generated_draft_uses_equipment_lists(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        draft = self.client.session["monster_builder_mobs"][0]
        self.assertIsInstance(draft["weapon_ids"], list)
        self.assertIsInstance(draft["implant_ids"], list)
        self.assertEqual(draft["abilities"], [])
        self.assertEqual(draft["overrides"], {})


    def test_manual_perception_override_recalculates_weapon_aim(self):
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
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        response = self.client.post(
            reverse("monster_builder_field"),
            {"index": 0, "field": "armor", "value": 35},
            follow=True,
        )
        mob = response.context["generated_mobs"][0]
        self.assertEqual(mob["armor"], 35)


    def test_builder_renders_compact_view_and_opt_in_edit_controls(self):
        response = self.client.post(
            reverse("monster_builder"),
            {"action": "generate", "quantity": 1, "level": 5},
        )
        self.assertContains(response, "✎ Modifier")
        self.assertContains(response, 'class="edit-only')
        self.assertContains(response, 'class="view-only')


    def test_edit_layer_css_strictly_hides_inactive_controls(self):
        response = self.client.get(reverse("monster_builder"))
        self.assertContains(
            response,
            ".mob-card:not(.is-editing) .edit-only { display: none !important; }",
        )
        self.assertContains(
            response,
            ".mob-card.is-editing .view-only { display: none !important; }",
        )


    def test_manual_weapon_addition_supports_three_weapons(self):
        from django.core.management import call_command
        from catalogue.models import MobWeapon

        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        weapons = list(MobWeapon.objects.all())
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["weapon_ids"] = [weapons[0].id, weapons[1].id]
        session["monster_builder_mobs"] = [draft]
        session.save()

        response = self.client.post(
            reverse("monster_builder_weapon"),
            {"index": 0, "action": "add", "weapon_id": weapons[2].id},
            follow=True,
        )
        self.assertEqual(len(self.client.session["monster_builder_mobs"][0]["weapon_ids"]), 3)
        self.assertEqual(len(response.context["generated_mobs"][0]["weapon_cards"]), 3)

    def test_manual_weapon_removal_removes_selected_list_item(self):
        from django.core.management import call_command
        from catalogue.models import MobWeapon

        call_command("seed_monster_catalogue", verbosity=0)
        weapons = list(MobWeapon.objects.all())
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["weapon_ids"] = [weapons[0].id, weapons[1].id, weapons[2].id]
        session["monster_builder_mobs"] = [draft]
        session.save()

        self.client.post(
            reverse("monster_builder_weapon"),
            {"index": 0, "action": "remove", "weapon_index": 1},
        )
        self.assertEqual(
            self.client.session["monster_builder_mobs"][0]["weapon_ids"],
            [weapons[0].id, weapons[2].id],
        )


    def test_manual_implant_addition_is_unrestricted_and_recalculates_card(self):
        from django.core.management import call_command
        from catalogue.models import MobImplant

        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 10})
        draft = self.client.session["monster_builder_mobs"][0]
        profile = draft["profile"]
        override = next(
            implant for implant in MobImplant.objects.all()
            if not implant.supports_profile(profile)
        )
        response = self.client.post(
            reverse("monster_builder_implant"),
            {"index": 0, "action": "add", "implant_id": override.id},
            follow=True,
        )
        self.assertIn(override.id, self.client.session["monster_builder_mobs"][0]["implant_ids"])
        self.assertTrue(any(card.implant.id == override.id for card in response.context["generated_mobs"][0]["implant_cards"]))

    def test_manual_implant_remove_can_leave_zero_implants(self):
        from django.core.management import call_command
        from catalogue.models import MobImplant

        call_command("seed_monster_catalogue", verbosity=0)
        implant = MobImplant.objects.first()
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["implant_ids"] = [implant.id]
        session["monster_builder_mobs"] = [draft]
        session.save()

        response = self.client.post(
            reverse("monster_builder_implant"),
            {"index": 0, "action": "remove", "implant_index": 0},
            follow=True,
        )
        self.assertEqual(self.client.session["monster_builder_mobs"][0]["implant_ids"], [])
        self.assertEqual(response.context["generated_mobs"][0]["implant_cards"], [])

    def test_manual_implant_list_can_exceed_randomizer_slot_limit(self):
        from django.core.management import call_command
        from catalogue.models import MobImplant

        call_command("seed_monster_catalogue", verbosity=0)
        implants = list(MobImplant.objects.all()[:4])
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 1})
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["implant_ids"] = []
        session["monster_builder_mobs"] = [draft]
        session.save()

        for implant in implants:
            self.client.post(
                reverse("monster_builder_implant"),
                {"index": 0, "action": "add", "implant_id": implant.id},
            )
        self.assertEqual(len(self.client.session["monster_builder_mobs"][0]["implant_ids"]), 4)


    def test_edit_mode_survives_field_post_redirect(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 2, "level": 5})
        response = self.client.post(
            reverse("monster_builder_field"),
            {"index": 1, "field": "armor", "value": 35},
            follow=True,
        )
        self.assertEqual(response.context["editing_index"], 1)
        self.assertContains(response, "mob-card is-editing", count=1)


    def test_custom_ability_fixed_effect_is_rendered(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 10})
        response = self.client.post(
            reverse("monster_builder_ability"),
            {
                "index": 0, "action": "add", "name": "Tension",
                "description": "Les cibles à distance sont renforcées.",
                "effect_type": "damage_distance", "scaling": "fixed", "value": 35,
            },
            follow=True,
        )
        ability = response.context["generated_mobs"][0]["abilities"][0]
        self.assertEqual(ability["name"], "Tension")
        self.assertEqual(ability["resolved_effect"]["value"], 35)
        self.assertContains(response, "Tension")
        self.assertContains(response, "Dégâts Distance")

    def test_custom_ability_level_effect_scales_with_mob_level(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 10})
        response = self.client.post(
            reverse("monster_builder_ability"),
            {
                "index": 0, "action": "add", "name": "Tension",
                "effect_type": "damage_distance", "scaling": "level", "value": 5,
            },
            follow=True,
        )
        self.assertEqual(
            response.context["generated_mobs"][0]["abilities"][0]["resolved_effect"]["value"],
            50,
        )

    def test_custom_ability_can_be_removed(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(
            reverse("monster_builder_ability"),
            {"index": 0, "action": "add", "name": "Test", "effect_type": "", "scaling": "", "value": ""},
        )
        response = self.client.post(
            reverse("monster_builder_ability"),
            {"index": 0, "action": "remove", "ability_index": 0},
            follow=True,
        )
        self.assertEqual(response.context["generated_mobs"][0]["abilities"], [])


    def test_custom_aim_effect_applies_live_before_validation(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 10})
        before = self.client.get(reverse("monster_builder")).context["generated_mobs"][0]["weapon_cards"][0].effective_aim
        response = self.client.post(
            reverse("monster_builder_ability"),
            {"index": 0, "action": "add", "name": "Thor", "effect_type": "aim", "scaling": "fixed", "value": 5},
            follow=True,
        )
        mob = response.context["generated_mobs"][0]
        self.assertEqual(mob["weapon_cards"][0].effective_aim, before + 5)

    def test_custom_distance_damage_effect_applies_live_and_scales(self):
        from django.core.management import call_command
        from catalogue.models import MobWeapon

        call_command("seed_monster_catalogue", verbosity=0)
        pistol = MobWeapon.objects.get(name="Pistolet")
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 10})
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["weapon_ids"] = [pistol.id]
        session["monster_builder_mobs"] = [draft]
        session.save()
        before = self.client.get(reverse("monster_builder")).context["generated_mobs"][0]["weapon_cards"][0].neutral_damage
        response = self.client.post(
            reverse("monster_builder_ability"),
            {"index": 0, "action": "add", "name": "Tension", "effect_type": "damage_distance", "scaling": "level", "value": 5},
            follow=True,
        )
        self.assertEqual(response.context["generated_mobs"][0]["weapon_cards"][0].neutral_damage, before + 50)


class BuilderValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user(username="validator", password="pwd")
        self.client.login(username="validator", password="pwd")

    def test_validate_one_moves_only_selected_draft_to_table(self):
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 3, "level": 5})
        response = self.client.post(
            reverse("monster_builder_validate"),
            {"action": "one", "index": 1},
            follow=True,
        )
        self.assertEqual(TableMob.objects.filter(game_table__owner=self.user).count(), 1)
        self.assertEqual(len(self.client.session["monster_builder_mobs"]), 2)
        self.assertEqual(len(response.context["generated_mobs"]), 2)

    def test_validate_all_moves_every_draft_to_table(self):
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 3, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        self.assertEqual(TableMob.objects.filter(game_table__owner=self.user).count(), 3)
        self.assertEqual(self.client.session["monster_builder_mobs"], [])

    def test_table_mob_can_return_to_builder_for_editing(self):
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        table_mob = TableMob.objects.get(game_table__owner=self.user)

        response = self.client.post(reverse("table_mob_edit", args=[table_mob.id]), follow=True)
        self.assertFalse(TableMob.objects.filter(id=table_mob.id).exists())
        self.assertEqual(len(self.client.session["monster_builder_mobs"]), 1)
        self.assertEqual(response.context["editing_index"], 0)


    def test_table_mob_can_be_deleted_without_returning_to_builder(self):
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        table_mob = TableMob.objects.get(game_table__owner=self.user)

        response = self.client.post(reverse("table_mob_delete", args=[table_mob.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TableMob.objects.filter(id=table_mob.id).exists())
        self.assertEqual(self.client.session.get("monster_builder_mobs", []), [])
