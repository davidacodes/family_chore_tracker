from django.urls import path

from . import views


app_name = "chores"

urlpatterns = [
    path("", views.home, name="home"),
    path("setup/kids/", views.setup_kids, name="setup_kids"),
]
