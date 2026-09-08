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


def set_today(monkeypatch, today):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: today)


@pytest.mark.django_db
def test_parent_mode_user_can_access_current_month_history(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 8))
    enter_parent_mode(client)

    response = client.get(reverse("chores:month_history"))

    assert response.status_code == 200
    assert b"Monthly History" in response.content
    assert b"Sep 1" in response.content
    assert b"Sep 8, 2026" in response.content


@pytest.mark.django_db
def test_non_parent_mode_user_cannot_access_current_month_history(client):
    HouseholdSettings.set_initial_parent_pin("1234")

    response = client.get(reverse("chores:month_history"))

    assert response.status_code == 302
    assert response.url == reverse("chores:enter_parent_mode")


@pytest.mark.django_db
def test_history_shows_completed_and_missed_chores(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 8))
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    completed = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    Chore.objects.create(name="Laundry", kid=kid, due_days=[Chore.MONDAY])
    ChoreCompletion.objects.create(completed_on=date(2026, 9, 8), chore=completed)

    response = client.get(reverse("chores:month_history"))

    content = response.content.decode()
    assert "Dishes for Maya" in content
    assert "Laundry for Maya" in content
    assert content.index("Completed") < content.index("Dishes for Maya")
    assert content.index("Missed") < content.index("Laundry for Maya")


@pytest.mark.django_db
def test_future_dates_in_current_month_are_not_counted_as_missed(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 1))
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    Chore.objects.create(name="Laundry", kid=kid, due_days=[Chore.WEDNESDAY])

    response = client.get(reverse("chores:month_history"))

    assert response.status_code == 200
    assert b"Wednesday, Sep 2" not in response.content
    assert b"Laundry for Maya" not in response.content


@pytest.mark.django_db
def test_completion_history_is_date_specific(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 15))
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(completed_on=date(2026, 9, 8), chore=chore)

    response = client.get(reverse("chores:month_history"))

    content = response.content.decode()
    assert "Tuesday, Sep 8" in content
    assert "Tuesday, Sep 15" not in content


@pytest.mark.django_db
def test_history_shows_no_kids_empty_state(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 8))
    enter_parent_mode(client)

    response = client.get(reverse("chores:month_history"))

    assert response.status_code == 200
    assert b"No kids yet" in response.content


@pytest.mark.django_db
def test_history_shows_no_chores_empty_state(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 8))
    enter_parent_mode(client)
    Kid.objects.create(name="Maya")

    response = client.get(reverse("chores:month_history"))

    assert response.status_code == 200
    assert b"No chores yet" in response.content


@pytest.mark.django_db
def test_history_shows_no_completed_or_missed_empty_state(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 1))
    enter_parent_mode(client)
    kid = Kid.objects.create(name="Maya")
    Chore.objects.create(name="Laundry", kid=kid, due_days=[Chore.WEDNESDAY])

    response = client.get(reverse("chores:month_history"))

    assert response.status_code == 200
    assert b"No completed or missed chores yet this month" in response.content
