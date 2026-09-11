from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from catalogue.models import CatalogueEntry


class Folder(models.Model):
    class Domain(models.TextChoices):
        BESTIARY = "BESTIARY", "Bestiaire"
        SCENARIOS = "SCENARIOS", "Scénarios"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="folders")
    domain = models.CharField(max_length=20, choices=Domain.choices)
    name = models.CharField(max_length=120)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")

    class Meta:
        ordering = ["domain", "name"]
        constraints = [models.UniqueConstraint(fields=["owner", "domain", "parent", "name"], name="unique_folder_name_per_parent")]

    def clean(self):
        super().clean()
        if self.parent_id:
            if self.parent_id == self.pk:
                raise ValidationError("Un dossier ne peut pas être son propre parent.")
            if self.parent.owner_id != self.owner_id or self.parent.domain != self.domain:
                raise ValidationError("Le parent doit appartenir au même utilisateur et au même arbre.")
            cursor = self.parent
            while cursor is not None:
                if cursor.pk == self.pk:
                    raise ValidationError("Un dossier ne peut pas être déplacé sous l'un de ses descendants.")
                cursor = cursor.parent

    def __str__(self):
        return self.name


class CharacterProfile(models.Model):
    class CharacterType(models.TextChoices):
        MOB = "MOB", "Mob"
        ELITE = "ELITE", "Élite"
        NPC = "NPC", "PNJ"
        ANTAGONIST = "ANTAGONIST", "Antagoniste"
        HERO = "HERO", "Héros / opérateur"

    class Mode(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        EVOLUTION = "EVOLUTION", "Évolution"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="character_profiles")
    name = models.CharField(max_length=120)
    character_type = models.CharField(max_length=20, choices=CharacterType.choices)
    faction = models.CharField(max_length=120, blank=True)
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.STANDARD)
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, null=True, blank=True, related_name="character_profiles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.folder_id and (self.folder.owner_id != self.owner_id or self.folder.domain != Folder.Domain.BESTIARY):
            raise ValidationError("Le dossier du profil doit appartenir au même utilisateur et au Bestiaire.")

    def __str__(self):
        return self.name


class TechniqueSpecialization(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CharacterBuildFields(models.Model):
    level = models.PositiveSmallIntegerField(default=1)
    force = models.PositiveSmallIntegerField(default=5)
    agility = models.PositiveSmallIntegerField(default=5)
    perception = models.PositiveSmallIntegerField(default=5)
    technique = models.PositiveSmallIntegerField(default=5)
    constitution = models.PositiveSmallIntegerField(default=8)
    willpower = models.PositiveSmallIntegerField(default=8)
    base_armor = models.PositiveSmallIntegerField(default=0)
    offensive_perk_18 = models.ForeignKey(
        CatalogueEntry,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    technique_specialization = models.ForeignKey(
        TechniqueSpecialization,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        abstract = True


class CharacterVersion(CharacterBuildFields):
    profile = models.ForeignKey(CharacterProfile, on_delete=models.CASCADE, related_name="versions")
    is_validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["profile", "level"]
        constraints = [models.UniqueConstraint(fields=["profile", "level"], name="unique_profile_level")]

    @property
    def owner(self):
        return self.profile.owner

    def __str__(self):
        return f"{self.profile.name} — N{self.level}"


class GameTable(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="game_table")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table de {self.owner}"


class TableInstance(CharacterBuildFields):
    class Camp(models.TextChoices):
        ALLY = "ALLY", "Allié"
        ENEMY = "ENEMY", "Ennemi"

    game_table = models.ForeignKey(GameTable, on_delete=models.CASCADE, related_name="instances")
    source_version = models.ForeignKey(CharacterVersion, on_delete=models.PROTECT, null=True, blank=True, related_name="table_instances")
    name = models.CharField(max_length=120)
    character_type = models.CharField(max_length=20, choices=CharacterProfile.CharacterType.choices)
    faction = models.CharField(max_length=120, blank=True)
    current_hp = models.PositiveIntegerField(default=0)
    camp = models.CharField(max_length=10, choices=Camp.choices, default=Camp.ENEMY)
    rank = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def owner(self):
        return self.game_table.owner

    def clean(self):
        super().clean()
        if self.source_version_id and self.source_version.profile.owner_id != self.game_table.owner_id:
            raise ValidationError("La version source doit appartenir au même utilisateur que la Table.")

    class Meta:
        ordering = ["camp", "rank", "id"]

    def __str__(self):
        return self.name


class Encounter(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="encounters")
    name = models.CharField(max_length=120)
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, null=True, blank=True, related_name="encounters")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.folder_id and (self.folder.owner_id != self.owner_id or self.folder.domain != Folder.Domain.SCENARIOS):
            raise ValidationError("Le dossier de rencontre doit appartenir au même utilisateur et à l'arbre Scénarios.")

    def __str__(self):
        return self.name


class EncounterEntry(models.Model):
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="entries")
    character_version = models.ForeignKey(CharacterVersion, on_delete=models.PROTECT, related_name="encounter_entries")
    quantity = models.PositiveIntegerField(default=1)
    camp = models.CharField(max_length=10, choices=TableInstance.Camp.choices, default=TableInstance.Camp.ENEMY)
    rank = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["rank", "id"]
        constraints = [models.CheckConstraint(condition=Q(quantity__gte=1), name="encounter_quantity_positive")]

    def clean(self):
        super().clean()
        if self.character_version.profile.owner_id != self.encounter.owner_id:
            raise ValidationError("Une rencontre ne peut pas référencer le profil d'un autre utilisateur.")


class EquipmentAssignment(models.Model):
    version = models.ForeignKey(CharacterVersion, on_delete=models.CASCADE, null=True, blank=True, related_name="equipment_assignments")
    instance = models.ForeignKey(TableInstance, on_delete=models.CASCADE, null=True, blank=True, related_name="equipment_assignments")
    catalogue_entry = models.ForeignKey(CatalogueEntry, on_delete=models.PROTECT, related_name="assignments")
    slot = models.CharField(max_length=40)
    position = models.PositiveSmallIntegerField(default=0)
    mounted_on = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="mounted_accessories")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(version__isnull=False, instance__isnull=True) | Q(version__isnull=True, instance__isnull=False)),
                name="assignment_exactly_one_owner",
            )
        ]

    @property
    def owner_id(self):
        if self.version_id:
            return self.version.profile.owner_id
        if self.instance_id:
            return self.instance.game_table.owner_id
        return None

    def clean(self):
        super().clean()
        if self.owner_id and self.catalogue_entry.owner_id != self.owner_id:
            raise ValidationError("L'équipement doit appartenir au même utilisateur que la fiche.")
        if self.mounted_on_id:
            if self.mounted_on_id == self.pk:
                raise ValidationError("Une occurrence ne peut pas être montée sur elle-même.")
            if self.mounted_on.owner_id != self.owner_id:
                raise ValidationError("Un accessoire doit être monté sur une arme de la même fiche.")
            if self.version_id != self.mounted_on.version_id or self.instance_id != self.mounted_on.instance_id:
                raise ValidationError("Le montage doit rester dans la même fiche.")


