from django.core.exceptions import ValidationError

import pytest

from chores.models import Chore
from chores.models import Kid


@pytest.mark.django_db
def test_can_create_valid_chore():
    kid = Kid.objects.create(name="Maya")

    chore = Chore.objects.create(
        name="Feed the fish",
        kid=kid,
        due_days=[Chore.SUNDAY, Chore.WEDNESDAY],
    )

    assert chore.name == "Feed the fish"
    assert chore.kid == kid
    assert chore.due_days == [Chore.SUNDAY, Chore.WEDNESDAY]
    assert str(chore) == "Feed the fish"


@pytest.mark.django_db
@pytest.mark.parametrize("blank_name", ["", "   "])
def test_blank_chore_name_is_rejected(blank_name):
    kid = Kid.objects.create(name="Maya")

    with pytest.raises(ValidationError):
        Chore.objects.create(name=blank_name, kid=kid, due_days=[Chore.SUNDAY])


@pytest.mark.django_db
def test_chore_name_is_trimmed_before_save():
    kid = Kid.objects.create(name="Maya")

    chore = Chore.objects.create(name="  Dishes  ", kid=kid, due_days=[Chore.MONDAY])

    assert chore.name == "Dishes"


@pytest.mark.django_db
def test_missing_kid_is_rejected():
    with pytest.raises(ValidationError):
        Chore.objects.create(name="Dishes", due_days=[Chore.MONDAY])


@pytest.mark.django_db
@pytest.mark.parametrize("due_days", [[], None, "1"])
def test_missing_due_days_are_rejected(due_days):
    kid = Kid.objects.create(name="Maya")

    with pytest.raises(ValidationError):
        Chore.objects.create(name="Dishes", kid=kid, due_days=due_days)


@pytest.mark.django_db
@pytest.mark.parametrize("due_days", [[-1], [7], ["1"], [True]])
def test_invalid_due_day_values_are_rejected(due_days):
    kid = Kid.objects.create(name="Maya")

    with pytest.raises(ValidationError):
        Chore.objects.create(name="Dishes", kid=kid, due_days=due_days)


@pytest.mark.django_db
def test_due_days_are_stored_once_in_sunday_starting_order():
    kid = Kid.objects.create(name="Maya")

    chore = Chore.objects.create(
        name="Dishes",
        kid=kid,
        due_days=[Chore.FRIDAY, Chore.SUNDAY, Chore.FRIDAY],
    )

    assert chore.due_days == [Chore.SUNDAY, Chore.FRIDAY]
