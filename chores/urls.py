from django.urls import path

from . import views


app_name = "chores"

urlpatterns = [
    path("", views.home, name="home"),
    path("parent/pin/set/", views.set_parent_pin, name="set_parent_pin"),
    path("parent/login/", views.enter_parent_mode_view, name="enter_parent_mode"),
    path("parent/logout/", views.leave_parent_mode_view, name="leave_parent_mode"),
    path("setup/kids/", views.setup_kids, name="setup_kids"),
    path("setup/chores/", views.setup_chores, name="setup_chores"),
    path("history/", views.month_history, name="month_history"),
    path("chores/<int:chore_id>/complete/", views.complete_chore, name="complete_chore"),
    path("chores/<int:chore_id>/undo/", views.undo_chore, name="undo_chore"),
]
