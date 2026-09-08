import pytest
from django.urls import reverse

from chores.models import HouseholdSettings
from chores.parent_mode import PARENT_MODE_SESSION_KEY


def enter_parent_mode(client):
    HouseholdSettings.set_initial_parent_pin("1234")
    session = client.session
    session[PARENT_MODE_SESSION_KEY] = True
    session.save()


@pytest.mark.django_db
def test_parent_navigation_links_are_visually_distinct(client):
    response = client.get(reverse("chores:home"))

    assert response.status_code == 200
    assert response.content.count(b'class="parent-tool-link"') == 3


@pytest.mark.django_db
def test_empty_states_use_consistent_class_on_main_and_setup_pages(client):
    enter_parent_mode(client)

    home_response = client.get(reverse("chores:home"))
    setup_response = client.get(reverse("chores:setup_kids"))
    history_response = client.get(reverse("chores:month_history"))

    assert b'class="empty-state"' in home_response.content
    assert b'class="empty-state"' in setup_response.content
    assert b'class="empty-state"' in history_response.content
