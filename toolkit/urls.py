from django.urls import path

from . import views

urlpatterns = [
    path("", views.table_home, name="table"),
    path("monster-builder/", views.monster_builder, name="monster_builder"),
    path("monster-builder/role/", views.monster_builder_role, name="monster_builder_role"),
    path("monster-builder/weapon/", views.monster_builder_weapon, name="monster_builder_weapon"),
    path("monster-builder/weapon/user/create/", views.monster_builder_user_weapon_create, name="monster_builder_user_weapon_create"),
    path("monster-builder/weapon/user/add/", views.monster_builder_user_weapon_add, name="monster_builder_user_weapon_add"),
    path("monster-builder/field/", views.monster_builder_field, name="monster_builder_field"),
    path("monster-builder/implant/", views.monster_builder_implant, name="monster_builder_implant"),
    path("monster-builder/implant/user/create/", views.monster_builder_user_implant_create, name="monster_builder_user_implant_create"),
    path("monster-builder/implant/user/add/", views.monster_builder_user_implant_add, name="monster_builder_user_implant_add"),
    path("monster-builder/ability/", views.monster_builder_ability, name="monster_builder_ability"),
    path("monster-builder/ability/library/", views.monster_builder_ability_library, name="monster_builder_ability_library"),
    path("ability-library/<int:ability_id>/delete/", views.ability_library_delete, name="ability_library_delete"),
    path("monster-builder/validate/", views.monster_builder_validate, name="monster_builder_validate"),
    path("monster-builder/save/", views.monster_builder_save, name="monster_builder_save"),
    path("bestiary/", views.bestiary_home, name="bestiary"),
    path("bestiary/<int:mob_id>/load/", views.bestiary_load, name="bestiary_load"),
    path("bestiary/<int:mob_id>/duplicate/", views.bestiary_duplicate, name="bestiary_duplicate"),
    path("bestiary/<int:mob_id>/delete/", views.bestiary_delete, name="bestiary_delete"),
    path("table/mob/<int:mob_id>/edit/", views.table_mob_edit, name="table_mob_edit"),
    path("table/mob/<int:mob_id>/delete/", views.table_mob_delete, name="table_mob_delete"),
    path("table/mob/<int:mob_id>/resource/", views.table_mob_resource, name="table_mob_resource"),
    path("table/mob/<int:mob_id>/weapon/<int:weapon_index>/roll/", views.table_mob_roll_weapon, name="table_mob_roll_weapon"),
    path("table/mob/<int:mob_id>/roll/", views.table_mob_roll_stat, name="table_mob_roll_stat"),
    path("table/next-round/", views.table_next_round, name="table_next_round"),
    path("table/mob/<int:mob_id>/condition/add/", views.table_condition_add, name="table_condition_add"),
    path("table/mob/<int:mob_id>/condition/<int:condition_id>/delete/", views.table_condition_delete, name="table_condition_delete"),
]
