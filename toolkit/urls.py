from django.urls import path

from . import views

urlpatterns = [
    path("", views.table_home, name="table"),
    path("monster-builder/", views.monster_builder, name="monster_builder"),
]
