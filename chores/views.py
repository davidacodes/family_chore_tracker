from datetime import timedelta

from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import timezone

from .calendar import DATE_QUERY_FORMAT, parse_selected_week, week_dates
from .forms import KidForm
from .forms import ParentPinForm
from .forms import SetParentPinForm
from .models import Kid
from .models import HouseholdSettings
from .parent_mode import enter_parent_mode
from .parent_mode import leave_parent_mode
from .parent_mode import parent_mode_required


def home(request):
    today = timezone.localdate()
    week_start = parse_selected_week(request.GET.get("week"), today)
    week = week_dates(week_start)

    context = {
        "week": week,
        "week_start": week_start,
        "week_end": week[-1],
        "previous_week": (week_start - timedelta(days=7)).strftime(DATE_QUERY_FORMAT),
        "current_week": today.strftime(DATE_QUERY_FORMAT),
        "next_week": (week_start + timedelta(days=7)).strftime(DATE_QUERY_FORMAT),
    }
    return render(request, "chores/home.html", context)


def set_parent_pin(request):
    if HouseholdSettings.has_parent_pin():
        return redirect("chores:enter_parent_mode")

    if request.method == "POST":
        form = SetParentPinForm(request.POST)
        if form.is_valid():
            HouseholdSettings.set_initial_parent_pin(form.cleaned_data["pin"])
            enter_parent_mode(request)
            return redirect("chores:setup_kids")
    else:
        form = SetParentPinForm()

    return render(request, "chores/set_parent_pin.html", {"form": form})


def enter_parent_mode_view(request):
    if not HouseholdSettings.has_parent_pin():
        return redirect("chores:set_parent_pin")

    if request.method == "POST":
        form = ParentPinForm(request.POST)
        settings = HouseholdSettings.get_settings()
        if form.is_valid() and settings.check_parent_pin(form.cleaned_data["pin"]):
            enter_parent_mode(request)
            return redirect("chores:setup_kids")
        form.add_error("pin", "Enter the correct parent PIN.")
    else:
        form = ParentPinForm()

    return render(request, "chores/enter_parent_mode.html", {"form": form})


def leave_parent_mode_view(request):
    leave_parent_mode(request)
    return redirect("chores:home")


@parent_mode_required
def setup_kids(request):
    if request.method == "POST":
        form = KidForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chores:setup_kids")
    else:
        form = KidForm()

    context = {
        "form": form,
        "kids": Kid.objects.all(),
    }
    return render(request, "chores/setup_kids.html", context)
