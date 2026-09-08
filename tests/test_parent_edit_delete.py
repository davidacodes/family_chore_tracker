from datetime import date

import pytest
from django.urls import reverse

from chores.models import Chore
from chores.models import ChoreCompletion
from chores.models import HouseholdSettings
from chores.models import Kid
from chores.parent_mode import PARENT_MODE_SESSION_KEY


def enter_parent_mode(client):
    HouseholdSettings.set_initial_parent_pin("1234")
    session = client.session
    session[PARENT_MODE_SESSION_KEY] = True
    session.save()


@pytest.mark.django_db
def test_parent_can_edit_kid_name(client):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")

    response = client.post(reverse("chores:edit_kid", args=[kid.id]), {"name": "Maya A"})

    kid.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse("chores:setup_kids")
    assert kid.name == "Maya A"


@pytest.mark.django_db
def test_parent_can_delete_kid_and_cascade_chores(client):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(reverse("chores:delete_kid", args=[kid.id]))

    assert response.status_code == 302
    assert Kid.objects.count() == 0
    assert Chore.objects.count() == 0


@pytest.mark.django_db
def test_parent_can_edit_chore_fields(client):
    enter_parent_mode(client)
    maya = Kid.objects.create(name="Maya")
    leo = Kid.objects.create(name="Leo")
    chore = Chore.objects.create(name="Dishes", kid=maya, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:edit_chore", args=[chore.id]),
        {
            "name": "Laundry",
            "kid": leo.id,
            "due_days": [Chore.MONDAY, Chore.FRIDAY],
        },
    )

    chore.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse("chores:setup_chores")
    assert chore.name == "Laundry"
    assert chore.kid == leo
    assert chore.due_days == [Chore.MONDAY, Chore.FRIDAY]


@pytest.mark.django_db
def test_parent_can_delete_chore_and_cascade_completions(client):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.post(reverse("chores:delete_chore", args=[chore.id]))

    assert response.status_code == 302
    assert Chore.objects.count() == 0
    assert ChoreCompletion.objects.count() == 0


@pytest.mark.django_db
def test_kid_facing_calendar_does_not_show_edit_or_delete_controls(client):
    kid = Kid.objects.create(name="Maya")
    Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"Edit" not in response.content
    assert b"Delete" not in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("route_name", "factory"),
    [
        ("edit_kid", lambda kid, chore: kid.id),
        ("delete_kid", lambda kid, chore: kid.id),
        ("edit_chore", lambda kid, chore: chore.id),
        ("delete_chore", lambda kid, chore: chore.id),
    ],
)
def test_direct_edit_and_delete_requests_are_blocked_without_parent_mode(
    client,
    route_name,
    factory,
):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.post(reverse(f"chores:{route_name}", args=[factory(kid, chore)]))

    assert response.status_code == 302
    assert response.url == reverse("chores:enter_parent_mode")


@pytest.mark.django_db
def test_invalid_kid_edit_shows_validation_error(client):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")

    response = client.post(reverse("chores:edit_kid", args=[kid.id]), {"name": "   "})

    kid.refresh_from_db()
    assert response.status_code == 200
    assert b"Enter a kid name" in response.content
    assert kid.name == "Maya"


@pytest.mark.django_db
def test_invalid_chore_edit_shows_validation_error(client):
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:edit_chore", args=[chore.id]),
        {"name": "", "kid": kid.id, "due_days": []},
    )

    chore.refresh_from_db()
    assert response.status_code == 200
    assert b"Enter a chore name" in response.content
    assert b"Select at least one due day" in response.content
    assert chore.name == "Dishes"
