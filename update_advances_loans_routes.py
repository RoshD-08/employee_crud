import re

with open('app.py', 'r') as f:
    content = f.read()

# Make sure we don't insert twice
if '/advances-loans' not in content:
    routes_code = """
@app.route("/advances-loans")
@login_required
@role_required("Admin", "HR")
def advances_loans():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, first_name, last_name, salary FROM employees WHERE employment_status = 'Active' ORDER BY first_name;")
            employees = cur.fetchall()
            
            cur.execute(\"""
                SELECT a.*, e.first_name, e.last_name 
                FROM advances a JOIN employees e ON a.employee_id = e.id 
                ORDER BY a.created_at DESC
            \""")
            advances = cur.fetchall()
            
            cur.execute(\"""
                SELECT l.*, e.first_name, e.last_name 
                FROM loans l JOIN employees e ON l.employee_id = e.id 
                ORDER BY l.created_at DESC
            \""")
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
                \"""INSERT INTO loans (employee_id, amount, installments, monthly_installment, remaining_amount, remaining_installments, reason)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)\""",
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
"""
    content = content.replace('if __name__ == "__main__":', routes_code + '\nif __name__ == "__main__":')
    with open('app.py', 'w') as f:
        f.write(content)
    print("Routes added successfully.")
else:
    print("Routes already present.")
