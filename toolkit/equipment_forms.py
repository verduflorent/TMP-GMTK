"""Personal equipment library forms, reusing the existing ability effect contract."""
from django import forms
from .models import UserWeapon, UserImplant, UserAbility
from .forms import ABILITY_EFFECT_CHOICES


class WeaponLibraryForm(forms.ModelForm):
    hands = forms.TypedChoiceField(choices=((1, "1 main"), (2, "2 mains")), coerce=int)
    optimal_range = forms.ChoiceField(choices=(
        ("CONTACT", "Contact"), ("SHORT", "Courte"),
        ("MEDIUM", "Moyenne"), ("LONG", "Longue"),
    ))

    class Meta:
        model = UserWeapon
        fields = ("name", "hands", "optimal_range", "power", "aim", "property_name", "property_text")


class ImplantLibraryForm(forms.ModelForm):
    class Meta:
        model = UserImplant
        fields = ("name", "property_name", "property_text")


class AbilityLibraryForm(forms.ModelForm):
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
