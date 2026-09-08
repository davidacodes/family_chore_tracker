from datetime import date
from datetime import timedelta

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .calendar import DATE_QUERY_FORMAT
from .calendar import build_month_history
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
        "calendar_rows": build_completion_week_grid(
            kids,
            chores,
            completions,
            week,
            today=today,
        ),
        "has_kids": kids.exists(),
        "week": week,
        "week_start": week_start,
        "week_end": week[-1],
        "previous_week": (week_start - timedelta(days=7)).strftime(DATE_QUERY_FORMAT),
        "current_week": today.strftime(DATE_QUERY_FORMAT),
        "next_week": (week_start + timedelta(days=7)).strftime(DATE_QUERY_FORMAT),
        **today_celebration_context(today),
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
    if is_htmx_request(request):
        return render_chore_item_response(request, chore, completed_on)
    return redirect(f"{reverse('chores:home')}?week={week_start_for(completed_on):%Y-%m-%d}")


def undo_chore(request, chore_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Undo must be submitted with POST.")

    completed_on = parse_completion_date(request.POST.get("completed_on"))
    if completed_on is None:
        return HttpResponseBadRequest("Enter a valid completion date.")

    chore = get_object_or_404(Chore, id=chore_id)
    if completed_on != timezone.localdate():
        return HttpResponseBadRequest("Only today's completions can be undone.")

    ChoreCompletion.objects.filter(chore=chore, completed_on=completed_on).delete()
    if is_htmx_request(request):
        return render_chore_item_response(request, chore, completed_on)
    return redirect(f"{reverse('chores:home')}?week={week_start_for(completed_on):%Y-%m-%d}")


def parse_completion_date(raw_date):
    if not raw_date:
        return None
    try:
        return date.fromisoformat(raw_date)
    except ValueError:
        return None


def is_htmx_request(request):
    return request.headers.get("HX-Request") == "true"


def chore_item_context(chore, completed_on):
    is_complete = ChoreCompletion.objects.filter(
        chore=chore,
        completed_on=completed_on,
    ).exists()
    return {
        "cell": {"date": completed_on},
        "item": {
            "chore": chore,
            "is_complete": is_complete,
            "can_undo": is_complete and completed_on == timezone.localdate(),
        },
    }


def render_chore_item_response(request, chore, completed_on):
    context = {
        **chore_item_context(chore, completed_on),
        **today_celebration_context(),
    }
    return render(request, "chores/_chore_item_response.html", context)


def today_celebration_context(today=None):
    today = today or timezone.localdate()
    due_today = [
        chore
        for chore in Chore.objects.all()
        if chore_is_due_on(chore, today)
    ]
    completed_chore_ids = set(
        ChoreCompletion.objects.filter(
            chore__in=due_today,
            completed_on=today,
        ).values_list("chore_id", flat=True)
    )
    return {
        "today_all_done": bool(due_today)
        and all(chore.id in completed_chore_ids for chore in due_today),
    }


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
def edit_kid(request, kid_id):
    kid = get_object_or_404(Kid, id=kid_id)
    if request.method == "POST":
        form = KidForm(request.POST, instance=kid)
        if form.is_valid():
            form.save()
            return redirect("chores:setup_kids")
    else:
        form = KidForm(instance=kid)

    return render(request, "chores/edit_kid.html", {"form": form, "kid": kid})


@parent_mode_required
def delete_kid(request, kid_id):
    kid = get_object_or_404(Kid, id=kid_id)
    if request.method == "POST":
        kid.delete()
        return redirect("chores:setup_kids")

    return render(request, "chores/delete_kid.html", {"kid": kid})


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


@parent_mode_required
def edit_chore(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    if request.method == "POST":
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect("chores:setup_chores")
    else:
        form = ChoreForm(instance=chore)

    return render(request, "chores/edit_chore.html", {"form": form, "chore": chore})


@parent_mode_required
def delete_chore(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    if request.method == "POST":
        chore.delete()
        return redirect("chores:setup_chores")

    return render(request, "chores/delete_chore.html", {"chore": chore})


@parent_mode_required
def month_history(request):
    today = timezone.localdate()
    kids = list(Kid.objects.all())
    chores = list(Chore.objects.select_related("kid"))
    completions = ChoreCompletion.objects.filter(
        completed_on__gte=today.replace(day=1),
        completed_on__lte=today,
    ).select_related("chore", "chore__kid")
    context = build_month_history(kids, chores, completions, today)
    return render(request, "chores/month_history.html", context)
