import re

with open('templates/attendance.html', 'r') as f:
    content = f.read()

content = content.replace("{{ employee.name }}'s Attendance", "{{ employee.first_name }} {{ employee.last_name }}'s Attendance")

with open('templates/attendance.html', 'w') as f:
    f.write(content)

