"""
app.py
Flask CRUD application for managing employee records in PostgreSQL.

Routes:
    GET  /                     -> list employees (with optional search)
    GET  /employees/new        -> show "add employee" form
    POST /employees/new        -> create employee
    GET  /employees/<id>/edit  -> show "edit employee" form
    POST /employees/<id>/edit  -> update employee
    POST /employees/<id>/delete-> delete employee
"""

import psycopg2
import psycopg2.extras
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Human Resources",
    "Finance",
    "Operations",
    "Customer Support",
]


def get_db_connection():
    """Open a new PostgreSQL connection using settings from Config."""
    return psycopg2.connect(**Config.db_connection_params())


def fetch_employee_or_none(employee_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM employees WHERE id = %s;", (employee_id,))
            return cur.fetchone()
    finally:
        conn.close()


def validate_employee_form(form):
    """Return (data_dict, list_of_errors) from a submitted form."""
    errors = []

    first_name = form.get("first_name", "").strip()
    last_name = form.get("last_name", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip()
    department = form.get("department", "").strip()
    position = form.get("position", "").strip()
    salary = form.get("salary", "").strip()
    hire_date = form.get("hire_date", "").strip()
    address = form.get("address", "").strip()
    latitude_raw = form.get("latitude", "").strip()
    longitude_raw = form.get("longitude", "").strip()

    if not first_name:
        errors.append("First name is required.")
    if not last_name:
        errors.append("Last name is required.")
    if not email:
        errors.append("Email is required.")
    if not department:
        errors.append("Department is required.")
    if not position:
        errors.append("Position is required.")
    if not hire_date:
        errors.append("Hire date is required.")
    if not address:
        errors.append("Address is required.")

    salary_value = None
    if salary:
        try:
            salary_value = float(salary)
            if salary_value < 0:
                errors.append("Salary cannot be negative.")
        except ValueError:
            errors.append("Salary must be a number.")
    else:
        errors.append("Salary is required.")

    # Coordinates dropped by clicking the map picker (see _location_picker.html).
    # Both are only present together — the hidden inputs are always written as a pair.
    picked_latitude = None
    picked_longitude = None
    if latitude_raw and longitude_raw:
        try:
            picked_latitude = float(latitude_raw)
            picked_longitude = float(longitude_raw)
        except ValueError:
            errors.append("That map pin looks invalid — click the map again to reset it.")

    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "department": department,
        "position": position,
        "salary": salary_value,
        "hire_date": hire_date,
        "address": address,
        "latitude": picked_latitude,
        "longitude": picked_longitude,
    }
    return data, errors


@app.route("/")
def list_employees():
    search = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = "SELECT * FROM employees WHERE TRUE"
            params = []

            if search:
                query += """ AND (
                    first_name ILIKE %s OR
                    last_name ILIKE %s OR
                    email ILIKE %s OR
                    position ILIKE %s
                )"""
                like_term = f"%{search}%"
                params.extend([like_term, like_term, like_term, like_term])

            if department:
                query += " AND department = %s"
                params.append(department)

            query += " ORDER BY id DESC;"
            cur.execute(query, params)
            employees = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        "index.html",
        employees=employees,
        search=search,
        selected_department=department,
        departments=DEPARTMENTS,
    )


