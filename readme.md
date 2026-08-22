# Employee Roster (Flask + PostgreSQL + Tailwind)

A simple CRUD app for managing employee records.

## Project structure

```text
employee_crud/
├── app.py                     # Flask routes (list, create, edit, delete, geocoding)
├── config.py                  # Reads DB settings from environment / .env
├── schema.sql                 # Creates the `employees` table (+ sample rows)
├── requirements.txt
├── .env.example
└── templates/
    ├── base.html               # Shared layout, nav, flash messages, Tailwind setup
    ├── index.html               # Employee list, search, filter
    ├── add_employee.html        # Create form
    ├── edit_employee.html       # Edit form
    ├── view_employee.html       # Single employee profile + location
    ├── employees_map.html       # Roster-wide "Map view" of every located employee
    └── _location_picker.html    # Shared click-to-pin address field (add/edit forms)
```

## 1. Set up PostgreSQL

Create a database and load the schema:

```bash
createdb employee_db
psql -d employee_db -f schema.sql
```

This creates the `employees` table and inserts 3 sample rows so the UI isn't empty.

## 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your real database credentials:

```env
SECRET_KEY=some-random-string
DB_HOST=localhost
DB_PORT=5432
DB_NAME=employee_db
DB_USER=postgres
DB_PASSWORD=your-password
```

## 3. Install dependencies and run

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

Visit **<http://127.0.0.1:5000>**.

## Features

- **List** — table of all employees with a monospace `EMP-000x` ID tag, search by name/email/position, and filter by department.
- **Create** — `/employees/new`, validates required fields and salary format, and flashes a duplicate-email error if one already exists.
- **Update** — `/employees/<id>/edit`, pre-fills the form with existing values.
- **Delete** — POST-only, with a JS confirmation prompt before removal.
- **View** — `/employees/<id>`, a full profile page (contact info, employment details, address, and a small map centered on that one employee).
- **Location picker** — the residential address field on the create/edit forms includes a click-to-pin Leaflet map: clicking anywhere drops a pin and reverse-geocodes it into the address text automatically (via `/api/reverse-geocode`). If you skip the map and just type an address, it's forward-geocoded on save instead.
- **Map view** — `/map`, a nav-bar link showing every located employee as a pin on one roster-wide map.

Geocoding (in both directions) is done via OpenStreetMap's **Nominatim** — free, no API key required, but rate-limited to about 1 request/second, so it's only suitable for light/internal use.

## Notes on going to production

- Set `SECRET_KEY` to a real random value and don't run with `debug=True`.
- Consider using a connection pool (e.g. `psycopg2.pool` or `SQLAlchemy`) instead of opening a new connection per request.
- Add authentication if this will be exposed beyond a trusted internal network — as written, anyone who can reach the app can edit or delete records, including everyone's home address.
- Nominatim's usage policy caps free requests to ~1/sec — for real traffic, switch to a paid geocoding provider or self-hosted Nominatim instance.
