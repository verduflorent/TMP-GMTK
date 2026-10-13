from django import forms
from toolkit.models import UserFolder
from .models import Scenario


class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ("title", "summary", "folder")
        widgets = {"summary": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["folder"].queryset = UserFolder.objects.filter(owner=owner)
        self.fields["folder"].required = False
