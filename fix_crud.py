import re

with open('app.py', 'r') as f:
    content = f.read()

# Modify add_employee
add_employee_code = """
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
                        photo_filename = handle_photo_upload(file)
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
                    elif "esi_number" in err_msg:
                        errors.append("An employee with that ESI Number already exists.")
                    else:
                        errors.append("A unique constraint violation occurred.")
                finally:
                    conn.close()
        for e in errors: flash(e, "error")
        return render_template("add_employee.html", employee=data, **_form_constants()), 400
    return render_template("add_employee.html", employee={}, **_form_constants())
"""

content = re.sub(r'def add_employee\(\):.*?return render_template\("add_employee\.html", employee=\{\}, \*\*_form_constants\(\)\)', add_employee_code.strip(), content, flags=re.DOTALL)

# Modify edit_employee
edit_employee_code = """
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
                        new_photo = handle_photo_upload(file)
                        if new_photo:
                            photo_filename = new_photo
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
                    elif "esi_number" in err_msg:
                        errors.append("An employee with that ESI Number already exists.")
                    else:
                        errors.append("A unique constraint violation occurred.")
                finally:
                    conn.close()
        for e in errors: flash(e, "error")
        return render_template("add_employee.html", employee=existing, **_form_constants()), 400
    return render_template("add_employee.html", employee=existing, **_form_constants())
"""

content = re.sub(r'def edit_employee\(employee_id\):.*?return render_template\("add_employee\.html", employee=existing, \*\*_form_constants\(\)\)', edit_employee_code.strip(), content, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(content)

