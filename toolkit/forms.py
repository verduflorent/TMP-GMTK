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


class MobRoleForm(forms.Form):
    index = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    profile = forms.ChoiceField(
        label="Rôle",
        choices=[
            ("C", "Combattant"),
            ("A", "Assassin"),
            ("T", "Tireur"),
            ("S", "Soutien"),
            ("K", "Contrôle"),
        ],
    )


class MobWeaponForm(forms.Form):
    index = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    slot = forms.ChoiceField(choices=[("primary", "Principale"), ("secondary", "Secondaire")], widget=forms.HiddenInput)
    weapon_id = forms.IntegerField(min_value=1)
