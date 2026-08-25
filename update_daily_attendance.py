import re

with open('app.py', 'r') as f:
    content = f.read()

new_routes = """
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
"""

pattern = r'(# ═══════════════════════════════════════════\n# ATTENDANCE ROUTES)'
content = re.sub(pattern, r'\1\n' + new_routes, content)

with open('app.py', 'w') as f:
    f.write(content)

