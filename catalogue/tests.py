from django.core.management import call_command
from django.test import TestCase

from catalogue.models import MobImplant, MobWeapon


class MonsterCatalogueSeedTests(TestCase):
    def test_seed_is_idempotent_and_complete(self):
        call_command("seed_monster_catalogue", verbosity=0)
        self.assertEqual(MobWeapon.objects.count(), 28)
        self.assertEqual(MobImplant.objects.count(), 16)

        call_command("seed_monster_catalogue", verbosity=0)
        self.assertEqual(MobWeapon.objects.count(), 28)
        self.assertEqual(MobImplant.objects.count(), 16)

    def test_seed_preserves_profile_and_weapon_structure(self):
        call_command("seed_monster_catalogue", verbosity=0)
        rocket = MobWeapon.objects.get(name="Lance-roquettes")
        self.assertEqual((rocket.tier, rocket.allowed_profiles, rocket.hands, rocket.power, rocket.aim), (4, "C", 2, 35, -3))

        pistol = MobWeapon.objects.get(name="Pistolet")
        self.assertEqual(pistol.allowed_profiles, "")
        self.assertTrue(pistol.supports_profile("A"))
        self.assertTrue(pistol.supports_profile("K"))

        aegis = MobImplant.objects.get(name="AEGIS")
        self.assertTrue(aegis.supports_profile("C"))
        self.assertTrue(aegis.supports_profile("S"))
        self.assertTrue(aegis.supports_profile("K"))
        self.assertFalse(aegis.supports_profile("A"))
