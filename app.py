"""
app.py
Flask Payroll System — CRUD, Attendance, Payroll & Overtime Management.

Employee Routes:
    GET  /                     -> list employees
    GET  /employees/new        -> add employee form
    POST /employees/new        -> create employee
    GET  /employees/<id>/edit  -> edit employee form
    POST /employees/<id>/edit  -> update employee
    POST /employees/<id>/delete-> delete employee
    GET  /employees/<id>       -> view employee profile
    GET  /map                  -> employee map

Attendance Routes:
    GET  /employees/<id>/attendance/<year>/<month> -> monthly grid
    POST /employees/<id>/attendance/<year>/<month> -> save attendance

Payroll Routes:
    GET  /payroll                            -> payroll dashboard
    POST /payroll/generate/<year>/<month>    -> auto-generate payroll
    GET  /payroll/<year>/<month>/<id>        -> view payslip
    POST /payroll/<year>/<month>/<id>/update -> update deductions

Settings:
    GET/POST /settings -> company settings (bonus, incentive)

API:
    GET  /api/reverse-geocode -> reverse geocode
"""

import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal

import os
import uuid
import psycopg2
import psycopg2.extras
from werkzeug.utils import secure_filename
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g

from config import Config

app = Flask(__name__)

@app.context_processor
def inject_globals():
    return {
        "departments": get_list_setting("departments", ["HR", "IT", "Sales", "Operations", "Finance", "Management", "Marketing", "Support"]),
        "employment_types": get_list_setting("employment_types", ["Full-time", "Part-time", "Contract", "Intern"]),
        "employment_statuses": get_list_setting("employment_statuses", ["Active", "On Leave", "Suspended", "Terminated", "Resigned"]),
        "tax_filing_statuses": get_list_setting("social_statuses", ["Single", "Married", "Other"]),
        "genders": get_list_setting("genders", ["Male", "Female", "Other", "Prefer not to say"]),
        "employee_categories": ["Employee", "Labourer"],
        "payment_methods": ["Bank Transfer", "Cash", "Cheque"],
        "attendance_statuses": ["Present", "Absent", "Half-day", "No-pay", "Leave"],
        "leave_types": ["Annual", "Casual", "Medical"]
    }

app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'static/uploads/photos'

