from django import forms

from .models import HouseholdSettings
from .models import Kid


class KidForm(forms.ModelForm):
    class Meta:
        model = Kid
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter a kid name.")
        return name


class ParentPinForm(forms.Form):
    pin = forms.CharField(
        label="Parent PIN",
        min_length=4,
        max_length=32,
        strip=True,
        widget=forms.PasswordInput,
    )


class SetParentPinForm(ParentPinForm):
    def clean_pin(self):
        pin = self.cleaned_data["pin"].strip()
        if HouseholdSettings.has_parent_pin():
            raise forms.ValidationError("A parent PIN already exists.")
        return pin
