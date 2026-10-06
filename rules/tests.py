from django.test import SimpleTestCase

from rules.engine import (
    attack_threshold,
    base_damage,
    max_hp,
    profile_derived,
    profile_stats,
    resolve_attack,
    roll_damage_modifier,
)


class MobScalingTests(SimpleTestCase):
    def test_hp_scales_linearly_beyond_level_ten(self):
        self.assertEqual(max_hp(1), 250)
        self.assertEqual(max_hp(5), 370)
        self.assertEqual(max_hp(3, constitution=12), 330)
        self.assertEqual(max_hp(10), 520)
        self.assertEqual(max_hp(20), 820)

    def test_damage_base_scales_linearly(self):
        self.assertEqual(base_damage(1), 50)
        self.assertEqual(base_damage(10), 140)
        self.assertEqual(base_damage(15), 190)

    def test_stats_are_capped_at_level_ten(self):
        self.assertEqual(profile_stats("C", 10), profile_stats("C", 15))
        self.assertEqual(profile_stats("T", 10).perception, 20)
        self.assertEqual(profile_stats("K", 10).force, 18)

    def test_profile_passives_are_integrated(self):
        self.assertEqual(profile_derived("C", 5).armor, 25)
        self.assertEqual(profile_derived("S", 5).shield, 100)
        self.assertEqual(profile_derived("A", 5).reactions, 2)
        self.assertEqual(profile_derived("T", 9).vigilance, 1)
        self.assertEqual(profile_derived("T", 10).vigilance, 2)


class MobAttackTests(SimpleTestCase):
    def test_attack_threshold_uses_perception_bonus_and_weapon_aim(self):
        self.assertEqual(attack_threshold(14, 1), 15)
        self.assertEqual(attack_threshold(14, 1, -2), 13)

    def test_ten_is_neutral_damage_roll(self):
        self.assertEqual(roll_damage_modifier(10), 0)
        self.assertEqual(roll_damage_modifier(6), 20)
        self.assertEqual(roll_damage_modifier(14), -20)

    def test_successful_attack_uses_monster_damage_formula(self):
        result = resolve_attack(level=1, perception=12, weapon_power=15, weapon_aim=1, roll=10)
        self.assertTrue(result.success)
        self.assertEqual(result.threshold, 13)
        self.assertEqual(result.damage, 80)

    def test_failed_attack_has_no_damage(self):
        result = resolve_attack(level=1, perception=10, weapon_power=15, weapon_aim=0, roll=15)
        self.assertFalse(result.success)
        self.assertIsNone(result.damage)

    def test_mobs_have_no_special_critical_rule(self):
        result = resolve_attack(level=1, perception=10, weapon_power=10, weapon_aim=2, roll=1)
        self.assertTrue(result.success)
        self.assertEqual(result.damage, 115)


class ResolvedCombatCardTests(SimpleTestCase):
    class Item:
        def __init__(self, name, power=0, aim=0, property_text=""):
            self.name = name
            self.power = power
            self.aim = aim
            self.property_text = property_text

    def test_revolver_integrates_power_bonus_and_neutral_damage(self):
        from rules.engine import resolve_weapon

        card = resolve_weapon(self.Item("Revolver", 10, 2, "+5 Puissance."), 3)
        self.assertEqual(card.effective_power, 15)
        self.assertEqual(card.neutral_damage, 100)

    def test_arc_level_33_displays_neutral_damage(self):
        from rules.engine import resolve_weapon

        card = resolve_weapon(self.Item("Arc", 15, 1, "Ignore les Couvertures légères."), 33)
        self.assertEqual(card.neutral_damage, 400)

    def test_scaled_weapon_property_is_resolved(self):
        from rules.engine import resolve_weapon

        card = resolve_weapon(self.Item("Smart Rifle", 15, 1, ""), 33)
        self.assertEqual(card.resolved_property, "+330 Dégâts contre une cible Marquée.")

    def test_zephyr_level_33_resolves_every_two_levels(self):
        from rules.engine import resolve_implant

        card = resolve_implant(self.Item("ZEPHYR", property_text=""), 33, 1210)
        self.assertEqual(card.resolved_property, "Attaques à distance : +80 Dégâts.")

    def test_armor_implants_modify_displayed_armor(self):
        from rules.engine import implant_armor_bonus

        implants = [self.Item("AEGIS"), self.Item("ANCHOR")]
        self.assertEqual(implant_armor_bonus(implants, 3), 21)


    def test_combat_mace_integrates_unconditional_level_damage(self):
        from rules.engine import resolve_weapon

        card = resolve_weapon(self.Item("Masse de combat", 25, 0, "+5 Dégâts × Niveau."), 10)
        self.assertEqual(card.neutral_damage, 240)
        self.assertEqual(card.resolved_property, "")


