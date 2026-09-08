from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.urls import reverse

import pytest

from chores.models import HouseholdSettings
from chores.parent_mode import PARENT_MODE_SESSION_KEY


@pytest.mark.django_db
def test_can_set_initial_parent_pin(client):
    response = client.post(reverse("chores:set_parent_pin"), {"pin": "1234"})

    settings = HouseholdSettings.objects.get()
    assert response.status_code == 302
    assert response.url == reverse("chores:setup_kids")
    assert settings.parent_pin_hash != "1234"
    assert identify_hasher(settings.parent_pin_hash) is not None
    assert client.session[PARENT_MODE_SESSION_KEY] is True


@pytest.mark.django_db
def test_only_one_parent_pin_settings_record_is_allowed():
    HouseholdSettings.set_initial_parent_pin("1234")

    with pytest.raises(ValidationError):
        HouseholdSettings.objects.create(parent_pin_hash="another-hash")


@pytest.mark.django_db
def test_can_enter_parent_mode_with_correct_pin(client):
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.post(reverse("chores:enter_parent_mode"), {"pin": "1234"})

    assert response.status_code == 302
    assert response.url == reverse("chores:setup_kids")
    assert client.session[PARENT_MODE_SESSION_KEY] is True


@pytest.mark.django_db
def test_incorrect_pin_keeps_user_out_of_parent_mode(client):
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.post(reverse("chores:enter_parent_mode"), {"pin": "9999"})

    assert response.status_code == 200
    assert client.session.get(PARENT_MODE_SESSION_KEY) is not True
    assert b"Enter the correct parent PIN" in response.content


@pytest.mark.django_db
def test_can_leave_parent_mode_from_ui_action(client):
    session = client.session
    session[PARENT_MODE_SESSION_KEY] = True
    session.save()

    response = client.post(reverse("chores:leave_parent_mode"))

    assert response.status_code == 302
    assert response.url == reverse("chores:home")
    assert client.session[PARENT_MODE_SESSION_KEY] is False


@pytest.mark.django_db
def test_parent_mode_shows_leave_parent_mode_action(client):
    HouseholdSettings.set_initial_parent_pin("1234")
    session = client.session
    session[PARENT_MODE_SESSION_KEY] = True
    session.save()

    response = client.get(reverse("chores:setup_kids"))

    assert response.status_code == 200
    assert b"Leave parent mode" in response.content


@pytest.mark.django_db
def test_protected_setup_redirects_to_set_pin_when_no_pin_exists(client):
    response = client.get(reverse("chores:setup_kids"))

    assert response.status_code == 302
    assert response.url == reverse("chores:set_parent_pin")


@pytest.mark.django_db
def test_protected_setup_redirects_to_parent_login_when_pin_exists(client):
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.get(reverse("chores:setup_kids"))

    assert response.status_code == 302
    assert response.url == reverse("chores:enter_parent_mode")
