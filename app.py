"""
app.py
Flask Payroll System — CRUD application for managing employee records
and payroll information in PostgreSQL.

Routes:
    GET  /                     -> list employees (with optional search)
    GET  /employees/new        -> show "add employee" form
    POST /employees/new        -> create employee
    GET  /employees/<id>/edit  -> show "edit employee" form
    POST /employees/<id>/edit  -> update employee
    POST /employees/<id>/delete-> delete employee
    GET  /employees/<id>       -> view employee profile
    GET  /map                  -> employee locations map
    GET  /api/reverse-geocode  -> reverse geocode API
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

EMPLOYMENT_TYPES = [
    "Full-time",
    "Part-time",
    "Contract",
    "Intern",
]

EMPLOYMENT_STATUSES = [
    "Active",
    "On Leave",
    "Suspended",
    "Terminated",
    "Resigned",
]

PAYMENT_METHODS = [
    "Bank Transfer",
    "Cash",
    "Cheque",
]

TAX_FILING_STATUSES = [
    "Single",
    "Married",
    "Other",
]

GENDERS = [
    "Male",
    "Female",
    "Other",
    "Prefer not to say",
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


def _form_constants():
    """Return the dict of dropdown constants passed to every form template."""
    return {
        "departments": DEPARTMENTS,
        "employment_types": EMPLOYMENT_TYPES,
        "employment_statuses": EMPLOYMENT_STATUSES,
        "payment_methods": PAYMENT_METHODS,
        "tax_filing_statuses": TAX_FILING_STATUSES,
        "genders": GENDERS,
    }


def validate_employee_form(form):
    """Return (data_dict, list_of_errors) from a submitted form."""
    errors = []

    # ── Personal details ──
    first_name = form.get("first_name", "").strip()
    last_name = form.get("last_name", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip()
    date_of_birth = form.get("date_of_birth", "").strip()
    gender = form.get("gender", "").strip()
    national_id = form.get("national_id", "").strip()

    # ── Emergency contact ──
    emergency_contact_name = form.get("emergency_contact_name", "").strip()
    emergency_contact_phone = form.get("emergency_contact_phone", "").strip()

    # ── Employment details ──
    department = form.get("department", "").strip()
    position = form.get("position", "").strip()
    employment_type = form.get("employment_type", "").strip()
    hire_date = form.get("hire_date", "").strip()
    employment_status = form.get("employment_status", "").strip()

    # ── Compensation ──
    salary = form.get("salary", "").strip()
    housing_allowance_raw = form.get("housing_allowance", "").strip()
    transport_allowance_raw = form.get("transport_allowance", "").strip()
    medical_allowance_raw = form.get("medical_allowance", "").strip()
    other_allowance_raw = form.get("other_allowance", "").strip()

    # ── Bank / payment ──
    payment_method = form.get("payment_method", "").strip()
    bank_name = form.get("bank_name", "").strip()
    bank_branch = form.get("bank_branch", "").strip()
    bank_account_number = form.get("bank_account_number", "").strip()

    # ── Tax & statutory ──
    tax_id = form.get("tax_id", "").strip()
    epf_number = form.get("epf_number", "").strip()
    esi_number = form.get("esi_number", "").strip()
    tax_filing_status = form.get("tax_filing_status", "").strip()

    # ── Address / location ──
    address = form.get("address", "").strip()
    latitude_raw = form.get("latitude", "").strip()
    longitude_raw = form.get("longitude", "").strip()

    # ── Required field validation ──
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
    if not employment_type:
        errors.append("Employment type is required.")
    if not employment_status:
        errors.append("Employment status is required.")

    # ── Salary validation ──
    salary_value = None
    if salary:
        try:
            salary_value = float(salary)
            if salary_value < 0:
                errors.append("Basic salary cannot be negative.")
        except ValueError:
            errors.append("Basic salary must be a number.")
    else:
        errors.append("Basic salary is required.")

    # ── Allowance validation (optional, default 0) ──
    def _parse_allowance(raw, label):
        if not raw:
            return 0.0
        try:
            val = float(raw)
            if val < 0:
                errors.append(f"{label} cannot be negative.")
                return 0.0
            return val
        except ValueError:
            errors.append(f"{label} must be a number.")
            return 0.0

    housing_allowance = _parse_allowance(housing_allowance_raw, "Housing allowance")
    transport_allowance = _parse_allowance(transport_allowance_raw, "Transport allowance")
    medical_allowance = _parse_allowance(medical_allowance_raw, "Medical allowance")
    other_allowance = _parse_allowance(other_allowance_raw, "Other allowance")

    # ── Bank details validation ──
    if payment_method == "Bank Transfer":
        if not bank_name:
            errors.append("Bank name is required for bank transfer payments.")
        if not bank_account_number:
            errors.append("Account number is required for bank transfer payments.")

    # ── Coordinates from map picker ──
    picked_latitude = None
    picked_longitude = None
    if latitude_raw and longitude_raw:
        try:
            picked_latitude = float(latitude_raw)
            picked_longitude = float(longitude_raw)
        except ValueError:
            errors.append("That map pin looks invalid — click the map again to reset it.")

    data = {
        # Personal
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "date_of_birth": date_of_birth or None,
        "gender": gender or None,
        "national_id": national_id or None,
        # Emergency contact
        "emergency_contact_name": emergency_contact_name or None,
        "emergency_contact_phone": emergency_contact_phone or None,
        # Employment
        "department": department,
        "position": position,
        "employment_type": employment_type,
        "hire_date": hire_date,
        "employment_status": employment_status,
        # Compensation
        "salary": salary_value,
        "housing_allowance": housing_allowance,
        "transport_allowance": transport_allowance,
        "medical_allowance": medical_allowance,
        "other_allowance": other_allowance,
        # Bank
        "payment_method": payment_method or "Bank Transfer",
        "bank_name": bank_name or None,
        "bank_branch": bank_branch or None,
        "bank_account_number": bank_account_number or None,
        # Tax
        "tax_id": tax_id or None,
        "epf_number": epf_number or None,
        "esi_number": esi_number or None,
        "tax_filing_status": tax_filing_status or None,
        # Location
        "address": address,
        "latitude": picked_latitude,
        "longitude": picked_longitude,
    }
    return data, errors


# ── All columns (excluding id, created_at, updated_at) for INSERT ──
_INSERT_COLS = [
    "first_name", "last_name", "email", "phone",
    "date_of_birth", "gender", "national_id",
    "emergency_contact_name", "emergency_contact_phone",
    "department", "position", "employment_type", "hire_date", "employment_status",
    "salary", "housing_allowance", "transport_allowance", "medical_allowance", "other_allowance",
    "payment_method", "bank_name", "bank_branch", "bank_account_number",
    "tax_id", "epf_number", "esi_number", "tax_filing_status",
    "address", "latitude", "longitude",
]

_INSERT_SQL = f"""
    INSERT INTO employees ({', '.join(_INSERT_COLS)})
    VALUES ({', '.join(['%s'] * len(_INSERT_COLS))});
