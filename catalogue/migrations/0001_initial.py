from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="EquipmentDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("WEAPON", "Arme"), ("ACCESSORY", "Accessoire"), ("IMPLANT", "Implant"), ("GADGET", "Gadget"), ("PERK", "Perk")], max_length=20)),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("is_native_reference", models.BooleanField(default=False)),
                ("source_key", models.CharField(blank=True, max_length=120, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="equipment_definitions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["kind", "name"]},
        ),
        migrations.AddConstraint(
            model_name="equipmentdefinition",
            constraint=models.CheckConstraint(condition=Q(("is_native_reference", False), ("owner__isnull", True), _connector="OR"), name="native_definition_has_no_owner"),
        ),
        migrations.CreateModel(
            name="CatalogueEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("allow_mob", models.BooleanField(default=False)),
                ("allow_elite", models.BooleanField(default=False)),
                ("mob_rarity", models.CharField(choices=[("COMMON", "Commun"), ("UNCOMMON", "Peu commun"), ("RARE", "Rare"), ("VERY_RARE", "Très rare")], default="COMMON", max_length=20)),
                ("elite_rarity", models.CharField(choices=[("COMMON", "Commun"), ("UNCOMMON", "Peu commun"), ("RARE", "Rare"), ("VERY_RARE", "Très rare")], default="COMMON", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("local_definition", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="local_entry", to="catalogue.equipmentdefinition")),
                ("native_definition", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="native_entries", to="catalogue.equipmentdefinition")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="catalogue_entries", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="catalogueentry",
            constraint=models.CheckConstraint(condition=Q(("native_definition__isnull", False), ("local_definition__isnull", False), _connector="OR"), name="catalogue_entry_has_definition"),
        ),
        migrations.AddConstraint(
            model_name="catalogueentry",
            constraint=models.UniqueConstraint(condition=Q(("native_definition__isnull", False)), fields=("owner", "native_definition"), name="unique_native_entry_per_owner"),
        ),
    ]
