with open('app.py', 'r') as f:
    content = f.read()

content = content.replace("def employee_attendance(employee_id, year, month):\n@login_required\n\n    employee =", "def employee_attendance(employee_id, year, month):\n    employee =")

with open('app.py', 'w') as f:
    f.write(content)