# ── Authentication ──
@app.before_request
def load_logged_in_user():
    g.user = None
    if 'user_id' in session:
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, username, role FROM users WHERE id = %s", (session['user_id'],))
                g.user = cur.fetchone()
        finally:
            conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None or g.user['role'] not in roles:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for('list_employees'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user and check_password_hash(user['password_hash'], password):
                    session.clear()
                    session['user_id'] = user['id']
                    return redirect(request.args.get('next') or url_for('list_employees'))
                else:
                    flash('Invalid username or password.', 'error')
        finally:
            conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Constants ──


# ── DB helpers ──

def get_db_connection():
    return psycopg2.connect(**Config.db_connection_params())


def fetch_employee_or_none(employee_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM employees WHERE id = %s;", (employee_id,))
            return cur.fetchone()
    finally:
        conn.close()



def get_company_setting(key, default="0"):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT setting_value FROM company_settings WHERE setting_key = %s;", (key,))
            row = cur.fetchone()
            return row[0] if row else default
    finally:
        conn.close()

def get_list_setting(key, default_list):
    val = get_company_setting(key, None)
    if not val:
        return default_list
    return [x.strip() for x in val.split(',') if x.strip()]

# ── Validation ──

def validate_employee_form(form):
    errors = []

    first_name = form.get("first_name", "").strip()
    last_name = form.get("last_name", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip()
    date_of_birth = form.get("date_of_birth", "").strip()
    gender = form.get("gender", "").strip()
    national_id = form.get("national_id", "").strip()
    emergency_contact_name = form.get("emergency_contact_name", "").strip()
    emergency_contact_phone = form.get("emergency_contact_phone", "").strip()
    department = form.get("department", "").strip()
    position = form.get("position", "").strip()
    employment_type = form.get("employment_type", "").strip()
    hire_date = form.get("hire_date", "").strip()
    employment_status = form.get("employment_status", "").strip()
    employee_category = form.get("employee_category", "").strip()
    salary = form.get("salary", "").strip()
    housing_allowance_raw = form.get("housing_allowance", "").strip()
    transport_allowance_raw = form.get("transport_allowance", "").strip()
    medical_allowance_raw = form.get("medical_allowance", "").strip()
    other_allowance_raw = form.get("other_allowance", "").strip()
    payment_method = form.get("payment_method", "").strip()
    bank_name = form.get("bank_name", "").strip()
    bank_branch = form.get("bank_branch", "").strip()
    bank_account_number = form.get("bank_account_number", "").strip()
    tax_id = form.get("tax_id", "").strip()
    epf_number = form.get("epf_number", "").strip()
    tax_filing_status = form.get("tax_filing_status", "").strip()
    address = form.get("address", "").strip()
    latitude_raw = form.get("latitude", "").strip()
    longitude_raw = form.get("longitude", "").strip()

    # Leave quotas
    annual_leave_raw = form.get("annual_leave_allowed", "14").strip()
    casual_leave_raw = form.get("casual_leave_allowed", "7").strip()
    medical_leave_raw = form.get("medical_leave_allowed", "7").strip()

    if not first_name: errors.append("First name is required.")
    if not last_name: errors.append("Last name is required.")
    if not email: errors.append("Email is required.")
    if not department: errors.append("Department is required.")
    if not position: errors.append("Position is required.")
    if not hire_date: errors.append("Hire date is required.")
    if not employment_type: errors.append("Employment type is required.")
    if not employment_status: errors.append("Employment status is required.")
    if not employee_category: errors.append("Employee category is required.")
    if not tax_id: errors.append("Tax ID is required.")
    if not epf_number: errors.append("EPF Number is required.")

    salary_value = None
    if salary:
        try:
            salary_value = float(salary)
            if salary_value < 0: errors.append("Basic salary cannot be negative.")
        except ValueError:
            errors.append("Basic salary must be a number.")
    else:
        errors.append("Basic salary is required.")

    def _parse_allowance(raw, label):
        if not raw: return 0.0
        try:
            val = float(raw)
            if val < 0: errors.append(f"{label} cannot be negative."); return 0.0
            return val
        except ValueError:
            errors.append(f"{label} must be a number."); return 0.0

    housing_allowance = _parse_allowance(housing_allowance_raw, "Housing allowance")
    transport_allowance = _parse_allowance(transport_allowance_raw, "Transport allowance")
    medical_allowance = _parse_allowance(medical_allowance_raw, "Medical allowance")
    other_allowance = _parse_allowance(other_allowance_raw, "Other allowance")

    def _parse_int(raw, label, default):
        if not raw: return default
        try:
            val = int(raw)
            if val < 0: errors.append(f"{label} cannot be negative."); return default
            return val
        except ValueError:
            errors.append(f"{label} must be a whole number."); return default

    annual_leave_allowed = _parse_int(annual_leave_raw, "Annual leave", 14)
    casual_leave_allowed = _parse_int(casual_leave_raw, "Casual leave", 7)
    medical_leave_allowed = _parse_int(medical_leave_raw, "Medical leave", 7)

    if payment_method == "Bank Transfer":
        if not bank_name: errors.append("Bank name is required for bank transfer payments.")
        if not bank_account_number: errors.append("Account number is required for bank transfer payments.")

    picked_latitude = None
    picked_longitude = None
    if latitude_raw and longitude_raw:
        try:
            picked_latitude = float(latitude_raw)
            picked_longitude = float(longitude_raw)
        except ValueError:
            errors.append("That map pin looks invalid — click the map again to reset it.")

    data = {
        "first_name": first_name, "last_name": last_name, "email": email, "phone": phone,
        "date_of_birth": date_of_birth or None, "gender": gender or None,
        "national_id": national_id or None,
        "emergency_contact_name": emergency_contact_name or None,
        "emergency_contact_phone": emergency_contact_phone or None,
        "department": department, "position": position,
        "employment_type": employment_type, "hire_date": hire_date,
        "employment_status": employment_status,
        "employee_category": employee_category,
        "salary": salary_value,
        "housing_allowance": housing_allowance, "transport_allowance": transport_allowance,
        "medical_allowance": medical_allowance, "other_allowance": other_allowance,
        "annual_leave_allowed": annual_leave_allowed,
        "casual_leave_allowed": casual_leave_allowed,
        "medical_leave_allowed": medical_leave_allowed,
        "payment_method": payment_method or "Bank Transfer",
        "bank_name": bank_name or None, "bank_branch": bank_branch or None,
        "bank_account_number": bank_account_number or None,
        "tax_id": tax_id or None, "epf_number": epf_number or None,
        "tax_filing_status": tax_filing_status or None,
        "address": address, "latitude": picked_latitude, "longitude": picked_longitude,
    }
    return data, errors


# ── Column lists for INSERT/UPDATE ──
_INSERT_COLS = [
    "first_name", "last_name", "email", "phone",
    "date_of_birth", "gender", "national_id",
    "emergency_contact_name", "emergency_contact_phone",
    "department", "position", "employment_type", "hire_date", "employment_status",
    "employee_category",
    "salary", "housing_allowance", "transport_allowance", "medical_allowance", "other_allowance",
    "annual_leave_allowed", "casual_leave_allowed", "medical_leave_allowed",
    "payment_method", "bank_name", "bank_branch", "bank_account_number",
    "tax_id", "epf_number", "tax_filing_status",
    "address", "latitude", "longitude",
    "photo",
]

_INSERT_SQL = f"""
    INSERT INTO employees ({', '.join(_INSERT_COLS)})
    VALUES ({', '.join(['%s'] * len(_INSERT_COLS))});
"""
_UPDATE_SETS = ', '.join(f"{col} = %s" for col in _INSERT_COLS)
_UPDATE_SQL = f"UPDATE employees SET {_UPDATE_SETS} WHERE id = %s;"



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def handle_photo_upload(file):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        return unique_filename
    return None

# ═══════════════════════════════════════════
# EMPLOYEE CRUD ROUTES
# ═══════════════════════════════════════════

@app.route("/")
@login_required
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
                query += " AND (first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s OR position ILIKE %s)"
                like = f"%{search}%"
                params.extend([like, like, like, like])
            if department:
                query += " AND department = %s"; params.append(department)
            if status:
                query += " AND employment_status = %s"; params.append(status)
            query += " ORDER BY id DESC;"
            cur.execute(query, params)
            employees = cur.fetchall()
    finally:
        conn.close()

    return render_template("index.html", employees=employees, search=search,
                           selected_department=department, selected_status=status)


@app.route("/employees/new", methods=["GET", "POST"])
@login_required
@role_required("Admin", "HR")

def add_employee():
    if request.method == "POST":
        data, errors = validate_employee_form(request.form)
        if not errors:
            if data["latitude"] is not None and data["longitude"] is not None:
                lat, lon = data["latitude"], data["longitude"]
            else:
                lat, lon = geocode_address(data["address"])
            data["latitude"], data["longitude"] = lat, lon
            
            photo_filename = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        from PIL import Image
                        try:
                            img = Image.open(file)
                            width, height = img.size
                            file.seek(0)
                            if width != height:
                                errors.append(f"Image must be square (current: {width}x{height}px).")
                            elif width < 200 or width > 400:
                                errors.append(f"Image dimensions must be between 200x200 and 400x400 pixels (current: {width}x{height}px).")
                            else:
                                photo_filename = handle_photo_upload(file)
                        except Exception:
                            file.seek(0)
                            errors.append("Invalid image file.")
                    else:
                        errors.append("Invalid photo format. Only JPG, JPEG, and PNG are allowed.")
            
            if not errors:
                data["photo"] = photo_filename
                conn = get_db_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute(_INSERT_SQL, tuple(data[c] for c in _INSERT_COLS))
                    conn.commit()
                    flash(f"{data['first_name']} {data['last_name']} was added.", "success")
                    if lat is None and data["address"]:
                        flash("Couldn't locate that address on the map.", "error")
                    return redirect(url_for("list_employees"))
                except psycopg2.errors.UniqueViolation as e:
                    conn.rollback()
                    err_msg = str(e)
                    if "email" in err_msg:
                        errors.append("An employee with that email already exists.")
                    elif "tax_id" in err_msg:
                        errors.append("An employee with that Tax ID already exists.")
                    elif "epf_number" in err_msg:
                        errors.append("An employee with that EPF Number already exists.")
                    else:
                        errors.append("A unique constraint violation occurred.")
                finally:
                    conn.close()
        for e in errors: flash(e, "error")
        return render_template("add_employee.html", employee=data), 400
    return render_template("add_employee.html", employee={})


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "HR")

def edit_employee(employee_id):
    existing = fetch_employee_or_none(employee_id)
    if existing is None:
        flash("That employee record doesn't exist.", "error")
        return redirect(url_for("list_employees"))
    if request.method == "POST":
        data, errors = validate_employee_form(request.form)
        if not errors:
            if data["latitude"] is not None and data["longitude"] is not None:
                lat, lon = data["latitude"], data["longitude"]
            elif data["address"] != (existing["address"] or ""):
                lat, lon = geocode_address(data["address"])
            else:
                lat, lon = existing["latitude"], existing["longitude"]
            data["latitude"], data["longitude"] = lat, lon
            
            photo_filename = existing.get("photo")
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        from PIL import Image
                        try:
                            img = Image.open(file)
                            width, height = img.size
                            file.seek(0)
                            if width != height:
                                errors.append(f"Image must be square (current: {width}x{height}px).")
                            elif width < 200 or width > 400:
                                errors.append(f"Image dimensions must be between 200x200 and 400x400 pixels (current: {width}x{height}px).")
                            else:
                                new_photo = handle_photo_upload(file)
                                if new_photo:
                                    photo_filename = new_photo
                        except Exception:
                            file.seek(0)
                            errors.append("Invalid image file.")
                    else:
                        errors.append("Invalid photo format. Only JPG, JPEG, and PNG are allowed.")

            if not errors:
                data["photo"] = photo_filename
                conn = get_db_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute(_UPDATE_SQL, tuple(data[c] for c in _INSERT_COLS) + (employee_id,))
                    conn.commit()
                    flash(f"{data['first_name']} {data['last_name']} was updated.", "success")
                    return redirect(url_for("list_employees"))
                except psycopg2.errors.UniqueViolation as e:
                    conn.rollback()
                    err_msg = str(e)
                    if "email" in err_msg:
                        errors.append("An employee with that email already exists.")
                    elif "tax_id" in err_msg:
                        errors.append("An employee with that Tax ID already exists.")
                    elif "epf_number" in err_msg:
                        errors.append("An employee with that EPF Number already exists.")
                    else:
                        errors.append("A unique constraint violation occurred.")
                finally:
                    conn.close()
        for e in errors: flash(e, "error")
        data["id"] = employee_id
        return render_template("edit_employee.html", employee=data), 400
    return render_template("edit_employee.html", employee=existing)


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "HR")

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


@app.route("/employees/<int:employee_id>")
@login_required

def view_employee(employee_id):
    employee = fetch_employee_or_none(employee_id)
    if employee is None:
        flash("That employee record doesn't exist.", "error")
        return redirect(url_for("list_employees"))
    now = date.today()
    return render_template("view_employee.html", employee=employee,
                           current_year=now.year, current_month=now.month)


@app.route("/map")
@login_required

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


# ═══════════════════════════════════════════
# GEOCODING
# ═══════════════════════════════════════════

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
NOMINATIM_HEADERS = {"User-Agent": "employee-roster-flask-app/1.0"}


def geocode_address(address):
    if not address: return None, None
    try:
        r = requests.get(NOMINATIM_SEARCH_URL, params={"q": address, "format": "json", "limit": 1},
                         headers=NOMINATIM_HEADERS, timeout=5)
        r.raise_for_status()
        results = r.json()
        if results: return float(results[0]["lat"]), float(results[0]["lon"])
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass
    return None, None


@app.route("/api/reverse-geocode")
@login_required

def reverse_geocode():
    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))
    except (TypeError, ValueError):
        return {"error": "Invalid coordinates."}, 400
    try:
        r = requests.get(NOMINATIM_REVERSE_URL, params={"lat": lat, "lon": lon, "format": "json"},
                         headers=NOMINATIM_HEADERS, timeout=5)
        r.raise_for_status()
        result = r.json()
    except (requests.RequestException, ValueError):
        return {"error": "Reverse geocoding failed."}, 502
    addr = result.get("display_name")
    if not addr: return {"error": "No address found."}, 404
    return {"address": addr}


