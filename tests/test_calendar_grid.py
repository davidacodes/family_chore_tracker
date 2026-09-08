import pytest
from django.urls import reverse

from chores.models import Chore
from chores.models import Kid


@pytest.mark.django_db
def test_home_page_shows_no_kids_empty_state(client):
    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"No kids yet" in response.content
    assert b"weekly calendar" in response.content
    assert b"<table" not in response.content


@pytest.mark.django_db
def test_calendar_columns_run_sunday_through_saturday(client):
    Kid.objects.create(name="Maya")

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    content = response.content.decode()
    assert content.index("Sunday") < content.index("Monday")
    assert content.index("Monday") < content.index("Tuesday")
    assert content.index("Tuesday") < content.index("Wednesday")
    assert content.index("Wednesday") < content.index("Thursday")
    assert content.index("Thursday") < content.index("Friday")
    assert content.index("Friday") < content.index("Saturday")


@pytest.mark.django_db
def test_calendar_shows_each_kid_as_a_row(client):
    Kid.objects.create(name="Maya")
    Kid.objects.create(name="Leo")

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"Maya" in response.content
    assert b"Leo" in response.content


@pytest.mark.django_db
def test_calendar_keeps_empty_kid_day_cells_visible(client):
    Kid.objects.create(name="Maya")

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    content = response.content.decode()
    assert content.count('class="empty-cell"') == 7


@pytest.mark.django_db
def test_calendar_places_chores_in_matching_kid_and_due_day_cells(client):
    maya = Kid.objects.create(name="Maya")
    leo = Kid.objects.create(name="Leo")
    Chore.objects.create(name="Dishes", kid=maya, due_days=[Chore.TUESDAY])
    Chore.objects.create(name="Laundry", kid=leo, due_days=[Chore.FRIDAY])

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    content = response.content.decode()
    maya_row = content[content.index("Maya") : content.index("Leo")]
    leo_row = content[content.index("Leo") :]
    assert "Dishes" in maya_row
    assert "Laundry" not in maya_row
    assert "Laundry" in leo_row


@pytest.mark.django_db
def test_calendar_shows_grid_when_kids_exist_but_no_chores(client):
    Kid.objects.create(name="Maya")

    response = client.get(reverse("chores:home"), {"week": "2026-09-08"})

    assert response.status_code == 200
    assert b"<table" in response.content
    assert b"Maya" in response.content
    assert b"No kids yet" not in response.content
