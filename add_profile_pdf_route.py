import re

with open('app.py', 'r') as f:
    content = f.read()

route_code = """
@app.route("/employees/<int:id>/pdf")
@login_required
def download_profile_pdf(id):
    from io import BytesIO
    from xhtml2pdf import pisa

    employee = fetch_employee_or_none(id)
    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for('list_employees'))

    html = render_template("profile_pdf.html", employee=employee)
    
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    
    if pisa_status.err:
        flash("Error generating PDF.", "error")
        return redirect(url_for('view_employee', id=id))
        
    pdf_buffer.seek(0)
    filename = f"Employee_Profile_{employee['first_name']}_{employee['last_name']}.pdf"
    
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
"""

# Insert before download_payslip_pdf
content = content.replace('def download_payslip_pdf', route_code + '\n@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/pdf")\n@login_required\n@role_required("Admin", "HR")\ndef download_payslip_pdf')

with open('app.py', 'w') as f:
    f.write(content)

