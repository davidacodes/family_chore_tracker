import re
from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from chores.models import Chore
from chores.models import ChoreCompletion
from chores.models import Kid


def csrf_token_from(response):
    match = re.search(
        r'name="csrfmiddlewaretoken" value="([^"]+)"',
        response.content.decode(),
    )
    assert match is not None
    return match.group(1)


@pytest.mark.django_db
def test_calendar_completion_button_has_htmx_attributes(client):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert f'hx-post="{reverse("chores:complete_chore", args=[chore.id])}"'.encode() in response.content
    assert b'hx-swap="outerHTML"' in response.content


@pytest.mark.django_db
def test_htmx_completion_returns_chore_item_fragment(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert response.content.strip().startswith(
        f'<li id="chore-{chore.id}-2026-09-08">'.encode()
    )
    assert b"checkbox-fake--checked" in response.content
    assert b"Undo Dishes" in response.content


@pytest.mark.django_db
def test_htmx_undo_returns_incomplete_chore_item_fragment(client, monkeypatch):
    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    ChoreCompletion.objects.create(chore=chore, completed_on=date(2026, 9, 8))

    response = client.post(
        reverse("chores:undo_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert response.content.strip().startswith(
        f'<li id="chore-{chore.id}-2026-09-08">'.encode()
    )
    assert b"Mark Dishes complete" in response.content
    assert b"Undo Dishes" not in response.content


@pytest.mark.django_db
def test_non_htmx_completion_still_redirects(client):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
    )

    assert response.status_code == 302
    assert response.url == "/?week=2026-09-06"


@pytest.mark.django_db
def test_non_htmx_undo_still_redirects(client, monkeypatch):
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


@pytest.mark.django_db
def test_htmx_blocked_action_returns_visible_error(client):
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-10"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 400
    assert b"Chore is not due on this date" in response.content


@pytest.mark.django_db
def test_csrf_protects_htmx_completion_request_without_token():
    client = Client(enforce_csrf_checks=True)
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-08"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 403
    assert ChoreCompletion.objects.count() == 0


@pytest.mark.django_db
def test_csrf_allows_htmx_completion_request_with_token():
    client = Client(enforce_csrf_checks=True)
    kid = Kid.objects.create(name="Maya")
    chore = Chore.objects.create(name="Dishes", kid=kid, due_days=[Chore.TUESDAY])
    home_response = client.get(reverse("chores:home"), {"week": "2026-09-08"})
    csrf_token = csrf_token_from(home_response)

    response = client.post(
        reverse("chores:complete_chore", args=[chore.id]),
        {"completed_on": "2026-09-08", "csrfmiddlewaretoken": csrf_token},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert ChoreCompletion.objects.filter(chore=chore).exists()
