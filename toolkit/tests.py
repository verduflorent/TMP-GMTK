from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from catalogue.models import MobProfile
from .models import BestiaryMob, Encounter, EncounterMob, GameTable, TableInstance, TableMob, UserAbility, UserWeapon, UserImplant
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
            if weapon.id != target["weapons"][0]["id"] and weapon.supports_profile(profile)
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
        self.assertEqual(after[0]["weapons"][0]["id"], replacement.id)

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
            self.client.session["monster_builder_mobs"][0]["weapons"][0]["id"],
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
        self.assertIsInstance(draft["weapons"], list)
        self.assertTrue(all("source" in ref and "id" in ref for ref in draft["weapons"]))
        self.assertIsInstance(draft["implants"], list)
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
        draft["weapons"] = [{"source": "catalogue", "id": weapons[0].id}, {"source": "catalogue", "id": weapons[1].id}]
        session["monster_builder_mobs"] = [draft]
        session.save()

        response = self.client.post(
            reverse("monster_builder_weapon"),
            {"index": 0, "action": "add", "weapon_id": weapons[2].id},
            follow=True,
        )
        self.assertEqual(len(self.client.session["monster_builder_mobs"][0]["weapons"]), 3)
        self.assertEqual(len(response.context["generated_mobs"][0]["weapon_cards"]), 3)

    def test_manual_weapon_removal_removes_selected_list_item(self):
        from django.core.management import call_command
        from catalogue.models import MobWeapon

        call_command("seed_monster_catalogue", verbosity=0)
        weapons = list(MobWeapon.objects.all())
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["weapons"] = [{"source": "catalogue", "id": weapons[0].id}, {"source": "catalogue", "id": weapons[1].id}, {"source": "catalogue", "id": weapons[2].id}]
        session["monster_builder_mobs"] = [draft]
        session.save()

        self.client.post(
            reverse("monster_builder_weapon"),
            {"index": 0, "action": "remove", "weapon_index": 1},
        )
        self.assertEqual(
            self.client.session["monster_builder_mobs"][0]["weapons"],
            [{"source": "catalogue", "id": weapons[0].id}, {"source": "catalogue", "id": weapons[2].id}],
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
        self.assertIn(
            {"source": "catalogue", "id": override.id},
            self.client.session["monster_builder_mobs"][0]["implants"],
        )
        self.assertTrue(any(card.implant.id == override.id for card in response.context["generated_mobs"][0]["implant_cards"]))

    def test_manual_implant_remove_can_leave_zero_implants(self):
        from django.core.management import call_command
        from catalogue.models import MobImplant

        call_command("seed_monster_catalogue", verbosity=0)
        implant = MobImplant.objects.first()
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["implants"] = [{"source": "catalogue", "id": implant.id}]
        session["monster_builder_mobs"] = [draft]
        session.save()

        response = self.client.post(
            reverse("monster_builder_implant"),
            {"index": 0, "action": "remove", "implant_index": 0},
            follow=True,
        )
        self.assertEqual(self.client.session["monster_builder_mobs"][0]["implants"], [])
        self.assertEqual(response.context["generated_mobs"][0]["implant_cards"], [])

    def test_manual_implant_list_can_exceed_randomizer_slot_limit(self):
        from django.core.management import call_command
        from catalogue.models import MobImplant

        call_command("seed_monster_catalogue", verbosity=0)
        implants = list(MobImplant.objects.all()[:4])
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 1})
        session = self.client.session
        draft = session["monster_builder_mobs"][0]
        draft["implants"] = []
        session["monster_builder_mobs"] = [draft]
        session.save()

        for implant in implants:
            self.client.post(
                reverse("monster_builder_implant"),
                {"index": 0, "action": "add", "implant_id": implant.id},
            )
        self.assertEqual(len(self.client.session["monster_builder_mobs"][0]["implants"]), 4)


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
        draft["weapons"] = [{"source": "catalogue", "id": pistol.id}]
        draft.pop("weapon_ids", None)
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


class BestiaryWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user(username="bestiary", password="pwd")
        self.client.login(username="bestiary", password="pwd")

    def test_builder_draft_can_be_saved_and_loaded_from_bestiary(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 10})
        original = self.client.session["monster_builder_mobs"][0]
        self.client.post(
            reverse("monster_builder_save"),
            {"index": 0, "name": "Tireur Kurogane"},
        )
        saved = BestiaryMob.objects.get(owner=self.user, name="Tireur Kurogane")
        expected = dict(original)
        expected["name"] = "Tireur Kurogane"
        self.assertEqual(saved.draft_payload, expected)

        session = self.client.session
        session["monster_builder_mobs"] = []
        session.save()
        response = self.client.post(reverse("bestiary_load", args=[saved.id]), follow=True)
        self.assertEqual(self.client.session["monster_builder_mobs"][0], expected)
        self.assertEqual(response.context["editing_index"], 0)

    def test_bestiary_is_private_per_user(self):
        other = User.objects.create_user(username="other", password="pwd")
        BestiaryMob.objects.create(
            owner=other, name="Secret", profile="C", level=1, draft_payload={"profile": "C", "level": 1}
        )
        response = self.client.get(reverse("bestiary"))
        self.assertNotContains(response, "Secret")

    def test_bestiary_mob_can_be_duplicated_and_deleted(self):
        mob = BestiaryMob.objects.create(
            owner=self.user, name="Ronin", profile="A", level=10,
            draft_payload={"profile": "A", "level": 10},
        )
        self.client.post(reverse("bestiary_duplicate", args=[mob.id]))
        self.assertTrue(BestiaryMob.objects.filter(owner=self.user, name="Ronin — Copie").exists())
        self.client.post(reverse("bestiary_delete", args=[mob.id]))
        self.assertFalse(BestiaryMob.objects.filter(id=mob.id).exists())


    def test_bestiary_page_displays_saved_mob(self):
        mob = BestiaryMob.objects.create(
            owner=self.user, name="Tireur Kurogane", profile="T", level=10,
            draft_payload={"profile": "T", "level": 10},
        )
        response = self.client.get(reverse("bestiary"))
        self.assertContains(response, "Tireur Kurogane")
        self.assertContains(response, "Charger dans Builder")
        self.assertContains(response, f"delete-bestiary-mob-{mob.id}")
        self.assertNotContains(response, "return confirm(")


    def test_bestiary_load_preserves_name_and_supports_quantity(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 6})
        self.client.post(reverse("monster_builder_save"), {"index": 0, "name": "Garde Kurogane"})
        mob = BestiaryMob.objects.get(owner=self.user, name="Garde Kurogane")

        session = self.client.session
        session["monster_builder_mobs"] = []
        session.save()
        response = self.client.post(
            reverse("bestiary_load", args=[mob.id]),
            {"quantity": 3},
            follow=True,
        )
        drafts = self.client.session["monster_builder_mobs"]
        self.assertEqual(len(drafts), 3)
        self.assertTrue(all(draft["name"] == "Garde Kurogane" for draft in drafts))
        self.assertContains(response, "<strong>Garde Kurogane", count=3, html=False)


    def test_manual_level_edit_recalculates_level_scaled_values(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(
            reverse("monster_builder_ability"),
            {"index": 0, "action": "add", "name": "Tension", "effect_type": "damage_distance", "scaling": "level", "value": 5},
        )
        response = self.client.post(
            reverse("monster_builder_field"),
            {"index": 0, "field": "level", "value": 10},
            follow=True,
        )
        mob = response.context["generated_mobs"][0]
        self.assertEqual(mob["level"], 10)
        self.assertEqual(mob["abilities"][0]["resolved_effect"]["value"], 50)
        self.assertEqual(self.client.session["monster_builder_mobs"][0]["level"], 10)


class AbilityLibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user(username="abilitylib", password="pwd")
        self.client.login(username="abilitylib", password="pwd")

    def test_created_ability_can_be_saved_to_personal_library(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 10})
        self.client.post(
            reverse("monster_builder_ability"),
            {
                "index": 0, "action": "add", "name": "Tension",
                "description": "Renforce la distance.",
                "effect_type": "damage_distance", "scaling": "level", "value": 5,
                "save_to_library": "on",
            },
        )
        ability = UserAbility.objects.get(owner=self.user, name="Tension")
        self.assertEqual(ability.effect_type, "damage_distance")
        self.assertEqual(ability.scaling, "level")
        self.assertEqual(ability.value, 5)

    def test_saved_ability_can_be_added_to_another_draft(self):
        ability = UserAbility.objects.create(
            owner=self.user, name="Thor", effect_type="aim", scaling="fixed", value=5
        )
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        response = self.client.post(
            reverse("monster_builder_ability_library"),
            {"index": 0, "ability_id": ability.id},
            follow=True,
        )
        mob = response.context["generated_mobs"][0]
        self.assertEqual(mob["abilities"][0]["name"], "Thor")
        self.assertEqual(mob["abilities"][0]["resolved_effect"]["value"], 5)

    def test_user_cannot_reuse_another_users_saved_ability(self):
        other = User.objects.create_user(username="abilityother", password="pwd")
        ability = UserAbility.objects.create(
            owner=other, name="Secret", effect_type="aim", value=99
        )
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(
            reverse("monster_builder_ability_library"),
            {"index": 0, "ability_id": ability.id},
        )
        self.assertEqual(self.client.session["monster_builder_mobs"][0]["abilities"], [])


class UserWeaponLibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user(username="weaponlib", password="pwd")
        self.client.login(username="weaponlib", password="pwd")

    def test_personal_weapon_can_be_created_and_added_to_draft(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        response = self.client.post(
            reverse("monster_builder_user_weapon_create"),
            {"index": 0, "name": "Boomstick", "hands": 2, "optimal_range": "SHORT", "power": 18, "aim": 1, "property_name": "Test", "property_text": "Perso."},
            follow=True,
        )
        weapon = UserWeapon.objects.get(owner=self.user, name="Boomstick")
        self.assertIn({"source": "user", "id": weapon.id}, self.client.session["monster_builder_mobs"][0]["weapons"])
        self.assertTrue(any(card.weapon.name == "Boomstick" for card in response.context["generated_mobs"][0]["weapon_cards"]))

    def test_personal_weapon_can_be_reused_and_is_private(self):
        weapon = UserWeapon.objects.create(owner=self.user, name="Perso", power=12, aim=2)
        other = User.objects.create_user(username="weaponother", password="pwd")
        secret = UserWeapon.objects.create(owner=other, name="Secret", power=99)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_user_weapon_add"), {"index": 0, "weapon_id": weapon.id})
        self.assertIn({"source": "user", "id": weapon.id}, self.client.session["monster_builder_mobs"][0]["weapons"])
        self.client.post(reverse("monster_builder_user_weapon_add"), {"index": 0, "weapon_id": secret.id})
        self.assertNotIn({"source": "user", "id": secret.id}, self.client.session["monster_builder_mobs"][0]["weapons"])


class UserImplantLibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user(username="implantlib", password="pwd")
        self.client.login(username="implantlib", password="pwd")

    def test_personal_implant_can_be_created_and_added_to_draft(self):
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        response = self.client.post(
            reverse("monster_builder_user_implant_create"),
            {"index": 0, "name": "ARES-X", "property_name": "Prototype", "property_text": "Effet personnel."},
            follow=True,
        )
        implant = UserImplant.objects.get(owner=self.user, name="ARES-X")
        self.assertIn({"source": "user", "id": implant.id}, self.client.session["monster_builder_mobs"][0]["implants"])
        self.assertTrue(any(card.implant.name == "ARES-X" for card in response.context["generated_mobs"][0]["implant_cards"]))

    def test_personal_implant_can_be_reused_and_is_private(self):
        implant = UserImplant.objects.create(owner=self.user, name="Perso")
        other = User.objects.create_user(username="implantother", password="pwd")
        secret = UserImplant.objects.create(owner=other, name="Secret")
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_user_implant_add"), {"index": 0, "implant_id": implant.id})
        self.assertIn({"source": "user", "id": implant.id}, self.client.session["monster_builder_mobs"][0]["implants"])
        self.client.post(reverse("monster_builder_user_implant_add"), {"index": 0, "implant_id": secret.id})
        self.assertNotIn({"source": "user", "id": secret.id}, self.client.session["monster_builder_mobs"][0]["implants"])


    def test_table_resources_can_be_spent_restored_and_hp_is_capped(self):
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        mob = TableMob.objects.get(game_table__owner=self.user)
        hp = mob.payload["current_hp"]

        self.client.post(reverse("table_mob_resource", args=[mob.id]), {"resource": "hp", "action": "subtract", "value": 30})
        mob.refresh_from_db()
        self.assertEqual(mob.payload["current_hp"], max(0, hp - 30))

        self.client.post(reverse("table_mob_resource", args=[mob.id]), {"resource": "hp", "action": "add", "value": 9999})
        mob.refresh_from_db()
        self.assertEqual(mob.payload["current_hp"], mob.payload["max_hp"])

        initial_reactions = mob.payload["initial_resources"]["reactions"]
        self.client.post(reverse("table_mob_resource", args=[mob.id]), {"resource": "reactions", "action": "subtract", "value": 1})
        self.client.post(reverse("table_mob_resource", args=[mob.id]), {"resource": "reactions", "action": "reset", "value": 0})
        mob.refresh_from_db()
        self.assertEqual(mob.payload["reactions"], initial_reactions)


    def test_next_round_refreshes_reactions_and_vigilance_without_healing(self):
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        mob = TableMob.objects.get(game_table__owner=self.user)
        initial = mob.payload["initial_resources"]
        hp = mob.payload["current_hp"]

        self.client.post(reverse("table_mob_resource", args=[mob.id]), {"resource": "hp", "action": "subtract", "value": 20})
        self.client.post(reverse("table_mob_resource", args=[mob.id]), {"resource": "reactions", "action": "subtract", "value": 1})
        self.client.post(reverse("table_mob_resource", args=[mob.id]), {"resource": "vigilance", "action": "subtract", "value": 1})
        self.client.post(reverse("table_next_round"))
        mob.refresh_from_db()
        self.assertEqual(mob.payload["current_hp"], max(0, hp - 20))
        self.assertEqual(mob.payload["reactions"], initial["reactions"])
        self.assertEqual(mob.payload["vigilance"], initial["vigilance"])

    def test_table_conditions_can_be_added_and_removed(self):
        from .models import TableMob, TableCondition

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        mob = TableMob.objects.get(game_table__owner=self.user)
        self.client.post(reverse("table_condition_add", args=[mob.id]), {"name": "Aveuglé"})
        condition = TableCondition.objects.get(mob=mob, name="Aveuglé")
        self.client.post(reverse("table_condition_delete", args=[mob.id, condition.id]))
        self.assertFalse(TableCondition.objects.filter(id=condition.id).exists())


    def test_table_weapon_roll_uses_effective_aim_and_reports_result(self):
        from unittest.mock import patch
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        mob = TableMob.objects.get(game_table__owner=self.user)
        weapon = mob.payload["weapons"][0]

        with patch("toolkit.views.random.randint", return_value=1):
            response = self.client.post(
                reverse("table_mob_roll_weapon", args=[mob.id, 0]),
                follow=True,
            )
        result = response.context["roll_result"]
        self.assertEqual(result["roll"], 1)
        self.assertEqual(result["aim"], 10 + weapon["aim"])
        self.assertTrue(result["success"])
        self.assertEqual(result["weapon"], weapon["name"])

    def test_table_weapon_roll_rejects_other_users_mob(self):
        from .models import GameTable, TableMob

        other = User.objects.create_user(username="rollother", password="pwd")
        table = GameTable.objects.create(owner=other)
        mob = TableMob.objects.create(
            game_table=table, name="Secret", profile="C", level=1,
            payload={"weapons": [{"name": "Secret gun", "aim": 20, "damage": 999}]},
        )
        response = self.client.post(
            reverse("table_mob_roll_weapon", args=[mob.id, 0]),
            follow=True,
        )
        self.assertIsNone(response.context["roll_result"])


    def test_table_weapon_roll_applies_context_modifier_and_damage_roll_scale(self):
        from unittest.mock import patch
        from .models import TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        mob = TableMob.objects.get(game_table__owner=self.user)
        weapon = mob.payload["weapons"][0]

        with patch("toolkit.views.random.randint", return_value=8):
            response = self.client.post(
                reverse("table_mob_roll_weapon", args=[mob.id, 0]),
                {"modifier": -2, "mode": "distance"},
                follow=True,
            )
        result = response.context["roll_result"]
        self.assertEqual(result["aim"], 10 + weapon["aim"] - 2)
        if result["success"]:
            self.assertEqual(result["roll_damage"], 10)


    def test_universal_table_roll_is_a_bare_d20(self):
        from unittest.mock import patch

        with patch("toolkit.views.random.randint", return_value=13):
            response = self.client.post(reverse("table_universal_roll"), follow=True)
        self.assertEqual(response.context["universal_roll_result"], 13)



class EncounterPreparationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user(username="encounterprep", password="pwd")
        self.client.login(username="encounterprep", password="pwd")
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 1, "level": 5})
        self.client.post(reverse("monster_builder_save"), {"index": 0, "name": "Muerto"})
        self.mob = BestiaryMob.objects.get(owner=self.user, name="Muerto")

    def test_encounter_can_store_quantity_and_load_independent_table_mobs(self):
        self.client.post(reverse("encounter_create"), {"name": "Planque Muertos"})
        encounter = Encounter.objects.get(owner=self.user, name="Planque Muertos")
        self.client.post(
            reverse("encounter_add_mob", args=[encounter.id]),
            {"bestiary_id": self.mob.id, "quantity": 3},
        )
        entry = encounter.draft_mobs.get()
        self.assertEqual(entry.quantity, 3)
        self.client.post(reverse("encounter_load_table", args=[encounter.id]))
        self.assertEqual(TableMob.objects.filter(game_table__owner=self.user).count(), 3)

    def test_encounter_snapshot_survives_bestiary_deletion(self):
        self.client.post(reverse("encounter_create"), {"name": "Snapshot"})
        encounter = Encounter.objects.get(owner=self.user, name="Snapshot")
        self.client.post(reverse("encounter_add_mob", args=[encounter.id]), {"bestiary_id": self.mob.id, "quantity": 1})
        self.mob.delete()
        self.assertTrue(encounter.draft_mobs.exists())

    def test_encounter_can_be_duplicated(self):
        self.client.post(reverse("encounter_create"), {"name": "Original"})
        encounter = Encounter.objects.get(owner=self.user, name="Original")
        self.client.post(reverse("encounter_add_mob", args=[encounter.id]), {"bestiary_id": self.mob.id, "quantity": 2})
        self.client.post(reverse("encounter_duplicate", args=[encounter.id]))
        copy = Encounter.objects.get(owner=self.user, name="Original — Copie")
        self.assertEqual(copy.draft_mobs.get().quantity, 2)


    def test_current_table_can_be_saved_as_encounter_without_bestiary(self):
        from .models import Encounter

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 3, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        self.client.post(reverse("table_save_encounter"), {"name": "Improvisée"})
        encounter = Encounter.objects.get(owner=self.user, name="Improvisée")
        self.assertEqual(encounter.draft_mobs.count(), 3)

    def test_saved_encounter_can_be_loaded_directly_from_table(self):
        from .models import Encounter, TableMob

        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 2, "level": 5})
        self.client.post(reverse("monster_builder_validate"), {"action": "all"})
        self.client.post(reverse("table_save_encounter"), {"name": "Reload"})
        encounter = Encounter.objects.get(owner=self.user, name="Reload")
        TableMob.objects.filter(game_table__owner=self.user).delete()

        self.client.post(reverse("table_load_encounter"), {"encounter_id": encounter.id})
        self.assertEqual(TableMob.objects.filter(game_table__owner=self.user).count(), 2)


class ScenarioFolderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="folders", password="pwd")
        self.client.login(username="folders", password="pwd")

    def test_same_folder_can_classify_bestiary_mob_and_encounter(self):
        from .models import UserFolder

        self.client.post(reverse("folder_create"), {"name": "Épisode 1", "next": "bestiary"})
        folder = UserFolder.objects.get(owner=self.user, name="Épisode 1")
        mob = BestiaryMob.objects.create(owner=self.user, name="Ronin", profile="A", level=5)
        encounter = Encounter.objects.create(owner=self.user, name="Embuscade")

        self.client.post(reverse("bestiary_move_folder", args=[mob.id]), {"folder_id": folder.id})
        self.client.post(reverse("encounter_move_folder", args=[encounter.id]), {"folder_id": folder.id})
        mob.refresh_from_db()
        encounter.refresh_from_db()
        self.assertEqual(mob.folder, folder)
        self.assertEqual(encounter.folder, folder)

    def test_deleting_folder_returns_content_to_unclassified(self):
        from .models import UserFolder

        folder = UserFolder.objects.create(owner=self.user, name="Épisode 2")
        mob = BestiaryMob.objects.create(owner=self.user, folder=folder, name="Garde", profile="C", level=2)
        encounter = Encounter.objects.create(owner=self.user, folder=folder, name="Planque")
        self.client.post(reverse("folder_delete", args=[folder.id]), {"next": "bestiary"})
        mob.refresh_from_db()
        encounter.refresh_from_db()
        self.assertIsNone(mob.folder)
        self.assertIsNone(encounter.folder)

    def test_user_cannot_assign_another_users_folder(self):
        from .models import UserFolder

        other = User.objects.create_user(username="folderother", password="pwd")
        foreign = UserFolder.objects.create(owner=other, name="Secret")
        mob = BestiaryMob.objects.create(owner=self.user, name="Mine", profile="C", level=1)
        self.client.post(reverse("bestiary_move_folder", args=[mob.id]), {"folder_id": foreign.id})
        mob.refresh_from_db()
        self.assertIsNone(mob.folder)


    def test_bestiary_folder_filter_supports_all_folder_and_unclassified(self):
        from .models import UserFolder

        folder = UserFolder.objects.create(owner=self.user, name="Épisode 1")
        BestiaryMob.objects.create(owner=self.user, folder=folder, name="Classé", profile="C", level=1)
        BestiaryMob.objects.create(owner=self.user, name="Libre", profile="A", level=1)

        response = self.client.get(reverse("bestiary"), {"folder": folder.id})
        self.assertContains(response, "Classé")
        self.assertNotContains(response, "Libre")
        response = self.client.get(reverse("bestiary"), {"folder": "unclassified"})
        self.assertContains(response, "Libre")
        self.assertNotContains(response, "Classé")
        response = self.client.get(reverse("bestiary"), {"folder": "all"})
        self.assertContains(response, "Classé")
        self.assertContains(response, "Libre")

    def test_encounter_folder_filter_uses_same_folder_selector(self):
        from .models import UserFolder

        folder = UserFolder.objects.create(owner=self.user, name="Épisode 2")
        Encounter.objects.create(owner=self.user, folder=folder, name="Planque")
        Encounter.objects.create(owner=self.user, name="Impro")
        response = self.client.get(reverse("encounters"), {"folder": folder.id})
        self.assertContains(response, "Planque")
        self.assertNotContains(response, "Impro")


    def test_builder_renders_dedicated_edit_dialog_for_each_mob(self):
        from django.core.management import call_command
        call_command("seed_monster_catalogue", verbosity=0)
        self.client.post(reverse("monster_builder"), {"action": "generate", "quantity": 2, "level": 5})
        response = self.client.get(reverse("monster_builder"))
        self.assertContains(response, 'class="mob-edit-dialog"', count=2)
        self.assertContains(response, "Profil &amp; niveau", count=2)
        self.assertContains(response, "Ressources", count=2)
