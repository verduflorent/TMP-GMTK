from django.test import SimpleTestCase

from rules.engine import (
    BuildStats,
    RuleCalculationError,
    apply_concentrated_fulgurance,
    defensive_budget,
    delta_coefficient,
    derive_build,
    force_shortfall_penalty,
    is_legal_level_one,
    offensive_budget,
    resolve_attack,
)


class BuildRulesTests(SimpleTestCase):
    def test_level_one_distribution_is_not_just_a_sum(self):
        self.assertTrue(is_legal_level_one(BuildStats(13, 10, 8, 5, 11, 10)))
        self.assertFalse(is_legal_level_one(BuildStats(9, 9, 9, 9, 11, 10)))

    def test_budgets_follow_level_progression(self):
        self.assertEqual(offensive_budget(1), 36)
        self.assertEqual(defensive_budget(1), 21)
        self.assertEqual(offensive_budget(10), 54)
        self.assertEqual(defensive_budget(10), 30)

    def test_threshold_rewards_drive_derived_values(self):
        derived = derive_build(BuildStats(18, 16, 12, 16, 16, 16))
        self.assertEqual(derived.max_hp, 26)
        self.assertEqual(derived.max_reactions, 2)
        self.assertEqual(derived.main_slots, 2)
        self.assertEqual(derived.secondary_slots, 1)
        self.assertEqual(derived.gadget_slots, 3)
        self.assertEqual(derived.implant_slots, 2)

    def test_force_shortfall_penalty_is_one_per_missing_point(self):
        self.assertEqual(force_shortfall_penalty(14, 15), -1)
        self.assertEqual(force_shortfall_penalty(15, 15), 0)


class AttackRulesTests(SimpleTestCase):
    def test_test_modifier_changes_margin_but_not_delta_coefficient(self):
        result = resolve_attack(stat_value=16, roll=7, power=5, test_modifier=-2)
        self.assertEqual(result.threshold, 14)
        self.assertEqual(result.delta_coefficient, 4)
        self.assertEqual(result.delta_bonus, 1)

    def test_critical_is_prioritary_and_negative_margin_delta_is_zero(self):
        result = resolve_attack(stat_value=2, roll=3, power=5, test_modifier=0, critical_bonus=2)
        self.assertEqual(result.verdict, "critical_success")
        self.assertEqual(result.delta_bonus, 0)
        self.assertEqual(result.damage, 10)

    def test_natural_twenty_is_always_critical_failure(self):
        result = resolve_attack(stat_value=25, roll=20, power=5)
        self.assertEqual(result.verdict, "critical_failure")
        self.assertIsNone(result.damage)

    def test_annihilation_only_multiplies_power(self):
        result = resolve_attack(stat_value=18, roll=6, power=5, annihilation=True)
        self.assertEqual(result.delta_bonus, 4)
        self.assertEqual(result.damage, 19)

    def test_explicit_delta_modifier_can_change_coefficient(self):
        self.assertEqual(delta_coefficient(16, -1), 3)

    def test_invalid_delta_override_fails_cleanly(self):
        with self.assertRaisesMessage(RuleCalculationError, "Coefficient Delta invalide"):
            delta_coefficient(18, -3)

    def test_concentrated_fulgurance_applies_armor_per_strike(self):
        self.assertEqual(apply_concentrated_fulgurance(5, 2), 6)