class FivePointQuantizationTests(SimpleTestCase):
    def test_round_to_five_uses_nearest_step(self):
        from rules.engine import round_to_5

        expected = {
            20: 20, 21: 20, 22: 20,
            23: 25, 24: 25, 25: 25,
            26: 25, 27: 25, 28: 30,
        }
        for value, rounded in expected.items():
            with self.subTest(value=value):
                self.assertEqual(round_to_5(value), rounded)


class MobStatModifierTests(SimpleTestCase):
    class Item:
        def __init__(self, name, power=0, aim=0, property_text=""):
            self.name = name
            self.power = power
            self.aim = aim
            self.property_text = property_text

    def test_stat_modifier_progression(self):
        from rules.engine import stat_modifier

        expected = {10: 0, 11: 0, 12: 1, 13: 1, 14: 2, 16: 3, 18: 4, 20: 5}
        for value, modifier in expected.items():
            with self.subTest(value=value):
                self.assertEqual(stat_modifier(value), modifier)

    def test_perception_modifier_is_applied_to_weapon_aim(self):
        from rules.engine import resolve_weapon

        card = resolve_weapon(self.Item("Arc", 15, 1, ""), 10, perception=16)
        self.assertEqual(card.effective_aim, 4)

    def test_tech_modifier_is_applied_to_med_rifle_healing(self):
        from rules.engine import resolve_weapon

        card = resolve_weapon(self.Item("Med Rifle", 15, 1, ""), 5, technique=16)
        self.assertEqual(card.resolved_property, "Soigne un allié de 160 PV.")

    def test_tech_modifier_is_applied_to_phalanx_barrier(self):
        from rules.engine import resolve_implant

        card = resolve_implant(self.Item("PHALANX", property_text=""), 5, 370, technique=16)
        self.assertEqual(card.resolved_property, "Réaction : déploie une barrière à 110 PV.")


class PropertyLineTests(SimpleTestCase):
    def test_semicolon_separates_distinct_card_effects(self):
        from rules.engine import split_property_lines

        self.assertEqual(
            split_property_lines("+20 Armure ; résistance aux Poussées."),
            ("+20 Armure", "résistance aux Poussées."),
        )

    def test_chakram_resolves_bond_and_throw_on_two_lines(self):
        from rules.engine import resolve_weapon

        class Item:
            name = "Chakram"
            power = 15
            aim = 1
            property_text = ""

        card = resolve_weapon(Item(), 6)
        self.assertEqual(card.effective_power, 20)
        self.assertEqual(len(card.property_lines), 2)
        self.assertIn("bondir", card.property_lines[0])
        self.assertIn("Portée Moyenne", card.property_lines[1])


class HybridWeaponDamageTests(SimpleTestCase):
    class Item:
        def __init__(self, name, power, aim=0, property_text=""):
            self.name = name
            self.power = power
            self.aim = aim
            self.property_text = property_text

    def test_short_shotgun_contextual_damage(self):
        from rules.engine import resolve_weapon
        card = resolve_weapon(self.Item("Fusil à pompe court", 10, 2), 5)
        self.assertEqual((card.effective_power, card.distance_damage, card.contact_damage), (10, 110, 130))

    def test_chakram_contextual_damage(self):
        from rules.engine import resolve_weapon
        card = resolve_weapon(self.Item("Chakram", 15, 1), 6)
        self.assertEqual((card.effective_power, card.distance_damage, card.contact_damage), (15, 130, 140))
        self.assertEqual(len(card.property_lines), 2)
