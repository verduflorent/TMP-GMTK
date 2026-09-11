from django.contrib import admin

from .models import (
    AbilityException,
    CharacterProfile,
    CharacterVersion,
    Encounter,
    EncounterEntry,
    EquipmentAssignment,
    Folder,
    GameTable,
    Override,
    RandomizerSettings,
    RollContribution,
    RollDie,
    RollHistoryEntry,
    TableInstance,
    TechniqueSpecialization,
)

for model in (
    Folder,
    CharacterProfile,
    CharacterVersion,
    TechniqueSpecialization,
    GameTable,
    TableInstance,
    Encounter,
    EncounterEntry,
    EquipmentAssignment,
    AbilityException,
    Override,
    RollHistoryEntry,
    RollDie,
    RollContribution,
    RandomizerSettings,
):
    admin.site.register(model)
