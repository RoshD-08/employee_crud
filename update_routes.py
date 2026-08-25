import re

def update_file():
    with open('app.py', 'r') as f:
        content = f.read()

    replacements = [
        (r'(@app\.route\("/"\)\n)def list_employees', r'\1@login_required\ndef list_employees'),
        (r'(@app\.route\("/employees/new".*\n)def add_employee', r'\1@login_required\n@role_required("Admin", "HR")\ndef add_employee'),
        (r'(@app\.route\("/employees/<int:employee_id>/edit".*\n)def edit_employee', r'\1@login_required\n@role_required("Admin", "HR")\ndef edit_employee'),
        (r'(@app\.route\("/employees/<int:employee_id>/delete".*\n)def delete_employee', r'\1@login_required\n@role_required("Admin", "HR")\ndef delete_employee'),
        (r'(@app\.route\("/employees/<int:employee_id>"\)\n)def view_employee', r'\1@login_required\ndef view_employee'),
        (r'(@app\.route\("/map"\)\n)def employees_map', r'\1@login_required\ndef employees_map'),
        (r'(@app\.route\("/api/reverse-geocode"\)\n)def reverse_geocode', r'\1@login_required\ndef reverse_geocode'),
        
        # Attendance routes
        (r'(@app\.route\("/employees/<int:employee_id>/attendance/<int:year>/<int:month>"\)\n)def employee_attendance', r'\1@login_required\ndef employee_attendance'),
        (r'(@app\.route\("/employees/<int:employee_id>/attendance/<int:year>/<int:month>", methods=\["POST"\]\)\n)def save_attendance', r'\1@login_required\n@role_required("Admin", "HR")\ndef save_attendance'),
        
        # Payroll routes
        (r'(@app\.route\("/payroll"\)\n)def payroll_dashboard', r'\1@login_required\ndef payroll_dashboard'),
        (r'(@app\.route\("/payroll/generate/<int:year>/<int:month>", methods=\["POST"\]\)\n)def generate_payroll', r'\1@login_required\n@role_required("Admin", "HR")\ndef generate_payroll'),
        (r'(@app\.route\("/payroll/<int:year>/<int:month>/<int:employee_id>"\)\n)def view_payslip', r'\1@login_required\ndef view_payslip'),
        (r'(@app\.route\("/payroll/<int:year>/<int:month>/<int:employee_id>/update", methods=\["POST"\]\)\n)def update_payslip', r'\1@login_required\n@role_required("Admin", "HR")\ndef update_payslip'),
        
        # Settings
        (r'(@app\.route\("/settings", methods=\["GET", "POST"\]\)\n)def company_settings', r'\1@login_required\n@role_required("Admin")\ndef company_settings'),
        
        # PDF & Bank routes
        (r'(@app\.route\("/payroll/<int:year>/<int:month>/<int:employee_id>/pdf"\)\n)def download_payslip_pdf', r'\1@login_required\ndef download_payslip_pdf'),
        (r'(@app\.route\("/payroll/<int:year>/<int:month>/bank-file"\)\n)def generate_bank_file', r'\1@login_required\n@role_required("Admin", "Finance")\ndef generate_bank_file'),
        (r'(@app\.route\("/payroll/<int:year>/<int:month>/<int:employee_id>/mark-paid", methods=\["POST"\]\)\n)def mark_payslip_paid', r'\1@login_required\n@role_required("Admin", "Finance")\ndef mark_payslip_paid'),
        (r'(@app\.route\("/payroll/<int:year>/<int:month>/mark-all-paid", methods=\["POST"\]\)\n)def mark_all_paid', r'\1@login_required\n@role_required("Admin", "Finance")\ndef mark_all_paid'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    with open('app.py', 'w') as f:
        f.write(content)

update_file()
