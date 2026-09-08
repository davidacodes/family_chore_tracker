from datetime import timedelta

from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import timezone

from .calendar import DATE_QUERY_FORMAT, parse_selected_week, week_dates
from .forms import KidForm
from .models import Kid


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
