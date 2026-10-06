from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from catalogue.models import MobImplant, MobProfile, MobWeapon


class GameTable(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_table",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table de {self.owner}"


class BestiaryMob(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bestiary_mobs",
    )
    name = models.CharField(max_length=120)
    profile = models.CharField(max_length=1, choices=MobProfile.choices)
    level = models.PositiveSmallIntegerField(default=1)
    weapon_primary = models.ForeignKey(
        MobWeapon,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="primary_bestiary_mobs",
    )
    weapon_secondary = models.ForeignKey(
        MobWeapon,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secondary_bestiary_mobs",
    )
    implant = models.ForeignKey(
        MobImplant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bestiary_mobs",
    )
    notes = models.TextField(blank=True)
    draft_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} — N{self.level}"


class Encounter(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="encounters",
    )
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EncounterMob(models.Model):
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="mobs")
    source = models.ForeignKey(
        BestiaryMob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="encounter_instances",
    )
    name = models.CharField(max_length=120)
    profile = models.CharField(max_length=1, choices=MobProfile.choices)
    level = models.PositiveSmallIntegerField(default=1)
    current_hp = models.PositiveIntegerField()
    max_hp = models.PositiveIntegerField()
    armor = models.PositiveIntegerField(default=0)
    shield = models.PositiveIntegerField(default=0)
    reactions = models.PositiveSmallIntegerField(default=1)
    vigilance = models.PositiveSmallIntegerField(default=1)
    weapon_primary = models.ForeignKey(
        MobWeapon,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="primary_encounter_mobs",
    )
    weapon_secondary = models.ForeignKey(
        MobWeapon,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secondary_encounter_mobs",
    )
    implant = models.ForeignKey(
        MobImplant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="encounter_mobs",
    )
    rank = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["rank", "id"]

    def clean(self):
        super().clean()
        if self.source_id and self.source.owner_id != self.encounter.owner_id:
            raise ValidationError("Le Mob source doit appartenir au même utilisateur que la rencontre.")

    def __str__(self):
        return self.name


class TableMob(models.Model):
    """Validated Monster Builder snapshot owned by one user's live Table."""
    game_table = models.ForeignKey(GameTable, on_delete=models.CASCADE, related_name="builder_mobs")
    name = models.CharField(max_length=120)
    profile = models.CharField(max_length=1, choices=MobProfile.choices)
    level = models.PositiveSmallIntegerField(default=1)
    payload = models.JSONField(default=dict)
    rank = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rank", "id"]

    def __str__(self):
        return f"{self.name} — N{self.level}"


class TableInstance(models.Model):
    game_table = models.ForeignKey(GameTable, on_delete=models.CASCADE, related_name="instances")
    source = models.ForeignKey(
        EncounterMob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="table_instances",
    )
    name = models.CharField(max_length=120)
    profile = models.CharField(max_length=1, choices=MobProfile.choices)
    level = models.PositiveSmallIntegerField(default=1)
    current_hp = models.PositiveIntegerField()
    max_hp = models.PositiveIntegerField()
    armor = models.PositiveIntegerField(default=0)
    shield = models.PositiveIntegerField(default=0)
    reactions = models.PositiveSmallIntegerField(default=1)
    vigilance = models.PositiveSmallIntegerField(default=1)
    weapon_primary = models.ForeignKey(
        MobWeapon,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="primary_table_instances",
    )
    weapon_secondary = models.ForeignKey(
        MobWeapon,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secondary_table_instances",
    )
    implant = models.ForeignKey(
        MobImplant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="table_instances",
    )
    rank = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["rank", "id"]

    def clean(self):
        super().clean()
        if self.source_id and self.source.encounter.owner_id != self.game_table.owner_id:
            raise ValidationError("Le Mob source doit appartenir au même utilisateur que la Table.")

    def __str__(self):
        return self.name
