import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("scenarios", "0003_scenarioimportreceipt")]

    operations = [
        migrations.CreateModel(
            name="ScenarioSplash",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("data", models.BinaryField()),
                ("content_type", models.CharField(default="image/webp", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("scenario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="splash_images", to="scenarios.scenario")),
            ],
        ),
    ]
