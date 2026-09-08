from datetime import date, timedelta


DATE_QUERY_FORMAT = "%Y-%m-%d"


def week_start_for(day):
    days_since_sunday = (day.weekday() + 1) % 7
    return day - timedelta(days=days_since_sunday)


def week_dates(week_start):
    return [week_start + timedelta(days=offset) for offset in range(7)]


def parse_selected_week(raw_week, today):
    if not raw_week:
        return week_start_for(today)

    try:
        selected_day = date.fromisoformat(raw_week)
    except ValueError:
        return week_start_for(today)

    return week_start_for(selected_day)
