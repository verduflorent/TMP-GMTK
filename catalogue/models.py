from django.db import models


class MobProfile(models.TextChoices):
    COMBATANT = "C", "Combattant"
    ASSASSIN = "A", "Assassin"
    TIREUR = "T", "Tireur"
    SOUTIEN = "S", "Soutien"
    CONTROLE = "K", "Contrôle"


class MobWeapon(models.Model):
    class Tier(models.IntegerChoices):
        T1 = 1, "T1"
        T2 = 2, "T2"
        T3 = 3, "T3"
        T4 = 4, "T4"

    class Hands(models.IntegerChoices):
        ONE = 1, "1 main"
        TWO = 2, "2 mains"

    class Range(models.TextChoices):
        CONTACT = "CONTACT", "Contact"
        SHORT = "SHORT", "Courte"
        MEDIUM = "MEDIUM", "Moyenne"
        LONG = "LONG", "Longue"

    name = models.CharField(max_length=120, unique=True)
    tier = models.PositiveSmallIntegerField(choices=Tier.choices)
    allowed_profiles = models.CharField(
        max_length=5,
        blank=True,
        help_text="Profils autorisés parmi C/A/T/S/K. Vide = universel.",
    )
    hands = models.PositiveSmallIntegerField(choices=Hands.choices)
    optimal_range = models.CharField(max_length=10, choices=Range.choices)
    power = models.IntegerField(default=0)
    aim = models.IntegerField(default=0)
    property_name = models.CharField(max_length=120, blank=True)
    property_text = models.TextField(blank=True)
    is_control = models.BooleanField(default=False)

    class Meta:
        ordering = ["tier", "name"]

    def supports_profile(self, profile: str) -> bool:
        return not self.allowed_profiles or profile in self.allowed_profiles

    def __str__(self):
        return self.name


class MobImplant(models.Model):
    name = models.CharField(max_length=120, unique=True)
    allowed_profiles = models.CharField(
        max_length=5,
        help_text="Profils autorisés parmi C/A/T/S/K.",
    )
    property_name = models.CharField(max_length=120, blank=True)
    property_text = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def supports_profile(self, profile: str) -> bool:
        return profile in self.allowed_profiles

    def __str__(self):
        return self.name
