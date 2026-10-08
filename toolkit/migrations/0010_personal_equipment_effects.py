from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("toolkit", "0009_userfolder")]

    operations = [
        migrations.AddField(model_name="userweapon", name="effect_type", field=models.CharField(blank=True, default="", max_length=40)),
        migrations.AddField(model_name="userweapon", name="scaling", field=models.CharField(default="fixed", max_length=10)),
        migrations.AddField(model_name="userweapon", name="value", field=models.IntegerField(default=0)),
        migrations.AddField(model_name="userimplant", name="effect_type", field=models.CharField(blank=True, default="", max_length=40)),
        migrations.AddField(model_name="userimplant", name="scaling", field=models.CharField(default="fixed", max_length=10)),
        migrations.AddField(model_name="userimplant", name="value", field=models.IntegerField(default=0)),
    ]
