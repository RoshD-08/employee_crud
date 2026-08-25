with open('templates/base.html', 'r') as f:
    content = f.read()

# Replace url_for('attendance_dashboard') with url_for('daily_attendance') in the navbar
content = content.replace("url_for('attendance_dashboard')", "url_for('daily_attendance')")

with open('templates/base.html', 'w') as f:
    f.write(content)

