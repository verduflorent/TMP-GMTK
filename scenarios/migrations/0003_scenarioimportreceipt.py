from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0002_scenariocreatereceipt"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ScenarioImportReceipt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.UUIDField()),
                ("fingerprint", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scenario_import_receipts", to=settings.AUTH_USER_MODEL)),
                ("scenario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="scenarios.scenario")),
            ],
        ),
        migrations.AddConstraint(
            model_name="scenarioimportreceipt",
            constraint=models.UniqueConstraint(fields=("owner", "key"), name="scenario_import_receipt_owner_key"),
        ),
    ]
