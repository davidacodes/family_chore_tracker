from datetime import date

import pytest
from django.urls import reverse

from chores.models import Chore
from chores.models import ChoreCompletion
from chores.models import Kid


@pytest.mark.django_db
def test_today_completed_chore_shows_undo_control(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"Undo Dishes" in response.content


@pytest.mark.django_db
def test_same_day_undo_removes_completion(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
    )

    assert response.status_code == 302
    assert response.url == "/?week=2026-09-06"
    assert ChoreCompletion.objects.count() == 0


@pytest.mark.django_db
def test_after_undo_today_chore_appears_incomplete(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    client.post(reverse("chores:undo_chore", args=[chore.id]), {"completed_on": "2026-09-08"})
    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert b"Mark Dishes complete" in response.content
    assert b"Undo Dishes" not in response.content


@pytest.mark.django_db
def test_past_completed_chore_does_not_show_undo_control(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 9))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"Undo Dishes" not in response.content
    assert b"checked disabled" in response.content


@pytest.mark.django_db
def test_direct_past_date_undo_is_blocked(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 9))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
    )

    assert response.status_code == 400
    assert ChoreCompletion.objects.count() == 1


@pytest.mark.django_db
def test_undoing_one_date_does_not_affect_other_dates(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 15))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 15))

    response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-15"},
    )

    assert response.status_code == 302
    assert ChoreCompletion.objects.filter(completed_on=date(2026, 9, 8)).exists()
    assert not ChoreCompletion.objects.filter(completed_on=date(2026, 9, 15)).exists()


@pytest.mark.django_db
def test_missing_completion_undo_returns_controlled_response(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
    )

    assert response.status_code == 302
    assert ChoreCompletion.objects.count() == 0
