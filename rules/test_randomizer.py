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


class WeaponLoadoutRandomizerTests(SimpleTestCase):
    class Weapon:
        def __init__(self, name, tier, profiles="", hands=1):
            self.name = name
            self.tier = tier
            self.profiles = profiles
            self.hands = hands

        def supports_profile(self, profile):
            return not self.profiles or profile in self.profiles

    class FixedRng:
        def __init__(self, random_values=None, choice_index=0):
            self.random_values = iter(random_values or [])
            self.choice_index = choice_index

        def random(self):
            return next(self.random_values)

        def choice(self, values):
            return values[min(self.choice_index, len(values) - 1)]

        def choices(self, values, weights=None, k=1):
            return [values[0]]

    def setUp(self):
        self.t1 = self.Weapon("Pistolet", 1, "", 1)
        self.t2 = self.Weapon("Pompe court", 2, "C", 1)
        self.t2_two_hands = self.Weapon("AR", 2, "C", 2)
        self.t4 = self.Weapon("Roquettes", 4, "C", 2)
        self.weapons = [self.t1, self.t2, self.t2_two_hands, self.t4]

    def test_t4_always_requests_a_t1_or_t2_secondary(self):
        from rules.randomizer import choose_secondary_weapon

        secondary = choose_secondary_weapon(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t4,
            rng=self.FixedRng(choice_index=1),
        )
        self.assertIsNotNone(secondary)
        self.assertIn(secondary.tier, (1, 2))

    def test_non_t4_secondary_uses_twenty_percent_chance(self):
        from rules.randomizer import choose_secondary_weapon

        yes = choose_secondary_weapon(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2_two_hands,
            rng=self.FixedRng([0.19]),
        )
        no = choose_secondary_weapon(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2_two_hands,
            rng=self.FixedRng([0.20]),
        )
        self.assertIsNotNone(yes)
        self.assertIsNone(no)

    def test_secondary_respects_profile_compatibility(self):
        from rules.randomizer import choose_secondary_weapon

        secondary = choose_secondary_weapon(
            self.weapons,
            profile=MobProfile.ASSASSIN,
            primary_weapon=self.t4,
            rng=self.FixedRng(),
        )
        self.assertEqual(secondary.name, "Pistolet")

    def test_akimbo_requires_one_handed_primary(self):
        from rules.randomizer import choose_akimbo_pair

        pair = choose_akimbo_pair(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2_two_hands,
            rng=self.FixedRng([0.0]),
        )
        self.assertIsNone(pair)

    def test_akimbo_uses_ten_percent_chance(self):
        from rules.randomizer import choose_akimbo_pair

        yes = choose_akimbo_pair(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2,
            rng=self.FixedRng([0.09, 0.0]),
        )
        no = choose_akimbo_pair(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2,
            rng=self.FixedRng([0.10]),
        )
        self.assertIsNotNone(yes)
        self.assertIsNone(no)

    def test_akimbo_eighty_percent_is_identical(self):
        from rules.randomizer import choose_akimbo_pair

        pair = choose_akimbo_pair(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2,
            rng=self.FixedRng([0.05, 0.79]),
        )
        self.assertIs(pair[0], pair[1])

    def test_akimbo_twenty_percent_is_mixed_when_possible(self):
        from rules.randomizer import choose_akimbo_pair

        pair = choose_akimbo_pair(
            self.weapons,
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2,
            rng=self.FixedRng([0.05, 0.80]),
        )
        self.assertNotEqual(pair[0].name, pair[1].name)

    def test_impossible_mixed_akimbo_falls_back_to_identical(self):
        from rules.randomizer import choose_akimbo_pair

        pair = choose_akimbo_pair(
            [self.t2],
            profile=MobProfile.COMBATANT,
            primary_weapon=self.t2,
            rng=self.FixedRng([0.05, 0.95]),
        )
        self.assertIs(pair[0], pair[1])

    def test_loadout_never_stacks_akimbo_with_a_third_weapon(self):
        from rules.randomizer import choose_weapon_loadout

        loadout = choose_weapon_loadout(
            [self.t1],
            profile=MobProfile.COMBATANT,
            level=1,
            rng=self.FixedRng([0.05, 0.0]),
        )
        self.assertTrue(loadout["akimbo"])
        self.assertEqual(loadout["primary"].name, "Pistolet")
        self.assertEqual(loadout["secondary"].name, "Pistolet")


