from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("toolkit", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="TableMob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("profile", models.CharField(choices=[("C", "Combattant"), ("A", "Assassin"), ("T", "Tireur"), ("S", "Soutien"), ("K", "Contrôle")], max_length=1)),
                ("level", models.PositiveSmallIntegerField(default=1)),
                ("payload", models.JSONField(default=dict)),
                ("rank", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("game_table", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="builder_mobs", to="toolkit.gametable")),
            ],
            options={"ordering": ["rank", "id"]},
        ),
    ]
