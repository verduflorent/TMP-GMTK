from django.urls import path

from . import views

urlpatterns = [
    path("", views.table_home, name="table"),
    path("monster-builder/", views.monster_builder, name="monster_builder"),
    path("monster-builder/role/", views.monster_builder_role, name="monster_builder_role"),
    path("monster-builder/weapon/", views.monster_builder_weapon, name="monster_builder_weapon"),
    path("monster-builder/field/", views.monster_builder_field, name="monster_builder_field"),
    path("monster-builder/implant/", views.monster_builder_implant, name="monster_builder_implant"),
    path("monster-builder/ability/", views.monster_builder_ability, name="monster_builder_ability"),
]