# ═══════════════════════════════════════════
# ATTENDANCE ROUTES

@app.route("/attendance/daily", methods=["GET", "POST"])
@login_required
@role_required("Admin", "HR")
def daily_attendance():
    date_str = request.args.get("date")
    if not date_str:
        target_date = date.today()
    else:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = date.today()

    conn = get_db_connection()
    try:
        if request.method == "POST":
            # Process bulk save
            is_sunday = target_date.weekday() == 6
            is_saturday = target_date.weekday() == 5
            
            with conn.cursor() as cur:
                # Get all active employees to loop through
                cur.execute("SELECT id FROM employees WHERE employment_status = 'Active';")
                employees = cur.fetchall()
                
                for emp in employees:
                    emp_id = emp[0]
                    prefix = f"emp_{emp_id}_"
                    
                    # Check if this employee was submitted in the form
                    if f"{prefix}status" not in request.form:
                        continue
                        
                    status = request.form.get(f"{prefix}status", "Present").strip()
                    leave_type = request.form.get(f"{prefix}leave_type", "").strip() or None
                    arrival = request.form.get(f"{prefix}arrival", "").strip() or None
                    departure = request.form.get(f"{prefix}departure", "").strip() or None
                    notes = request.form.get(f"{prefix}notes", "").strip() or None
                    
                    late = False
                    early = False
                    ot_hours = 0.0
                    ot_hours_sunday = 0.0
                    
                    if arrival and departure and status == "Present":
                        try:
                            arr = datetime.strptime(arrival, "%H:%M")
                            dep = datetime.strptime(departure, "%H:%M")
                            arr_time = arr.time()
                            dep_time = dep.time()
                            
                            standard_start = datetime.strptime("08:00", "%H:%M").time()
                            
                            if is_sunday:
                                total_worked = max(0, (dep - arr).total_seconds() / 3600)
                                ot_hours_sunday = round(total_worked, 2)
                            elif is_saturday:
                                standard_end_sat = datetime.strptime("13:00", "%H:%M").time()
                                if arr_time > standard_start: late = True
                                if dep_time < standard_end_sat: early = True
                                if dep_time > standard_end_sat:
                                    ot_dt = datetime.strptime("13:00", "%H:%M")
                                    ot_hours = round(max(0, (dep - ot_dt).total_seconds() / 3600), 2)
                            else:
                                standard_end = datetime.strptime("17:00", "%H:%M").time()
                                if arr_time > standard_start: late = True
                                if dep_time < standard_end: early = True
                                if dep_time > standard_end:
                                    ot_dt = datetime.strptime("17:00", "%H:%M")
                                    ot_hours = round(max(0, (dep - ot_dt).total_seconds() / 3600), 2)
                        except ValueError:
                            pass
                            
                    cur.execute('''
                        INSERT INTO attendance (employee_id, work_date, arrival_time, departure_time,
                            is_sunday, status, leave_type, late_arrival, early_departure,
                            ot_hours, ot_hours_sunday, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (employee_id, work_date)
                        DO UPDATE SET arrival_time = EXCLUDED.arrival_time,
                            departure_time = EXCLUDED.departure_time,
                            is_sunday = EXCLUDED.is_sunday,
                            status = EXCLUDED.status,
                            leave_type = EXCLUDED.leave_type,
                            late_arrival = EXCLUDED.late_arrival,
                            early_departure = EXCLUDED.early_departure,
                            ot_hours = EXCLUDED.ot_hours,
                            ot_hours_sunday = EXCLUDED.ot_hours_sunday,
                            notes = EXCLUDED.notes;
                    ''', (emp_id, target_date, arrival, departure, is_sunday, status,
                          leave_type, late, early, ot_hours, ot_hours_sunday, notes))
            conn.commit()
            flash("Daily attendance saved successfully.", "success")
            return redirect(url_for('daily_attendance', date=target_date.strftime("%Y-%m-%d")))

        # GET request: fetch data
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('''
                SELECT e.id as emp_id, e.first_name, e.last_name, e.department, e.position,
                       a.status, a.leave_type, a.arrival_time, a.departure_time, a.notes,
                       a.late_arrival, a.early_departure, a.ot_hours, a.ot_hours_sunday
                FROM employees e
                LEFT JOIN attendance a ON e.id = a.employee_id AND a.work_date = %s
                WHERE e.employment_status = 'Active'
                ORDER BY e.first_name, e.last_name;
            ''', (target_date,))
            records = cur.fetchall()
            
    finally:
        conn.close()

    is_sunday = target_date.weekday() == 6
    is_saturday = target_date.weekday() == 5
    
    # Process records for template
    for r in records:
        if r['arrival_time']: r['arrival_time'] = r['arrival_time'].strftime("%H:%M")
        else: r['arrival_time'] = ""
        
        if r['departure_time']: r['departure_time'] = r['departure_time'].strftime("%H:%M")
        else: r['departure_time'] = ""
        
        if not r['status']: r['status'] = 'Present'

    return render_template("daily_attendance.html", 
                           target_date=target_date, 
                           records=records,
                           is_sunday=is_sunday,
                           is_saturday=is_saturday,
                           attendance_statuses=ATTENDANCE_STATUSES,
                           leave_types=LEAVE_TYPES)

