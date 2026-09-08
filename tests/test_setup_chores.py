import pytest
from django.urls import reverse

from chores.models import Chore
from chores.models import HouseholdSettings
from chores.models import Kid
from chores.parent_mode import PARENT_MODE_SESSION_KEY


def enter_parent_mode(client):
    HouseholdSettings.set_initial_parent_pin("1234")
    session = client.session
    session[PARENT_MODE_SESSION_KEY] = True
    session.save()


@pytest.mark.django_db
def test_parent_mode_user_can_open_add_chore_page(client):
    enter_parent_mode(client)
    Kid.objects.create(name="Maya")

    response = client.get(reverse("chores:setup_chores"))

    assert response.status_code == 200
    assert b"Chore name" in response.content
    assert b"Kid" in response.content
    assert b"Sunday" in response.content
    assert b"Saturday" in response.content


@pytest.mark.django_db
def test_non_parent_mode_user_cannot_open_add_chore_page(client):
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.get(reverse("chores:setup_chores"))

    assert response.status_code == 302
    assert response.url == reverse("chores:enter_parent_mode")


@pytest.mark.django_db
def test_non_parent_mode_user_cannot_post_chore(client):
    kid = Kid.objects.create(name="Maya")
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.post(
        reverse("chores:setup_chores"),
        {
            "name": "Dishes",
            "kid": kid.id,
            "due_days": [Chore.SUNDAY],
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("chores:enter_parent_mode")
    assert Chore.objects.count() == 0


@pytest.mark.django_db
def test_setup_chores_creates_valid_chore(client):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")

    response = client.post(
        reverse("chores:setup_chores"),
        {
            "name": "Dishes",
            "kid": kid.id,
            "due_days": [Chore.SUNDAY, Chore.WEDNESDAY],
        },
    )

    chore = Chore.objects.get()
    assert response.status_code == 302
    assert response.url == reverse("chores:setup_chores")
    assert chore.name == "Dishes"
    assert chore.kid == kid
    assert chore.due_days == [Chore.SUNDAY, Chore.WEDNESDAY]


@pytest.mark.django_db
def test_setup_chores_lists_created_chore(client):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.SUNDAY])

    response = client.get(reverse("chores:setup_chores"))

    assert response.status_code == 200
    assert b"Dishes for Maya" in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"name": "", "kid": "", "due_days": [Chore.SUNDAY]}, b"Enter a chore name"),
        ({"name": "Dishes", "kid": "", "due_days": [Chore.SUNDAY]}, b"This field is required"),
        ({"name": "Dishes", "kid": "", "due_days": []}, b"Select at least one due day"),
    ],
)
def test_setup_chores_shows_validation_errors(client, payload, message):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    if payload["kid"] == "":
        payload["kid"] = ""
    else:
        payload["kid"] = kid.id

    response = client.post(reverse("chores:setup_chores"), payload)

    assert response.status_code == 200
    assert Chore.objects.count() == 0
    assert message in response.content


@pytest.mark.django_db
def test_setup_chores_no_kids_state_blocks_chore_creation(client):
    enter_parent_mode(client)

    get_response = client.get(reverse("chores:setup_chores"))
    post_response = client.post(
        reverse("chores:setup_chores"),
        {
            "name": "Dishes",
            "kid": "",
            "due_days": [Chore.SUNDAY],
        },
    )

    assert get_response.status_code == 200
    assert b"Add kids before creating chores" in get_response.content
    assert post_response.status_code == 200
    assert Chore.objects.count() == 0
