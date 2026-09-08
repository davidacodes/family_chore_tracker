from datetime import date, timedelta


DATE_QUERY_FORMAT = "%Y-%m-%d"


def week_start_for(day):
    days_since_sunday = (day.weekday() + 1) % 7
    return day - timedelta(days=days_since_sunday)


def week_dates(week_start):
    return [week_start + timedelta(days=offset) for offset in range(7)]


def sunday_based_weekday(day):
    return (day.weekday() + 1) % 7


def parse_selected_week(raw_week, today):
    if not raw_week:
        return week_start_for(today)

    try:
        selected_day = date.fromisoformat(raw_week)
    except ValueError:
        return week_start_for(today)

    return week_start_for(selected_day)


def build_week_grid(kids, chores, week):
    chores_by_kid_and_day = {}
    for chore in chores:
        for due_day in chore.due_days:
            chores_by_kid_and_day.setdefault((chore.kid_id, due_day), []).append(chore)

    rows = []
    for kid in kids:
        cells = []
        for day in week:
            cells.append(
                {
                    "date": day,
                    "chores": chores_by_kid_and_day.get(
                        (kid.id, sunday_based_weekday(day)),
                        [],
                    ),
                }
            )
        rows.append({"kid": kid, "cells": cells})

    return rows


def build_completion_week_grid(kids, chores, completions, week):
    completed_chore_dates = {
        (completion.chore_id, completion.completed_on) for completion in completions
    }
    rows = build_week_grid(kids, chores, week)

    for row in rows:
        for cell in row["cells"]:
            cell["chore_items"] = [
                {
                    "chore": chore,
                    "is_complete": (chore.id, cell["date"]) in completed_chore_dates,
                }
                for chore in cell["chores"]
            ]

    return rows


def chore_is_due_on(chore, day):
    return sunday_based_weekday(day) in chore.due_days
