from django import forms

from .models import Chore
from .models import HouseholdSettings
from .models import Kid


DUE_DAY_CHOICES = [
    (Chore.SUNDAY, "Sunday"),
    (Chore.MONDAY, "Monday"),
    (Chore.TUESDAY, "Tuesday"),
    (Chore.WEDNESDAY, "Wednesday"),
    (Chore.THURSDAY, "Thursday"),
    (Chore.FRIDAY, "Friday"),
    (Chore.SATURDAY, "Saturday"),
]


class KidForm(forms.ModelForm):
    class Meta:
        model = Kid
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter a kid name.")
        return name


class ChoreForm(forms.ModelForm):
    due_days = forms.MultipleChoiceField(
        choices=DUE_DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": "Select at least one due day."},
    )

    class Meta:
        model = Chore
        fields = ["name", "kid", "due_days"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kid"].queryset = Kid.objects.all()
        self.fields["kid"].empty_label = "Choose a kid"

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter a chore name.")
        return name

    def clean_due_days(self):
        return [int(due_day) for due_day in self.cleaned_data["due_days"]]


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
