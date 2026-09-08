import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page_loads(client):
    response = client.get(reverse("chores:home"))

    assert response.status_code == 200
    assert b"Family Chore Tracker" in response.content
