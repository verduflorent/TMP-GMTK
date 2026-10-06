import random

from django.test import SimpleTestCase

from catalogue.models import MobProfile
from rules.randomizer import PROFILE_WEIGHTS, generate_profiles, specialist_cap


class ProfileRandomizerTests(SimpleTestCase):
    def test_profile_weights_match_design_ratio(self):
        self.assertEqual(
            PROFILE_WEIGHTS,
            {
                MobProfile.COMBATANT: 5,
                MobProfile.ASSASSIN: 3,
                MobProfile.TIREUR: 5,
                MobProfile.SOUTIEN: 2,
                MobProfile.CONTROLE: 1,
            },
        )

    def test_small_groups_allow_at_most_one_of_each_specialist(self):
        for seed in range(100):
            profiles = generate_profiles(4, random.Random(seed))
            self.assertLessEqual(profiles.count(MobProfile.SOUTIEN), 1)
            self.assertLessEqual(profiles.count(MobProfile.CONTROLE), 1)

    def test_groups_from_five_to_ten_allow_at_most_two_of_each_specialist(self):
        for quantity in (5, 7, 10):
            for seed in range(100):
                profiles = generate_profiles(quantity, random.Random(seed))
                self.assertLessEqual(profiles.count(MobProfile.SOUTIEN), 2)
                self.assertLessEqual(profiles.count(MobProfile.CONTROLE), 2)

    def test_specialist_cap_scales_for_larger_batches(self):
        self.assertEqual(specialist_cap(4), 1)
        self.assertEqual(specialist_cap(5), 2)
        self.assertEqual(specialist_cap(10), 2)
        self.assertEqual(specialist_cap(15), 4)

    def test_seeded_generation_is_reproducible(self):
        first = generate_profiles(10, random.Random(42))
        second = generate_profiles(10, random.Random(42))
        self.assertEqual(first, second)

    def test_large_sample_tracks_expected_weight_order(self):
        profiles = generate_profiles(10000, random.Random(2026))
        counts = {profile: profiles.count(profile) for profile in PROFILE_WEIGHTS}
        self.assertGreater(counts[MobProfile.COMBATANT], counts[MobProfile.ASSASSIN])
        self.assertGreater(counts[MobProfile.TIREUR], counts[MobProfile.ASSASSIN])
        self.assertGreater(counts[MobProfile.ASSASSIN], counts[MobProfile.SOUTIEN])
        self.assertGreater(counts[MobProfile.SOUTIEN], counts[MobProfile.CONTROLE])

    def test_quantity_must_be_positive(self):
        with self.assertRaises(ValueError):
            generate_profiles(0, random.Random(1))


class WeaponTierRandomizerTests(SimpleTestCase):
    def test_design_anchor_weights_are_exact(self):
        from rules.randomizer import tier_weights

        self.assertEqual(tier_weights(1), (80.0, 20.0, 0.0, 0.0))
        self.assertEqual(tier_weights(3), (70.0, 25.0, 5.0, 0.0))
        self.assertEqual(tier_weights(6), (50.0, 35.0, 10.0, 5.0))

    def test_locked_tiers_cannot_appear_early(self):
        from rules.randomizer import tier_weights

        self.assertEqual(tier_weights(1)[2:], (0.0, 0.0))
        self.assertEqual(tier_weights(2)[2:], (0.0, 0.0))
        self.assertEqual(tier_weights(3)[3], 0.0)
        self.assertEqual(tier_weights(5)[3], 0.0)

    def test_intermediate_weights_are_progressive_and_normalized(self):
        from rules.randomizer import tier_weights

        n2 = tier_weights(2)
        n5 = tier_weights(5)
        self.assertAlmostEqual(sum(n2), 100.0)
        self.assertAlmostEqual(sum(n5), 100.0)
        self.assertGreater(n2[0], tier_weights(3)[0])
        self.assertGreater(n5[2], tier_weights(3)[2])

    def test_high_levels_converge_to_fixed_cap(self):
        from rules.randomizer import tier_weights

        self.assertEqual(tier_weights(20), (30.0, 40.0, 20.0, 10.0))
        self.assertEqual(tier_weights(30), (30.0, 40.0, 20.0, 10.0))

    def test_seeded_tier_selection_is_reproducible(self):
        from rules.randomizer import choose_weapon_tier

        first = [choose_weapon_tier(10, random.Random(seed)) for seed in range(30)]
        second = [choose_weapon_tier(10, random.Random(seed)) for seed in range(30)]
        self.assertEqual(first, second)

    def test_primary_weapon_respects_profile_and_selected_tier(self):
        from dataclasses import dataclass
        from rules.randomizer import choose_primary_weapon

        @dataclass
        class Weapon:
            name: str
            tier: int
            profiles: str

            def supports_profile(self, profile):
                return not self.profiles or profile in self.profiles

        weapons = [
            Weapon("Pistolet", 1, ""),
            Weapon("AR", 2, "C"),
            Weapon("Arc", 3, "T"),
        ]
        weapon = choose_primary_weapon(
            weapons, profile=MobProfile.COMBATANT, level=3, rng=random.Random(1)
        )
        self.assertTrue(weapon.supports_profile(MobProfile.COMBATANT))
        self.assertIn(weapon.tier, (1, 2))

    def test_primary_weapon_falls_back_to_lower_tier_if_pool_is_empty(self):
        from dataclasses import dataclass
        from rules.randomizer import choose_primary_weapon

        @dataclass
        class Weapon:
            name: str
            tier: int
            profiles: str

            def supports_profile(self, profile):
                return not self.profiles or profile in self.profiles

        weapons = [Weapon("Pistolet", 1, "")]
        weapon = choose_primary_weapon(
            weapons, profile=MobProfile.CONTROLE, level=20, rng=random.Random(2)
        )
        self.assertEqual(weapon.name, "Pistolet")
