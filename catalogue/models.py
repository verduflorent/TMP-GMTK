from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class EquipmentDefinition(models.Model):
    class Kind(models.TextChoices):
        WEAPON = "WEAPON", "Arme"
        ACCESSORY = "ACCESSORY", "Accessoire"
        IMPLANT = "IMPLANT", "Implant"
        GADGET = "GADGET", "Gadget"
        PERK = "PERK", "Perk"
        ARMOR = "ARMOR", "GPB"
        BIOCHIP = "BIOCHIP", "Biopuce"
        DRUG = "DRUG", "D.R.U.G."

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="equipment_definitions",
        null=True,
        blank=True,
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_native_reference = models.BooleanField(default=False)
    source_key = models.CharField(max_length=120, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "name"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(is_native_reference=False) | Q(owner__isnull=True)),
                name="native_definition_has_no_owner",
            )
        ]

    def clean(self):
        super().clean()
        if self.is_native_reference and self.owner_id is not None:
            raise ValidationError("Une référence native TMP ne peut appartenir à un compte privé.")
        if not self.is_native_reference and self.owner_id is None:
            raise ValidationError("Une définition locale doit appartenir à un utilisateur.")

    def __str__(self):
        return self.name


class CatalogueEntry(models.Model):
    class Rarity(models.TextChoices):
        COMMON = "COMMON", "Commun"
        UNCOMMON = "UNCOMMON", "Peu commun"
        RARE = "RARE", "Rare"
        VERY_RARE = "VERY_RARE", "Très rare"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="catalogue_entries")
    native_definition = models.ForeignKey(
        EquipmentDefinition,
        on_delete=models.PROTECT,
        related_name="native_entries",
        null=True,
        blank=True,
    )
    local_definition = models.OneToOneField(
        EquipmentDefinition,
        on_delete=models.PROTECT,
        related_name="local_entry",
        null=True,
        blank=True,
    )
    allow_mob = models.BooleanField(default=False)
    allow_elite = models.BooleanField(default=False)
    mob_rarity = models.CharField(max_length=20, choices=Rarity.choices, default=Rarity.COMMON)
    elite_rarity = models.CharField(max_length=20, choices=Rarity.choices, default=Rarity.COMMON)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(native_definition__isnull=False) | Q(local_definition__isnull=False),
                name="catalogue_entry_has_definition",
            ),
            models.UniqueConstraint(
                fields=["owner", "native_definition"],
                condition=Q(native_definition__isnull=False),
                name="unique_native_entry_per_owner",
            ),
        ]

    @property
    def active_definition(self):
        return self.local_definition or self.native_definition

    def clean(self):
        super().clean()
        if not self.native_definition_id and not self.local_definition_id:
            raise ValidationError("Une entrée de catalogue doit avoir une définition active ou native.")
        if self.native_definition_id and not self.native_definition.is_native_reference:
            raise ValidationError("native_definition doit référencer une définition native TMP.")
        if self.local_definition_id:
            if self.local_definition.is_native_reference:
                raise ValidationError("local_definition ne peut pas être une référence native.")
            if self.local_definition.owner_id != self.owner_id:
                raise ValidationError("La définition locale doit appartenir au même utilisateur.")
        if self.native_definition_id and self.local_definition_id and self.native_definition.kind != self.local_definition.kind:
            raise ValidationError("Une personnalisation locale doit conserver la nature de sa référence native.")

    def __str__(self):
        definition = self.active_definition
        return definition.name if definition else f"CatalogueEntry #{self.pk}"


class WeaponProfile(models.Model):
    """Structured mechanical profile; values come from the catalogue, not the rules engine."""

    class Stat(models.TextChoices):
        FORCE = "FOR", "Force"
        AGILITY = "AGI", "Agilité"
        PERCEPTION = "PER", "Perception"
        TECHNIQUE = "TEC", "Technique"

    class Weight(models.TextChoices):
        LIGHT = "LIGHT", "Légère"
        MEDIUM = "MEDIUM", "Moyenne"
        HEAVY = "HEAVY", "Lourde"

    class Slot(models.TextChoices):
        PRIMARY = "PRIMARY", "Principale"
        SECONDARY = "SECONDARY", "Secondaire"

    class Range(models.TextChoices):
        CONTACT = "CONTACT", "Contact"
        SHORT = "SHORT", "Courte"
        MEDIUM = "MEDIUM", "Moyenne"
        LONG = "LONG", "Longue"

    definition = models.OneToOneField(
        EquipmentDefinition, on_delete=models.CASCADE, related_name="weapon_profile"
    )
    stat = models.CharField(max_length=3, choices=Stat.choices)
    weight = models.CharField(max_length=10, choices=Weight.choices)
    slot = models.CharField(max_length=10, choices=Slot.choices)
    optimal_range = models.CharField(max_length=10, choices=Range.choices)
    power = models.IntegerField(default=0)
    minimum_force = models.PositiveSmallIntegerField(null=True, blank=True)
    profile_label = models.CharField(max_length=40, blank=True)

    def clean(self):
        super().clean()
        if self.definition.kind != EquipmentDefinition.Kind.WEAPON:
            raise ValidationError("Un profil d’arme doit appartenir à une définition d’arme.")


class WeaponVariant(models.Model):
    """Ascend/Overcome configuration of the same weapon definition."""

    class Path(models.TextChoices):
        ASCEND = "ASCEND", "Ascend"
        OVERCOME = "OVERCOME", "Overcome"

    weapon = models.ForeignKey(WeaponProfile, on_delete=models.CASCADE, related_name="variants")
    path = models.CharField(max_length=10, choices=Path.choices)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    stat = models.CharField(max_length=3, choices=WeaponProfile.Stat.choices, blank=True)
    weight = models.CharField(max_length=10, choices=WeaponProfile.Weight.choices, blank=True)
    slot = models.CharField(max_length=10, choices=WeaponProfile.Slot.choices, blank=True)
    optimal_range = models.CharField(max_length=10, choices=WeaponProfile.Range.choices, blank=True)
    power = models.IntegerField(null=True, blank=True)
    minimum_force = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["weapon", "path"], name="unique_weapon_variant_path")
        ]


class StructuredEffect(models.Model):
    """Small, explicit effects GMTK can calculate; tactical prose remains descriptive."""

    class Target(models.TextChoices):
        POWER = "POWER", "Puissance"
        AIM = "AIM", "Visée"
        CRITICAL = "CRITICAL", "Critique"
        DELTA = "DELTA", "Coefficient Delta"
        MAX_HP = "MAX_HP", "PV max"
        ARMOR = "ARMOR", "Armure"
        CRITICAL_RESISTANCE = "CRITICAL_RESISTANCE", "Résistance critique"
        REACTIONS = "REACTIONS", "Réactions"
        IGNORED_ARMOR = "IGNORED_ARMOR", "Armure ignorée"

    definition = models.ForeignKey(
        EquipmentDefinition, on_delete=models.CASCADE, related_name="structured_effects"
    )
    target = models.CharField(max_length=30, choices=Target.choices)
    value = models.IntegerField()
    condition_key = models.CharField(
        max_length=80,
        blank=True,
        help_text="Condition explicite du jet, ex. target_marked, target_robot, toggle_icarus.",
    )
    description = models.CharField(max_length=200, blank=True)
