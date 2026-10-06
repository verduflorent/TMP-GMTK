from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="MobImplant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("allowed_profiles", models.CharField(help_text="Profils autorisés parmi C/A/T/S/K.", max_length=5)),
                ("property_name", models.CharField(blank=True, max_length=120)),
                ("property_text", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="MobWeapon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("tier", models.PositiveSmallIntegerField(choices=[(1, "T1"), (2, "T2"), (3, "T3"), (4, "T4")])),
                ("allowed_profiles", models.CharField(blank=True, help_text="Profils autorisés parmi C/A/T/S/K. Vide = universel.", max_length=5)),
                ("hands", models.PositiveSmallIntegerField(choices=[(1, "1 main"), (2, "2 mains")])),
                ("optimal_range", models.CharField(choices=[("CONTACT", "Contact"), ("SHORT", "Courte"), ("MEDIUM", "Moyenne"), ("LONG", "Longue")], max_length=10)),
                ("power", models.IntegerField(default=0)),
                ("aim", models.IntegerField(default=0)),
                ("property_name", models.CharField(blank=True, max_length=120)),
                ("property_text", models.TextField(blank=True)),
                ("is_control", models.BooleanField(default=False)),
            ],
            options={"ordering": ["tier", "name"]},
        ),
    ]
