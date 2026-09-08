from datetime import date

import pytest
from django.urls import reverse

from chores.models import Chore
from chores.models import ChoreCompletion
from chores.models import Kid


@pytest.mark.django_db
def test_core_v1_parent_setup_and_kid_completion_workflow(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))

    set_pin_response = client.post(reverse("chores:set_parent_pin"), {"pin": "1234"})
    assert set_pin_response.status_code == 302
    assert set_pin_response.url == reverse("chores:setup_kids")

    logout_response = client.post(reverse("chores:leave_parent_mode"))
    assert logout_response.status_code == 302

    blocked_setup_response = client.get(reverse("chores:setup_kids"))
    assert blocked_setup_response.status_code == 302
    assert blocked_setup_response.url == reverse("chores:enter_parent_mode")

    login_response = client.post(reverse("chores:enter_parent_mode"), {"pin": "1234"})
    assert login_response.status_code == 302
    assert login_response.url == reverse("chores:setup_kids")

    add_kid_response = client.post(reverse("chores:setup_kids"), {"name": "Maya"})
    kid = Kid.objects.get(name="Maya")
    assert add_kid_response.status_code == 302

    add_chore_response = client.post(
        reverse("chores:setup_chores"),
        {
            "name": "Dishes",
            "kid": kid.id,
            "due_days": [Chore.TUESDAY, Chore.THURSDAY],
        },
    )
    chore = Chore.objects.get(name="Dishes")
    assert add_chore_response.status_code == 302
    assert chore.kid == kid
    assert chore.due_days == [Chore.TUESDAY, Chore.THURSDAY]

    calendar_response = client.get(reverse("chores:home"), {"week": "2026-09-08"})
    assert calendar_response.status_code == 200
    assert b"Maya" in calendar_response.content
    assert b"Mark Dishes complete for September 8, 2026" in calendar_response.content

    client.post(reverse("chores:leave_parent_mode"))
    completion_response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
    )
    assert completion_response.status_code == 302
    assert ChoreCompletion.objects.filter(
        chore=chore,
        completed_on=date(2026, 9, 8),
    ).exists()

    undo_response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
    )
    assert undo_response.status_code == 302
    assert not ChoreCompletion.objects.filter(
        chore=chore,
        completed_on=date(2026, 9, 8),
    ).exists()

    past_completion_response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-01"},
    )
    blocked_past_undo_response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-01"},
    )
    assert past_completion_response.status_code == 302
    assert blocked_past_undo_response.status_code == 400
    assert ChoreCompletion.objects.filter(
        chore=chore,
        completed_on=date(2026, 9, 1),
    ).exists()


@pytest.mark.django_db
def test_current_month_history_workflow_uses_completed_and_missed_dates(
    client,
    monkeypatch,
):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))

    client.post(reverse("chores:set_parent_pin"), {"pin": "1234"})
    client.post(reverse("chores:setup_kids"), {"name": "Maya"})
    kid = Kid.objects.get(name="Maya")
    client.post(
        reverse("chores:setup_chores"),
        {
            "name": "Dishes",
            "kid": kid.id,
            "due_days": [Chore.TUESDAY],
        },
    )
    client.post(
        reverse("chores:setup_chores"),
        {
            "name": "Laundry",
            "kid": kid.id,
            "due_days": [Chore.MONDAY],
        },
    )
    dishes = Chore.objects.get(name="Dishes")

    client.post(
        reverse("chores:complete_chore", args=[dishes.id]),
        {"completed_on": "2026-09-08"},
    )
    history_response = client.get(reverse("chores:month_history"))

    assert history_response.status_code == 200
    content = history_response.content.decode()
    assert "Dishes for Maya" in content
    assert "Laundry for Maya" in content
    assert "Completed" in content
    assert "Missed" in content