class ImplantRandomizerTests(SimpleTestCase):
    class Implant:
        def __init__(self, name, profiles, property_name="", property_text=""):
            self.name = name
            self.profiles = profiles
            self.property_name = property_name
            self.property_text = property_text

        def supports_profile(self, profile):
            return profile in self.profiles

    class FixedRng:
        def __init__(self, random_values=None):
            self.random_values = iter(random_values or [])

        def random(self):
            return next(self.random_values)

        def choice(self, values):
            return values[0]

    def test_implant_slot_anchor_chances_match_design(self):
        from rules.randomizer import implant_slot_chances

        self.assertEqual(implant_slot_chances(1), (0.20, 0.00, 0.00))
        self.assertEqual(implant_slot_chances(4), (0.50, 0.10, 0.00))
        self.assertEqual(implant_slot_chances(7), (0.85, 0.50, 0.10))
        self.assertEqual(implant_slot_chances(15), (1.00, 1.00, 0.50))

    def test_locked_implant_slots_cannot_proc(self):
        from rules.randomizer import roll_implant_slots

        self.assertEqual(roll_implant_slots(3, self.FixedRng([0.0])), [1])
        self.assertEqual(roll_implant_slots(6, self.FixedRng([0.0, 0.0])), [1, 2])

    def test_slots_are_rolled_independently_and_compacted(self):
        from rules.randomizer import roll_implant_slots

        # N7: slot 1 fails, slot 2 succeeds, slot 3 succeeds.
        self.assertEqual(
            roll_implant_slots(7, self.FixedRng([0.90, 0.40, 0.05])),
            [2, 3],
        )

    def test_level_fifteen_always_has_first_two_slots(self):
        from rules.randomizer import roll_implant_slots

        for seed in range(100):
            slots = roll_implant_slots(15, random.Random(seed))
            self.assertIn(1, slots)
            self.assertIn(2, slots)

    def test_high_level_chances_cap_instead_of_growing_forever(self):
        from rules.randomizer import implant_slot_chances

        self.assertEqual(implant_slot_chances(20), (1.0, 1.0, 0.75))
        self.assertEqual(implant_slot_chances(50), (1.0, 1.0, 0.75))

    def test_implants_respect_profile_compatibility(self):
        from rules.randomizer import choose_implants

        implants = [
            self.Implant("AEGIS", "CSK"),
            self.Implant("VELOS", "A"),
            self.Implant("MINOS", "AC"),
        ]
        selected = choose_implants(
            implants,
            profile=MobProfile.COMBATANT,
            level=15,
            rng=self.FixedRng([0.0, 0.0, 0.9]),
        )
        self.assertEqual([implant.name for implant in selected], ["AEGIS", "MINOS"])

    def test_implant_selection_avoids_duplicates(self):
        from rules.randomizer import choose_implants

        implants = [
            self.Implant("AEGIS", "C"),
            self.Implant("MINOS", "C"),
            self.Implant("PHALANX", "C"),
        ]
        selected = choose_implants(
            implants,
            profile=MobProfile.COMBATANT,
            level=20,
            rng=self.FixedRng([0.0, 0.0, 0.0]),
        )
        names = [implant.name for implant in selected]
        self.assertEqual(len(names), 3)
        self.assertEqual(len(set(names)), 3)

    def test_not_enough_compatible_implants_returns_available_only(self):
        from rules.randomizer import choose_implants

        implants = [self.Implant("VELOS", "A")]
        selected = choose_implants(
            implants,
            profile=MobProfile.ASSASSIN,
            level=20,
            rng=self.FixedRng([0.0, 0.0, 0.0]),
        )
        self.assertEqual([implant.name for implant in selected], ["VELOS"])


