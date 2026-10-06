from django.contrib import admin

from .models import BestiaryMob, Encounter, EncounterMob, GameTable, TableInstance

for model in (BestiaryMob, Encounter, EncounterMob, GameTable, TableInstance):
    admin.site.register(model)
