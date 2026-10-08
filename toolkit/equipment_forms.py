"""Personal equipment library forms, reusing the existing ability effect contract."""
from django import forms
from .models import UserWeapon, UserImplant, UserAbility
from .forms import ABILITY_EFFECT_CHOICES

FRENCH_LABELS = {"name": "Nom", "hands": "Prise en main", "optimal_range": "Portée", "power": "Puissance", "aim": "Visée", "property_name": "Propriété", "property_text": "Description de la propriété", "description": "Description", "effect_type": "Effet mécanique", "scaling": "Calcul", "value": "Valeur"}


class FrenchEquipmentForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, label in FRENCH_LABELS.items():
            if key in self.fields:
                self.fields[key].label = label



class WeaponLibraryForm(FrenchEquipmentForm, forms.ModelForm):
    hands = forms.TypedChoiceField(choices=((1, "1 main"), (2, "2 mains")), coerce=int)
    optimal_range = forms.ChoiceField(choices=(
        ("CONTACT", "Contact"), ("SHORT", "Courte"),
        ("MEDIUM", "Moyenne"), ("LONG", "Longue"),
    ))

    effect_type = forms.ChoiceField(choices=[("", "Aucun effet mécanique"), *ABILITY_EFFECT_CHOICES], required=False)
    scaling = forms.ChoiceField(choices=(("fixed", "Fixe"), ("level", "Par niveau")), required=False, initial="fixed")
    value = forms.IntegerField(required=False, initial=0)

    def clean(self):
        data = super().clean()
        data["scaling"] = data.get("scaling") or "fixed"
        data["value"] = data.get("value") if data.get("value") is not None else 0
        return data

    class Meta:
        model = UserWeapon
        fields = ("name", "hands", "optimal_range", "power", "aim", "property_name", "property_text", "effect_type", "scaling", "value")


class ImplantLibraryForm(FrenchEquipmentForm, forms.ModelForm):
    effect_type = forms.ChoiceField(choices=[("", "Aucun effet mécanique"), *ABILITY_EFFECT_CHOICES], required=False)
    scaling = forms.ChoiceField(choices=(("fixed", "Fixe"), ("level", "Par niveau")), required=False, initial="fixed")
    value = forms.IntegerField(required=False, initial=0)

    def clean(self):
        data = super().clean()
        data["scaling"] = data.get("scaling") or "fixed"
        data["value"] = data.get("value") if data.get("value") is not None else 0
        return data

    class Meta:
        model = UserImplant
        fields = ("name", "property_name", "property_text", "effect_type", "scaling", "value")


class AbilityLibraryForm(FrenchEquipmentForm, forms.ModelForm):
    effect_type = forms.ChoiceField(
        choices=[("", "Aucun effet mécanique"), *ABILITY_EFFECT_CHOICES],
        required=False,
    )
    scaling = forms.ChoiceField(choices=(("fixed", "Fixe"), ("level", "Par niveau")))

    class Meta:
        model = UserAbility
        fields = ("name", "description", "effect_type", "scaling", "value")


EQUIPMENT_FORMS = {
    "weapon": (UserWeapon, WeaponLibraryForm, "Armes"),
    "implant": (UserImplant, ImplantLibraryForm, "Implants"),
    "ability": (UserAbility, AbilityLibraryForm, "Capacités"),
}
