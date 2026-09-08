from django import forms

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
