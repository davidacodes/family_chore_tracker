from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from .calendar import DATE_QUERY_FORMAT, parse_selected_week, week_dates


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
