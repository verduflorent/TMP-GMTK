from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("toolkit", "0008_encounterdraftmob"),
    ]
    operations = [
        migrations.CreateModel(
            name="UserFolder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="gmtk_folders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name", "id"]},
        ),
        migrations.AddConstraint(
            model_name="userfolder",
            constraint=models.UniqueConstraint(fields=("owner", "name"), name="unique_user_folder_name"),
        ),
        migrations.AddField(
            model_name="bestiarymob", name="folder",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="bestiary_mobs", to="toolkit.userfolder"),
        ),
        migrations.AddField(
            model_name="encounter", name="folder",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="encounters", to="toolkit.userfolder"),
        ),
    ]
