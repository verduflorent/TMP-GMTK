from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("toolkit", "0006_userimplant")]
    operations = [
        migrations.CreateModel(
            name="TableCondition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("mob", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="conditions", to="toolkit.tablemob")),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