"""

_UPDATE_SETS = ', '.join(f"{col} = %s" for col in _INSERT_COLS)
_UPDATE_SQL = f"""
    UPDATE employees SET {_UPDATE_SETS} WHERE id = %s;
"""


@app.route("/")
def list_employees():
    search = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()

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

            if status:
                query += " AND employment_status = %s"
                params.append(status)

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
        selected_status=status,
        departments=DEPARTMENTS,
        employment_statuses=EMPLOYMENT_STATUSES,
    )


@app.route("/employees/new", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        data, errors = validate_employee_form(request.form)

        if not errors:
            if data["latitude"] is not None and data["longitude"] is not None:
                latitude, longitude = data["latitude"], data["longitude"]
            else:
                latitude, longitude = geocode_address(data["address"])

            data["latitude"] = latitude
            data["longitude"] = longitude

            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        _INSERT_SQL,
                        tuple(data[col] for col in _INSERT_COLS),
                    )
                conn.commit()
                flash(f"{data['first_name']} {data['last_name']} was added.", "success")
                if latitude is None and data["address"]:
                    flash("Couldn't find that address on the map — you can edit it later to try again.", "error")
                return redirect(url_for("list_employees"))
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                errors.append("An employee with that email already exists.")
            finally:
                conn.close()

        for error in errors:
            flash(error, "error")
        return render_template("add_employee.html", employee=data, **_form_constants()), 400

    return render_template("add_employee.html", employee={}, **_form_constants())


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
                latitude, longitude = data["latitude"], data["longitude"]
            elif data["address"] != (existing["address"] or ""):
                latitude, longitude = geocode_address(data["address"])
            else:
                latitude, longitude = existing["latitude"], existing["longitude"]

            data["latitude"] = latitude
            data["longitude"] = longitude

            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        _UPDATE_SQL,
                        tuple(data[col] for col in _INSERT_COLS) + (employee_id,),
                    )
                conn.commit()
                flash(f"{data['first_name']} {data['last_name']} was updated.", "success")
                if latitude is None and data["address"]:
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
        return render_template("edit_employee.html", employee=data, **_form_constants()), 400

    return render_template("edit_employee.html", employee=existing, **_form_constants())


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