class AbilityException(models.Model):
    class Action(models.TextChoices):
        ADD = "ADD", "Ajouter"
        REMOVE = "REMOVE", "Retirer"

    version = models.ForeignKey(CharacterVersion, on_delete=models.CASCADE, null=True, blank=True, related_name="ability_exceptions")
    instance = models.ForeignKey(TableInstance, on_delete=models.CASCADE, null=True, blank=True, related_name="ability_exceptions")
    perk = models.ForeignKey(CatalogueEntry, on_delete=models.PROTECT, related_name="ability_exceptions")
    action = models.CharField(max_length=10, choices=Action.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(version__isnull=False, instance__isnull=True) | Q(version__isnull=True, instance__isnull=False)),
                name="ability_exception_exactly_one_owner",
            )
        ]

    def clean(self):
        super().clean()
        owner_id = self.version.profile.owner_id if self.version_id else self.instance.game_table.owner_id if self.instance_id else None
        if owner_id and self.perk.owner_id != owner_id:
            raise ValidationError("Le Perk doit appartenir au même utilisateur que la fiche.")


class Override(models.Model):
    class Target(models.TextChoices):
        MAX_HP = "MAX_HP", "PV max"
        TOTAL_ARMOR = "TOTAL_ARMOR", "Armure totale"
        MAX_REACTIONS = "MAX_REACTIONS", "Réactions max"
        WEAPON_POWER = "WEAPON_POWER", "Puissance d'arme"
        DELTA_COEFFICIENT = "DELTA_COEFFICIENT", "Coefficient Delta"
        MAIN_SLOTS = "MAIN_SLOTS", "Slots principaux"
        SECONDARY_SLOTS = "SECONDARY_SLOTS", "Slots secondaires"
        GADGET_SLOTS = "GADGET_SLOTS", "Slots gadgets"
        IMPLANT_SLOTS = "IMPLANT_SLOTS", "Slots implants"

    version = models.ForeignKey(CharacterVersion, on_delete=models.CASCADE, null=True, blank=True, related_name="overrides")
    instance = models.ForeignKey(TableInstance, on_delete=models.CASCADE, null=True, blank=True, related_name="overrides")
    target = models.CharField(max_length=30, choices=Target.choices)
    value = models.IntegerField()
    equipment_assignment = models.ForeignKey(EquipmentAssignment, on_delete=models.CASCADE, null=True, blank=True, related_name="overrides")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(version__isnull=False, instance__isnull=True) | Q(version__isnull=True, instance__isnull=False)),
                name="override_exactly_one_owner",
            )
        ]

    def clean(self):
        super().clean()
        if self.equipment_assignment_id:
            if self.version_id != self.equipment_assignment.version_id or self.instance_id != self.equipment_assignment.instance_id:
                raise ValidationError("Une override d'équipement doit cibler une occurrence de la même fiche.")


class RollHistoryEntry(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roll_history")
    actor_name = models.CharField(max_length=120)
    roll_type = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class RollDie(models.Model):
    entry = models.ForeignKey(RollHistoryEntry, on_delete=models.CASCADE, related_name="dice")
    ordinal = models.PositiveSmallIntegerField()
    value = models.PositiveSmallIntegerField()
    selected = models.BooleanField(default=False)

    class Meta:
        ordering = ["ordinal"]
        constraints = [models.UniqueConstraint(fields=["entry", "ordinal"], name="unique_roll_die_ordinal")]


class RollContribution(models.Model):
    entry = models.ForeignKey(RollHistoryEntry, on_delete=models.CASCADE, related_name="contributions")
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    ordinal = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordinal", "id"]


class RandomizerSettings(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="randomizer_settings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