class CompleteMobGenerationTests(SimpleTestCase):
    class Weapon:
        def __init__(
            self,
            name,
            tier,
            profiles="",
            hands=2,
            power=15,
            aim=1,
            property_name="",
            property_text="",
        ):
            self.name = name
            self.tier = tier
            self.profiles = profiles
            self.hands = hands
            self.power = power
            self.aim = aim
            self.property_name = property_name
            self.property_text = property_text

        def supports_profile(self, profile):
            return not self.profiles or profile in self.profiles

    class Implant:
        def __init__(self, name, profiles, property_name="", property_text=""):
            self.name = name
            self.profiles = profiles
            self.property_name = property_name
            self.property_text = property_text

        def supports_profile(self, profile):
            return profile in self.profiles

    def setUp(self):
        self.weapons = [
            self.Weapon("Pistolet", 1, "", 1, 10, 2),
            self.Weapon("AR", 2, "C", 2),
            self.Weapon("Arme de lancer", 2, "A", 1, 10, 2),
            self.Weapon("Carabine", 2, "T", 2),
            self.Weapon("Med Rifle", 2, "S", 2),
            self.Weapon("Smartgun", 2, "K", 1, 10, 2),
        ]
        self.implants = [
            self.Implant("AEGIS", "CSK"),
            self.Implant("VELOS", "A"),
            self.Implant("ARGUS", "TS"),
            self.Implant("ZEPHYR", "AT"),
            self.Implant("MEDUSA", "K"),
        ]

    def test_generated_mob_contains_stats_derived_values_and_equipment(self):
        from rules.randomizer import generate_mob

        mob = generate_mob(
            self.weapons,
            self.implants,
            level=5,
            profile=MobProfile.COMBATANT,
            rng=random.Random(42),
        )
        self.assertEqual(mob["profile"], MobProfile.COMBATANT)
        self.assertEqual(mob["level"], 5)
        self.assertEqual(mob["max_hp"], 390)
        self.assertEqual(mob["current_hp"], 390)
        # N5 Combattant: 25 Armure de profil + AEGIS tiré par ce seed (+25).
        self.assertEqual(mob["armor"], 50)
        self.assertEqual(mob["stats"].force, 14)
        self.assertTrue(mob["primary"].supports_profile(MobProfile.COMBATANT))
        self.assertTrue(all(i.supports_profile(MobProfile.COMBATANT) for i in mob["implants"]))

    def test_generated_support_integrates_profile_shield(self):
        from rules.randomizer import generate_mob

        mob = generate_mob(
            self.weapons,
            self.implants,
            level=5,
            profile=MobProfile.SOUTIEN,
            rng=random.Random(10),
        )
        self.assertEqual(mob["shield"], 100)

    def test_group_generation_applies_profile_quotas(self):
        from rules.randomizer import generate_mobs

        mobs = generate_mobs(
            self.weapons,
            self.implants,
            quantity=4,
            level=5,
            rng=random.Random(123),
        )
        profiles = [mob["profile"] for mob in mobs]
        self.assertEqual(len(mobs), 4)
        self.assertLessEqual(profiles.count(MobProfile.SOUTIEN), 1)
        self.assertLessEqual(profiles.count(MobProfile.CONTROLE), 1)

    def test_role_reroll_keeps_level_and_rebuilds_profile_values(self):
        from rules.randomizer import reroll_mob_role

        mob = reroll_mob_role(
            self.weapons,
            self.implants,
            level=5,
            profile=MobProfile.ASSASSIN,
            rng=random.Random(7),
        )
        self.assertEqual(mob["level"], 5)
        self.assertEqual(mob["profile"], MobProfile.ASSASSIN)
        self.assertEqual(mob["max_hp"], 370)
        self.assertEqual(mob["reactions"], 2)
        self.assertEqual(mob["stats"].agility, 15)
        self.assertTrue(mob["primary"].supports_profile(MobProfile.ASSASSIN))

    def test_level_above_ten_uses_capped_stats_but_continued_scaling(self):
        from rules.randomizer import generate_mob

        mob = generate_mob(
            self.weapons,
            self.implants,
            level=15,
            profile=MobProfile.TIREUR,
            rng=random.Random(4),
        )
        self.assertEqual(mob["stats"].perception, 20)
        self.assertEqual(mob["max_hp"], 690)
        self.assertGreaterEqual(len(mob["implants"]), 2)

    def test_forced_unknown_profile_is_rejected(self):
        from rules.randomizer import generate_mob

        with self.assertRaises(ValueError):
            generate_mob(
                self.weapons,
                self.implants,
                level=5,
                profile="X",
                rng=random.Random(1),
            )


