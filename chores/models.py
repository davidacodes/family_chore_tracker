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
