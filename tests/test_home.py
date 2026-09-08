import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse


@pytest.mark.django_db
def test_home_page_loads(client):
    response = client.get(reverse("chores:home"))

    assert response.status_code == 200
    assert b"Family Chore Tracker" in response.content


@pytest.mark.django_db
def test_home_page_loads_base_layout_assets(client):
    response = client.get(reverse("chores:home"))

    assert response.status_code == 200
    assert b'href="/static/css/app.css"' in response.content
    assert b"htmx.org" in response.content


def test_project_css_resolves_through_staticfiles():
    assert finders.find("css/app.css") is not None


@pytest.mark.django_db
def test_week_query_renders_selected_sunday_starting_week(client):
    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"Sep 6, 2026" in response.content
    assert b"Sep 12, 2026" in response.content
    assert b"Sunday, Sep 6" in response.content


@pytest.mark.django_db
def test_week_navigation_links_to_previous_current_and_next_weeks(client):
    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"?week=2026-08-30" in response.content
    assert b"?week=2026-09-13" in response.content
    assert b"Current week" in response.content


@pytest.mark.django_db
def test_invalid_week_query_falls_back_to_current_week(client, monkeypatch):
    from datetime import date

    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))

    response = client.get(reverse("chores:home"), {"week": "not-a-date"})

    assert response.status_code == 200
    assert b"Sep 6, 2026" in response.content
    assert b"Sep 12, 2026" in response.content


@pytest.mark.django_db
def test_missing_week_query_defaults_to_current_week(client, monkeypatch):
    from datetime import date

    from chores import views

    monkeypatch.setattr(views.timezone, "localdate", lambda: date(2026, 9, 8))

    response = client.get(reverse("chores:home"))

    assert response.status_code == 200
    assert b"Sep 6, 2026" in response.content
    assert b"Sep 12, 2026" in response.content