class ResolvedLoadoutIntegrationTests(SimpleTestCase):
    class Weapon:
        def __init__(self, name, tier, profiles="", hands=1, power=10, aim=2, property_name="", property_text=""):
            self.name = name
            self.tier = tier
            self.profiles = profiles
            self.hands = hands
            self.power = power
            self.aim = aim
            self.property_name = property_name
            self.property_text = property_text

        def supports_profile(self, profile):
            return not self.profiles or profile in self.profiles

    class Implant:
        def __init__(self, name, profiles, property_text=""):
            self.name = name
            self.profiles = profiles
            self.property_name = name
            self.property_text = property_text

        def supports_profile(self, profile):
            return profile in self.profiles

    def test_non_akimbo_secondary_cannot_duplicate_primary(self):
        from rules.randomizer import choose_secondary_weapon

        pistol = self.Weapon("Pistolet", 1)
        revolver = self.Weapon("Revolver", 2, "T")
        for seed in range(50):
            secondary = choose_secondary_weapon(
                [pistol, revolver],
                profile=MobProfile.TIREUR,
                primary_weapon=pistol,
                rng=random.Random(seed),
            )
            if secondary is not None:
                self.assertNotEqual(secondary.name, pistol.name)

    def test_generated_card_integrates_implant_armor(self):
        from rules.randomizer import generate_mob

        pistol = self.Weapon("Pistolet", 1)
        aegis = self.Implant("AEGIS", "C", "+5 Armure × Niveau.")
        # At N15 slots 1 and 2 proc, but only one compatible implant exists.
        mob = generate_mob(
            [pistol],
            [aegis],
            level=15,
            profile=MobProfile.COMBATANT,
            rng=random.Random(1),
        )
        self.assertEqual(mob["armor"], 75 + 75)
        self.assertEqual(mob["primary_card"].neutral_damage, 210)


class IdenticalAkimboResolutionTests(SimpleTestCase):
    class Weapon:
        def __init__(self):
            self.name = "Pistolet"
            self.tier = 1
            self.profiles = ""
            self.hands = 1
            self.power = 10
            self.aim = 2
            self.property_name = ""
            self.property_text = ""

        def supports_profile(self, profile):
            return True

    def test_identical_akimbo_compacts_and_adds_power(self):
        from rules.randomizer import generate_mob

        # Search deterministic seeds until the 10% Akimbo roll produces identical Akimbo.
        for seed in range(500):
            mob = generate_mob(
                [self.Weapon()],
                [],
                level=3,
                profile=MobProfile.ASSASSIN,
                rng=random.Random(seed),
            )
            if mob["akimbo_identical"]:
                self.assertEqual(mob["primary_card"].effective_power, 20)
                self.assertEqual(mob["primary_card"].neutral_damage, 110)
                return
        self.fail("Aucun Akimbo identique trouvé dans les seeds de test.")
