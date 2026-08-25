import re

with open('templates/base.html', 'r') as f:
    content = f.read()

# Find the navbar links block
# It looks like:
#           <a href="{{ url_for('list_employees') }}" class="inline-flex items-center ...">Employees</a>
#           <a href="{{ url_for('payroll_dashboard') }}" class="inline-flex items-center ...">Payroll</a>

attendance_link = """
          <a href="{{ url_for('attendance_dashboard') }}" class="inline-flex items-center px-1 pt-1 border-b-2 {% if request.endpoint == 'attendance_dashboard' %}border-accent text-ink{% else %}border-transparent text-ink/70 hover:border-line hover:text-ink{% endif %} text-sm font-medium transition-colors">
            Attendance
          </a>
"""

# Insert it after Payroll
pattern = r'(<a href="\{\{ url_for\(\'payroll_dashboard\'\) \}\}"[^>]+>Payroll</a>)'
content = re.sub(pattern, r'\1' + attendance_link, content)

with open('templates/base.html', 'w') as f:
    f.write(content)

