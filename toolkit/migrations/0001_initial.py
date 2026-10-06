from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalogue", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="GameTable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="game_table", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="BestiaryMob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("profile", models.CharField(choices=[("C", "Combattant"), ("A", "Assassin"), ("T", "Tireur"), ("S", "Soutien"), ("K", "Contrôle")], max_length=1)),
                ("level", models.PositiveSmallIntegerField(default=1)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("implant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="bestiary_mobs", to="catalogue.mobimplant")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bestiary_mobs", to=settings.AUTH_USER_MODEL)),
                ("weapon_primary", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="primary_bestiary_mobs", to="catalogue.mobweapon")),
                ("weapon_secondary", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="secondary_bestiary_mobs", to="catalogue.mobweapon")),
            ],
        ),
        migrations.CreateModel(
            name="Encounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="encounters", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="EncounterMob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("profile", models.CharField(choices=[("C", "Combattant"), ("A", "Assassin"), ("T", "Tireur"), ("S", "Soutien"), ("K", "Contrôle")], max_length=1)),
                ("level", models.PositiveSmallIntegerField(default=1)),
                ("current_hp", models.PositiveIntegerField()), ("max_hp", models.PositiveIntegerField()),
                ("armor", models.PositiveIntegerField(default=0)), ("shield", models.PositiveIntegerField(default=0)),
                ("reactions", models.PositiveSmallIntegerField(default=1)), ("vigilance", models.PositiveSmallIntegerField(default=1)),
                ("rank", models.PositiveIntegerField(default=0)), ("notes", models.TextField(blank=True)),
                ("encounter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mobs", to="toolkit.encounter")),
                ("implant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="encounter_mobs", to="catalogue.mobimplant")),
                ("source", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="encounter_instances", to="toolkit.bestiarymob")),
                ("weapon_primary", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="primary_encounter_mobs", to="catalogue.mobweapon")),
                ("weapon_secondary", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="secondary_encounter_mobs", to="catalogue.mobweapon")),
            ],
            options={"ordering":["rank","id"]},
        ),
        migrations.CreateModel(
            name="TableInstance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("profile", models.CharField(choices=[("C", "Combattant"), ("A", "Assassin"), ("T", "Tireur"), ("S", "Soutien"), ("K", "Contrôle")], max_length=1)),
                ("level", models.PositiveSmallIntegerField(default=1)),
                ("current_hp", models.PositiveIntegerField()), ("max_hp", models.PositiveIntegerField()),
                ("armor", models.PositiveIntegerField(default=0)), ("shield", models.PositiveIntegerField(default=0)),
                ("reactions", models.PositiveSmallIntegerField(default=1)), ("vigilance", models.PositiveSmallIntegerField(default=1)),
                ("rank", models.PositiveIntegerField(default=0)), ("notes", models.TextField(blank=True)),
                ("game_table", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="instances", to="toolkit.gametable")),
                ("implant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="table_instances", to="catalogue.mobimplant")),
                ("source", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="table_instances", to="toolkit.encountermob")),
                ("weapon_primary", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="primary_table_instances", to="catalogue.mobweapon")),
                ("weapon_secondary", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="secondary_table_instances", to="catalogue.mobweapon")),
            ],
            options={"ordering":["rank","id"]},
        ),
    ]
