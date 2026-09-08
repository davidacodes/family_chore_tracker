from django.core.exceptions import ValidationError

import pytest

from chores.models import Kid


@pytest.mark.django_db
def test_can_create_valid_kid():
    kid = Kid.objects.create(name="Maya")

    assert kid.name == "Maya"
    assert str(kid) == "Maya"


@pytest.mark.django_db
@pytest.mark.parametrize("blank_name", ["", "   "])
def test_blank_kid_name_is_rejected(blank_name):
    with pytest.raises(ValidationError):
        Kid.objects.create(name=blank_name)


@pytest.mark.django_db
def test_kid_name_is_trimmed_before_save():
    kid = Kid.objects.create(name="  Leo  ")

    assert kid.name == "Leo"


@pytest.mark.django_db
def test_kids_use_creation_order_by_default():
    first = Kid.objects.create(name="First")
    second = Kid.objects.create(name="Second")

    assert list(Kid.objects.values_list("id", flat=True)) == [first.id, second.id]
