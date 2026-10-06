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
    weapon_index = forms.IntegerField(min_value=0, required=False)
    action = forms.ChoiceField(choices=[("add", "Ajouter"), ("replace", "Remplacer"), ("remove", "Retirer")])
    weapon_id = forms.IntegerField(min_value=1, required=False)


class MobFieldOverrideForm(forms.Form):
    index = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    field = forms.ChoiceField(
        choices=[
            ("force", "FOR"), ("agility", "AGI"), ("perception", "PER"),
            ("technique", "TECH"), ("constitution", "CON"), ("willpower", "VOL"),
            ("level", "Niveau"), ("max_hp", "PV"), ("armor", "Armure"), ("shield", "PB"),
            ("reactions", "Réactions"), ("vigilance", "Vigilance"),
        ]
    )
    value = forms.IntegerField(min_value=0)


class MobImplantForm(forms.Form):
    index = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    implant_index = forms.IntegerField(min_value=0, required=False)
    action = forms.ChoiceField(choices=[("add", "Ajouter"), ("replace", "Remplacer"), ("remove", "Retirer")])
    implant_id = forms.IntegerField(min_value=1, required=False)


ABILITY_EFFECT_CHOICES = [
    ("damage_contact", "Dégâts Contact"),
    ("damage_distance", "Dégâts Distance"),
    ("aim", "Visée"),
    ("armor", "Armure"),
    ("shield", "PB"),
    ("healing", "Soin"),
    ("max_hp", "PV"),
    ("reactions", "Réactions"),
    ("vigilance", "Vigilance"),
]


class MobAbilityForm(forms.Form):
    index = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    ability_index = forms.IntegerField(min_value=0, required=False)
    action = forms.ChoiceField(choices=[("add", "Ajouter"), ("remove", "Retirer")])
    name = forms.CharField(max_length=120, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    effect_type = forms.ChoiceField(choices=ABILITY_EFFECT_CHOICES, required=False)
    scaling = forms.ChoiceField(choices=[("fixed", "Fixe"), ("level", "× Niveau")], required=False)
    value = forms.IntegerField(required=False)
    save_to_library = forms.BooleanField(required=False)


class BestiaryMobSaveForm(forms.Form):
    index = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    name = forms.CharField(max_length=120)


class MobAbilityLibraryForm(forms.Form):
    index = forms.IntegerField(min_value=0)
    ability_id = forms.IntegerField(min_value=1)
