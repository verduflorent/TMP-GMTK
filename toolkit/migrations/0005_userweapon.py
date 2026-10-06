from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("toolkit", "0004_userability"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserWeapon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("hands", models.PositiveSmallIntegerField(default=1)),
                ("optimal_range", models.CharField(default="SHORT", max_length=10)),
                ("power", models.IntegerField(default=0)),
                ("aim", models.IntegerField(default=0)),
                ("property_name", models.CharField(blank=True, max_length=120)),
                ("property_text", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="monster_weapons", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
