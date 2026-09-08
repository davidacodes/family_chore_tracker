from datetime import date

from django.db import IntegrityError
from django.urls import reverse

import pytest

from chores.models import Chore
from chores.models import ChoreCompletion
from chores.models import HouseholdSettings
from chores.models import Kid


@pytest.mark.django_db
def test_can_create_chore_completion_for_concrete_date():
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    completion = ChoreCompletion.objects.create(
        chore=chore,
        completed_on=date(2026, 9, 8),
    )

    assert completion.chore == chore
    assert completion.completed_on == date(2026, 9, 8)


@pytest.mark.django_db
def test_duplicate_chore_completion_for_same_date_is_rejected():
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    with pytest.raises(IntegrityError):
        ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))


@pytest.mark.django_db
def test_calendar_shows_unchecked_control_for_incomplete_due_chore(client):
    kid = Kid.objects.create(name="Maya")
    Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"Mark Dishes complete" in response.content
    assert b"checked disabled" not in response.content


@pytest.mark.django_db
def test_kid_can_mark_due_chore_complete_without_parent_mode(client):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
    )

    assert response.status_code == 302
    assert response.url == "/?week=2026-09-06"
    assert ChoreCompletion.objects.filter(
        chore=chore,
        completed_on=date(2026, 9, 8),
    ).exists()


@pytest.mark.django_db
def test_completed_chore_appears_checked_on_calendar(client):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"checkbox-fake--checked" in response.content
    assert b"Dishes" in response.content


@pytest.mark.django_db
def test_completion_state_is_date_specific(client):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    current_week_response = client.get(reverse("chores:home"), {"week": "2026-09-08"})
    next_week_response = client.get(reverse("chores:home"), {"week": "2026-09-15"})

    assert b"checkbox-fake--checked" in current_week_response.content
    assert b"checkbox-fake--checked" not in next_week_response.content
    assert b"Mark Dishes complete" in next_week_response.content


@pytest.mark.django_db
def test_completion_for_unscheduled_date_is_rejected(client):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-10"},
    )

    assert response.status_code == 400
    assert ChoreCompletion.objects.count() == 0
