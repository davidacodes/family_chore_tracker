# Family Chore Tracker

A shared-screen family chore tracker and scheduler built with Django, HTMX, and SQLite.

## Development

Run these commands from the repository root.

Install dependencies:

```bash
uv sync
```

Apply database migrations:

```bash
uv run python manage.py migrate
```

Start the Django development server:

```bash
uv run python manage.py runserver
```

Run the tests:

```bash
uv run pytest
```

## V1 Notes

V1 uses SQLite for local development and storage.

Parent mode protects setup and edit actions, including kid setup, chore setup,
and editing or deleting existing kids and chores. Kids can mark due chores
complete from the shared calendar without entering the parent PIN.

Completion history is stored by concrete calendar date, so the app can show
which chores were completed or missed on each day.