# ═══════════════════════════════════════════

@app.route("/employees/<int:employee_id>/attendance/<int:year>/<int:month>")
@login_required
def employee_attendance(employee_id, year, month):
    employee = fetch_employee_or_none(employee_id)
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("list_employees"))

    num_days = calendar.monthrange(year, month)[1]
    days = []
    for d in range(1, num_days + 1):
        dt = date(year, month, d)
        days.append({
            "date": dt, "day_name": dt.strftime("%a"),
            "is_sunday": dt.weekday() == 6,
        })

    # Fetch existing attendance
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM attendance
                WHERE employee_id = %s AND work_date >= %s AND work_date <= %s
                ORDER BY work_date;
            """, (employee_id, date(year, month, 1), date(year, month, num_days)))
            records = {r["work_date"]: r for r in cur.fetchall()}
    finally:
        conn.close()

    for day in days:
        rec = records.get(day["date"])
        if rec:
            day["arrival_time"] = rec["arrival_time"].strftime("%H:%M") if rec["arrival_time"] else ""
            day["departure_time"] = rec["departure_time"].strftime("%H:%M") if rec["departure_time"] else ""
            day["status"] = rec["status"]
            day["leave_type"] = rec["leave_type"] or ""
            day["ot_hours"] = float(rec["ot_hours"] or 0)
            day["ot_hours_sunday"] = float(rec["ot_hours_sunday"] or 0)
            day["late_arrival"] = rec["late_arrival"]
            day["early_departure"] = rec["early_departure"]
            day["notes"] = rec["notes"] or ""
        else:
            day.update({"arrival_time": "", "departure_time": "", "status": "Present",
                        "leave_type": "", "ot_hours": 0, "ot_hours_sunday": 0,
                        "late_arrival": False, "early_departure": False, "notes": ""})

    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    month_name = calendar.month_name[month]

    return render_template("attendance.html", employee=employee, days=days,
                           year=year, month=month, month_name=month_name,
                           prev_year=prev_year, prev_month=prev_month,
                           next_year=next_year, next_month=next_month,
                           attendance_statuses=ATTENDANCE_STATUSES,
                           leave_types=LEAVE_TYPES)


@app.route("/employees/<int:employee_id>/attendance/<int:year>/<int:month>", methods=["POST"])
@login_required
@role_required("Admin", "HR")
def save_attendance(employee_id, year, month):
    employee = fetch_employee_or_none(employee_id)
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("list_employees"))

    num_days = calendar.monthrange(year, month)[1]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for d in range(1, num_days + 1):
                dt = date(year, month, d)
                prefix = f"day_{d}_"

                status = request.form.get(f"{prefix}status", "Present").strip()
                leave_type = request.form.get(f"{prefix}leave_type", "").strip() or None
                arrival = request.form.get(f"{prefix}arrival", "").strip() or None
                departure = request.form.get(f"{prefix}departure", "").strip() or None
                notes = request.form.get(f"{prefix}notes", "").strip() or None
                is_sunday = dt.weekday() == 6
                
                late = False
                early = False
                ot_hours = 0.0
                ot_hours_sunday = 0.0
                
                if arrival and departure and status == "Present":
                    try:
                        from datetime import datetime
                        arr = datetime.strptime(arrival, "%H:%M")
                        dep = datetime.strptime(departure, "%H:%M")
                        arr_time = arr.time()
                        dep_time = dep.time()
                        
                        standard_start = datetime.strptime("08:00", "%H:%M").time()
                        
                        if is_sunday:
                            total_worked = max(0, (dep - arr).total_seconds() / 3600)
                            ot_hours_sunday = round(total_worked, 2)
                        elif dt.weekday() == 5:
                            # Saturday (Half Day)
                            standard_end_sat = datetime.strptime("13:00", "%H:%M").time()
                            if arr_time > standard_start: late = True
                            if dep_time < standard_end_sat: early = True
                            if dep_time > standard_end_sat:
                                ot_dt = datetime.strptime("13:00", "%H:%M")
                                ot_hours = round(max(0, (dep - ot_dt).total_seconds() / 3600), 2)
                        else:
                            # Weekday
                            standard_end = datetime.strptime("17:00", "%H:%M").time()
                            if arr_time > standard_start: late = True
                            if dep_time < standard_end: early = True
                            if dep_time > standard_end:
                                ot_dt = datetime.strptime("17:00", "%H:%M")
                                ot_hours = round(max(0, (dep - ot_dt).total_seconds() / 3600), 2)
                    except ValueError:
                        pass

                cur.execute("""
                    INSERT INTO attendance (employee_id, work_date, arrival_time, departure_time,
                        is_sunday, status, leave_type, late_arrival, early_departure,
                        ot_hours, ot_hours_sunday, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (employee_id, work_date)
                    DO UPDATE SET arrival_time = EXCLUDED.arrival_time,
                        departure_time = EXCLUDED.departure_time,
                        is_sunday = EXCLUDED.is_sunday,
                        status = EXCLUDED.status,
                        leave_type = EXCLUDED.leave_type,
                        late_arrival = EXCLUDED.late_arrival,
                        early_departure = EXCLUDED.early_departure,
                        ot_hours = EXCLUDED.ot_hours,
                        ot_hours_sunday = EXCLUDED.ot_hours_sunday,
                        notes = EXCLUDED.notes;
                """, (employee_id, dt, arrival, departure, is_sunday, status,
                      leave_type, late, early, ot_hours, ot_hours_sunday, notes))

        conn.commit()
        flash(f"Attendance for {calendar.month_name[month]} {year} saved.", "success")
    except Exception as ex:
        conn.rollback()
        flash(f"Error saving attendance: {ex}", "error")
    finally:
        conn.close()

    return redirect(url_for("employee_attendance", employee_id=employee_id, year=year, month=month))



@app.route("/attendance")
@login_required
def attendance_dashboard():
    year = request.args.get("year", default=datetime.now().year, type=int)
    month = request.args.get("month", default=datetime.now().month, type=int)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get start and end date for the month
            num_days = calendar.monthrange(year, month)[1]
            start_date = date(year, month, 1)
            end_date = date(year, month, num_days)
            
            cur.execute('''
                SELECT 
                    e.id, e.first_name, e.last_name, e.department,
                    COUNT(a.id) FILTER (WHERE a.status = 'Present') as working_days,
                    COUNT(a.id) FILTER (WHERE a.status = 'Absent') as absences,
                    COUNT(a.id) FILTER (WHERE a.status = 'No-pay') as no_pay_days,
                    COUNT(a.id) FILTER (WHERE a.late_arrival = true) as late_arrivals,
                    COUNT(a.id) FILTER (WHERE a.early_departure = true) as early_departures,
                    COALESCE(SUM(a.ot_hours), 0) as weekday_ot,
                    COALESCE(SUM(a.ot_hours_sunday), 0) as sunday_ot,
                    COUNT(a.id) FILTER (WHERE a.status = 'Leave') as leave_days
                FROM employees e
                LEFT JOIN attendance a ON e.id = a.employee_id 
                    AND a.work_date >= %s AND a.work_date <= %s
                WHERE e.employment_status = 'Active'
                GROUP BY e.id
                ORDER BY e.first_name, e.last_name;
            ''', (start_date, end_date))
            
            records = cur.fetchall()
            
            # Prepare months list for the dropdown
            months = [(i, calendar.month_name[i]) for i in range(1, 13)]
            month_name = calendar.month_name[month]
    finally:
        conn.close()
        
    return render_template("attendance_dashboard.html", 
                           records=records, 
                           year=year, month=month, 
                           months=months, month_name=month_name)


# ═══════════════════════════════════════════
# PAYROLL ROUTES
# ═══════════════════════════════════════════

def _calculate_ot_payment(basic, category, weekday_hours, sunday_hours):
    """Calculate overtime payment based on employee category and hours."""
    basic = float(basic or 0)
    weekday_hours = float(weekday_hours or 0)
    sunday_hours = float(sunday_hours or 0)
    divisor = 26 if category == "Labourer" else 30
    base_rate = (basic / divisor) / 8 if basic > 0 else 0

    weekday_ot = base_rate * 1.5 * weekday_hours

    # Sunday: first 8 hours at double, beyond 8 at triple
    sun_regular = min(sunday_hours, 8) * base_rate * 2
    sun_triple_hours = max(sunday_hours - 8, 0)
    sun_triple = sun_triple_hours * base_rate * 3

    return round(weekday_ot + sun_regular + sun_triple, 2), round(sun_triple_hours, 2)


@app.route("/payroll")
@login_required
def payroll_dashboard():
    now = date.today()
    year = int(request.args.get("year", now.year))
    month = int(request.args.get("month", now.month))

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # All active employees
            cur.execute("SELECT * FROM employees WHERE employment_status = 'Active' ORDER BY id;")
            employees = cur.fetchall()

            # Existing payroll records for this month
            cur.execute("SELECT * FROM payroll WHERE year = %s AND month = %s;", (year, month))
            payroll_records = {r["employee_id"]: r for r in cur.fetchall()}
    finally:
        conn.close()

    for emp in employees:
        emp["payroll"] = payroll_records.get(emp["id"])

    month_name = calendar.month_name[month]
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    return render_template("payroll_dashboard.html", employees=employees,
                           year=year, month=month, month_name=month_name,
                           months=months)


@app.route("/payroll/generate/<int:year>/<int:month>", methods=["POST"])
@login_required
@role_required("Admin", "HR")
def generate_payroll(year, month):
    """Auto-generate payroll for all active employees from attendance data."""
    bonus = float(get_company_setting("annual_bonus", "0"))
    incentive = float(get_company_setting("monthly_incentive", "0"))

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM employees WHERE employment_status = 'Active' ORDER BY id;")
            employees = cur.fetchall()

            generated = 0
            for emp in employees:
                eid = emp["id"]
                basic = float(emp["salary"] or 0)
                category = emp["employee_category"] or "Employee"
                total_allowances = sum(float(emp[k] or 0) for k in
                                       ["housing_allowance", "transport_allowance",
                                        "medical_allowance", "other_allowance"])

                # Summarize attendance for the month
                num_days = calendar.monthrange(year, month)[1]
                cur.execute("""
                    SELECT * FROM attendance
                    WHERE employee_id = %s AND work_date >= %s AND work_date <= %s;
                """, (eid, date(year, month, 1), date(year, month, num_days)))
                att_records = cur.fetchall()

                working_days = sum(1 for a in att_records if a["status"] == "Present")
                late_arrivals = sum(1 for a in att_records if a["late_arrival"])
                early_departures = sum(1 for a in att_records if a["early_departure"])
                absences = sum(1 for a in att_records if a["status"] == "Absent")
                no_pay_days = sum(1 for a in att_records if a["status"] == "No-pay")
                annual_leave = sum(1 for a in att_records if a["leave_type"] == "Annual")
                casual_leave = sum(1 for a in att_records if a["leave_type"] == "Casual")
                medical_leave = sum(1 for a in att_records if a["leave_type"] == "Medical")

                ot_weekday = sum(float(a["ot_hours"] or 0) for a in att_records)
                ot_sunday = sum(float(a["ot_hours_sunday"] or 0) for a in att_records)

                ot_payment, sun_triple_hours = _calculate_ot_payment(basic, category, ot_weekday, ot_sunday)

                # EPF / ETF
                epf_employee = round(basic * 0.08, 2)
                epf_employer = round(basic * 0.12, 2)
                etf_employer = round(basic * 0.03, 2)

                # No-pay deduction
                divisor = 26 if category == "Labourer" else 30
                no_pay_deduction = round((basic / divisor) * no_pay_days, 2) if no_pay_days > 0 else 0

                # Bonus: yearly, applied in December only
                month_bonus = bonus if month == 12 else 0

                gross = basic + total_allowances + ot_payment + month_bonus + incentive

                # --- Advances Deduction ---
                cur.execute("SELECT id, amount FROM advances WHERE employee_id = %s AND status = 'Approved'", (eid,))
                new_advances = cur.fetchall()
                print("EID:", eid, "NEW ADV:", new_advances)
                for adv in new_advances:
                    cur.execute("UPDATE advances SET status = 'Deducted', deduction_year = %s, deduction_month = %s WHERE id = %s", (year, month, adv["id"]))
                
                cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM advances WHERE employee_id = %s AND status = 'Deducted' AND deduction_year = %s AND deduction_month = %s", (eid, year, month))
                salary_advance = float(cur.fetchone()["total"])
                
                # --- Loans Deduction ---
                cur.execute("SELECT * FROM loans WHERE employee_id = %s AND status = 'Approved' AND remaining_amount > 0", (eid,))
                active_loans = cur.fetchall()
                for loan in active_loans:
                    cur.execute("SELECT amount FROM loan_installments WHERE loan_id = %s AND year = %s AND month = %s", (loan["id"], year, month))
                    if not cur.fetchone():
                        deduct_amt = min(float(loan["monthly_installment"]), float(loan["remaining_amount"]))
                        cur.execute("INSERT INTO loan_installments (loan_id, year, month, amount) VALUES (%s, %s, %s, %s)", (loan["id"], year, month, deduct_amt))
                        new_rem = float(loan["remaining_amount"]) - deduct_amt
                        new_rem_inst = int(loan["remaining_installments"]) - 1
                        new_status = 'Completed' if new_rem <= 0 else 'Approved'
                        cur.execute("UPDATE loans SET remaining_amount = %s, remaining_installments = %s, status = %s WHERE id = %s", (new_rem, new_rem_inst, new_status, loan["id"]))
                
                cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM loan_installments JOIN loans ON loan_installments.loan_id = loans.id WHERE loans.employee_id = %s AND year = %s AND month = %s", (eid, year, month))
                loan_deduction = float(cur.fetchone()["total"])

                total_deductions = epf_employee + no_pay_deduction + salary_advance + loan_deduction
                net = gross - total_deductions

                cur.execute("""
                    INSERT INTO payroll (employee_id, year, month,
                        basic_salary, total_allowances,
                        ot_hours_weekday, ot_hours_sunday, ot_hours_sunday_triple,
                        ot_payment, bonus, incentive, gross_salary,
                        epf_employee, no_pay_deduction, salary_advance, loan_deduction,
                        other_deductions, total_deductions,
                        epf_employer, etf_employer, net_salary,
                        working_days, late_arrivals, early_departures, absences,
                        no_pay_days, annual_leave_taken, casual_leave_taken, medical_leave_taken,
                        status)
                    VALUES (%s,%s,%s, %s,%s, %s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, 0,%s, %s,%s,%s,
                            %s,%s,%s,%s, %s,%s,%s,%s, 'Draft')
                    ON CONFLICT (employee_id, year, month) DO UPDATE SET
                        basic_salary=EXCLUDED.basic_salary, total_allowances=EXCLUDED.total_allowances,
                        ot_hours_weekday=EXCLUDED.ot_hours_weekday, ot_hours_sunday=EXCLUDED.ot_hours_sunday,
                        ot_hours_sunday_triple=EXCLUDED.ot_hours_sunday_triple,
                        ot_payment=EXCLUDED.ot_payment, bonus=EXCLUDED.bonus, incentive=EXCLUDED.incentive,
                        gross_salary=EXCLUDED.gross_salary,
                        epf_employee=EXCLUDED.epf_employee, no_pay_deduction=EXCLUDED.no_pay_deduction,
                        salary_advance=EXCLUDED.salary_advance, loan_deduction=EXCLUDED.loan_deduction,
                        total_deductions=EXCLUDED.total_deductions,
                        epf_employer=EXCLUDED.epf_employer, etf_employer=EXCLUDED.etf_employer,
                        net_salary=EXCLUDED.net_salary,
                        working_days=EXCLUDED.working_days, late_arrivals=EXCLUDED.late_arrivals,
                        early_departures=EXCLUDED.early_departures, absences=EXCLUDED.absences,
                        no_pay_days=EXCLUDED.no_pay_days,
                        annual_leave_taken=EXCLUDED.annual_leave_taken,
                        casual_leave_taken=EXCLUDED.casual_leave_taken,
                        medical_leave_taken=EXCLUDED.medical_leave_taken,
                        status='Draft'
                    WHERE payroll.status = 'Draft';
                """, (eid, year, month, basic, total_allowances,
                      ot_weekday, ot_sunday, sun_triple_hours,
                      ot_payment, month_bonus, incentive, gross,
                      epf_employee, no_pay_deduction, salary_advance, loan_deduction, total_deductions,
                      epf_employer, etf_employer, net,
                      working_days, late_arrivals, early_departures, absences,
                      no_pay_days, annual_leave, casual_leave, medical_leave))
                generated += 1

        conn.commit()
        flash(f"Payroll generated for {generated} employee(s) — {calendar.month_name[month]} {year}.", "success")
    except Exception as ex:
        conn.rollback()
        flash(f"Error generating payroll: {ex}", "error")
    finally:
        conn.close()

    return redirect(url_for("payroll_dashboard", year=year, month=month))


@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>")
@login_required
def view_payslip(year, month, employee_id):
    employee = fetch_employee_or_none(employee_id)
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("payroll_dashboard"))

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM payroll WHERE employee_id=%s AND year=%s AND month=%s;",
                        (employee_id, year, month))
            payslip = cur.fetchone()
    finally:
        conn.close()

    if payslip is None:
        flash("No payroll record found for this period. Generate payroll first.", "error")
        return redirect(url_for("payroll_dashboard", year=year, month=month))

    month_name = calendar.month_name[month]
    return render_template("payslip.html", employee=employee, payslip=payslip,
                           year=year, month=month, month_name=month_name)


@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/update", methods=["POST"])
@login_required
@role_required("Admin", "HR")
def update_payslip(year, month, employee_id):
    """Update manual deductions and recalculate net salary."""
    salary_advance = float(request.form.get("salary_advance", "0") or 0)
    loan_deduction = float(request.form.get("loan_deduction", "0") or 0)
    other_deductions = float(request.form.get("other_deductions", "0") or 0)

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM payroll WHERE employee_id=%s AND year=%s AND month=%s;",
                        (employee_id, year, month))
            payslip = cur.fetchone()
            if payslip is None:
                flash("Payroll record not found.", "error")
                return redirect(url_for("payroll_dashboard", year=year, month=month))

            total_deductions = (float(payslip["epf_employee"]) +
                                float(payslip["no_pay_deduction"]) +
                                salary_advance + loan_deduction + other_deductions)
            net = float(payslip["gross_salary"]) - total_deductions

            cur.execute("""
                UPDATE payroll SET salary_advance=%s, loan_deduction=%s,
                    other_deductions=%s, total_deductions=%s, net_salary=%s
                WHERE employee_id=%s AND year=%s AND month=%s;
            """, (salary_advance, loan_deduction, other_deductions,
                  total_deductions, net, employee_id, year, month))
        conn.commit()
        flash("Payslip deductions updated.", "success")
    finally:
        conn.close()

    return redirect(url_for("view_payslip", year=year, month=month, employee_id=employee_id))


# ═══════════════════════════════════════════
# SETTINGS ROUTE
# ═══════════════════════════════════════════

@app.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def company_settings():
    if request.method == "POST":
        bonus = request.form.get("annual_bonus", "0").strip()
        incentive = request.form.get("monthly_incentive", "0").strip()
        
        departments = request.form.get("departments", "").strip()
        employment_types = request.form.get("employment_types", "").strip()
        employment_statuses = request.form.get("employment_statuses", "").strip()
        social_statuses = request.form.get("social_statuses", "").strip()
        genders = request.form.get("genders", "").strip()
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                for key, val in [
                    ('annual_bonus', bonus),
                    ('monthly_incentive', incentive),
                    ('departments', departments),
                    ('employment_types', employment_types),
                    ('employment_statuses', employment_statuses),
                    ('social_statuses', social_statuses),
                    ('genders', genders)
                ]:
                    cur.execute("""
                        INSERT INTO company_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value,
                            updated_at = CURRENT_TIMESTAMP;
                    """, (key, val))
            conn.commit()
            flash("Company settings saved.", "success")
        finally:
            conn.close()
        return redirect(url_for("company_settings"))

    bonus = get_company_setting("annual_bonus", "0")
    incentive = get_company_setting("monthly_incentive", "0")
    return render_template("settings.html", annual_bonus=bonus, monthly_incentive=incentive)


# ═══════════════════════════════════════════
# PDF PAYSLIP GENERATION
# ═══════════════════════════════════════════

@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/pdf")
@login_required
def download_payslip_pdf(year, month, employee_id):
    """Generate and download a professional PDF payslip."""
    from io import BytesIO
    from xhtml2pdf import pisa

    employee = fetch_employee_or_none(employee_id)
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("payroll_dashboard"))

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM payroll WHERE employee_id=%s AND year=%s AND month=%s;",
                        (employee_id, year, month))
            payslip = cur.fetchone()
    finally:
        conn.close()

    if payslip is None:
        flash("No payroll record found.", "error")
        return redirect(url_for("payroll_dashboard", year=year, month=month))

    month_name = calendar.month_name[month]
    html = render_template("payslip_pdf.html", employee=employee, payslip=payslip,
                           year=year, month=month, month_name=month_name)

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        flash("Error generating PDF.", "error")
        return redirect(url_for("view_payslip", year=year, month=month, employee_id=employee_id))

    pdf_buffer.seek(0)
    filename = f"Payslip_{employee['first_name']}_{employee['last_name']}_{month_name}_{year}.pdf"

    from flask import send_file
    return send_file(pdf_buffer, mimetype="application/pdf",
                     as_attachment=True, download_name=filename)


# ═══════════════════════════════════════════
# BANK PAYMENT FILE & PAYMENT TRACKING
# ═══════════════════════════════════════════

@app.route("/payroll/<int:year>/<int:month>/bank-file")
@login_required
@role_required("Admin", "Finance")
def generate_bank_file(year, month):
    """Generate a CSV bank payment file for all payroll records of the month."""
    import csv
    from io import StringIO

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.*, e.first_name, e.last_name, e.email,
                       e.bank_name, e.bank_branch, e.bank_account_number,
                       e.payment_method, e.employee_category
                FROM payroll p
                JOIN employees e ON p.employee_id = e.id
                WHERE p.year = %s AND p.month = %s AND p.net_salary > 0
                ORDER BY e.last_name, e.first_name;
            """, (year, month))
            records = cur.fetchall()
    finally:
        conn.close()

    if not records:
        flash("No payroll records found for this period.", "error")
        return redirect(url_for("payroll_dashboard", year=year, month=month))

    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "Payment Reference", "Employee ID", "Employee Name", "Bank Name",
        "Bank Branch", "Account Number", "Payment Method", "Net Salary (LKR)",
        "Pay Period", "Payment Status"
    ])

    month_name = calendar.month_name[month]
    for rec in records:
        ref = f"PAY-{year}{month:02d}-{rec['employee_id']:04d}"
        writer.writerow([
            ref,
            f"EMP-{rec['employee_id']:04d}",
            f"{rec['first_name']} {rec['last_name']}",
            rec["bank_name"] or "",
            rec["bank_branch"] or "",
            rec["bank_account_number"] or "",
            rec["payment_method"] or "Bank Transfer",
            f"{float(rec['net_salary']):.2f}",
            f"{month_name} {year}",
            rec.get("payment_status", "Pending"),
        ])

    # Summary
    total_net = sum(float(r["net_salary"]) for r in records)
    writer.writerow([])
    writer.writerow(["TOTAL", "", f"{len(records)} employees", "", "", "", "", f"{total_net:.2f}", "", ""])

    output.seek(0)
    filename = f"Bank_Payment_{month_name}_{year}.csv"

    from flask import Response
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/mark-paid", methods=["POST"])
@login_required
@role_required("Admin", "Finance")
def mark_payslip_paid(year, month, employee_id):
    """Mark an individual payslip as paid."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            ref = f"PAY-{year}{month:02d}-{employee_id:04d}"
            cur.execute("""
                UPDATE payroll SET payment_status = 'Paid', payment_date = CURRENT_DATE,
                    payment_reference = %s, status = 'Paid'
                WHERE employee_id = %s AND year = %s AND month = %s;
            """, (ref, employee_id, year, month))
        conn.commit()
        flash("Payment recorded.", "success")
    finally:
        conn.close()
    return redirect(url_for("view_payslip", year=year, month=month, employee_id=employee_id))


@app.route("/payroll/<int:year>/<int:month>/mark-all-paid", methods=["POST"])
@login_required
@role_required("Admin", "Finance")
def mark_all_paid(year, month):
    """Mark all payslips for a month as paid."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE payroll SET payment_status = 'Paid', payment_date = CURRENT_DATE,
                    payment_reference = 'PAY-' || %s || lpad(%s::text, 2, '0') || '-' || lpad(employee_id::text, 4, '0'),
                    status = 'Paid'
                WHERE year = %s AND month = %s AND payment_status != 'Paid';
            """, (str(year), month, year, month))
            count = cur.rowcount
        conn.commit()
        flash(f"{count} payslip(s) marked as paid.", "success")
    finally:
        conn.close()
    return redirect(url_for("payroll_dashboard", year=year, month=month))


@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/approve", methods=["POST"])
@login_required
@role_required("Admin", "Finance")
def approve_payslip(year, month, employee_id):
    """Finance approves a draft payslip."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE payroll SET status = 'Approved'
                WHERE employee_id = %s AND year = %s AND month = %s AND status = 'Draft';
            """, (employee_id, year, month))
        conn.commit()
        flash("Payslip approved.", "success")
    finally:
        conn.close()
    return redirect(url_for("view_payslip", year=year, month=month, employee_id=employee_id))

@app.route("/payroll/<int:year>/<int:month>/approve-all", methods=["POST"])
@login_required
@role_required("Admin", "Finance")
def approve_all(year, month):
    """Finance approves all draft payslips for a month."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE payroll SET status = 'Approved'
                WHERE year = %s AND month = %s AND status = 'Draft';
            """, (year, month))
            count = cur.rowcount
        conn.commit()
        flash(f"{count} payslip(s) approved.", "success")
    finally:
        conn.close()
    return redirect(url_for("payroll_dashboard", year=year, month=month))


@app.route("/advances-loans")
@login_required
@role_required("Admin", "HR")
def advances_loans():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, first_name, last_name, salary FROM employees WHERE employment_status = 'Active' ORDER BY first_name;")
            employees = cur.fetchall()
            
            cur.execute("""
                SELECT a.*, e.first_name, e.last_name 
                FROM advances a JOIN employees e ON a.employee_id = e.id 
                ORDER BY a.created_at DESC
            """)
            advances = cur.fetchall()
            
            cur.execute("""
                SELECT l.*, e.first_name, e.last_name 
                FROM loans l JOIN employees e ON l.employee_id = e.id 
                ORDER BY l.created_at DESC
            """)
            loans = cur.fetchall()
    finally:
        conn.close()
    return render_template("advances_loans.html", employees=employees, advances=advances, loans=loans)

@app.route("/advances/new", methods=["POST"])
@login_required
@role_required("Admin", "HR")
def create_advance():
    employee_id = request.form.get("employee_id")
    amount = float(request.form.get("amount") or 0)
    reason = request.form.get("reason", "")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT salary FROM employees WHERE id = %s", (employee_id,))
            emp = cur.fetchone()
            max_advance = float(emp["salary"]) * 0.40
            if amount > max_advance:
                flash(f"Advance amount exceeds 40% of salary ({max_advance:.2f}).", "error")
                return redirect(url_for("advances_loans"))
            
            cur.execute(
                "INSERT INTO advances (employee_id, amount, reason) VALUES (%s, %s, %s)",
                (employee_id, amount, reason)
            )
        conn.commit()
        flash("Advance request created.", "success")
    finally:
        conn.close()
    return redirect(url_for("advances_loans"))

@app.route("/advances/<int:id>/update", methods=["POST"])
@login_required
@role_required("Admin", "HR")
def update_advance(id):
    status = request.form.get("status")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE advances SET status = %s WHERE id = %s", (status, id))
        conn.commit()
        flash(f"Advance {status.lower()}.", "success")
    finally:
        conn.close()
    return redirect(url_for("advances_loans"))

@app.route("/loans/new", methods=["POST"])
@login_required
@role_required("Admin", "HR")
def create_loan():
    employee_id = request.form.get("employee_id")
    amount = float(request.form.get("amount") or 0)
    installments = int(request.form.get("installments") or 1)
    reason = request.form.get("reason", "")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT salary FROM employees WHERE id = %s", (employee_id,))
            emp = cur.fetchone()
            max_loan = float(emp["salary"]) * 2
            if amount > max_loan:
                flash(f"Loan amount exceeds 2x salary ({max_loan:.2f}).", "error")
                return redirect(url_for("advances_loans"))
            if installments < 1 or installments > 12:
                flash("Installments must be between 1 and 12.", "error")
                return redirect(url_for("advances_loans"))
            
            monthly_installment = round(amount / installments, 2)
            
            cur.execute(
                """INSERT INTO loans (employee_id, amount, installments, monthly_installment, remaining_amount, remaining_installments, reason)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (employee_id, amount, installments, monthly_installment, amount, installments, reason)
            )
        conn.commit()
        flash("Loan request created.", "success")
    finally:
        conn.close()
    return redirect(url_for("advances_loans"))

@app.route("/loans/<int:id>/update", methods=["POST"])
@login_required
@role_required("Admin", "HR")
def update_loan(id):
    status = request.form.get("status")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE loans SET status = %s WHERE id = %s", (status, id))
        conn.commit()
        flash(f"Loan {status.lower()}.", "success")
    finally:
        conn.close()
    return redirect(url_for("advances_loans"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)