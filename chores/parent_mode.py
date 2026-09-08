from functools import wraps

from django.shortcuts import redirect

from .models import HouseholdSettings


PARENT_MODE_SESSION_KEY = "is_parent_mode"


def enter_parent_mode(request):
    request.session[PARENT_MODE_SESSION_KEY] = True


def leave_parent_mode(request):
    request.session[PARENT_MODE_SESSION_KEY] = False


def is_parent_mode(request):
    return request.session.get(PARENT_MODE_SESSION_KEY) is True


def parent_mode_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if is_parent_mode(request):
            return view_func(request, *args, **kwargs)
        if not HouseholdSettings.has_parent_pin():
            return redirect("chores:set_parent_pin")
        return redirect("chores:enter_parent_mode")

    return wrapper


def parent_mode_context(request):
    return {
        "is_parent_mode": is_parent_mode(request),
    }
