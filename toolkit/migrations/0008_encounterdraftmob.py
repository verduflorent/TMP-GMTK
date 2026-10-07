from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("toolkit", "0007_tablecondition")]
    operations = [
        migrations.CreateModel(
            name="EncounterDraftMob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("quantity", models.PositiveSmallIntegerField(default=1)),
                ("payload", models.JSONField(default=dict)),
                ("rank", models.PositiveIntegerField(default=0)),
                ("encounter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="draft_mobs", to="toolkit.encounter")),
            ],
            options={"ordering": ["rank", "id"]},
        ),
    ]
