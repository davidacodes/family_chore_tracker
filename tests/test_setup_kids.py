import pytest
from django.urls import reverse

from chores.models import Kid


@pytest.mark.django_db
def test_setup_kids_shows_empty_state(client):
    response = client.get(reverse("chores:setup_kids"))

    assert response.status_code == 200
    assert b"No kids yet" in response.content
    assert b"Add kid names before creating chores" in response.content


@pytest.mark.django_db
def test_setup_kids_creates_valid_kid(client):
    response = client.post(reverse("chores:setup_kids"), {"name": "Maya"})

    assert response.status_code == 302
    assert response.url == reverse("chores:setup_kids")
    assert Kid.objects.get().name == "Maya"


@pytest.mark.django_db
def test_setup_kids_lists_existing_kids_in_model_order(client):
    Kid.objects.create(name="Maya")
    Kid.objects.create(name="Leo")

    response = client.get(reverse("chores:setup_kids"))

    assert response.status_code == 200
    content = response.content.decode()
    assert content.index("Maya") < content.index("Leo")


@pytest.mark.django_db
@pytest.mark.parametrize("blank_name", ["", "   "])
def test_setup_kids_rejects_blank_name(client, blank_name):
    response = client.post(reverse("chores:setup_kids"), {"name": blank_name})

    assert response.status_code == 200
    assert Kid.objects.count() == 0
    assert b"Enter a kid name" in response.content
