from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalogue", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Folder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(choices=[("BESTIARY", "Bestiaire"), ("SCENARIOS", "Scénarios")], max_length=20)),
                ("name", models.CharField(max_length=120)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="folders", to=settings.AUTH_USER_MODEL)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="children", to="toolkit.folder")),
            ],
            options={"ordering": ["domain", "name"]},
        ),
        migrations.AddConstraint(
            model_name="folder",
            constraint=models.UniqueConstraint(fields=("owner", "domain", "parent", "name"), name="unique_folder_name_per_parent"),
        ),
        migrations.CreateModel(
            name="TechniqueSpecialization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=80)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="GameTable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="game_table", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="RandomizerSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="randomizer_settings", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="RollHistoryEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("actor_name", models.CharField(max_length=120)),
                ("roll_type", models.CharField(max_length=60)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="roll_history", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
        migrations.CreateModel(
            name="CharacterProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("character_type", models.CharField(choices=[("MOB", "Mob"), ("ELITE", "Élite"), ("NPC", "PNJ"), ("ANTAGONIST", "Antagoniste"), ("HERO", "Héros / opérateur")], max_length=20)),
                ("faction", models.CharField(blank=True, max_length=120)),
                ("mode", models.CharField(choices=[("STANDARD", "Standard"), ("EVOLUTION", "Évolution")], default="STANDARD", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("folder", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="character_profiles", to="toolkit.folder")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="character_profiles", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Encounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("folder", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="encounters", to="toolkit.folder")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="encounters", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="CharacterVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("level", models.PositiveSmallIntegerField(default=1)),
                ("force", models.PositiveSmallIntegerField(default=5)),
                ("agility", models.PositiveSmallIntegerField(default=5)),
                ("perception", models.PositiveSmallIntegerField(default=5)),
                ("technique", models.PositiveSmallIntegerField(default=5)),
                ("constitution", models.PositiveSmallIntegerField(default=8)),
                ("willpower", models.PositiveSmallIntegerField(default=8)),
                ("base_armor", models.PositiveSmallIntegerField(default=0)),
                ("is_validated", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("offensive_perk_18", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="catalogue.catalogueentry")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="toolkit.characterprofile")),
                ("technique_specialization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="toolkit.techniquespecialization")),
            ],
            options={"ordering": ["profile", "level"]},
        ),
        migrations.AddConstraint(
            model_name="characterversion",
            constraint=models.UniqueConstraint(fields=("profile", "level"), name="unique_profile_level"),
        ),
        migrations.CreateModel(
            name="TableInstance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("level", models.PositiveSmallIntegerField(default=1)),
                ("force", models.PositiveSmallIntegerField(default=5)),
                ("agility", models.PositiveSmallIntegerField(default=5)),
                ("perception", models.PositiveSmallIntegerField(default=5)),
                ("technique", models.PositiveSmallIntegerField(default=5)),
                ("constitution", models.PositiveSmallIntegerField(default=8)),
                ("willpower", models.PositiveSmallIntegerField(default=8)),
                ("base_armor", models.PositiveSmallIntegerField(default=0)),
                ("name", models.CharField(max_length=120)),
                ("character_type", models.CharField(choices=[("MOB", "Mob"), ("ELITE", "Élite"), ("NPC", "PNJ"), ("ANTAGONIST", "Antagoniste"), ("HERO", "Héros / opérateur")], max_length=20)),
                ("faction", models.CharField(blank=True, max_length=120)),
                ("current_hp", models.PositiveIntegerField(default=0)),
                ("camp", models.CharField(choices=[("ALLY", "Allié"), ("ENEMY", "Ennemi")], default="ENEMY", max_length=10)),
                ("rank", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("game_table", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="instances", to="toolkit.gametable")),
                ("offensive_perk_18", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="catalogue.catalogueentry")),
                ("source_version", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="table_instances", to="toolkit.characterversion")),
                ("technique_specialization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="toolkit.techniquespecialization")),
            ],
            options={"ordering": ["camp", "rank", "id"]},
        ),
        migrations.CreateModel(
            name="EncounterEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("camp", models.CharField(choices=[("ALLY", "Allié"), ("ENEMY", "Ennemi")], default="ENEMY", max_length=10)),
                ("rank", models.PositiveIntegerField(default=0)),
                ("character_version", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="encounter_entries", to="toolkit.characterversion")),
                ("encounter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="entries", to="toolkit.encounter")),
            ],
            options={"ordering": ["rank", "id"]},
        ),
        migrations.AddConstraint(
            model_name="encounterentry",
            constraint=models.CheckConstraint(condition=Q(("quantity__gte", 1)), name="encounter_quantity_positive"),
        ),
        migrations.CreateModel(
            name="EquipmentAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slot", models.CharField(max_length=40)),
                ("position", models.PositiveSmallIntegerField(default=0)),
                ("catalogue_entry", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assignments", to="catalogue.catalogueentry")),
                ("instance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="equipment_assignments", to="toolkit.tableinstance")),
                ("mounted_on", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="mounted_accessories", to="toolkit.equipmentassignment")),
                ("version", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="equipment_assignments", to="toolkit.characterversion")),
            ],
        ),
        migrations.AddConstraint(
            model_name="equipmentassignment",
            constraint=models.CheckConstraint(condition=Q(Q(("instance__isnull", True), ("version__isnull", False)), Q(("instance__isnull", False), ("version__isnull", True)), _connector="OR"), name="assignment_exactly_one_owner"),
        ),
        migrations.CreateModel(
            name="AbilityException",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("ADD", "Ajouter"), ("REMOVE", "Retirer")], max_length=10)),
                ("instance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="ability_exceptions", to="toolkit.tableinstance")),
                ("perk", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ability_exceptions", to="catalogue.catalogueentry")),
                ("version", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="ability_exceptions", to="toolkit.characterversion")),
            ],
        ),
        migrations.AddConstraint(
            model_name="abilityexception",
            constraint=models.CheckConstraint(condition=Q(Q(("instance__isnull", True), ("version__isnull", False)), Q(("instance__isnull", False), ("version__isnull", True)), _connector="OR"), name="ability_exception_exactly_one_owner"),
        ),
        migrations.CreateModel(
            name="Override",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target", models.CharField(choices=[("MAX_HP", "PV max"), ("TOTAL_ARMOR", "Armure totale"), ("MAX_REACTIONS", "Réactions max"), ("WEAPON_POWER", "Puissance d'arme"), ("DELTA_COEFFICIENT", "Coefficient Delta"), ("MAIN_SLOTS", "Slots principaux"), ("SECONDARY_SLOTS", "Slots secondaires"), ("GADGET_SLOTS", "Slots gadgets"), ("IMPLANT_SLOTS", "Slots implants")], max_length=30)),
                ("value", models.IntegerField()),
                ("equipment_assignment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="overrides", to="toolkit.equipmentassignment")),
                ("instance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="overrides", to="toolkit.tableinstance")),
                ("version", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="overrides", to="toolkit.characterversion")),
            ],
        ),
        migrations.AddConstraint(
            model_name="override",
            constraint=models.CheckConstraint(condition=Q(Q(("instance__isnull", True), ("version__isnull", False)), Q(("instance__isnull", False), ("version__isnull", True)), _connector="OR"), name="override_exactly_one_owner"),
        ),
        migrations.CreateModel(
            name="RollContribution",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=120)),
                ("value", models.CharField(max_length=120)),
                ("ordinal", models.PositiveSmallIntegerField(default=0)),
                ("entry", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contributions", to="toolkit.rollhistoryentry")),
            ],
            options={"ordering": ["ordinal", "id"]},
        ),
        migrations.CreateModel(
            name="RollDie",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ordinal", models.PositiveSmallIntegerField()),
                ("value", models.PositiveSmallIntegerField()),
                ("selected", models.BooleanField(default=False)),
                ("entry", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dice", to="toolkit.rollhistoryentry")),
            ],
            options={"ordering": ["ordinal"]},
        ),
        migrations.AddConstraint(
            model_name="rolldie",
            constraint=models.UniqueConstraint(fields=("entry", "ordinal"), name="unique_roll_die_ordinal"),
        ),
    ]
