from datetime import date
from datetime import timedelta

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .calendar import DATE_QUERY_FORMAT
from .calendar import build_completion_week_grid
from .calendar import chore_is_due_on
from .calendar import parse_selected_week
from .calendar import week_start_for
from .calendar import week_dates
from .forms import ChoreForm
from .forms import KidForm
from .forms import ParentPinForm
from .forms import SetParentPinForm
from .models import Chore
from .models import ChoreCompletion
from .models import Kid
from .models import HouseholdSettings
from .parent_mode import enter_parent_mode
from .parent_mode import leave_parent_mode
from .parent_mode import parent_mode_required


def home(request):
    today = timezone.localdate()
    week_start = parse_selected_week(request.GET.get("week"), today)
    week = week_dates(week_start)
    kids = Kid.objects.all()
    chores = Chore.objects.select_related("kid")
    completions = ChoreCompletion.objects.filter(completed_on__in=week).select_related(
        "chore"
    )

    context = {
        "calendar_rows": build_completion_week_grid(kids, chores, completions, week),
        "has_kids": kids.exists(),
        "week": week,
        "week_start": week_start,
        "week_end": week[-1],
        "previous_week": (week_start - timedelta(days=7)).strftime(DATE_QUERY_FORMAT),
        "current_week": today.strftime(DATE_QUERY_FORMAT),
        "next_week": (week_start + timedelta(days=7)).strftime(DATE_QUERY_FORMAT),
    }
    return render(request, "chores/home.html", context)


def complete_chore(request, chore_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Completion must be submitted with POST.")

    completed_on = parse_completion_date(request.POST.get("completed_on"))
    if completed_on is None:
        return HttpResponseBadRequest("Enter a valid completion date.")

    chore = get_object_or_404(Chore, id=chore_id)
    if not chore_is_due_on(chore, completed_on):
        return HttpResponseBadRequest("Chore is not due on this date.")

    ChoreCompletion.objects.get_or_create(chore=chore, completed_on=completed_on)
    return redirect(f"{reverse('chores:home')}?week={week_start_for(completed_on):%Y-%m-%d}")


def parse_completion_date(raw_date):
    if not raw_date:
        return None
    try:
        return date.fromisoformat(raw_date)
    except ValueError:
        return None


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


@parent_mode_required
def setup_chores(request):
    kids = Kid.objects.all()
    if request.method == "POST" and kids.exists():
        form = ChoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chores:setup_chores")
    else:
        form = ChoreForm()

    context = {
        "form": form,
        "kids": kids,
        "chores": Chore.objects.select_related("kid"),
    }
    return render(request, "chores/setup_chores.html", context)
