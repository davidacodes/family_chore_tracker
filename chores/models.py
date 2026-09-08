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
