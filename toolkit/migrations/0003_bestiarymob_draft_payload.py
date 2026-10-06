from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("toolkit", "0002_tablemob")]

    operations = [
        migrations.AddField(
            model_name="bestiarymob",
            name="draft_payload",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
