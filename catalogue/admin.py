from django.contrib import admin

from .models import CatalogueEntry, EquipmentDefinition

admin.site.register(EquipmentDefinition)
admin.site.register(CatalogueEntry)
