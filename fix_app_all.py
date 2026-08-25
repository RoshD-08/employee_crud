import re

with open('app.py', 'r') as f:
    content = f.read()

# Replace any decorators that were placed directly after a def statement
# For example:
# def save_attendance(employee_id, year, month):
# @login_required
# @role_required("Admin", "HR")
#
#    employee = fetch_employee_or_none(employee_id)

pattern = r'(def [a-zA-Z0-9_]+\(.*?\):)\n(@login_required\n)?(@role_required\(".*?"(, ".*?")*\)\n)?\n*'
replacement = r'\1\n'

content = re.sub(pattern, replacement, content)

with open('app.py', 'w') as f:
    f.write(content)

