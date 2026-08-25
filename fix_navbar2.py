with open('templates/base.html', 'r') as f:
    content = f.read()

payroll_link = """          <a href="{{ url_for('payroll_dashboard') }}"
             class="inline-flex items-center gap-2 border border-white/25 hover:bg-white/10 text-white text-sm font-semibold px-4 py-2 rounded-md">
            Payroll
          </a>"""

attendance_link = """
          <a href="{{ url_for('attendance_dashboard') }}"
             class="inline-flex items-center gap-2 border border-white/25 hover:bg-white/10 text-white text-sm font-semibold px-4 py-2 rounded-md">
            Attendance
          </a>"""

if payroll_link in content:
    content = content.replace(payroll_link, payroll_link + attendance_link)
    with open('templates/base.html', 'w') as f:
        f.write(content)
        print("Success")
else:
    print("Failed to find payroll_link block")
