from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import models


class Kid(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "Enter a kid name."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class HouseholdSettings(models.Model):
    parent_pin_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "household settings"

    def __str__(self):
        return "Household settings"

    @classmethod
    def get_settings(cls):
        return cls.objects.order_by("id").first()

    @classmethod
    def has_parent_pin(cls):
        return cls.get_settings() is not None

    @classmethod
    def set_initial_parent_pin(cls, pin):
        if cls.has_parent_pin():
            raise ValidationError("A parent PIN already exists.")
        settings = cls(parent_pin_hash=make_password(pin))
        settings.full_clean()
        settings.save()
        return settings

    def check_parent_pin(self, pin):
        return check_password(pin, self.parent_pin_hash)

    def clean(self):
        super().clean()
        if not self.parent_pin_hash:
            raise ValidationError({"parent_pin_hash": "Parent PIN hash is required."})
        if not self.pk and HouseholdSettings.objects.exists():
            raise ValidationError("Only one household settings record is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Chore(models.Model):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

    VALID_DUE_DAYS = {
        SUNDAY,
        MONDAY,
        TUESDAY,
        WEDNESDAY,
        THURSDAY,
        FRIDAY,
        SATURDAY,
    }

    name = models.CharField(max_length=120)
    kid = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="chores")
    due_days = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "Enter a chore name."})
        self.due_days = self._clean_due_days(self.due_days)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @classmethod
    def _clean_due_days(cls, due_days):
        if not isinstance(due_days, list) or not due_days:
            raise ValidationError({"due_days": "Select at least one due day."})

        cleaned_due_days = []
        for due_day in due_days:
            if isinstance(due_day, bool) or not isinstance(due_day, int):
                raise ValidationError({"due_days": "Select valid due days."})
            if due_day not in cls.VALID_DUE_DAYS:
                raise ValidationError({"due_days": "Select valid due days."})
            if due_day not in cleaned_due_days:
                cleaned_due_days.append(due_day)

        return sorted(cleaned_due_days)


class ChoreCompletion(models.Model):
    chore = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chore", "completed_on"],
                name="unique_chore_completion_date",
            ),
        ]
        ordering = ["-completed_on", "chore_id"]

    def __str__(self):
        return f"{self.chore} completed on {self.completed_on}"
