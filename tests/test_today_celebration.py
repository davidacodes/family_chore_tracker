from datetime import date

import pytest
from django.urls import reverse

from chores.models import Chore
from chores.models import ChoreCompletion
from chores.models import Kid


def set_today(monkeypatch, today):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: today)


@pytest.mark.django_db
def test_celebration_appears_when_all_due_today_chores_are_complete(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"All chores for today are done" in response.content


@pytest.mark.django_db
def test_celebration_does_not_appear_when_any_due_today_chore_is_incomplete(
    client,
    monkeypatch,
):
    set_today(monkeypatch, date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    complete_chore = Chore.objects.create(
        name="Dishes",
        kid=kid,
        due_days=[Chore.TUESDAY],
    )
    Chore.objects.create(name="Laundry", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(
        chore=complete_chore,
        completed_on=date(2026, 9, 8),
    )

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"All chores for today are done" not in response.content


@pytest.mark.django_db
def test_celebration_does_not_appear_when_no_chores_are_due_today(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    Chore.objects.create(name="Laundry", kid=kid, due_days=[Chore.WEDNESDAY])

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"All chores for today are done" not in response.content


@pytest.mark.django_db
def test_final_completion_makes_celebration_visible_in_htmx_response(
    client,
    monkeypatch,
):
    set_today(monkeypatch, date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b'hx-swap-oob="true"' in response.content
    assert b"All chores for today are done" in response.content


@pytest.mark.django_db
def test_undo_after_complete_hides_celebration_in_htmx_response(client, monkeypatch):
    set_today(monkeypatch, date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b'hx-swap-oob="true"' in response.content
    assert b"All chores for today are done" not in response.content
