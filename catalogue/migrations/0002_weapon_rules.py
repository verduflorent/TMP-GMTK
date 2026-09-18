# Generated manually for PR2 catalogue reconciliation.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("catalogue", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="equipmentdefinition",
            name="kind",
            field=models.CharField(
                choices=[
                    ("WEAPON", "Arme"), ("ACCESSORY", "Accessoire"), ("IMPLANT", "Implant"),
                    ("GADGET", "Gadget"), ("PERK", "Perk"), ("ARMOR", "GPB"),
                    ("BIOCHIP", "Biopuce"), ("DRUG", "D.R.U.G."),
                ],
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="WeaponProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stat", models.CharField(choices=[("FOR", "Force"), ("AGI", "Agilité"), ("PER", "Perception"), ("TEC", "Technique")], max_length=3)),
                ("weight", models.CharField(choices=[("LIGHT", "Légère"), ("MEDIUM", "Moyenne"), ("HEAVY", "Lourde")], max_length=10)),
                ("slot", models.CharField(choices=[("PRIMARY", "Principale"), ("SECONDARY", "Secondaire")], max_length=10)),
                ("optimal_range", models.CharField(choices=[("CONTACT", "Contact"), ("SHORT", "Courte"), ("MEDIUM", "Moyenne"), ("LONG", "Longue")], max_length=10)),
                ("power", models.IntegerField(default=0)),
                ("minimum_force", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("profile_label", models.CharField(blank=True, max_length=40)),
                ("definition", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="weapon_profile", to="catalogue.equipmentdefinition")),
            ],
        ),
        migrations.CreateModel(
            name="WeaponVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(choices=[("ASCEND", "Ascend"), ("OVERCOME", "Overcome")], max_length=10)),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("stat", models.CharField(blank=True, choices=[("FOR", "Force"), ("AGI", "Agilité"), ("PER", "Perception"), ("TEC", "Technique")], max_length=3)),
                ("weight", models.CharField(blank=True, choices=[("LIGHT", "Légère"), ("MEDIUM", "Moyenne"), ("HEAVY", "Lourde")], max_length=10)),
                ("slot", models.CharField(blank=True, choices=[("PRIMARY", "Principale"), ("SECONDARY", "Secondaire")], max_length=10)),
                ("optimal_range", models.CharField(blank=True, choices=[("CONTACT", "Contact"), ("SHORT", "Courte"), ("MEDIUM", "Moyenne"), ("LONG", "Longue")], max_length=10)),
                ("power", models.IntegerField(blank=True, null=True)),
                ("minimum_force", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("weapon", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="catalogue.weaponprofile")),
            ],
        ),
        migrations.AddConstraint(
            model_name="weaponvariant",
            constraint=models.UniqueConstraint(fields=("weapon", "path"), name="unique_weapon_variant_path"),
        ),
        migrations.CreateModel(
            name="StructuredEffect",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target", models.CharField(choices=[("POWER", "Puissance"), ("AIM", "Visée"), ("CRITICAL", "Critique"), ("DELTA", "Coefficient Delta"), ("MAX_HP", "PV max"), ("ARMOR", "Armure"), ("CRITICAL_RESISTANCE", "Résistance critique"), ("REACTIONS", "Réactions"), ("IGNORED_ARMOR", "Armure ignorée")], max_length=30)),
                ("value", models.IntegerField()),
                ("condition_key", models.CharField(blank=True, help_text="Condition explicite du jet, ex. target_marked, target_robot, toggle_icarus.", max_length=80)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("definition", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="structured_effects", to="catalogue.equipmentdefinition")),
            ],
        ),
    ]
