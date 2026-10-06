from django import forms


class MonsterBuilderForm(forms.Form):
    quantity = forms.IntegerField(
        label="Nombre de Mobs",
        min_value=1,
        max_value=50,
        initial=5,
    )
    level = forms.IntegerField(
        label="Niveau",
        min_value=1,
        max_value=99,
        initial=1,
    )