@app.route("/employees/new", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        data, errors = validate_employee_form(request.form)

        if not errors:
            if data["latitude"] is not None and data["longitude"] is not None:
                # User dropped a pin on the map picker — trust it over the text address.
                latitude, longitude = data["latitude"], data["longitude"]
            else:
                latitude, longitude = geocode_address(data["address"])

            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO employees
                            (first_name, last_name, email, phone, department,
                             position, salary, hire_date, address, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """,
                        (
                            data["first_name"], data["last_name"], data["email"],
                            data["phone"], data["department"], data["position"],
                            data["salary"], data["hire_date"], data["address"],
                            latitude, longitude,
                        ),
                    )
                conn.commit()
                flash(f"{data['first_name']} {data['last_name']} was added.", "success")
                if latitude is None:
                    flash("Couldn't find that address on the map — you can edit it later to try again.", "error")
                return redirect(url_for("list_employees"))
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                errors.append("An employee with that email already exists.")
            finally:
                conn.close()

        for error in errors:
            flash(error, "error")
        return render_template("add_employee.html", employee=data, departments=DEPARTMENTS), 400

    return render_template("add_employee.html", employee={}, departments=DEPARTMENTS)


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
def edit_employee(employee_id):
    existing = fetch_employee_or_none(employee_id)
    if existing is None:
        flash("That employee record doesn't exist.", "error")
        return redirect(url_for("list_employees"))

    if request.method == "POST":
        data, errors = validate_employee_form(request.form)

        if not errors:
            if data["latitude"] is not None and data["longitude"] is not None:
                # User dropped a pin on the map picker — trust it over the text address.
                latitude, longitude = data["latitude"], data["longitude"]
            elif data["address"] != (existing["address"] or ""):
                latitude, longitude = geocode_address(data["address"])
            else:
                latitude, longitude = existing["latitude"], existing["longitude"]

            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE employees
                        SET first_name = %s, last_name = %s, email = %s, phone = %s,
                            department = %s, position = %s, salary = %s, hire_date = %s,
                            address = %s, latitude = %s, longitude = %s
                        WHERE id = %s;
                        """,
                        (
                            data["first_name"], data["last_name"], data["email"],
                            data["phone"], data["department"], data["position"],
                            data["salary"], data["hire_date"], data["address"],
                            latitude, longitude, employee_id,
                        ),
                    )
                conn.commit()
                flash(f"{data['first_name']} {data['last_name']} was updated.", "success")
                if latitude is None:
                    flash("Couldn't find that address on the map — you can refine it and save again.", "error")
                return redirect(url_for("list_employees"))
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                errors.append("An employee with that email already exists.")
            finally:
                conn.close()

        for error in errors:
            flash(error, "error")
        data["id"] = employee_id
        return render_template("edit_employee.html", employee=data, departments=DEPARTMENTS), 400

    return render_template("edit_employee.html", employee=existing, departments=DEPARTMENTS)


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def delete_employee(employee_id):
    existing = fetch_employee_or_none(employee_id)
    if existing is None:
        flash("That employee record doesn't exist.", "error")
        return redirect(url_for("list_employees"))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM employees WHERE id = %s;", (employee_id,))
        conn.commit()
        flash(f"{existing['first_name']} {existing['last_name']} was removed.", "success")
    finally:
        conn.close()

    return redirect(url_for("list_employees"))

# Free geocoding via OpenStreetMap's Nominatim — no API key needed.
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
NOMINATIM_HEADERS = {"User-Agent": "employee-roster-flask-app/1.0"}


def geocode_address(address):
    """Forward geocode: address text -> (latitude, longitude), or (None, None)
    if not found/unreachable. Used as a fallback when no pin was dropped on the
    map picker."""
    if not address:
        return None, None
    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params={"q": address, "format": "json", "limit": 1},
            headers=NOMINATIM_HEADERS,
            timeout=5,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass
    return None, None


@app.route("/api/reverse-geocode")
def reverse_geocode():
    """Reverse geocode: lat/lon -> a human-readable address. Called by the
    map picker (_location_picker.html) whenever the user clicks the map, so
    the address field can fill itself in from the pin."""
    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))
    except (TypeError, ValueError):
        return {"error": "Invalid coordinates."}, 400

    try:
        response = requests.get(
            NOMINATIM_REVERSE_URL,
            params={"lat": lat, "lon": lon, "format": "json"},
            headers=NOMINATIM_HEADERS,
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError):
        return {"error": "Reverse geocoding failed. Try again."}, 502

    address = result.get("display_name")
    if not address:
        return {"error": "No address found for that location."}, 404
    return {"address": address}

# New routes
@app.route("/employees/<int:employee_id>")
def view_employee(employee_id):
    employee = fetch_employee_or_none(employee_id)
    if employee is None:
        flash("That employee record doesn't exist.", "error")
        return redirect(url_for("list_employees"))
    return render_template("view_employee.html", employee=employee)


@app.route("/map")
def employees_map():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM employees ORDER BY last_name, first_name;")
            employees = cur.fetchall()
    finally:
        conn.close()

    located = [e for e in employees if e["latitude"] is not None and e["longitude"] is not None]
    missing = [e for e in employees if e not in located]
    markers = [
        {"id": e["id"], "name": f"{e['first_name']} {e['last_name']}",
         "department": e["department"], "position": e["position"],
         "address": e["address"], "lat": float(e["latitude"]), "lng": float(e["longitude"])}
        for e in located
    ]
    return render_template("employees_map.html", markers=markers, missing=missing)

if __name__ == "__main__":
    app.run(debug=True)