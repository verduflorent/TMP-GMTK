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
