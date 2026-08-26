import re

with open('app.py', 'r') as f:
    content = f.read()

old_code = """                # Bonus: yearly, applied in December only
                month_bonus = bonus if month == 12 else 0

                gross = basic + total_allowances + ot_payment + month_bonus + incentive
                total_deductions = epf_employee + no_pay_deduction
                net = gross - total_deductions"""

new_code = """                # Bonus: yearly, applied in December only
                month_bonus = bonus if month == 12 else 0

                gross = basic + total_allowances + ot_payment + month_bonus + incentive

                # --- Advances Deduction ---
                cur.execute("SELECT id, amount FROM advances WHERE employee_id = %s AND status = 'Approved'", (eid,))
                new_advances = cur.fetchall()
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
                net = gross - total_deductions"""

if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Now we need to update the INSERT statement in app.py
    # Change: VALUES (%s,%s,%s, %s,%s, %s,%s,%s, %s,%s,%s,%s, %s,%s,0,0, 0,%s, %s,%s,%s,
    # To: VALUES (%s,%s,%s, %s,%s, %s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, 0,%s, %s,%s,%s,
    # And add salary_advance, loan_deduction to the parameter tuple
    
    insert_old = """                    VALUES (%s,%s,%s, %s,%s, %s,%s,%s, %s,%s,%s,%s, %s,%s,0,0, 0,%s, %s,%s,%s,
                            %s,%s,%s,%s, %s,%s,%s,%s, 'Draft')"""
    insert_new = """                    VALUES (%s,%s,%s, %s,%s, %s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, 0,%s, %s,%s,%s,
                            %s,%s,%s,%s, %s,%s,%s,%s, 'Draft')"""
    content = content.replace(insert_old, insert_new)
    
    conflict_update_old = """                        epf_employee=EXCLUDED.epf_employee, no_pay_deduction=EXCLUDED.no_pay_deduction,
                        total_deductions=EXCLUDED.total_deductions,"""
    conflict_update_new = """                        epf_employee=EXCLUDED.epf_employee, no_pay_deduction=EXCLUDED.no_pay_deduction,
                        salary_advance=EXCLUDED.salary_advance, loan_deduction=EXCLUDED.loan_deduction,
                        total_deductions=EXCLUDED.total_deductions,"""
    content = content.replace(conflict_update_old, conflict_update_new)

    params_old = """                      epf_employee, no_pay_deduction, total_deductions,
                      epf_employer, etf_employer, net,"""
    params_new = """                      epf_employee, no_pay_deduction, salary_advance, loan_deduction, total_deductions,
                      epf_employer, etf_employer, net,"""
    content = content.replace(params_old, params_new)

    with open('app.py', 'w') as f:
        f.write(content)
    print("Payroll logic updated successfully.")
else:
    print("Code snippet not found, maybe already updated.")
