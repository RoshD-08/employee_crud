import re

with open('app.py', 'r') as f:
    content = f.read()

new_route = """
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

"""

# Insert before '# ═══════════════════════════════════════════\n# PAYROLL ROUTES'
pattern = r'(# ═══════════════════════════════════════════\n# PAYROLL ROUTES)'
content = re.sub(pattern, new_route + r'\n\1', content)

with open('app.py', 'w') as f:
    f.write(content)

